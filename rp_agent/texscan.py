"""Static analysis of a LaTeX paper for the 1st-draft skill (standard library only).

These scans are aids: they find candidates (undefined-looking symbols, unreferenced equations, banned phrases,
short subsections). Claude still judges each one by reading the text.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

DISPLAY_ENVS = r"equation|align|gather|multline|eqnarray|displaymath|flalign|alignat|split|subequations|dmath"
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")

# Commands that are structure or formatting, not symbols.
NON_SYMBOL_CMDS = {
    "frac", "dfrac", "tfrac", "left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr",
    "cdot", "cdots", "ldots", "dots", "quad", "qquad", "label", "nonumber", "notag", "text", "textrm", "mathrm",
    "operatorname", "sum", "prod", "int", "iint", "oint", "lim", "sqrt", "partial", "nabla", "infty", "to",
    "times", "pm", "mp", "le", "leq", "ge", "geq", "ne", "neq", "approx", "sim", "simeq", "equiv", "propto",
    "in", "forall", "exp", "log", "ln", "sin", "cos", "tan", "sinh", "cosh", "tanh", "max", "min", "sup", "inf",
    "hat", "tilde", "bar", "vec", "dot", "ddot", "overline", "underline", "mathbf", "bm", "boldsymbol", "mathcal",
    "mathsf", "mathbb", "mathit", "mathfrak", "displaystyle", "textstyle", "begin", "end", "tag", "ref", "eqref",
    "cref", "Cref", "intertext", "shortintertext", "hspace", "vspace", "mathrel", "mathop", "limits", "nolimits",
    "colon", "mid", "vert", "Vert", "langle", "rangle", "lbrace", "rbrace", "{", "}", ",", ";", "!", "qty", "dd",
    "cite", "citep", "citet", "phantom", "underbrace", "overbrace", "substack", "stackrel", "overset", "underset",
    "rightarrow", "leftarrow", "Rightarrow", "Leftrightarrow", "mapsto", "otimes", "oplus", "circ", "ast", "star",
    "prime", "perp", "parallel", "cdotp", "ddots", "vdots", "Re", "Im", "arg", "det", "tr", "lVert", "rVert",
}
GREEK = set("alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi varpi "
            "rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma "
            "Upsilon Phi Psi Omega".split())

BANNED_PHRASES = [
    "it is important to note", "it should be noted", "it is worth noting", "it is worth mentioning",
    "plays a crucial role", "plays a vital role", "plays a key role", "plays an important role",
    "in this section we will", "in this section, we will", "we will now", "let us now", "as we can see",
    "as can be seen", "needless to say", "it goes without saying", "delve", "delves", "in the realm of",
    "a myriad of", "a plethora of", "paves the way", "shed light", "sheds light", "a testament to",
    "in today's", "ever-evolving", "cutting-edge", "groundbreaking", "game-changer", "seamless", "robust framework",
    "comprehensive analysis", "holistic", "leverage", "leverages", "utilize", "utilizes", "utilization",
    "in order to", "due to the fact that", "very ", "really ", "obviously", "clearly,", "of course",
    "interestingly,", "notably,", "importantly,", "furthermore,", "moreover,", "additionally,",
    "first and foremost", "last but not least", "in conclusion,", "to summarize,", "overall,",
    "novel", "for the first time", "unprecedented",
]


@dataclass
class TexLine:
    file: str
    lineno: int
    text: str          # comment-stripped line
    in_display: bool   # whole line belongs to a display-math environment


def strip_comments(line: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", line)


def collect(root: Path, main: str = "main.tex") -> list[TexLine]:
    """All lines of main.tex with \\input files expanded in document order."""
    out: list[TexLine] = []
    seen: set[Path] = set()

    def walk(f: Path) -> None:
        if f in seen or not f.exists():
            return
        seen.add(f)
        depth = 0
        for i, raw in enumerate(f.read_text(errors="replace").splitlines(), 1):
            line = strip_comments(raw)
            opens = len(re.findall(r"\\begin\{(?:" + DISPLAY_ENVS + r")\*?\}", line)) + line.count("\\[")
            closes = len(re.findall(r"\\end\{(?:" + DISPLAY_ENVS + r")\*?\}", line)) + line.count("\\]")
            in_disp = depth > 0 or opens > 0
            depth = max(0, depth + opens - closes)
            out.append(TexLine(str(f.relative_to(root)), i, line, in_disp))
            for inc in re.findall(r"\\(?:input|include)\{([^}]+)\}", line):
                walk(root / (inc if inc.endswith(".tex") else inc + ".tex"))

    walk(root / main)
    return out


def math_segments(tl: TexLine) -> list[str]:
    if tl.in_display:
        return [tl.text]
    segs = re.findall(r"(?<!\\)\$(.+?)(?<!\\)\$", tl.text)
    segs += re.findall(r"\\\((.+?)\\\)", tl.text)
    return segs


TOKEN_RE = re.compile(
    r"\\(?:bm|boldsymbol|mathbf|mathcal|mathsf|mathrm|hat|tilde|bar|vec|dot|overline)\{\\?[A-Za-z]+\}(?:_\{[^{}]*\}|_\\?[A-Za-z0-9]+)?"
    r"|\\[A-Za-z]+(?:_\{[^{}]*\}|_\\?[A-Za-z0-9]+)?"
    r"|(?<![A-Za-z\\])[A-Za-z](?:_\{[^{}]*\}|_\\?[A-Za-z0-9]+)?(?![A-Za-z])"
)


def symbols(lines: list[TexLine]) -> "OrderedDict[str, dict]":
    """Symbols in math, in order of first appearance, with locations and the sections they appear in."""
    table: "OrderedDict[str, dict]" = OrderedDict()
    section = "(front matter)"
    for tl in lines:
        m = SECTION_RE.search(tl.text)
        if m and m.group(1) == "section":
            section = m.group(2)
        for seg in math_segments(tl):
            seg = re.sub(r"\\(?:label|text|textrm|mathrm\{d\}|tag|eqref|ref|cref|Cref)\{[^}]*\}", " ", seg)
            for tok in TOKEN_RE.findall(seg):
                name = re.match(r"\\([A-Za-z]+)", tok)
                if name and name.group(1) in NON_SYMBOL_CMDS and not tok.startswith(("\\bm{", "\\hat{", "\\tilde{",
                                                                                        "\\bar{", "\\vec{", "\\dot{",
                                                                                        "\\mathbf{", "\\mathcal{",
                                                                                        "\\boldsymbol{", "\\mathsf{",
                                                                                        "\\overline{", "\\mathrm{")):
                    continue
                entry = table.setdefault(tok, {"first": f"{tl.file}:{tl.lineno}", "count": 0, "sections": []})
                entry["count"] += 1
                if section not in entry["sections"]:
                    entry["sections"].append(section)
    return table


def _words(text: str) -> list[str]:
    text = re.sub(r"(?<!\\)\$.+?(?<!\\)\$", " X ", text)
    text = re.sub(r"\\(?:cite\w*|c?ref|Cref|eqref|label|includegraphics)\*?(?:\[[^\]]*\])*\{[^}]*\}", " X ", text)
    text = re.sub(r"\\[A-Za-z]+\*?", " ", text)
    return re.findall(r"[A-Za-z][A-Za-z\-']*", text)


def lint(lines: list[TexLine]) -> dict:
    report: dict = {"sections": [], "short_subsections": [], "banned": [], "long_sentences": [],
                    "unreferenced_labels": [], "figure_order": [], "findings": [], "stats": {}}
    prose_lines = [tl for tl in lines if not tl.in_display]
    full = "\n".join(tl.text for tl in lines)

    # Sections and subsection sizes (main matter only, before \appendix).
    current = None
    for tl in lines:
        if "\\appendix" in tl.text:
            if current and current["level"] == "subsection" and current["words"] < 150:
                report["short_subsections"].append(current)
            current = None
            report["sections"].append({"title": "(appendix follows)", "where": f"{tl.file}:{tl.lineno}"})
            break
        m = SECTION_RE.search(tl.text)
        if m:
            if current and current["level"] == "subsection" and current["words"] < 150:
                report["short_subsections"].append(current)
            current = {"level": m.group(1), "title": m.group(2), "where": f"{tl.file}:{tl.lineno}", "words": 0}
            if m.group(1) == "section":
                report["sections"].append({"title": m.group(2), "where": f"{tl.file}:{tl.lineno}"})
            continue
        if current and not tl.in_display:
            current["words"] += len(_words(tl.text))
    if current and current["level"] == "subsection" and current["words"] < 150:
        report["short_subsections"].append(current)
    n_sections = len([s for s in report["sections"] if s["title"] != "(appendix follows)"])
    report["stats"]["main_sections"] = n_sections

    # Banned phrases.
    for tl in prose_lines:
        low = tl.text.lower()
        for ph in BANNED_PHRASES:
            if re.search(r"(?<![a-z])" + re.escape(ph.strip()) + r"(?![a-z])", low):
                report["banned"].append(f"{tl.file}:{tl.lineno}: '{ph.strip()}'")

    # Sentence lengths (prose only).
    prose = " ".join(tl.text for tl in prose_lines if not tl.text.lstrip().startswith("\\"))
    sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", prose) if len(_words(s)) > 3]
    lengths = [len(_words(s)) for s in sentences]
    if lengths:
        report["stats"]["sentences"] = len(lengths)
        report["stats"]["mean_sentence_words"] = round(sum(lengths) / len(lengths), 1)
        report["stats"]["share_under_12_words"] = round(sum(l < 12 for l in lengths) / len(lengths), 2)
        report["stats"]["share_over_40_words"] = round(sum(l > 40 for l in lengths) / len(lengths), 2)
    for s, n in zip(sentences, lengths):
        if n > 50:
            report["long_sentences"].append(f"{n} words: {s[:140]}...")

    # Labels never referenced (equations that need no number, or figures never discussed).
    labels = re.findall(r"\\label\{([^}]+)\}", full)
    refs = set()
    for group in re.findall(r"\\(?:ref|eqref|cref|Cref|autoref|pageref|crefrange|Crefrange)\{([^}]+)\}", full):
        refs.update(k.strip() for k in group.split(","))
    report["unreferenced_labels"] = [l for l in labels if l not in refs]
    report["stats"]["equation_refs"] = len(re.findall(r"\\(?:eqref|[cC]ref)\{eq", full))
    report["stats"]["figure_refs"] = len(re.findall(r"\\(?:ref|[cC]ref)\{fig", full))

    # Each figure should be cited before (or at) the point where the float appears.
    for m in re.finditer(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", full, re.S):
        lab = re.search(r"\\label\{([^}]+)\}", m.group(1))
        if not lab:
            report["figure_order"].append(f"figure without label at offset {m.start()}")
            continue
        first_ref = re.search(r"\\(?:ref|[cC]ref|autoref)\{[^}]*\b" + re.escape(lab.group(1)) + r"\b", full)
        if not first_ref:
            report["figure_order"].append(f"{lab.group(1)}: never referenced in the text")
        elif first_ref.start() > m.start():
            report["figure_order"].append(f"{lab.group(1)}: first referenced after the figure appears")

    # \finding{...} blocks and whether each has a citation nearby (same paragraph).
    paragraphs = re.split(r"\n\s*\n", full)
    for para in paragraphs:
        for fm in re.finditer(r"\\finding\{", para):
            snippet = para[fm.end(): fm.end() + 160].replace("\n", " ")
            has_cite = bool(re.search(r"\\cite\w*\{", para))
            report["findings"].append({"text": snippet, "cited_in_paragraph": has_cite})
    return report
