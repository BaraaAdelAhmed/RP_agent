# The five strongest points (ranked) — 2nd-draft pass

Each survived the referee review (`notes/referee_report.md`). The closest prior work is Faltas et al. (2026,
porous sphere near a Brinkman half-space; content to be confirmed by the authors), Zhang et al. (2023, rigid sphere
and rigid wall) and Sherwood (2020, porous wall without particle).

1. **A permeable layer becomes hydrodynamically transparent above a gap-independent frequency
   Wo_c↓ = α_p²/(6√2) ≈ 0.118 α_p², i.e. ω ≈ μb²/(72ρk_p²).**
   - Evidence: Eq. (transparency), Fig. 5 (crossovers vs α_p, with the law overlaid), check15 (computed/law → 0.985–0.993),
     gap independence within 3 % (ε = 1–3).
   - New: Zhang et al. have no permeability; Sherwood's porous wall has no particle and no crossover. A closed-form,
     gap-independent frequency fingerprint of k_p has not been reported.
   - Matters: measures layer permeability without knowing the probe–wall distance.
2. **The low-frequency negative wall-induced added mass is the Basset memory force removed by the wall:
   −χ̂_int → Wo/√2 (ratio 0.99 normal, 0.96 parallel at Wo = 0.01).**
   - Evidence: Fig. 3(c,d), `code/basset_fraction.py`; holds for permeable layers with α_p ≳ 1.
   - New: explains the sign of the frequency-shift crossover observed by Zhang et al. by a stated mechanism; the
     frequency-domain counterpart of wall-modified Brownian long-time tails (Felderhof 2005; Mo et al. 2015).
   - Matters: identifies what AFM frequency-shift measurements near a wall actually probe at low frequency.
3. **Permeability raises the lower crossover and closes the positive-added-mass window below a threshold
   (α_p ≈ 6–9 normal, 4–6 parallel), with a double window in parallel oscillation near the threshold.**
   - Evidence: Figs. 3 and 5, Sec. V B; mechanism from the potential/vortical decomposition (check9).
   - New: no crossover map with permeability exists for rigid-wall theories.
   - Matters: qualitative test of layer permeability (a sign that disappears) at kHz frequencies for 10 µm probes.
4. **Particle softness suppresses near-wall damping approximately as Ω², the square of the particle's own drag ratio, and
   reshapes the crossovers non-monotonically.**
   - Evidence: Fig. 6, Table IV, `code/soft_scaling.py` (0.58/0.74/0.87 vs Ω² = 0.64/0.79/0.89); CTC/WBC force ratio
     1.45–1.53 vs Ω² prediction 1.40.
   - New: core–shell particle with slip core near a porous wall not treated before.
   - Matters: soft carriers and cells differ in near-wall force by a predictable factor (acoustofluidic contrast,
     mucus-penetrating carriers).
5. **A validated semi-analytical method with explicit admissibility bounds: exact dipolar particle response + exact
   Fourier reflection + self-consistent closure, accurate to 5 % (normal) and 1.5 % (parallel) at ε = 1, converging as
   x⁴; positive stress jumps act as interfacial energy sources (β ≤ 0.5).**
   - Evidence: Sec. III, Table III, Fig. 2, App. C (energy identity, spectral radius ≤ 0.5), FEM benchmark (authors).
   - New: method combining the two exact representations; first admissibility analysis of the OTW coefficient sign in
     this setting (to the authors' knowledge — to confirm against Faltas et al. 2026).
   - Matters: the parameter ranges can be trusted, and the β range used in the literature is restricted.

## Placement (Stage 3)
| Point | Abstract | Introduction (contributions) | Body (where established) | Figure caption | Conclusion | Title |
|---|---|---|---|---|---|---|
| 1 | Key results bullet | bullet 4 | Sec. V B, Eq. (transparency) | Fig. 5 | bullet | "high-frequency transparency" |
| 2 | Key results bullet | bullet 3 | Sec. V A | Fig. 3 | bullet | "added-mass crossovers" |
| 3 | Key results bullet | bullet 4 | Sec. V A–B | Figs. 3, 5 | bullet | "added-mass crossovers" |
| 4 | Key results bullet | bullet 5 | Sec. VI A–B | Figs. 6, 7 | bullet | "soft particle" |
| 5 | What-we-do bullet | bullets 1–2 | Secs. III–IV, App. C | Fig. 2 | bullet | — |

## Title
Previous: "Oscillatory hydrodynamics of a soft core–shell particle near a fluid–porous interface with stress jump".
New: **"Added-mass crossovers and high-frequency transparency of a soft particle oscillating near a porous layer"**
(15 words). It names the two effects that carry the strongest points (1–3), keeps the system (soft particle, porous
layer) and the physics (oscillation), and drops "stress jump", which is a model ingredient rather than a result.
