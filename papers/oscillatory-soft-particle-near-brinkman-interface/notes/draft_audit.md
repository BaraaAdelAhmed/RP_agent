# Second-pass audit (no edits) — 2026-11-26

Snapshot of the audited draft: `versions/v1/` (= commit 8c221d5). The first-pass audit is kept in
`notes/draft_audit_v0.md`. This pass applies the updated skill, which adds `docs/paper-standards.md`: mathematical
sufficiency (§1), equation layout (§2), figure physics and quality (§3–4) and the schematic (§5).
Tools run: `rp.py check` (clean), `lint`, `symbols`, `layout`, `render --figures`, `render --pages 1-20`.
New verification scripts: `notes/checks/check8`–`check11` (outputs saved). Figure review: `notes/figure_review.md`.

Severity: **critical** = wrong or undefined; **major** = breaks the reader's flow or fails a standard;
**minor** = wording.

---

## 1. Notation table — changes since v0
All v0 clashes are resolved (κ, 𝒦_j/ℐ_j, E₁…G₂, δ_v). `rp.py symbols`: every symbol is defined before use in the core
sections. Remaining items:

| Item | Location | Severity |
|---|---|---|
| "rigid particle" (Sec. V title) vs "impermeable particle" (text, Prop. 1) for the same object; "rigid wall" is used for the impermeable no-slip wall | rigid.tex:1, soft.tex, conclusion | **minor** — use "impermeable" for the particle throughout |
| \hat χ_int called "reactive coefficient" (PF) and "reactive part" (Res) | PF:168, rigid.tex | minor |
| 𝒮 (traction amplitudes) vs 𝖲_inc (response matrix) | analysis.tex:80, 108 | minor (distinct fonts; acceptable) |
| Ω (drag ratio) defined twice (Tab. III caption and soft.tex:21) with the same meaning | validation.tex, soft.tex | minor — define once in Sec. IV |

## 2. Physical terms
All terms flagged in v0 are now defined physically at first use. New in this draft without a definition:
"Froude–Krylov force" (analysis.tex:126, defined in passing ✓), "re-entrant" windows (soft.tex:41, **minor**),
"symmetric logarithmic axis" (caption, ✓).

## 3. Equation checks (new this pass)
| Check | Result | Script |
|---|---|---|
| Positivity of wall-induced damping over all stored spectra | min γ̂_int = 0.035 > 0 ✓ | check10 |
| Positivity of total damping (sampled κ, α_s, α_p, Wo, both directions) | > 0 in all cases ✓ | check10 |
| Positivity of total damping with β_p, β_s ∈ {−1, −0.5} | min 0.75 > 0 ✓ | check11 |
| **Correction (made during Pass 2):** the energy identity shows that, with the paper's sign convention, a **positive** β removes dissipation (the row above wrongly said negative). check11b/check14: for β_s = 1 an isolated porous particle has negative dissipation (κ = 0, α_s ≥ 5, even steady); for β_s = 0.5 only at α_s = 2, Wo ≈ 200. All reported configurations (β ≤ 0.5) are dissipative. **Critical** → Remark (uniqueness and admissible stress jumps) added; Table I range restricted to β ≤ 0.5; sign convention flagged to the author | check11b, check14 |
| Convergence of the reflection series (Prop. 2): spectral radius of 𝖲_inc𝐌 | ≤ 0.50 at ε = 1; 0.62 at ε = 0.5; 0.69 at ε = 0.25 ✓ | check10 |
| High-Wo rigid-wall damping γ_int ∝ Wo (Stokes layer) | local slope 0.80 → 0.98 for Wo = 20 → 200 ✓ | check8c |
| Low-Wo memory removal for permeable layers | −χ̂/(Wo/√2) = 0.98–0.99 at Wo = 0.01 for α_p ≥ 1; 0.96 (α_p = 0.3); 0.88 (α_p = 0.1) ✓ (holds while δ_v ≫ max(h, √k_p)) | check8b |
| Persistence of the double positive window (parallel) | identical crossings with doubled quadrature, 120-point grid ✓ | check8a |
| Mechanism of the double window | potential-image + vortical-reflection decomposition ✓ | check9 |
v0 checks (check1–7) remain valid; no equation changed since.

## 4. Reverse outline — flow issues (core sections)
- **Sec. III** — fine overall; Prop. 2 is stated "if the spectral radius is below one" without saying it is (now
  verified: ≤ 0.5 at ε = 1) → **major** (§1: justify the truncation/series).
- **Sec. V A** — the double window in parallel oscillation is mentioned only in V B as "splits into two" without a
  mechanism → **major** (now available from check9).
- **Sec. VI C Limitations** (129 words) — too short to stand alone (lint) → fold into the closing paragraph of Sec. VI.
- No section opens or closes without a statement of purpose / outcome (fixed in v0 pass).

## 5. Claim–evidence map — changes
| Claim | Evidence | Status |
|---|---|---|
| "Close to the threshold the parallel window splits into two" (rigid.tex:109) | Fig. 5, check8a | supported; **add mechanism** (check9) |
| Re-entrant windows for κ = 0.5, 0.8 (soft.tex:41) | Fig. 6(d) | supported at the computed α_s values; persistence at finer α_s not checked (TODO in text) — keep the TODO |
| "Total damping positive", "admissible β range" | — | **not stated in the paper**; now verified → add one sentence (Sec. IV) |
| All other claims | as in v0 audit | supported |

## 6. Referencing
- Every numbered equation is referenced (lint). Unreferenced labels are section labels only (justified).
- Figures cited in order and discussed. Captions self-contained. Fig. 3 caption explains the symlog axis ✓.
- **minor:** the file names of figures 4–6 no longer match their numbers (fig6_steady.pdf is Fig. 4, etc.) → rename
  files for the author's sanity.

## 7. Language
lint: 232 sentences, mean 27.1 words, 0 banned phrases. Long-sentence flags are bullet lists, tables and captions
(scanner artefacts), except: analysis.tex:157–166 (reflection-matrix sentence, ~60 words) and soft.tex:2–5 (section
opener, ~40 words) → split. Tense and register are consistent.

## 8. Restructuring plan
The draft already has **7 main sections**; no structural change. Small adjustments:

| Current | Proposed |
|---|---|
| V "Rigid Particle near a Permeable Layer: Spectra, Crossovers and Transparency" | V "**Impermeable Particle** near a Permeable Layer: Spectra, Crossovers and Transparency" |
| VI C "Limitations" (subsection, 129 words) | closing paragraph of Sec. VI (no subsection) |
| Appendices A, B | A, B, plus **C "Convergence and admissibility checks"** (quadrature study, spectral radius, positivity of dissipation, β < 0 range) |

## 9. Candidate physical insights (new this pass)
1. **Two positive added-mass windows in parallel oscillation near a permeable layer.** Evidence: Figs. 3(b), 5(b), 6(d);
   persistence check8a; mechanism check9 (vortical-reflection window near Wo ≈ 1 decays before the weakened, delayed
   potential image turns positive). Reference supporting the decomposition into viscous-memory and inviscid
   added-mass parts: Maxey & Riley (1983) and Mazur & Bedeaux (1974), both already in the bibliography.
2. **Condition for full memory removal:** δ_v ≫ max(h, √k_p) — extends finding F1 (check8b). Support: Felderhof (2005),
   Mo et al. (2015) (already cited).

## 10. Mathematical sufficiency (§1)
| Gap | Location | Severity | Proposed fix |
|---|---|---|---|
| Well-posedness not argued | Sec. II/III | **major** | Remark: energy identity (multiply by ū, integrate) — Re part = viscous + Darcy dissipation + β-terms; uniqueness for β ≥ 0 by positivity; for β < 0 positivity of the total dissipation verified numerically over the stated range (check11) |
| Reflection matrix displayed with "⋯" in its second column | analysis.tex:161–162 | **major** (not reproducible) | write both columns explicitly (second column: same projections with the vortical source) or give the full 2 × 2 entries in App. B |
| Radial derivatives g′, g″, g‴ of 𝒦_j, ℐ_j needed to assemble the 6 × 6 system are not given | App. A | **major** | list them in App. A |
| Truncation (dipolar closure): order of neglected terms only shown numerically | Sec. IV | **major** | state in Sec. III that the closure reproduces the reflection series through O(x³) and omits O(x⁴) terms, with the numerical evidence (check2) and the spectral-radius bound (check10) in App. C |
| Quadrature convergence stated in one sentence | analysis.tex:182–186 | minor | table in App. C |
| Richardson-extrapolation error for the steady limit not quantified; limited by Wo·h at large ε | Sec. III end | minor | one sentence + App. C (check2b) |
| Appendices lack a short introduction | appendix.tex | minor | add one sentence each |

## 11. Figure review (detail in `notes/figure_review.md`)
**No figure shows wrong physics.** Every expected limit, sign, slope and bound was checked and holds.
- **Major (quality, §4):** all multi-panel figures are drawn at 6.8 in and scaled to ≈ 4.7 in → fonts ≈ 5–6 pt; spectra
  use 46 points (kinks at sign changes); steady curves 17 points; Fig. 2(a) reference curves are 9-point polylines;
  Fig. 7 contours on a 13 × 21 grid; legends with 5 entries inside axes; duplicated "rigid sphere" legend entry in
  Fig. 6(c,d).
- **Major (§5):** the schematic shows interface conditions (β_p, β_s, "slip ℓ_c"), lacks coordinate axes and the gap.

## 12. Layout
- The class produces a **single 396 pt column** in this TeX installation (verified with a minimal document and with
  the `twocolumn` option: no change). The static two-column estimates of `rp.py layout` therefore do not apply; the
  only real overflow is **analysis.tex:80 (16.9 pt)**, the inline traction formula (visible on page 8) → **major**:
  display it.
- All tables fit the 396 pt column (pages 6, 11, 16 rendered). No equation block holds unrelated equations.

## 13. Errors proposed for fixing (equations, data, figures)
None in equations or data. Figures: regenerate for quality (no data change except denser sampling of the same
computation); redraw the schematic.

## 14. Questions for the author
1. **Column layout.** This class compiles single-column here. Keep it (figures sized for the 13.9 cm text width), or
   do you want a two-column layout (figures at 8.6/17.8 cm and equation breaking for 8.6 cm columns)? I recommend
   keeping the class as compiled.
2. **Appendix C** with the convergence and admissibility checks — add it? (Recommended: it answers referee comment 1.)
3. Present the **double parallel window** as a blue finding with its mechanism? (Recommended.)
