---
name: 1st-draft-paper
description: Turn a structured LaTeX paper (made with the research-paper skill) into a polished first draft. A line-by-line audit of every symbol, term, equation, claim and figure (physical validity first), layout fixes for equations and tables that overflow columns or margins; a narrative pass over the Problem Formulation, Analysis and Results; a language pass towards scientific-paper register; merging to 6-7 sections; results discussed by main point, with new physical insights backed by well-established references and highlighted in blue. Use when the user asks for a first draft, a polish, or a language/consistency revision of a paper in papers/.
---

# 1st draft paper

You are the senior co-author who turns a structured paper into a first draft that a demanding referee would read
without losing the thread. You change the text, never the science: equations, data and figures change only to fix
an error you have verified, and every such change is reported to the author.

Scope: the **Problem Formulation**, **Analysis** and **Results and Discussion** sections are the core of this pass.
The Abstract and Conclusion are aligned with them. The **Introduction stays as guide points**: fix its references and
symbols, but do not write it as prose. The style is generic (no journal-specific rules) unless the author asks.

## Tools

Everything from the research-paper skill (`python3 scripts/rp.py ...`: `status`, `search`, `addref`, `rmref`,
`check`, `compile`, `approve`), plus:

| Command | Purpose |
|---|---|
| `rp.py draft1-start <slug>` | Snapshot all sources to `versions/vN/` (never edit it) and lock `.tex` edits until the plan is approved |
| `rp.py symbols <slug>` | Every math token in document order: first use (file:line), count, sections where it appears; user macros |
| `rp.py lint <slug>` | Section count, short subsections (<150 words), banned phrases, sentence statistics, very long sentences, labels never referenced, figure citation order, `\finding` blocks without a citation |
| `rp.py approve <slug> draftplan --quote "<user's words>"` | Record the author's approval of the audit and plan; unlocks editing |
| `rp.py diff <slug>` | Word diff against the snapshot in `notes/`, plus `diff.tex` via latexdiff when installed |
| `rp.py draft1-done <slug>` | Mark the pass finished |
| `rp.py layout <slug> [--log main.log]` | Overfull equations/tables and oversized floats from the LaTeX log, by file; plus a static estimate of display rows, crowded equation blocks and tables too wide for their column |
| `rp.py render <slug> [--pages a-b] [--figures]` | PNGs of PDF pages or of each figure, to inspect with the Read tool |

`docs/paper-standards.md` (mathematics, equation and table typesetting, figure validity and quality, the schematic)
is part of these instructions: read it before Pass 1.

The scanners find candidates; they do not judge. Read every flagged line yourself (the sentence scanner, for
example, also counts table rows and captions).

If the hooks are not active (the repository was attached after the session started), apply the lock yourself: no
`.tex` edits between `draft1-start` and the `draftplan` approval, never edit `versions/`, and change `references.bib`
only through `addref` / `rmref`.

**Saving the work:** commit `papers/<slug>/` (including `.session/`, `versions/` and `notes/`) and push to the session
branch at the end of every pass.

## Pass 0 — Set up
1. `rp.py status <slug>`; read `notes/novelty_report.md` and `notes/outline.md` so you know the paper's strong point
   and the contribution claims you are allowed to make.
2. Ask the author anything that changes the draft (for example a section they want kept separate, or words they
   insist on). Keep it to what matters.
3. `rp.py draft1-start <slug>`.

## Pass 1 — Line-by-line audit (no edits) → `notes/draft_audit.md`
Read every file in document order, line by line and word by word. Run `rp.py symbols`, `rp.py lint` and
`rp.py check`. Then write the audit, every item with a location (`file:line`) and a severity (**critical**: wrong or
undefined; **major**: breaks the reader's flow; **minor**: wording):

1. **Notation table**: symbol | meaning | units or dimensionless | where defined | where used. Flag symbols used before
   they are defined, never defined, defined twice, used with two meanings, or two symbols for one quantity;
   subscripts used inconsistently; vectors/tensors not typeset consistently; dimensional and dimensionless variables
   mixed.
2. **Physical terms**: every technical term (for example "added mass", "stress jump", "Womersley number") with where
   it is first defined and whether the definition is physical (what it means) and not only mathematical.
3. **Equation checks**: dimensional consistency of every numbered equation; consistency of the non-dimensionalisation
   across sections; signs and conventions. Verify the key derivation steps independently: re-derive them with sympy,
   or evaluate them numerically, in scripts under `notes/checks/` (install sympy/numpy with pip if needed). Check the
   limiting cases against classical results the paper should recover, and say which were verified and how.
4. **Reverse outline** of the Problem Formulation, Analysis and Results: one sentence per paragraph. Mark where the
   story jumps, repeats, or uses something before it is motivated.
5. **Claim–evidence map**: every claim in the Abstract, Results and Conclusion against the equation, figure or table
   that supports it. Flag unsupported claims and claims stronger than the evidence.
6. **Referencing**: equations referenced never or too often; figures cited after they appear, or never discussed;
   figure captions that are not self-contained; axes without variables or units.
7. **Language**: banned phrases, textbook tone, stacked short sentences, overlong sentences, inconsistent tense.
8. **Restructuring plan** to **6–7 main sections** (Introduction through Conclusion; appendices do not count): a
   table old section/subsection → new section/subsection, merging short ones (see `lint`) and anything too thin to
   stand alone. Give each new heading a title that suits the paper.
9. **Candidate physical insights**: results that go beyond the known physics, each with the evidence, the check that
   it is not a numerical artefact (resolution, convergence, limit), and the well-established reference you propose to
   support it (searched and confirmed to exist; see Pass 4).
10. **Mathematical sufficiency** against `docs/paper-standards.md` §1: what a referee could not reproduce, missing
    justifications (well-posedness, convergence of truncations, order of neglected terms), and which derivations
    should move to an appendix in full detail or be expanded there.
11. **Figure review** — the most important item. For every figure, in `notes/figure_review.md` (§3 of the standards):
    the behaviour physics predicts before looking, what the figure shows, every disagreement and its investigation
    (rerun the scripts at higher resolution, check limits and signs, compare with the literature), and a verdict.
    A figure showing wrong physics is **critical**: never propose wording that justifies it.
    Also the quality items of §4 (too few points / jagged curves, legends over data or too crowded, fonts, styles)
    and the schematic rules of §5 (list any boundary-condition or equation elements to remove).
12. **Layout:** run `rp.py layout` and render the pages; list every overfull equation or table, tables crossing the
    column gap or page margin, and equation blocks that hold several unrelated equations and should be split.
13. **Errors you propose to fix in equations, data or figures** (if any), each with the verification.
14. **Questions for the author.**

Summarise the critical and major items, the restructuring table and the candidate insights in chat. Ask the author to
approve or adjust the plan. Only when they explicitly approve, run `rp.py approve <slug> draftplan --quote "..."`.

## Pass 2 — Structure, narrative and definitions
- Apply the approved restructuring. Keep `main.tex`, labels, `\cref`s and the outline consistent; move labels with
  their content, never renumber by hand.
- Define every symbol at its first use, in the sentence that introduces it, with its physical meaning (and units for
  dimensional quantities). Define each physical term the first time it is used. If the paper has many symbols, keep a
  compact notation table in the Problem Formulation. Use one symbol per quantity and one meaning per symbol everywhere.
- Build the narrative of the core sections: every section opens by saying what it does and why it is needed after the
  previous one, and closes with what the reader now has. Introduce each important equation by its purpose and follow
  it with its interpretation. Remove repetition; move derivations that interrupt the story to an appendix.
- Fix the critical items from the audit.
- Bring the analysis to the standard of `docs/paper-standards.md` §1: add the missing steps and justifications; move
  long derivations to an appendix and write them there in full, every step shown, with a pointer from the main text.
- Split equation blocks that hold several separate ideas into individual `equation` environments, each introduced by
  its own sentence; keep `subequations` only for one coupled system (§2).

## Pass 2b — Figures: physics, then quality
- Act on `notes/figure_review.md`. Where the physics is wrong, find and fix the cause in the computation, regenerate,
  and re-review; tell the author what was wrong. Where it is unresolved, the figure is not discussed as a result until
  the author decides.
- Regenerate figures that fail the quality rules (§4) from their scripts: dense, refined sampling so no curve has
  edges; legends outside the axes or shared when crowded; print-size fonts; consistent styles across figures.
- Redraw the schematic without boundary-condition or equation elements (§5).
- Render every figure and look at it before moving on.

## Pass 3 — Language: a scientific paper, not a textbook
- **Register:** report and argue; do not teach. No pedagogical scaffolding ("we will now", "let us", "recall that"
  for standard material, step-by-step walkthroughs of routine algebra). Assume an expert reader.
- **Sentences:** build them with logical connections that carry the argument (subordinate clauses with "whereas",
  "so that", "such that", "which", participial phrases), aiming at roughly 20–30 words on average with real
  variation. Merge chains of short declarative sentences into one well-built sentence; split sentences that run past
  about 45 words or nest more than two clauses. Clarity wins over complexity.
- **Human, not machine, prose:** precise verbs; no filler; no reflexive triplets, no stacks of "Notably,"/"Moreover,"
  openers, no em-dash or colon in every sentence, no "not only … but also" habit. Use "we" for the authors' choices and
  the passive for procedures. Present tense for what the paper shows; past tense for what was computed.
- **Equation references:** cite an equation where its content is used ("substituting the slip condition
  \eqref{eq:bc} into …"), not decoratively; normally no more than one or two per sentence. Every numbered equation is
  referenced at least once; leave unnumbered any equation that is never referenced.
- **Figure references:** cite each figure where its evidence enters the argument, before the float appears, with the
  panel ("\cref{fig:spectra}(b)"). Every figure is discussed in the text, not just cited.
- **Claims:** calibrated hedging ("suggests" for indirect evidence, "shows" for direct); "novel" or "first" only where
  the novelty report supports it.
- Finish with `rp.py lint`: no banned phrases, 6–7 main sections, no unreferenced labels you have not justified.

## Pass 4 — Results and discussion by main point; findings in blue
- Organise the Results and Discussion into its **main points**, each a paragraph (or a short group of paragraphs)
  that opens with a **bold lead-in sentence stating the point**, then gives the evidence (figure/table/equation),
  the mechanism in terms of the analysis, and the implication. Write it as prose, not bullet lists. Keep the list of
  main points in `notes/key_findings.md`.
- **New physical insight:** when a result goes beyond the known physics, first confirm it is real (consistent with
  the limits, converged, not an artefact). Then find support in the literature with `rp.py search` and web search:
  prefer seminal, highly cited, well-established works (classic papers, standard monographs, major reviews) that
  establish the underlying mechanism or the classical counterpart the new result extends. Add it with `addref`, cite
  it in the sentence, and wrap the insight in `\finding{...}`.
- Never cite a reference you have not confirmed exists and supports the statement. If no suitable reference exists,
  keep the `\finding` and add `\TODO{supporting reference needed}`. If a result contradicts established physics, do
  not present it as a finding: flag it for the author with your analysis.
- Add to the preamble of `main.tex` (once):
  ```latex
  \newif\ifshowfindings \showfindingstrue   % \showfindingsfalse for submission: findings print in black
  \newcommand{\finding}[1]{\ifshowfindings\textcolor{blue}{#1}\else#1\fi}
  ```
- For each finding, `notes/key_findings.md` records: the statement, the evidence (figure/equation), the check that it is
  not an artefact, and the supporting reference with why it supports it.

## Pass 5 — Abstract and Conclusion
Align both with the revised results: same claims, same numbers, same symbols, no claim without evidence. Keep their
current format (guide bullets stay bullets) unless the author asks for prose. Leave the Introduction as guide points,
updating its contribution bullets and organisation paragraph to the new structure.

## Pass 6 — Verify and hand over
1. `rp.py compile <slug>` (or `check` without LaTeX) until clean; `rp.py lint`; `rp.py symbols` again to confirm
   every symbol is defined before use.
2. `rp.py layout <slug>` until no equation or table overflows its column or the page; render the pages and look at
   every page with equations, tables or figures. If LaTeX cannot run here, ask the author for Overleaf's `main.log`
   and run `layout --log main.log`; do not trust a PDF compiled with a different document class.
3. `rp.py diff <slug>` for the word diff (and `diff.tex` when latexdiff is available).
4. Write `notes/draft1_report.md`: what changed and why (by section), equation/data/figure corrections with their
   verification, the findings list, remaining `\TODO`s, and a **simulated referee report**: the 5–8 comments a tough
   reviewer would most likely make, each with a suggested fix.
5. `rp.py draft1-done <slug>`, commit and push. Tell the author which files to open, how to switch the blue findings off
   (`\showfindingsfalse`), and how to see the changes (word diff, or latexdiff on a machine with LaTeX).
