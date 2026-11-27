# Second-draft report (2nd-draft-paper skill) — 2026-11-27

Input: the authors' third draft (`57d278af-main_3rd_draft.pdf`, text-only changes). Its prose was ported verbatim into
the sources (`versions/v3/` = the authors' draft as ported; `versions/v2/` = the previous pass). Word diff of this pass
against the authors' draft: `notes/draft1_word_diff_v3.txt`; highlighted PDF: run
`latexdiff --flatten versions/v3/main.tex main.tex > diff.tex` on a machine with LaTeX.

## 0. Porting the authors' third draft
- Sections II–VI and Appendices A–C rewritten from the PDF text (assumption list as prose, theorem-like environments
  removed, author-named citations, the asymptotic transparency law, the FEM benchmark, mucus/glycocalyx values). The
  equations were kept from the sources; the force decomposition now reads F_int = (−γ_int + iωm_int)U as in the
  draft. Abstract, Introduction and Conclusion were unchanged in the draft.
- Remaining differences in the extracted text were float placement and ligature artefacts only.

## 1. Referee verdict
- **Before:** major revision — undistinguished overlap with a paper published one month ago; unrealistic and uncited
  parameter mapping (glycocalyx-like α_p = 20 for micrometre particles); FEM benchmark not reproducible.
- **After:** **minor revision**, conditional on the author actions listed in §8. Full report with responses:
  `notes/referee_report.md`.

| # | Issue | Severity | Response |
|---|---|---|---|
| R1 | Faltas et al. (2026), Chin. J. Phys. 104, 1193 — porous sphere oscillating near a Brinkman half-space with stress jump (abstract not accessible) | major | cited (Introduction, Sec. II A); Gap bullet rewritten; strongest points avoid overlapping claims; `\TODO` to distinguish precisely |
| R2 | Mucus pore size ↔ √k_p mapping uncited | major | Duncan et al. (2016) and Suk et al. (2009) cited; pore size used as an upper bound on √k_p; accessible frequencies stated |
| R3 | "Glycocalyx-like" α_p = 20 | major | for micrometre particles the glycocalyx is effectively rigid (α_p ≳ 10³); Sec. VI and Figs. 7–8 now say "permeable (mucus-like) layer"; glycocalyx value marked `\TODO{citation needed}` |
| R4 | FEM numbers not reproducible | major | kept as authors' data; `\TODO` to add script and data to `code/` |
| R5 | 0.116 vs 0.1179 in abstract/conclusion; "future work: asymptotic theory" | minor | abstract and conclusion rewritten |
| R6 | "identical for normal and parallel" | minor | "at leading order", with the computed 98.5 %/99.3 % |
| — | **Authors' new asymptotic law** | — | verified independently (`notes/checks/check15`): R_Φ from the full interface system, Z_pB expansion, prefactor √2/12, and convergence of the computed crossovers to the law |

## 2. The five strongest points (`notes/strongest_points.md`) and where they now appear
| Point | Abstract | Intro (contributions) | Body | Caption | Conclusion | Title |
|---|---|---|---|---|---|---|
| 1 Gap-independent transparency law α_p²/(6√2) | ✓ (i) | ✓ | Sec. V B, Eq. (transparency), App. D | Fig. 6 | ✓ | ✓ |
| 2 Basset memory removed by the wall | ✓ (ii) | ✓ | Sec. V A | Figs. 3, 4 | ✓ | ✓ ("added-mass crossovers") |
| 3 Crossover map, window closure, double window | ✓ (iii) | ✓ | Sec. V A–B | Figs. 3, 6 | ✓ | ✓ |
| 4 Ω² softness scaling | ✓ (iv) | ✓ | Sec. VI A–B | Figs. 7–8 | ✓ | ✓ ("soft particle") |
| 5 Validated method + admissibility (β ≤ 0.5) | ✓ (what we do) | ✓ | Secs. III–IV, App. A | Figs. 2, 9 | ✓ | — |

## 3. Title
- Old: "Oscillatory hydrodynamics of a soft core–shell particle near a fluid–porous interface with stress jump".
- **New: "Added-mass crossovers and high-frequency transparency of a soft particle oscillating near a porous layer"**
  (15 words). It names the two effects behind the strongest points while keeping the system and the physics; "stress
  jump" is a model ingredient, not a result. Both titles are in the comment block of `main.tex`.

## 4. Figures (`notes/figure_plan.md`, `notes/figure_review.md`)
- **Added:** Fig. 4 flow fields (4 panels: rigid vs permeable, Wo = 0.5 vs 10; `code/flow_fields.py`), Fig. 9 error
  analysis (Appendix A; quadrature convergence and x⁴ truncation error; `code/make_results5.py`).
- **Replaced:** the crossover scatter by the regime map Fig. 6 (sign of m_int over (α_p, Wo), crossover points, the
  closed-form law, Wo = α_p).
- **Extended:** Fig. 3 now overlays the Basset asymptote −Wo/√2.
- **Kept:** Figs. 1, 2, 5 (steady), 7 (soft), 8 (acoustic). Files renamed to their numbers.
- **Not possible:** comparison with published AFM data (Zhang et al. 2023 data not available) — `\TODO`.
- All new figures passed the physics review before being discussed.

## 5. References
- Added: Faltas et al. 2026 (scoop), Duncan et al. 2016, Suk et al. 2009. All 30 entries have a DOI; every entry is
  cited; citations name their authors (house style).
- Open: glycocalyx Darcy permeability (citation needed); permeability–mesh-size relation (supporting reference needed).

## 6. Mathematics moved to appendices
- New **Appendix D (asymptotic limits)**: full derivations of the inviscid image added mass (from Sec. III C) and of the
  transparency law (from Sec. V B), every step shown; the body keeps the statements, Eqs. (inviscid) and (transparency)
  and their meaning. Auxiliary symbols Γ₁, Γ₂, η, 𝒢 are confined to the appendix.
- Appendices reordered as first cited: A convergence and admissibility (energy identity, Fig. 9), B particle system,
  C interface system, D asymptotic limits; each opens with what it establishes.
- Long inline formulas in Appendix A displayed (no overfull lines).

## 7. House style and checks
- `rp.py lint`: no bold/italic in text, no theorem environments, no Ref.-style citations, one cross-reference command
  (`\cref`), no unjustified bridging words; acronyms spelled out at first use (μ-PIV and CTC flagged by the scanner but
  spelled out). Section V opening rewritten as a question with its physical stakes.
- `rp.py compile`: clean (27 pages); `rp.py layout`: no overfull boxes; `rp.py symbols`: new symbols defined at first use.
- Number consistency re-checked after all changes (abstract, body, captions, conclusion).

## 8. For the authors to check
1. **Faltas et al. (2026):** state what that paper computes and confirm that the strongest points 1–4 are not in it
   (Introduction `\TODO`).
2. **FEM benchmark:** add the script, mesh and output to `code/` (Sec. IV `\TODO`).
3. **Glycocalyx permeability** citation; **permeability vs mesh size** reference (Sec. V B `\TODO`s).
4. **OTW sign convention** (Sec. II / Appendix A).
5. The new title.
6. Introduction prose, abstract and conclusion prose, author list, funding, code repository link.
7. Optional: overlay published AFM frequency-shift data (Zhang et al. 2023) on Fig. 3.
