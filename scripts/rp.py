#!/usr/bin/env python3
"""Command-line helpers for the research-paper skill (standard library only).

  python3 scripts/rp.py new "<project name>"
  python3 scripts/rp.py status <project>
  python3 scripts/rp.py search "<query>" [--limit 10] [--year-from 2023] [--sources openalex arxiv semantic_scholar]
  python3 scripts/rp.py addref <project> <DOI | arXiv ID | OpenAlex W-ID> [--key KEY]
  python3 scripts/rp.py rmref <project> <key>
  python3 scripts/rp.py approve <project> novelty|structure --quote "<user's exact words>"
  python3 scripts/rp.py stage <project> idea|novelty|structure|drafting|review [--title T] [--verdict V]
  python3 scripts/rp.py check <project>        # cite keys vs .bib, labels vs refs, missing inputs/figures
  python3 scripts/rp.py compile <project>      # latexmk/pdflatex if installed, then `check`

  1st-draft skill:
  python3 scripts/rp.py draft1-start <project>   # snapshot sources to versions/vN/, lock .tex edits until plan approval
  python3 scripts/rp.py approve <project> draftplan --quote "<user's exact words>"
  python3 scripts/rp.py symbols <project>        # every math symbol: first use, count, sections
  python3 scripts/rp.py lint <project>           # sections, short subsections, banned phrases, sentence stats, refs
  python3 scripts/rp.py diff <project> [--from vN]  # latexdiff (if installed) + word diff in notes/
  python3 scripts/rp.py draft1-done <project>

  Layout and figures (both skills):
  python3 scripts/rp.py layout <project> [--log main.log]  # overfull equations/tables from the LaTeX log + static estimate
  python3 scripts/rp.py render <project> [--pages 1-4] [--figures]  # PNGs of PDF pages / figure files to look at
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rp_agent import literature, texscan  # noqa: E402
from rp_agent.project import STAGE_LABELS, STAGES, Project  # noqa: E402

LAST_PROMPT = ROOT / ".claude" / "last_user_prompt.txt"


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def existing(name: str) -> Project:
    if name not in Project.list_all():
        die(f"No project '{name}'. Existing: {', '.join(Project.list_all()) or 'none'}")
    return Project.open(name)


# ------------------------------------------------------------------ commands

def cmd_new(a):
    p = Project.open(a.name)
    print(f"Project folder: papers/{p.name}/  (use '{p.name}' in later commands)")


def cmd_status(a):
    p = existing(a.project)
    s = p.state
    cur = STAGES.index(s.stage)
    for i, st in enumerate(STAGES):
        print(("[x] " if i < cur else "[>] " if i == cur else "[ ] ") + STAGE_LABELS[st])
    print(f"novelty_approved={s.novelty_approved}  structure_approved={s.structure_approved}")
    if s.working_title:
        print(f"working title: {s.working_title}")
    if s.novelty_verdict:
        print(f"novelty verdict: {s.novelty_verdict}")
    print("files:", ", ".join(p.list_files()) or "(none)")


def cmd_search(a):
    res = literature.search_literature(a.query, a.limit, a.year_from, a.sources)
    print(f"Query: {res['query']} — {res['count']} results")
    for i, r in enumerate(res["results"], 1):
        ident = r.get("doi") or (f"arXiv:{r['id']}" if r["source"] == "arxiv" else r.get("arxiv") or r["id"])
        authors = ", ".join(r["authors"][:4]) + (" et al." if len(r["authors"]) > 4 else "")
        print(f"\n[{i}] {r['title']} ({r['year']})\n    {authors} | {r['venue']} | id: {ident} | cited by: {r['citations']}"
              f"\n    Abstract: {r['abstract'] or '(not available)'}")
    if res["notes"]:
        print("\nNotes: " + "; ".join(res["notes"]))


def cmd_addref(a):
    p = existing(a.project)
    bib = p.root / "references.bib"
    text = bib.read_text() if bib.exists() else ""
    ident_norm = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:|arxiv:)", "", a.identifier.strip(), flags=re.I).lower()
    if ident_norm and ident_norm in text.lower():
        print(f"Already in references.bib. Keys: {', '.join(literature.bib_keys(text))}")
        return
    try:
        key, entry = literature.bibtex_entry(a.identifier, a.key)
    except Exception as e:
        die(f"Could not fetch BibTeX for '{a.identifier}': {e}")
    keys = literature.bib_keys(text)
    base, n = key, 0
    while key in keys:
        key = f"{base}{chr(ord('a') + n)}"
        n += 1
    if key != base:
        entry = re.sub(r"^(@\w+\{)[^,]+,", lambda m: f"{m.group(1)}{key},", entry, count=1)
    bib.write_text(text.rstrip() + ("\n\n" if text.strip() else "") + entry + "\n")
    title = re.search(r"title\s*=\s*\{(.+?)\},?\n", entry)
    print(f"Added \\cite{{{key}}} — {title.group(1) if title else a.identifier}")


def cmd_rmref(a):
    p = existing(a.project)
    bib = p.root / "references.bib"
    text = bib.read_text() if bib.exists() else ""
    new, n = re.subn(r"@\w+\s*\{\s*" + re.escape(a.key) + r"\s*,.*?\n\}\s*", "", text, flags=re.S)
    if not n:
        die(f"No entry with key '{a.key}'.")
    bib.write_text(new)
    print(f"Removed {a.key}.")


def cmd_approve(a):
    p = existing(a.project)
    quote = a.quote.strip().strip('"').strip()
    norm = lambda s: " ".join(s.lower().split())
    if not quote:
        die("Give the user's approval words with --quote.")
    if LAST_PROMPT.exists():
        if norm(quote) not in norm(LAST_PROMPT.read_text(errors="replace")):
            die("The quote must be copied word for word from the user's latest message. If the user has not clearly "
                "approved yet, ask them.")
        verified = True
    else:
        # Hooks did not load (e.g. the repository was attached after the session started), so the user's message
        # was not captured. Record the approval, but flag it as not machine-checked.
        print("NOTE: hooks are not active in this session, so the quote could not be checked automatically. "
              "Only record approvals the user really gave, in their own words.")
        verified = False
    if a.gate == "structure" and not p.state.novelty_approved:
        die("Novelty must be approved before the structure.")
    if a.gate == "draftplan":
        if p.state.draft1_status != "audit":
            die("Run `rp.py draft1-start` and present the audit and restructuring plan before approving it.")
        p.state.draft1_status = "editing"
    else:
        setattr(p.state, f"{a.gate}_approved", True)
    p.state.approvals.append({"gate": a.gate, "quote": quote, "verified_by_hook": verified})
    p.save_state()
    print(f"Recorded the user's approval for '{a.gate}'.")


def cmd_stage(a):
    p = existing(a.project)
    i = STAGES.index(a.stage)
    if i >= STAGES.index("structure") and not p.state.novelty_approved:
        die("Cannot move past 'novelty' until the user approves the novelty assessment.")
    if i >= STAGES.index("drafting") and not p.state.structure_approved:
        die("Cannot start drafting until the user approves the titles and structure.")
    p.state.stage = a.stage
    if a.title:
        p.state.working_title = a.title
    if a.verdict:
        p.state.novelty_verdict = a.verdict
    p.save_state()
    print(f"Stage: {STAGE_LABELS[a.stage]}")


def _strip_comments(tex: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", tex)


def run_check(p: Project) -> int:
    main = p.root / "main.tex"
    if not main.exists():
        die("main.tex does not exist yet.")
    tex_files, queue = [], [main]
    problems = []
    while queue:
        f = queue.pop()
        tex_files.append(f)
        for inc in re.findall(r"\\(?:input|include)\{([^}]+)\}", _strip_comments(f.read_text(errors="replace"))):
            g = p.root / (inc if inc.endswith(".tex") else inc + ".tex")
            if g.exists():
                queue.append(g)
            else:
                problems.append(f"missing \\input file: {inc} (in {f.relative_to(p.root)})")
    src = "\n".join(_strip_comments(f.read_text(errors="replace")) for f in tex_files)

    bib = p.root / "references.bib"
    bib_keys = set(literature.bib_keys(bib.read_text())) if bib.exists() else set()
    cites = set()
    for group in re.findall(r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", src):
        cites.update(k.strip() for k in group.split(",") if k.strip())
    for k in sorted(cites - bib_keys):
        problems.append(f"\\cite key not in references.bib: {k}")
    unused = sorted(bib_keys - cites)

    labels = set(re.findall(r"\\label\{([^}]+)\}", src))
    refs = set()
    for group in re.findall(r"\\(?:ref|eqref|cref|Cref|autoref|pageref)\{([^}]+)\}", src):
        refs.update(k.strip() for k in group.split(","))
    for k in sorted(refs - labels):
        problems.append(f"reference to undefined label: {k}")
    for dup in sorted({l for l in re.findall(r"\\label\{([^}]+)\}", src)
                       if re.findall(r"\\label\{([^}]+)\}", src).count(l) > 1}):
        problems.append(f"duplicate label: {dup}")

    for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", src):
        cands = [p.root / g] + [p.root / (g + ext) for ext in (".pdf", ".png", ".jpg", ".eps")]
        if not any(c.exists() for c in cands):
            problems.append(f"missing figure file: {g} (use \\figplaceholder until it exists)")

    begins = re.findall(r"\\begin\{([^}]+)\}", src)
    ends = re.findall(r"\\end\{([^}]+)\}", src)
    for env in sorted(set(begins) | set(ends)):
        if begins.count(env) != ends.count(env):
            problems.append(f"unbalanced environment '{env}': {begins.count(env)} begin vs {ends.count(env)} end")

    todos = len(re.findall(r"\\TODO\{", src))
    print(f"Checked {len(tex_files)} .tex files, {len(cites)} cited keys, {len(bib_keys)} .bib entries, "
          f"{len(labels)} labels, {todos} \\TODO items.")
    if unused:
        print("Unused .bib entries (fine if the Introduction will cite them): " + ", ".join(unused))
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems))
    else:
        print("No problems found.")
    return 1 if problems else 0


def cmd_check(a):
    sys.exit(run_check(existing(a.project)))


def cmd_compile(a):
    p = existing(a.project)
    if shutil.which("latexmk"):
        cmds = [["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]]
    elif shutil.which("pdflatex"):
        pdf = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        cmds = [pdf, ["bibtex", "main"], pdf, pdf]
    else:
        print("No LaTeX installation found; running static checks only. (Compile on Overleaf to get the PDF.)")
        sys.exit(run_check(p))
    for c in cmds:
        proc = subprocess.run(c, cwd=p.root, capture_output=True, text=True, timeout=300)
        if proc.returncode != 0 and c[0] != "bibtex":
            print(f"{c[0]} FAILED")
            break
    log = (p.root / "main.log").read_text(errors="replace") if (p.root / "main.log").exists() else ""
    issues = [l for l in log.splitlines() if l.startswith("!") or "undefined" in l.lower()]
    print("\n".join(dict.fromkeys(issues)) or "No LaTeX errors or undefined references.")
    print("PDF:", "papers/" + p.name + "/main.pdf" if (p.root / "main.pdf").exists() else "not produced")
    overfull = texscan.overfull_from_log(log)
    print("Overfull boxes / oversized floats:\n  " + "\n  ".join(overfull) if overfull else "No overfull boxes.")
    sys.exit(run_check(p))


# ------------------------------------------------------------------ 1st-draft skill

SOURCE_SUFFIXES = {".tex", ".bib", ".bst", ".cls", ".sty"}


def _sources(p: Project) -> list[str]:
    return [f for f in p.list_files()
            if Path(f).suffix in SOURCE_SUFFIXES and not f.startswith("versions/") and not f.endswith("Notes.bib")]


def cmd_draft1_start(a):
    p = existing(a.project)
    if not (p.root / "main.tex").exists():
        die("main.tex does not exist; write the paper with the research-paper skill first.")
    vdir = p.root / "versions"
    n = 0
    while (vdir / f"v{n}").exists():
        n += 1
    snap = vdir / f"v{n}"
    for rel in _sources(p):
        dst = snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p.root / rel, dst)
    p.state.draft1_status = "audit"
    p.save_state()
    print(f"Snapshot of {len(_sources(p))} source files saved to papers/{p.name}/versions/v{n}/ (never edit it).")
    print("LaTeX edits are locked until the user approves the audit and restructuring plan "
          "(rp.py approve <project> draftplan --quote ...).")


def cmd_draft1_done(a):
    p = existing(a.project)
    p.state.draft1_status = "done"
    p.save_state()
    print("1st draft marked done.")


def cmd_symbols(a):
    p = existing(a.project)
    lines = texscan.collect(p.root)
    table = texscan.symbols(lines)
    print(f"{len(table)} distinct math tokens, in order of first appearance "
          f"(token | first use | count | sections). Macros defined in main.tex are listed by name.")
    for tok, e in table.items():
        print(f"{tok:28s} {e['first']:40s} {e['count']:4d}  {' / '.join(s[:30] for s in e['sections'])}")
    defs = re.findall(r"\\(?:newcommand|renewcommand|DeclareMathOperator)\*?\{?(\\[A-Za-z]+)\}?(?:\[\d\])?\{(.+)\}",
                      (p.root / "main.tex").read_text(errors="replace"))
    if defs:
        print("\nUser macros (main.tex):")
        for name, body in defs:
            print(f"  {name} -> {body[:60]}")


def cmd_lint(a):
    p = existing(a.project)
    r = texscan.lint(texscan.collect(p.root))
    st = r["stats"]
    print(f"Main sections: {st.get('main_sections')} (target 6-7)")
    for s in r["sections"]:
        print(f"  - {s['title']}  [{s['where']}]")
    print(f"\nSentences: {st.get('sentences')}, mean {st.get('mean_sentence_words')} words, "
          f"{st.get('share_under_12_words')} under 12 words, {st.get('share_over_40_words')} over 40 words")
    print(f"Equation references: {st.get('equation_refs')}, figure references: {st.get('figure_refs')}")
    def block(title, items):
        print(f"\n{title} ({len(items)}):")
        for it in items[:80]:
            print("  " + (it if isinstance(it, str) else str(it)))
    block("Short subsections (<150 words; merge candidates)",
          [f"{s['title']} — {s['words']} words [{s['where']}]" for s in r["short_subsections"]])
    block("Banned or suspect phrases", r["banned"])
    block("Very long sentences (>50 words)", r["long_sentences"])
    block("Labels never referenced", r["unreferenced_labels"])
    block("Figure citation order", r["figure_order"])
    sc = texscan.style_check(texscan.collect(p.root))
    block("House style: titled paragraphs or bold lead-ins (fold into running prose)", sc["paragraph_titles"])
    block("House style: italic/bold in the text", sc["emphasis"])
    block("House style: remark/lemma/proposition/definition environments (discuss in prose; heavy maths to an appendix)",
          sc["theorem_envs"])
    block("House style: citation wording ('Ref. [n]', 'in [n]'; write 'studied by Author et al. [n]')",
          sc["citation_wording"])
    block("House style: mixed cross-reference or citation styles", sc["crossref_mix"])
    block("House style: acronyms not spelled out at first use", sc["acronyms"])
    block("House style: section openers that announce contents", sc["roadmap_openers"])
    block("House style: short paragraphs (<60 words; merge into fuller paragraphs)", sc["short_paragraphs"])
    block("House style: bridging words that need a justification next to them ('by symmetry', 'can be expressed as', ...)",
          sc["bridging_words"])
    block("\\finding blocks", [f"{'cited' if f['cited_in_paragraph'] else 'NO CITATION in paragraph'}: "
                               f"{f['text'][:100]}" for f in r["findings"]])


def cmd_diff(a):
    p = existing(a.project)
    vdir = p.root / "versions"
    versions = sorted((d.name for d in vdir.iterdir() if d.is_dir()), key=lambda v: int(v[1:])) if vdir.exists() else []
    if not versions:
        die("No snapshot found; run draft1-start first.")
    base = vdir / (a.from_ or versions[-1])
    if not base.exists():
        die(f"No snapshot {a.from_}. Available: {', '.join(versions)}")
    notes = p.root / "notes"
    notes.mkdir(exist_ok=True)
    out = notes / f"draft1_word_diff_{base.name}.txt"
    chunks = []
    for rel in sorted(set(_sources(p)) | {str(f.relative_to(base)) for f in base.rglob("*") if f.is_file()}):
        old, new = base / rel, p.root / rel
        proc = subprocess.run(["git", "diff", "--no-index", "--word-diff=plain", "--word-diff-regex=[^[:space:]]+",
                               "-U2", str(old if old.exists() else "/dev/null"), str(new if new.exists() else "/dev/null")],
                              capture_output=True, text=True)
        if proc.stdout.strip():
            chunks.append(f"=================== {rel}\n{proc.stdout}")
    out.write_text("\n".join(chunks) or "No differences.\n")
    print(f"Word diff ([-removed-] {{+added+}}) written to {out.relative_to(p.root.parent.parent)}")
    if shutil.which("latexdiff"):
        flat = shutil.which("latexpand")
        diff_tex = p.root / "diff.tex"
        if flat:
            old_flat = subprocess.run(["latexpand", "main.tex"], cwd=base, capture_output=True, text=True).stdout
            new_flat = subprocess.run(["latexpand", "main.tex"], cwd=p.root, capture_output=True, text=True).stdout
            (notes / "_old_flat.tex").write_text(old_flat)
            (notes / "_new_flat.tex").write_text(new_flat)
            proc = subprocess.run(["latexdiff", str(notes / "_old_flat.tex"), str(notes / "_new_flat.tex")],
                                  capture_output=True, text=True)
        else:
            proc = subprocess.run(["latexdiff", "--flatten", str(base / "main.tex"), str(p.root / "main.tex")],
                                  capture_output=True, text=True)
        if proc.returncode == 0:
            diff_tex.write_text(proc.stdout)
            print(f"latexdiff written to papers/{p.name}/diff.tex (compile it to see changes highlighted).")
        else:
            print("latexdiff failed: " + proc.stderr[-500:])
    else:
        print("latexdiff is not installed here. To get a highlighted PDF, run on a machine with LaTeX:\n"
              f"  latexdiff --flatten versions/{base.name}/main.tex main.tex > diff.tex   (inside papers/{p.name}/)")


def cmd_layout(a):
    p = existing(a.project)
    main_tex = (p.root / "main.tex").read_text(errors="replace")
    log_path = Path(a.log) if a.log else p.root / "main.log"
    if not log_path.is_absolute():
        log_path = p.root / log_path
    if log_path.exists():
        stale = (p.root / "main.pdf").exists() is False or any(
            (p.root / f).stat().st_mtime > log_path.stat().st_mtime for f in _sources(p))
        print(f"From {log_path.name}{' (OLDER than the sources: recompile for current results)' if stale else ''}:")
        issues = texscan.overfull_from_log(log_path.read_text(errors="replace"))
        print("  " + "\n  ".join(issues) if issues else "  No overfull boxes or oversized floats.")
    else:
        print("No LaTeX log found. Compile (rp.py compile) or export main.log from Overleaf "
              "(Logs and output files -> Other logs) into the project and pass --log.")
    r = texscan.layout_static(texscan.collect(p.root), main_tex)
    print(f"\nStatic estimate ({'two-column' if r['two_column'] else 'one-column'}, ~{r['column_capacity']} "
          f"math characters per line; candidates only, confirm on the PDF):")
    for title, key in (("Equation rows that may overflow", "wide_equations"),
                       ("Equation blocks to consider splitting", "crowded_equation_blocks"),
                       ("Tables that may overflow their column/page", "wide_tables")):
        print(f"  {title} ({len(r[key])}):")
        for it in r[key]:
            print("    " + it)


def cmd_render(a):
    p = existing(a.project)
    if not shutil.which("pdftoppm"):
        die("pdftoppm (poppler) is not installed, so pages cannot be rendered.")
    out = p.root / "notes" / "render"
    out.mkdir(parents=True, exist_ok=True)
    made = []
    if a.figures:
        for f in sorted((p.root / "figures").glob("*.pdf")):
            subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", str(f), str(out / f.stem)], check=False)
            made.append(out / (f.stem + ".png"))
    else:
        pdf = p.root / "main.pdf"
        if not pdf.exists():
            die("main.pdf not found; compile first.")
        first, _, last = (a.pages or "1-50").partition("-")
        subprocess.run(["pdftoppm", "-png", "-r", "70", "-f", first, "-l", last or first, str(pdf), str(out / "page")],
                       check=False)
        made = sorted(out.glob("page-*.png"))
    print("Rendered (open each with the Read tool to inspect):")
    for m in made:
        if m.exists():
            print("  " + str(m.relative_to(ROOT)))
    print("notes/render/ is scratch output; do not commit it.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("name"); s.set_defaults(f=cmd_new)
    s = sub.add_parser("status"); s.add_argument("project"); s.set_defaults(f=cmd_status)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=10)
    s.add_argument("--year-from", type=int); s.add_argument("--sources", nargs="+",
                                                            choices=["openalex", "arxiv", "semantic_scholar"])
    s.set_defaults(f=cmd_search)
    s = sub.add_parser("addref"); s.add_argument("project"); s.add_argument("identifier"); s.add_argument("--key")
    s.set_defaults(f=cmd_addref)
    s = sub.add_parser("rmref"); s.add_argument("project"); s.add_argument("key"); s.set_defaults(f=cmd_rmref)
    s = sub.add_parser("approve"); s.add_argument("project"); s.add_argument("gate", choices=["novelty", "structure", "draftplan"])
    s.add_argument("--quote", required=True); s.set_defaults(f=cmd_approve)
    s = sub.add_parser("stage"); s.add_argument("project"); s.add_argument("stage", choices=STAGES)
    s.add_argument("--title"); s.add_argument("--verdict"); s.set_defaults(f=cmd_stage)
    s = sub.add_parser("check"); s.add_argument("project"); s.set_defaults(f=cmd_check)
    s = sub.add_parser("compile"); s.add_argument("project"); s.set_defaults(f=cmd_compile)
    s = sub.add_parser("draft1-start"); s.add_argument("project"); s.set_defaults(f=cmd_draft1_start)
    s = sub.add_parser("draft1-done"); s.add_argument("project"); s.set_defaults(f=cmd_draft1_done)
    s = sub.add_parser("symbols"); s.add_argument("project"); s.set_defaults(f=cmd_symbols)
    s = sub.add_parser("lint"); s.add_argument("project"); s.set_defaults(f=cmd_lint)
    s = sub.add_parser("diff"); s.add_argument("project"); s.add_argument("--from", dest="from_")
    s.set_defaults(f=cmd_diff)
    s = sub.add_parser("layout"); s.add_argument("project"); s.add_argument("--log"); s.set_defaults(f=cmd_layout)
    s = sub.add_parser("render"); s.add_argument("project"); s.add_argument("--pages"); s.add_argument("--figures",
                                                                                                    action="store_true")
    s.set_defaults(f=cmd_render)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
