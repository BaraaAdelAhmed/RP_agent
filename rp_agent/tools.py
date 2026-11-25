"""Client-side tools the agent can call, with input validation.

Each tool is a pydantic model (its JSON schema is what Claude sees) plus a handler.
Because the agent streams with `eager_input_streaming`, the API does not validate
tool inputs; every input is validated here before a handler runs.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from typing import Callable, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from . import literature
from .project import STAGES, WRITABLE_SUFFIXES, Project


class ToolError(Exception):
    """Raised by a handler; returned to Claude as an is_error tool_result."""


# ------------------------------------------------------------------ input models

class SearchLiterature(BaseModel):
    """Search scholarly databases (OpenAlex, arXiv, Semantic Scholar) for papers. Returns title, authors, year, venue,
    DOI/arXiv ID, citation count and abstract for each hit. Use many differently-worded queries (synonyms, method +
    application combinations, adjacent-field terminology) when checking novelty. Use the returned DOI or arXiv ID with
    add_reference to put a paper in references.bib."""
    query: str = Field(description="Search terms, e.g. 'federated learning over-the-air computation power control'.")
    limit: int = Field(default=10, ge=1, le=25, description="Max results per source.")
    year_from: Optional[int] = Field(default=None, description="Only works published in or after this year.")
    sources: Optional[list[Literal["openalex", "arxiv", "semantic_scholar"]]] = Field(
        default=None, description="Subset of sources; default is all.")


class AddReference(BaseModel):
    """Fetch the authoritative BibTeX for a real paper (from doi.org, arXiv or OpenAlex) and add it to references.bib.
    This is the ONLY way to add references: never type BibTeX yourself. Returns the citation key to use in \\cite{}."""
    identifier: str = Field(description="DOI (10.xxxx/...), arXiv ID (e.g. 2101.01234) or OpenAlex work ID (W123...).")
    key: Optional[str] = Field(default=None, description="Optional citation key; default is author+year+word.")


class RemoveReference(BaseModel):
    """Remove an entry from references.bib by its citation key."""
    key: str


class WriteFile(BaseModel):
    """Create or overwrite a text file in the paper project (e.g. main.tex, sections/problem_formulation.tex,
    notes/novelty_report.md, figures/plot_results.py). Write each LaTeX section to its own file so no single call is
    huge. references.bib cannot be written here; use add_reference."""
    path: str = Field(description="Path relative to the project root.")
    content: str = Field(description="Full file contents.")


class ReadFile(BaseModel):
    """Read a text file from the paper project (including user uploads under inputs/ that are text)."""
    path: str


class ListFiles(BaseModel):
    """List all files in the paper project."""


class SetStage(BaseModel):
    """Record which workflow stage the project is in. The stages are: idea, novelty, structure, drafting, review.
    Moving to 'structure' requires the user's approval of the novelty assessment; moving to 'drafting' requires the
    user's approval of the titles and structure (see record_user_approval)."""
    stage: Literal["idea", "novelty", "structure", "drafting", "review"]
    working_title: Optional[str] = Field(default=None, description="Current working title, if one is chosen.")
    novelty_verdict: Optional[str] = Field(default=None, description="Short verdict, e.g. 'Novel (high confidence)'.")


class RecordUserApproval(BaseModel):
    """Record that the USER explicitly approved a gate in their latest message. Only call this when the user has
    clearly said so (e.g. 'yes, the idea is novel enough, go on' / 'use title 2 and this structure'). Never call it on
    your own judgement."""
    gate: Literal["novelty", "structure"]
    user_quote: str = Field(description="The user's words that give the approval, quoted verbatim.")


class RunPython(BaseModel):
    """Run a Python script locally inside the project folder (matplotlib/numpy if installed; MPLBACKEND=Agg). Use it
    to numerically evaluate the expressions derived in the analysis, run small simulations, and save figures to
    figures/*.pdf and tables to *.csv. Only available when the user has enabled it in the app. Every number that
    appears in the Results section must come from a script run this way or from data the user supplied."""
    script_path: str = Field(description="Where to save the script, e.g. figures/fig_rate_vs_snr.py")
    code: str = Field(description="Full Python source.")
    timeout_s: int = Field(default=180, ge=5, le=900)


class CompileLatex(BaseModel):
    """Compile main.tex (pdflatex + bibtex via latexmk when available) and return errors/warnings that matter
    (undefined citations or references, LaTeX errors). Returns a notice if no LaTeX installation is found."""


# ------------------------------------------------------------------ handlers

def _search(p: Project, a: SearchLiterature, ctx: dict) -> str:
    res = literature.search_literature(a.query, a.limit, a.year_from, a.sources)
    lines = [f"Query: {res['query']} — {res['count']} results"]
    for i, r in enumerate(res["results"], 1):
        ident = r.get("doi") or (f"arXiv:{r['id']}" if r["source"] == "arxiv" else r.get("arxiv") or r["id"])
        lines.append(
            f"\n[{i}] {r['title']} ({r['year']})\n    {', '.join(r['authors'][:4])}{' et al.' if len(r['authors']) > 4 else ''}"
            f" | {r['venue']} | id: {ident} | cited by: {r['citations']}\n    Abstract: {r['abstract'] or '(not available)'}")
    if res["notes"]:
        lines.append("\nNotes: " + "; ".join(res["notes"]))
    return "\n".join(lines)


def _bib_path(p: Project):
    return p.root / "references.bib"


def _add_reference(p: Project, a: AddReference, ctx: dict) -> str:
    try:
        key, entry = literature.bibtex_entry(a.identifier, a.key)
    except Exception as e:  # network or not-found errors become tool errors
        raise ToolError(f"Could not fetch BibTeX for '{a.identifier}': {e}")
    bib = _bib_path(p)
    text = bib.read_text() if bib.exists() else ""
    existing = literature.bib_keys(text)
    ident_norm = a.identifier.lower().replace("https://doi.org/", "").replace("arxiv:", "")
    if ident_norm and ident_norm in text.lower():
        return f"Already in references.bib (identifier present). Existing keys: {', '.join(existing)}"
    base, n = key, 2
    while key in existing:
        key = f"{base}{chr(ord('a') + n - 2)}"
        n += 1
    if key != base:
        entry = re.sub(r"^(@\w+\{)[^,]+,", lambda m: f"{m.group(1)}{key},", entry, count=1)
    bib.write_text(text.rstrip() + ("\n\n" if text.strip() else "") + entry + "\n")
    title = re.search(r"title\s*=\s*\{(.+?)\},?\n", entry)
    return f"Added \\cite{{{key}}} — {title.group(1) if title else a.identifier}"


def _remove_reference(p: Project, a: RemoveReference, ctx: dict) -> str:
    bib = _bib_path(p)
    text = bib.read_text() if bib.exists() else ""
    pattern = re.compile(r"@\w+\s*\{\s*" + re.escape(a.key) + r"\s*,.*?\n\}\s*", re.S)
    new, n = pattern.subn("", text)
    if not n:
        raise ToolError(f"No entry with key '{a.key}'.")
    bib.write_text(new)
    return f"Removed {a.key}."


def _write_file(p: Project, a: WriteFile, ctx: dict) -> str:
    target = p.resolve(a.path)
    rel = str(target.relative_to(p.root))
    if target.name == "references.bib":
        raise ToolError("references.bib is managed by add_reference/remove_reference only.")
    if target.suffix.lower() not in WRITABLE_SUFFIXES:
        raise ToolError(f"Cannot write '{target.suffix}' files. Allowed: {sorted(WRITABLE_SUFFIXES)}")
    is_paper_source = target.suffix.lower() == ".tex"
    if is_paper_source and not (p.state.novelty_approved and p.state.structure_approved):
        raise ToolError(
            "The LaTeX paper is locked until the user approves (1) the novelty assessment and (2) the titles and "
            f"structure. Current approvals: novelty={p.state.novelty_approved}, structure={p.state.structure_approved}. "
            "Ask the user for whatever is missing.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(a.content)
    return f"Wrote {rel} ({len(a.content.splitlines())} lines)."


def _read_file(p: Project, a: ReadFile, ctx: dict) -> str:
    target = p.resolve(a.path)
    if not target.is_file():
        raise ToolError(f"No such file: {a.path}")
    if target.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        raise ToolError("Binary file. PDFs and images the user uploaded are already in the conversation.")
    text = target.read_text(errors="replace")
    return text if len(text) < 120_000 else text[:120_000] + "\n... [truncated]"


def _list_files(p: Project, a: ListFiles, ctx: dict) -> str:
    files = p.list_files()
    return "\n".join(files) if files else "(empty project)"


def _set_stage(p: Project, a: SetStage, ctx: dict) -> str:
    order = STAGES.index(a.stage)
    if order >= STAGES.index("structure") and not p.state.novelty_approved:
        raise ToolError("Cannot move past 'novelty' until the user approves the novelty assessment.")
    if order >= STAGES.index("drafting") and not p.state.structure_approved:
        raise ToolError("Cannot start drafting until the user approves the titles and structure.")
    p.state.stage = a.stage
    if a.working_title:
        p.state.working_title = a.working_title
    if a.novelty_verdict:
        p.state.novelty_verdict = a.novelty_verdict
    p.save_state()
    return f"Stage set to '{a.stage}'."


def _record_approval(p: Project, a: RecordUserApproval, ctx: dict) -> str:
    last_user = ctx.get("last_user_text", "")
    quote = a.user_quote.strip().strip('"')
    if not quote or quote.lower() not in last_user.lower():
        raise ToolError("The quote must be copied verbatim from the user's latest message. If the user has not "
                        "explicitly approved yet, ask them.")
    if a.gate == "structure" and not p.state.novelty_approved:
        raise ToolError("Novelty must be approved before the structure.")
    setattr(p.state, f"{a.gate}_approved", True)
    p.state.approvals.append({"gate": a.gate, "quote": quote})
    p.save_state()
    return f"Recorded user approval for '{a.gate}'."


def _run_python(p: Project, a: RunPython, ctx: dict) -> str:
    if not ctx.get("allow_python"):
        raise ToolError("Local Python execution is disabled by the user (toggle in the app sidebar). Describe the "
                        "figure/table and its expected content instead, with clear \\TODO placeholders for numbers.")
    script = p.resolve(a.script_path)
    if script.suffix != ".py":
        raise ToolError("script_path must end in .py")
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(a.code)
    before = {f: (p.root / f).stat().st_mtime for f in p.list_files()}
    env = {**os.environ, "MPLBACKEND": "Agg"}
    try:
        proc = subprocess.run([sys.executable, str(script)], cwd=p.root, capture_output=True, text=True,
                              timeout=a.timeout_s, env=env)
    except subprocess.TimeoutExpired:
        raise ToolError(f"Timed out after {a.timeout_s}s.")
    after = p.list_files()
    changed = [f for f in after if f not in before or (p.root / f).stat().st_mtime != before[f]]
    out = (proc.stdout[-8000:] or "(no stdout)") + ("\n--- stderr ---\n" + proc.stderr[-6000:] if proc.stderr else "")
    msg = f"Exit code {proc.returncode}\nFiles created/updated: {', '.join(changed) or 'none'}\n{out}"
    if proc.returncode != 0:
        raise ToolError(msg)
    return msg


def _compile_latex(p: Project, a: CompileLatex, ctx: dict) -> str:
    main = p.root / "main.tex"
    if not main.exists():
        raise ToolError("main.tex does not exist yet.")
    if shutil.which("latexmk"):
        cmds = [["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]]
    elif shutil.which("pdflatex"):
        pdf = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        cmds = [pdf, ["bibtex", "main"], pdf, pdf] if shutil.which("bibtex") else [pdf, pdf]
    else:
        return ("No LaTeX installation found on this machine, so the paper was not compiled. Check consistency "
                "manually instead: every \\cite key exists in references.bib, every \\ref has a \\label, every "
                "\\input file exists.")
    for c in cmds:
        try:
            proc = subprocess.run(c, cwd=p.root, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            raise ToolError(f"{c[0]} timed out.")
        if proc.returncode != 0 and c[0] != "bibtex":
            break
    log = (p.root / "main.log").read_text(errors="replace") if (p.root / "main.log").exists() else proc.stdout
    important = [l for l in log.splitlines() if l.startswith("!") or "undefined" in l.lower() or "Warning: Citation" in l]
    status = "PDF built: main.pdf" if (p.root / "main.pdf").exists() and proc.returncode == 0 else "Build FAILED"
    tail = "\n".join(log.splitlines()[-25:]) if status == "Build FAILED" else ""
    return f"{status}\nIssues:\n" + ("\n".join(dict.fromkeys(important))[:6000] or "none") + (f"\n\nLog tail:\n{tail}" if tail else "")


# ------------------------------------------------------------------ registry

Handler = Callable[[Project, BaseModel, dict], str]

TOOLS: dict[str, tuple[type[BaseModel], Handler]] = {
    "search_literature": (SearchLiterature, _search),
    "add_reference": (AddReference, _add_reference),
    "remove_reference": (RemoveReference, _remove_reference),
    "write_file": (WriteFile, _write_file),
    "read_file": (ReadFile, _read_file),
    "list_files": (ListFiles, _list_files),
    "set_stage": (SetStage, _set_stage),
    "record_user_approval": (RecordUserApproval, _record_approval),
    "run_python": (RunPython, _run_python),
    "compile_latex": (CompileLatex, _compile_latex),
}

# Tools whose inputs can be large; these stream eagerly.
_LARGE_INPUT = {"write_file", "run_python"}


def _schema(model: type[BaseModel]) -> dict:
    s = model.model_json_schema()
    s.pop("title", None)
    s.pop("description", None)
    for prop in s.get("properties", {}).values():
        prop.pop("title", None)
    return s


def tool_definitions() -> list[dict]:
    defs = []
    for name, (model, _) in TOOLS.items():
        d = {"name": name, "description": " ".join((model.__doc__ or "").split()), "input_schema": _schema(model)}
        if name in _LARGE_INPUT:
            d["eager_input_streaming"] = True
        defs.append(d)
    return defs


def run_tool(project: Project, name: str, raw_input: object, ctx: dict) -> tuple[str, bool]:
    """Validate and run one tool call. Returns (content, is_error)."""
    if name not in TOOLS:
        return f"Unknown tool '{name}'.", True
    model, handler = TOOLS[name]
    try:
        args = model.model_validate(raw_input if isinstance(raw_input, dict) else {})
    except ValidationError as e:
        # With eager input streaming a malformed/truncated input lands here instead of in the API.
        import json
        return json.dumps({"INVALID_INPUT": str(e)[:2000],
                           "hint": "Re-send the call with valid, complete arguments. Split very long files."}), True
    try:
        return handler(project, args, ctx), False
    except (ToolError, ValueError) as e:
        return str(e), True
