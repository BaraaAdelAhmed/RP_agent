# Paper standards: mathematics, figures and layout

Shared by the `research-paper` and `1st-draft-paper` skills. Read this file before writing or revising the Analysis,
the Results, any figure or the LaTeX layout.

## 1. Mathematical analysis (applied mathematics standard)

The paper is judged as applied mathematics: the analysis must be complete and checkable by a referee.

- **Problem statement:** the governing equations, boundary and interface conditions, conditions at infinity and
  regularity conditions are all stated; the non-dimensionalisation and every dimensionless group are defined; the
  assumptions and their range of validity (in terms of the dimensionless groups) are explicit.
- **Solution method:** every step that a referee needs to reproduce the result is present. State which
  representation is used and why (e.g. the eigenfunction expansion, transform, singularity or reflection method),
  how the unknown coefficients are determined, and the final closed form or linear system.
- **Rigour where it matters:** existence and uniqueness, or well-posedness, are at least argued; truncation of
  series or expansions is justified by a convergence argument or by a convergence study with a stated tolerance;
  asymptotic results state the order of the neglected terms.
- **Checks:** the solution recovers the classical limits (name them and cite the classical results), satisfies the
  symmetries and reciprocity of the problem, and gives physically admissible quantities (for example dissipation
  cannot be negative).
- **Main text vs appendix:** the Analysis section keeps the logic, the key intermediate results and the final results
  (stated as propositions or with numbered equations). Any derivation longer than about half a column, routine
  algebra, coefficient lists, matrix entries and convergence studies go to an appendix, **in full detail with every
  step**, and the main text points to it ("the coefficients are given in \cref{app:coeffs}"). An appendix is not a
  dumping ground: it has its own short introduction and the same notation.

## 2. Equations: typesetting

- Every display fits within its column (two-column layouts: about 8.6 cm). Break long equations at a relation or a
  binary operator with `multline`, `split` or `aligned`, keeping the operator at the start of the continued line; or
  introduce an auxiliary symbol (defined in the text) for a recurring group. Do not shrink fonts.
- One equation environment holds one idea. Use `subequations` only for a set that forms one system read together (a
  boundary-value problem, an optimisation problem, a set of matching conditions). Split a block of unrelated or loosely
  related equations into separate `equation` environments, each introduced by its own sentence, so that each can be
  referenced and explained on its own. As a rule, more than three or four rows in one block need a reason.
- Number only what is referenced; use `\nonumber`/`equation*` for the rest. Punctuate displays as part of the sentence.
- Wide tables: in two-column layouts a table must fit its column; if it cannot be made to fit by abbreviating headers,
  moving units to the header, or transposing, use `table*` (full width at the top or bottom of a page). Never let a
  table cross the gap between columns or the page margin, and never use `\resizebox` to shrink a table's text below
  the caption size.

**Checking:** `python3 scripts/rp.py layout <slug>` reads the LaTeX log (overfull boxes, oversized floats, by file) and
adds a static estimate for each display row and table. Fix every overfull box above 1 pt. Then look at the pages with
`python3 scripts/rp.py render <slug> --pages a-b` and the Read tool. If LaTeX cannot run in this session, say so and
ask the author to compile on Overleaf and add `main.log` to the project (Overleaf: Logs and output files → Other logs),
then run `layout --log main.log`. A PDF compiled with a different document class than `main.tex` declares does not
show the real layout.

## 3. Figures: physical validity first

A figure that shows wrong physics destroys the credibility of the whole article. Never write a discussion that
justifies a curve before you have established that the curve is right.

For every figure, before discussing it, write down in `notes/figure_review.md`:
1. **Expected behaviour from physics alone**, without looking at the plot: limits (small and large values of each
   parameter), monotonicity, sign, asymptotic slopes and scalings, symmetries, bounds (positivity of dissipation or
   drag, energy bounds, causality / Kramers–Kronig type relations between in-phase and out-of-phase parts where they
   apply), and known values from the literature (with references).
2. **What the figure shows**, checked against each item.
3. **Every disagreement investigated**, not explained away: check the code (units, signs, branch cuts of square roots,
   truncation, resolution, conditioning), rerun at higher resolution, compare against an independent limit or a
   published result. A feature survives only if it persists under refinement **and** has a physical mechanism you can
   state. Record the outcome; if the physics in the figure is wrong, fix the computation, not the text.
4. **Verdict:** valid / valid after fix (what changed) / unresolved (tell the author; do not discuss it as a result).

## 4. Figures: quality

- **Smooth curves:** sample densely enough that no curve shows kinks or polygon edges: at least 200 points per curve,
  logarithmic spacing on log axes, and extra refinement where the curve changes quickly (peaks, sign changes,
  crossovers, near-singular limits). Markers only for discrete data, validation points or sparse reference values.
- **Size and fonts:** produce the figure at its printed width (one column ≈ 8.6 cm / 3.4 in, full width ≈ 17.8 cm /
  7 in) so that fonts print at 8–9 pt, close to the caption size; vector PDF; no titles inside panels; panel labels
  (a), (b), … consistently placed.
- **Axes:** every axis labelled with the symbol and units (or "dimensionless"), the same symbols as the text; sensible
  limits with no wasted space; log axes where the data span decades.
- **Lines and colours:** a colour-blind-safe palette, also distinguishable in greyscale (vary line style or markers
  too); the same parameter value keeps the same colour and style in every figure.
- **Legends:** never covering data. With more than about four entries, or whenever space is tight, place the legend
  outside the axes (to the right or above), use a shared legend for multi-panel figures, or label curves directly.
- **Captions:** self-contained: what is plotted, the fixed parameter values, and what the reader should notice.
- After regenerating, render the figure (`rp.py render <slug> --figures`) and look at it at print size.

## 5. The main schematic figure

The schematic shows the physical configuration, not the mathematics:
- **Include:** geometry and length scales, the coordinate system and origin, each region with its name and material
  parameters (only those that define the region), the forcing or motion (direction and amplitude symbol), and the
  key dimensionless distance(s).
- **Do not include:** boundary or interface conditions (no "no slip", "stress jump", "slip", continuity labels, BC
  equations), governing equations, solution-method elements, or result values. Those belong in the text.
- Symbols identical to those in the text; minimal words; same fonts and colours as the other figures; scaled so that
  labels are legible at column width.
