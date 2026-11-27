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


# ------------------------------------------------------------------ layout (static estimates)

def column_chars(main_tex: str) -> tuple[int, bool]:
    """Rough capacity of one text line in 'rendered math characters', and whether the layout is two-column."""
    m = re.search(r"\\documentclass(\[[^\]]*\])?\{([^}]+)\}", main_tex)
    opts, cls = (m.group(1) or "", m.group(2)) if m else ("", "article")
    two = ("twocolumn" in opts or "reprint" in opts or cls == "IEEEtran" and "onecolumn" not in opts
           or (cls.startswith("revtex") and "preprint" not in opts))
    return (52 if two else 95), two


def _math_width(s: str) -> float:
    s = re.sub(r"\\(?:label|tag|text|mathrm|operatorname)\{([^}]*)\}", lambda m: "" if "label" in m.group(0) or "tag" in m.group(0) else m.group(1), s)
    s = re.sub(r"\\(?:nonumber|notag|left|right|big|Big|bigg|Bigg|displaystyle|bm|boldsymbol|mathbf|hat|tilde|bar|vec)\b", "", s)
    s = re.sub(r"\\q?quad", "    ", s)
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", lambda m: "x" * max(len(m.group(1)), len(m.group(2))), s)
    width = 0.0
    for scr in re.findall(r"[_^](\{[^{}]*\}|\\?[A-Za-z0-9])", s):
        width += 0.6 * len(re.sub(r"\\[A-Za-z]+", "x", scr.strip("{}")))
    s = re.sub(r"[_^](\{[^{}]*\}|\\?[A-Za-z0-9])", "", s)
    s = re.sub(r"\\[A-Za-z]+", "x", s)
    s = re.sub(r"[{}&\s]", "", s)
    return width + len(s)


def layout_static(lines: list[TexLine], main_tex: str) -> dict:
    cap, two = column_chars(main_tex)
    full_lines = [(tl.file, tl.lineno, tl.text) for tl in lines]
    out = {"two_column": two, "column_capacity": cap, "wide_equations": [], "crowded_equation_blocks": [],
           "wide_tables": []}
    # Display-math rows wider than a column.
    env_start = None
    rows: list[tuple[str, int, str]] = []
    env_name = ""
    for f, n, t in full_lines:
        b = re.search(r"\\begin\{(equation|align|gather|multline|eqnarray|subequations|flalign|alignat)\*?\}", t)
        if b and env_start is None:
            env_start, env_name, rows = (f, n), b.group(1), []
        if env_start is not None:
            rows.append((f, n, t))
            if re.search(r"\\end\{" + env_name + r"\*?\}", t):
                body = " ".join(r[2] for r in rows)
                body = re.sub(r"\\(?:begin|end)\{[^}]*\}(\{[^}]*\})?", " ", body)
                eq_rows = [r for r in re.split(r"\\\\", body) if r.strip()]
                for r in eq_rows:
                    w = _math_width(r)
                    if w > cap and env_name != "multline":
                        out["wide_equations"].append(f"{env_start[0]}:{env_start[1]} ({env_name}): ~{w:.0f} chars "
                                                     f"vs ~{cap} per {'column' if two else 'line'}: {r.strip()[:80]}")
                labels = len(re.findall(r"\\label\{", body))
                if env_name == "subequations" and len(eq_rows) > 3 or (env_name in ("align", "gather", "eqnarray")
                                                                       and len(eq_rows) > 4):
                    out["crowded_equation_blocks"].append(
                        f"{env_start[0]}:{env_start[1]} ({env_name}): {len(eq_rows)} rows, {labels} labels — split "
                        f"unless they form one system")
                env_start = None
    # Tables in a single column whose rows look too wide.
    text = "\n".join(t for _, _, t in full_lines)
    for m in re.finditer(r"\\begin\{table(\*?)\}(.*?)\\end\{table\*?\}", text, re.S):
        star, body = m.group(1), m.group(2)
        tab = re.search(r"\\begin\{tabular\*?\}(?:\{[^}]*\})?\{([^}]*)\}(.*?)\\end\{tabular", body, re.S)
        if not tab:
            continue
        cap_here = cap * (2 if (two and star) else 1)
        widest = 0.0
        for row in re.split(r"\\\\", tab.group(2)):
            row = re.sub(r"\\(?:toprule|midrule|bottomrule|hline|cline\{[^}]*\}|multicolumn\{\d+\}\{[^}]*\})", "", row)
            cells = row.split("&")
            w = sum(_math_width(c) * 0.9 for c in cells) + 2 * len(cells)
            widest = max(widest, w)
        lab = re.search(r"\\label\{([^}]+)\}", body)
        name = lab.group(1) if lab else f"table at offset {m.start()}"
        if widest > cap_here:
            out["wide_tables"].append(f"{name}: widest row ~{widest:.0f} chars vs ~{cap_here} "
                                      f"({'table*' if star else 'single column'})")
    return out


def overfull_from_log(log: str, min_pt: float = 1.0) -> list[str]:
    """Overfull boxes and oversized floats from a LaTeX log, attributed to the .tex file being read."""
    issues, stack = [], []
    for line in log.splitlines():
        o = re.search(r"Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\) (.*)", line)
        cur = next((f for f in reversed(stack) if f), "main.tex")
        if o and float(o.group(1)) >= min_pt:
            kind = "display math" if "detected at line" in o.group(2) or "alignment" in o.group(2) else "paragraph/table"
            issues.append(f"{cur}: {o.group(1)}pt too wide ({kind}) — {o.group(2).strip()}")
        if "Float too large" in line:
            issues.append(f"{cur}: " + line.strip())
        # Track the file being read: "(./file.tex" opens it, ")" closes the innermost group.
        for m in re.finditer(r"\((\./[^\s()]+\.tex)?|\)", line):
            if m.group(0).startswith("("):
                stack.append(m.group(1)[2:] if m.group(1) else None)
            elif stack:
                stack.pop()
    return issues


# ------------------------------------------------------------------ house-style checks (author's writing rules)

THEOREM_ENVS = r"remark|lemma|proposition|theorem|corollary|definition|assumption|claim|conjecture|example"
ROADMAP_PHRASES = ["in this section", "this section", "in what follows", "in the following", "we first", "we then",
                   "we begin by", "we start by", "is organised", "is organized", "the rest of", "the remainder of",
                   "we present", "we describe", "we derive", "we discuss", "will be", "below we", "next, we"]
BRIDGING_PHRASES = ["by symmetry", "by linearity", "by superposition", "by reciprocity", "owing to symmetry",
                    "due to symmetry", "from symmetry", "it follows that", "it follows from", "can be expressed as",
                    "can be written as", "may be written as", "may be expressed as", "takes the form", "take the form",
                    "it can be shown", "can be shown", "one can show", "one may show", "it is easy to see",
                    "it is easily seen", "easily shown", "clearly", "obviously", "trivially", "trivial",
                    "straightforward", "readily", "naturally", "without loss of generality", "similarly",
                    "in general", "it is evident", "evidently", "immediately", "hence", "thus", "therefore"]
NOT_ACRONYMS = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "OK", "TODO", "PDF", "LHS",
                "RHS", "MHz", "GHz", "kHz", "MPa", "GPa", "kPa", "DC", "AC"}


def style_check(lines: list[TexLine]) -> dict:
    r = {"paragraph_titles": [], "emphasis": [], "theorem_envs": [], "citation_wording": [], "crossref_mix": [],
         "acronyms": [], "roadmap_openers": [], "short_paragraphs": [], "bridging_words": []}
    body = [tl for tl in lines if not tl.in_display]

    for tl in lines:
        loc = f"{tl.file}:{tl.lineno}"
        if re.search(r"\\paragraph\*?\{", tl.text):
            r["paragraph_titles"].append(f"{loc}: {tl.text.strip()[:80]}")
        m = re.search(r"\\begin\{(" + THEOREM_ENVS + r")\}", tl.text)
        if m:
            r["theorem_envs"].append(f"{loc}: {m.group(1)}")
    for tl in body:
        loc = f"{tl.file}:{tl.lineno}"
        if "introduction.tex" in tl.file or "abstract.tex" in tl.file:
            continue  # guide points
        for em in re.findall(r"\\(?:textbf|textit|emph|textsl|underline)\{[^}]{0,40}|\{\\(?:bf|it|em|sl)\s[^}]{0,40}", tl.text):
            r["emphasis"].append(f"{loc}: {em}")
        if re.match(r"\s*\\textbf\{", tl.text):
            r["paragraph_titles"].append(f"{loc}: bold lead-in")
        low = tl.text
        for pat, why in ((r"\bRefs?\.?\s*~?\\(?:online)?cite", "'Ref. [n]'"),
                         (r"\b[Rr]eferences?\s*~?\\(?:online)?cite", "'reference [n]'"),
                         (r"\b(?:in|In|see|See|of|from)\s*~?\\(?:online)?cite", "citation used as a noun ('in [n]')"),
                         (r"(?:^|[.!?]\s+)\\(?:online)?cite", "sentence starts with a citation"),
                         (r"\\(?:online)?cite[pt]?\{[^}]*\}\s+(?:showed|found|studied|reported|proposed|derived|obtained|considered)",
                          "citation used as the subject")):
            if re.search(pat, low):
                r["citation_wording"].append(f"{loc}: {why}: {tl.text.strip()[:90]}")

    # Bridging words that must come with a justification (candidates; the reader judges each one).
    strong = BRIDGING_PHRASES[:-3]
    for tl in body:
        if "introduction.tex" in tl.file or "abstract.tex" in tl.file:
            continue
        low = tl.text.lower()
        for ph in strong:
            if re.search(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])", low):
                r["bridging_words"].append(f"{tl.file}:{tl.lineno}: '{ph}': {tl.text.strip()[:90]}")

    text = "\n".join(tl.text for tl in body)
    # Mixed cross-reference styles.
    mix = {
        "\\cref/\\Cref": len(re.findall(r"\\[cC]ref\{", text)),
        "\\ref": len(re.findall(r"(?<![a-zA-Z])\\ref\{", text)),
        "\\eqref": len(re.findall(r"\\eqref\{", text)),
        "literal 'Fig.'": len(re.findall(r"\bFig\.\s*~?\\ref", text)),
        "literal 'Figure'": len(re.findall(r"\bFigure\s*~?\\ref", text)),
        "literal 'Eq.'": len(re.findall(r"\bEqs?\.\s*~?(?:\\ref|\\eqref|\()", text)),
        "literal 'Equation'": len(re.findall(r"\bEquations?\s*~?(?:\\ref|\\eqref|\()", text)),
        "literal 'Section'/'Sec.'": len(re.findall(r"\b(?:Section|Sec\.)\s*~?\\ref", text)),
    }
    used = {k: v for k, v in mix.items() if v}
    if len([k for k in used if k.startswith("\\")]) > 1 or len([k for k in used if k.startswith("literal")]) > 0:
        r["crossref_mix"].append("; ".join(f"{k}: {v}" for k, v in used.items()))
    cite_cmds = {c: len(re.findall(r"\\" + c + r"\{", text)) for c in ("cite", "citep", "citet", "citealp", "onlinecite")}
    if len([c for c, n in cite_cmds.items() if n]) > 1:
        r["crossref_mix"].append("citation commands mixed: " + ", ".join(f"\\{c}: {n}" for c, n in cite_cmds.items() if n))

    # Acronyms: first use in the body (abstract excluded) must spell them out.
    seen: dict[str, str] = {}
    for tl in body:
        if "abstract.tex" in tl.file:
            continue
        clean = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", tl.text)
        clean = re.sub(r"\$[^$]*\$", " ", clean)
        for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,}[a-z]?)s?\b", clean):
            acr = m.group(1)
            if acr in NOT_ACRONYMS or acr in seen:
                continue
            defined = f"({acr})" in clean or f"({acr}s)" in clean
            seen[acr] = f"{tl.file}:{tl.lineno}"
            if not defined:
                r["acronyms"].append(f"{acr}: first used at {tl.file}:{tl.lineno} without being spelled out there")

    # Section openers that announce contents instead of opening the topic.
    lines_list = list(lines)
    for i, tl in enumerate(lines_list):
        if re.search(r"\\section\*?\{", tl.text) and "introduction" not in tl.text.lower():
            opener = " ".join(x.text for x in lines_list[i + 1:i + 8] if not x.in_display).lower()
            first = re.split(r"(?<=[.!?])\s", opener.strip(), maxsplit=2)[:2]
            hits = [p for p in ROADMAP_PHRASES if p in " ".join(first)]
            if hits:
                r["roadmap_openers"].append(f"{tl.file}:{tl.lineno} '{tl.text.strip()[:50]}': opens with {hits}")

    # Short paragraphs (merge candidates) outside the guide-point sections.
    para, start = [], None
    for tl in lines_list + [TexLine("", 0, "", False)]:
        if tl.text.strip() == "" or re.match(r"\s*\\(?:sub)*section|\\begin\{(?:figure|table)", tl.text):
            words = len(_words(" ".join(x.text for x in para if not x.in_display)))
            if para and 0 < words < 60 and not any(s in para[0].file for s in ("introduction", "abstract", "main.tex")) \
                    and not re.match(r"\s*\\(?:end|caption|label|includegraphics|centering)", para[0].text):
                r["short_paragraphs"].append(f"{para[0].file}:{para[0].lineno}: {words} words")
            para = []
        else:
            para.append(tl)
    return r
