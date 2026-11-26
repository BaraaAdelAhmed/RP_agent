# Figure review (second pass, 2026-11-26)

Checks run for this review: `notes/checks/check8_figure_physics.py`, `check9_decomposition.py`,
`check10_admissibility.py`, `check11_negative_beta.py` (outputs saved alongside). Renders: `notes/render/` (scratch).
Printed width: the class (REVTeX `aip,pof,reprint`) produces a **single 396 pt (13.9 cm) column** here, also with the
`twocolumn` option (tested in a scratch copy); figures are included at `0.85\textwidth` ≈ 11.9 cm (`figure*`) or
`\linewidth` ≈ 13.9 cm (`figure`).

---

## Fig. 1 — schematic (`fig1_schematic.pdf`)
- **Expected (§5):** geometry and length scales (a, b, h, gap), coordinate system with origin, regions with their
  defining parameters (fluid ρ, μ; shell k_s, μ_s; layer k_p, μ_p), the motion (U e^{-iωt}, normal and parallel), the
  key distance ε. No boundary conditions.
- **Shows:** "interface: stress jump β_p", "slip ℓ_c" on the core and β_s in the shell label (all interface
  conditions); no coordinate axes or origin; the gap h − b / ε not marked (only h); a hand-drawn dot pattern; fonts
  ~7 pt at print size.
- **Verdict:** **redraw** (§5 violations; no physics error). Remove β_p, β_s, ℓ_c and "slip"; add x–z axes with origin
  on the interface below the centre, mark h and the gap εb; keep ρ, μ, k_s, μ_s, k_p, μ_p, a = κb, b.

## Fig. 2 — validation (`fig2_validation.pdf`)
- **Expected:** (a) F/F∞ > 1, decreasing monotonically to 1 as ε → ∞; normal above parallel; closure below Brenner and
  close to the O(x³) series, converging to Brenner as ε grows; Faxén close to the present parallel values.
  (b) m_int/m_f decreasing towards 3/(16h³) = 0.0234 (normal) and 3/(32h³) = 0.0117 (parallel) as Wo → ∞, with an
  O(Wo⁻¹) approach.
- **Shows:** all of the above. Values match Table III and check1/check2.
- **Quality:** Brenner, reflection-series and Faxén curves are polylines through 9 points (visible kinks, §4);
  5-entry legend inside panel (a), close to the data; panel (b) has 6 points only (markers + lines; acceptable as
  validation points, but a dense curve would show the O(Wo⁻¹) approach); fonts ~6 pt at print size.
- **Verdict:** **valid**; regenerate (dense analytic curves for Brenner/series/Faxén; legend outside; print-size fonts;
  add a dense present curve in (b) with the 6 points as markers).

## Fig. 3 — spectra vs α_p (`fig3_spectra_alphap.pdf`)
- **Expected:**
  1. Low Wo: γ_int → steady wall correction (rigid wall 1.018), smaller for permeable layers; χ_int < 0 with
     −χ_int → Wo/√2 (memory removed) when δ_v ≫ max(h, √k_p).
  2. High Wo, rigid wall: χ_int ∝ Wo² (image added mass), γ_int ∝ Wo (Stokes-layer dissipation, slope → 1).
  3. α_p → ∞ approaches the rigid wall; Wo ≫ α_p: layer transparent, F_int → 0.
  4. γ_int ≥ 0 and total damping > 0.
- **Shows / checks:** (1) −χ_int/(Wo/√2) = 0.98–0.99 at Wo = 0.01 for every α_p ≥ 1, 0.96 at α_p = 0.3, 0.88 at
  α_p = 0.1 (check8b) — the universality holds while δ_v exceeds the Brinkman length, as expected. (2) slope of γ_int:
  0.80, 0.91, 0.96, 0.98 at Wo = 20, 50, 100, 200 (check8c) → 1 ✓; χ_int(50) = 14.7 = (2/9)·2500·0.0265 ✓. (3) ✓
  (α_p = 50 coincides with the wall up to Wo ≈ 10; α_p = 5 decays to 0.07 at Wo = 50). (4) min γ_int over all stored
  spectra = 0.035 > 0; total damping > 0 in all sampled cases (check10).
- **Feature investigated:** two positive windows in (b) at α_p = 8.6–10 and a tiny one (χ ≤ 0.001) at α_p = 5.
  Persistence: identical crossings on a 120-point grid with base and doubled quadrature (check8a:
  α_p = 10 → Wo ≈ 0.97, 2.88, 3.26, 11.27). Mechanism (check9): χ_int = potential-image part + vortical-reflection
  part. The vortical part is positive near Wo ≈ 1 and decays once vorticity no longer reaches the wall (≈ 0 by Wo ≈ 3.5);
  the image part is negative at low Wo and turns positive at Wo ≈ 2.6 for the rigid wall but only at ≈ 3.4 for
  α_p = 10, because the permeable layer weakens and delays the image. Between the two, the sum dips to zero → two
  windows. In normal motion the vortical part is weaker relative to the image, so no split occurs.
- **Quality:** 46 points per curve → visible kinks at the sharp sign changes on the symlog axis (§4 requires ≥ 200
  with refinement near crossovers); 5-entry legend inside (a) top; fonts ~6 pt.
- **Verdict:** **valid**; the double window is real and has a mechanism (the text currently states it without one —
  add the decomposition). Regenerate with ≥ 200 log-spaced points plus refinement at sign changes; shared legend
  outside; print size.

## Fig. 4 (in text: `fig:steady`, file `fig6_steady.pdf`) — steady resistance vs ε
- **Expected:** F/F∞ > 1, decreasing monotonically to 1; permeable layers below the rigid wall; β_p > 0 lowers it
  (more slip-like interface); curves merge at large ε; normal > parallel.
- **Shows:** all ✓ (values match the text).
- **Quality:** 17 points per curve (smooth functions, but below the 200-point rule); legend inside covering the upper
  part of the curves in (a); fonts ~7 pt.
- **Verdict:** **valid**; regenerate densely (Richardson-extrapolated values on ≥ 200 ε points), legend outside.

## Fig. 5 (`fig:woc_ap`, file `fig4_Woc_alphap.pdf`) — crossovers vs α_p
- **Expected:** Wo_c↑ → rigid-wall value (2.92 / 0.955) as α_p → ∞ from above; Wo_c↓ → ∞ as α_p → ∞; window closes
  as α_p decreases; β_p effect fades for large α_p.
- **Shows:** ✓. Fit 0.116 α_p² ✓ (exponent 2.08). Gap independence of Wo_c↓ verified (`code/gap_independence.py`).
- **Quality:** discrete data as markers ✓; 5-entry legend inside (a) — acceptable position (empty corner) but >4
  entries → move outside/shared; fonts ~6 pt.
- **Verdict:** **valid**; restyle only.

## Fig. 6 (`fig:soft`, file `fig5_soft_particle.pdf`) — soft particles
- **Expected:** permeable shells → smaller damping (≈ Ω² scaling); α_s → ∞ and κ → 1 recover the impermeable sphere;
  χ_int negative at low Wo with a magnitude set by the particle's own memory force, which is weaker for a more
  permeable particle (the curves in (b) separate slightly at low Wo, in this order).
- **Shows:** ✓ (α_s = 50 crossovers sit on the dashed impermeable lines; κ = 0.95 indistinguishable from impermeable).
  Re-entrant windows in (d) for κ = 0.5, 0.8: same mechanism as Fig. 3(b) (vortical window followed by delayed image);
  persistence not yet re-checked at finer α_s (a TODO in the text).
- **Quality:** 46-point curves in (a,b); legend in (c) partly over markers and with a **duplicated "rigid sphere"
  entry** (two dashed lines labelled); fonts ~5–6 pt at print size (worst of all figures).
- **Verdict:** **valid** for (a–c); (d) re-entrant windows valid by the Fig. 3 mechanism but should be confirmed at
  finer α_s before being discussed beyond one sentence. Regenerate.

## Fig. 7 (`fig:acoustic`) — CTC-like vs leukocyte-like
- **Expected:** phase arg(−F/U) from 0 (viscous) towards −90° (inertial) as Wo increases, nearly independent of ε
  (interaction small at large Wo); force-magnitude ratio → (Ω_CTC/Ω_WBC)² = 1.40 at low Wo; ratio weakly dependent on ε.
- **Shows:** ✓ (ratio 1.45–1.53 at Wo = 0.1; phase difference ≤ 13°).
- **Quality:** 13 × 21 grid → coarse contours (visible facets); phase panel from 21 points; fonts ~6 pt; colour bar now
  labelled.
- **Verdict:** **valid**; regenerate on a dense grid (≥ 200 points in Wo for the lines, ≥ 60 × 40 for the contours).

---

## Summary
| Figure | Physics | Quality | Action |
|---|---|---|---|
| 1 schematic | n/a | §5 violations | redraw |
| 2 validation | valid | polylines, legend, fonts | regenerate |
| 3 spectra | valid (double window explained) | 46 pts, legend, fonts | regenerate + add mechanism to text |
| 4 steady | valid | 17 pts, legend | regenerate |
| 5 crossovers | valid | legend, fonts | restyle |
| 6 soft | valid; (d) to confirm | 46 pts, duplicated legend, fonts | regenerate |
| 7 acoustic | valid | coarse grid, fonts | regenerate |

No figure shows wrong physics. All need regeneration for §4 quality (print-size fonts and density).
