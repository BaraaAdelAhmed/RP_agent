# Figure plan (2nd-draft pass) — 2026-11-27

## Inventory (`rp.py figures`)
| Fig. | Varies | Fixed | Plotted | Supports | Weaknesses |
|---|---|---|---|---|---|
| 1 schematic | — | — | geometry | formulation | none |
| 2 validation | ε (a); Wo (b) | rigid sphere/wall | F/F∞; m_int/m_f | accuracy, limits | no convergence/error-order figure |
| 3 spectra | Wo; α_p ∈ {∞,50,20,10,5} | ε = 1, β_p = 0 | γ̂_int, χ̂_int | points 2, 3 | low-Wo asymptote (Basset) not overlaid |
| 4 steady | ε; α_p, β_p | Wo → 0 | F/F∞ | "steady drag is a weak probe" | single message; kept (links to Faltas et al. 2021) |
| 5 crossovers | α_p; β_p | ε = 1 | crossover points | points 1, 3 | scatter only; shows regimes indirectly; law plotted as the fit 0.116 α_p² |
| 6 soft | Wo, α_s, κ | α_p = 20 | γ̂, χ̂, crossovers | point 4 | — |
| 7 acoustic | Wo, ε | two particles | phase, force ratio | applications | — |

## Gaps → new figures
1. **Flow fields (4 panels, new Fig.):** real part of the velocity (streamlines + speed) in the plane y = 0 for normal
   oscillation, ε = 1: rigid wall vs permeable layer (α_p = 5) at low (Wo = 0.5) and high (Wo = 10) frequency. Shows the
   physical contrast behind points 1–3: at low Wo the wall blocks the long-range flow (memory removal); at high Wo the
   permeable layer lets the disturbance through (transparency). Computed from the paper's solution
   (`code/flow_fields.py`: closure dipoles + Fourier-reflected and transmitted fields).
2. **Regime map (replaces the scatter of Fig. 5):** sign of χ̂_int over (Wo, α_p) for normal and parallel oscillation,
   with the crossover points, the asymptotic law α_p²/(6√2) and the line Wo = α_p (`code/make_results5.py`). Merges the
   old Fig. 5 (same data) into a figure that shows the regimes directly.
3. **Asymptotic overlays:** Basset asymptote −χ̂ = Wo/√2 added to Fig. 3(c,d); the closed-form law (instead of the fit)
   in the regime map; Fig. 2 already overlays Brenner, the reflection series and the inviscid image.
4. **Error analysis (new figure in Appendix C):** (a) relative change of M vs Gauss nodes per panel (exponential
   convergence); (b) relative error of the closure vs Brenner against x = b/h on log axes, with slope 4.
5. **Comparison with published data:** the AFM data of Zhang et al. (2023) are not available here; `\TODO` for the
   authors to overlay their measured frequency shift if they can obtain it.

## Budget
Fig. 5 scatter → regime map (merged). New: flow fields (body), error analysis (appendix). Total 8 body figures + 1
appendix figure; Fig. 4 kept because it is the only steady-limit comparison with the authors' earlier problem.
