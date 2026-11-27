# Key findings (main points of Secs. V–VI)

Main points (bold lead-ins in the paper):
1. Near a rigid wall the wall-induced added mass is negative at low and positive at high frequency (Sec. V A).
2. A permeable layer weakens the steady interaction and introduces a dissipation maximum at Wo = O(α_p) (V A).
3. In steady motion the layer changes the resistance by only a few per cent (V A).
4. Permeability raises the lower crossover (V B).
5. A permeable layer becomes transparent above an upper crossover ∝ α_p², independent of the gap (V B).
6. Below a threshold permeability the positive-added-mass window closes (V B).
7. The two crossovers give a gap-independent measure of layer permeability (V B).
8. A permeable shell suppresses the wall-induced damping roughly as Ω² (VI A).
9. The crossover depends non-monotonically on particle structure and can disappear (VI A).
10. Surface slip matters for impermeable particles; the shell stress jump matters for soft ones (VI A, Table IV).
11. Soft carriers experience less near-wall resistance (VI A).
12. Cell-like particles differing in softness differ most in near-wall force at Wo = O(1) (VI B).

## Findings marked `\finding{}` (blue)

### F1 — Low-frequency negative added mass = Basset memory removed by the wall (rigid.tex, Sec. V A)
- **Statement:** the negative m_int at low Wo is the part of the Basset history force that the wall removes; as Wo → 0, −χ̂_int → Wo/√2, the full unbounded Basset reactive term.
- **Evidence:** Fig. 3; `code/basset_fraction.py`: −χ̂_int/(Wo/√2) = 0.988 (normal, ε = 1), 0.962 (parallel) at Wo = 0.01, decreasing with Wo and with ε.
- **Artefact check:** rigid-wall limit validated (Table III, Fig. 2); quadrature converged to 1e−13; trend monotonic in Wo and ε.
- **References:** Maxey & Riley (1983) (`maxey1983equation`) define the Basset history force whose frequency-domain form is −6πμbλU; Felderhof (2005) (`felderhof2005effect`) shows theoretically that a wall changes the long-time tail of the velocity autocorrelation, i.e. the hydrodynamic memory; Mo, Simha & Raizen (2015) (`mo2015broadband`) observe the wall effect on this memory experimentally. Together they establish that walls modify the memory force, which our result quantifies in the frequency domain.

### F2 — Dissipation maximum at Wo/α_p ≈ 1–2 (rigid.tex, Sec. V A; stated as interpretation)
- **Statement:** a damping maximum appears where the viscous penetration depth matches the layer's Brinkman length; the flow enters the layer and does work against its Darcy drag.
- **Evidence:** Fig. 3; `code/damping_peak.py`: maxima at Wo = 9.8, 29.6, 105 for α_p = 10, 20, 50 (not at range edges); 2.2× rigid wall at α_p = 50.
- **Artefact check:** extended Wo range, interior maxima, converged quadrature.
- **Reference:** Sherwood (2020) (`sherwood2020unsteady`): unsteady flow next to an oscillating Brinkman wall, where penetration into the porous medium is controlled by the same competition between inertia and Darcy drag.
- **Caveat in text:** stated explicitly as an interpretation consistent with the peak location.

### F3 — Gap-independent transparency crossover Wo_c↓ ≈ 0.116 α_p² (rigid.tex, Sec. V B)
- **Statement:** above Wo_c↓ the layer behaves as a fluid with additional Darcy drag (λ_p → λ_f, Prop. 3(i)); Wo_c↓ ≈ 0.116 α_p², i.e. ω ≈ 0.0135 μb²/(ρk_p²), independent of the gap.
- **Evidence:** Fig. 4 (exponent 2.08, ratio 0.112–0.116 for α_p ≥ 12); `code/gap_independence.py`: Wo_c↓ = 34.7/35.3/35.5 (α_p = 17.3) and 70.2/71.2/71.5 (α_p = 24.6) for ε = 1/2/3.
- **Artefact check:** Brent-refined roots; present for all β_p; quadrature converged.
- **Rejected mechanism:** a scaling argument (χ̂ linear in α_p² at fixed Wo ≫ α_p) was tested in `notes/checks/check4_scaling.py` and fails; the paper says so and leaves the derivation as a TODO.
- **Reference:** Sherwood (2020) for the frequency dependence of unsteady flow at a Brinkman wall, which the finding extends to a finite particle.

### F4 — Soft-shell suppression of damping ∝ Ω² (soft.tex, Sec. VI A)
- **Statement:** γ_int/γ_int^rigid ≈ Ω², with Ω the particle's own drag ratio, from the first reflection (Prop. 2).
- **Evidence:** `code/soft_scaling.py`: ratios 0.58/0.74/0.87 vs Ω² = 0.64/0.79/0.89 (κ = 0.7, α_s = 5/10/20); also predicts the CTC/WBC force ratio 1.40 vs computed 1.45–1.53.
- **Artefact check:** consistent across κ = 0 and 0.7; approximate (computed ratio 5–30% below Ω²), stated as "approximately".
- **References:** Brinkman (1949) (`brinkman1949calculation`) and Ollila et al. (2012) (`ollila2012hydrodynamic`) for the reduction of the drag of a permeable particle by flow through it.

### Not marked as findings (classical or consequences)
- Inviscid image added mass (Prop. 4): classical.
- Closure of the positive window (main point 6): consequence of F1 and F3 meeting.

## Second pass (v1 → v2)
13. **(main point, Sec. V B) In parallel oscillation near a permeable layer the positive window can split into two.**

### F5 — Double positive added-mass window in parallel oscillation (rigid.tex, Sec. V B)
- **Statement:** the reactive interaction is the sum of a vortical-reflection part (positive near Wo ≈ 1, decaying once δ_v < gap) and a potential-image part (negative at low Wo, positive at high Wo); a permeable layer weakens and delays the image (sign change at Wo ≈ 3.4 instead of 2.6 for α_p = 10), so the sum returns to zero in between → two windows (crossings 0.97, 2.88, 3.26, 11.3 at α_p = 10).
- **Evidence:** Fig. 3(d), Fig. 5(b), Fig. 6(d); decomposition `notes/checks/check9_decomposition.py`.
- **Artefact check:** identical crossings on a 120-point grid with doubled quadrature (`check8a`).
- **References:** Maxey & Riley (1983) and Mazur & Bedeaux (1974): the unsteady force separates into a viscous-memory part and an inviscid added-mass part; the finding is the near-wall counterpart of this separation.

### Correction to the record
- The admissibility of stress jumps was re-examined: positive β acts as an interfacial energy source (Remark 2); all findings above concern configurations with β ≤ 0.5, verified dissipative (`check14`).

## 2nd-draft pass
- F3 is now **derived** (authors' third draft): Wo_c↓ = α_p²/(6√2), verified independently in `notes/checks/check15`
  (R_Φ from the full system, Z_pB expansion, prefactor √2/12, computed crossovers → 0.985–0.993 of the law).
- New visual evidence for F1 and F3: Fig. 4 flow fields (blocking of vorticity at low Wo; transmission of the dipole at
  high Wo); regime map Fig. 6.
