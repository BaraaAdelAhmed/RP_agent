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

from rp_agent import literature  # noqa: E402
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
    last = LAST_PROMPT.read_text(errors="replace") if LAST_PROMPT.exists() else ""
    norm = lambda s: " ".join(s.lower().split())
    if not quote or norm(quote) not in norm(last):
        die("The quote must be copied word for word from the user's latest message. If the user has not clearly "
            "approved yet, ask them.")
    if a.gate == "structure" and not p.state.novelty_approved:
        die("Novelty must be approved before the structure.")
    setattr(p.state, f"{a.gate}_approved", True)
    p.state.approvals.append({"gate": a.gate, "quote": quote})
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
    sys.exit(run_check(p))


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
    s = sub.add_parser("approve"); s.add_argument("project"); s.add_argument("gate", choices=["novelty", "structure"])
    s.add_argument("--quote", required=True); s.set_defaults(f=cmd_approve)
    s = sub.add_parser("stage"); s.add_argument("project"); s.add_argument("stage", choices=STAGES)
    s.add_argument("--title"); s.add_argument("--verdict"); s.set_defaults(f=cmd_stage)
    s = sub.add_parser("check"); s.add_argument("project"); s.set_defaults(f=cmd_check)
    s = sub.add_parser("compile"); s.add_argument("project"); s.set_defaults(f=cmd_compile)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
