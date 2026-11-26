# First-draft report (1st-draft-paper pass) — 2026-11-26

Snapshot before the pass: `versions/v0/`. Word diff: `notes/draft1_word_diff_v0.txt`. Audit: `notes/draft_audit.md`.
Approval of the plan: "I approve the draft plan". The five audit questions were not answered, so the recommended
defaults were applied (listed below).

## Defaults applied for the unanswered questions
1. Core ratio renamed γ → **κ = a/b** everywhere (text, tables, figure labels); γ_int kept for the damping, as in Zhang et al.
2. Kernels h_j, i_j → **𝒦_j, ℐ_j**; shell coefficients E, F, G, H → **E₁, E₂, G₁, G₂**.
3. New **Table IV** (slip and β_s sensitivity) added from `code/make_results3.py`.
4. **7-section structure** applied.
5. Abstract and Conclusion kept as **guide bullets**.

## What changed, by section
- **main.tex:** inputs the new section files (`validation.tex`, `rigid.tex`, `soft.tex`; `results.tex` removed, its
  content redistributed); `\finding` macro added (`\showfindingsfalse` prints findings in black); unused macros removed;
  Data Availability lists every script.
- **II Problem Formulation:** merged into three subsections (geometry+assumptions; governing equations+interface
  conditions; dimensionless problem+observables). Every symbol and term is defined at first use with its physical meaning
  (Darcy permeability, Brinkman viscosity, stress jump, added mass, damping, Womersley number). Corrected δ_v. The
  "three difficulties" list became prose leading into Sec. III.
- **III Solution Method:** Lemma 2 (force from centre values) moved before the field representation that uses it;
  renamed symbols; "C → 0" corrected to the confinement of the vortical field; pressure coefficients c_j defined in
  Lemma 1; quadrature sizes N_θ, N_k defined; proofs that are sketches labelled as such; accuracy remark moved to Sec. IV;
  unreferenced equations unnumbered or referenced.
- **IV Validation and Accuracy (new):** setup, Table II, Table III, Fig. 2, error envelope; the O(x³) claim weakened to
  what check2 supports.
- **V Rigid particle near a permeable layer (new):** spectra (Fig. 3), steady limit (Fig. 5) and crossover map (Fig. 4),
  organised by main points with bold lead-ins; three findings in blue.
- **VI Soft particles and biomedical implications (new):** soft-particle results (Fig. 6, new Table IV), acoustofluidic
  contrast (Fig. 7), limitations as prose; one finding in blue.
- **Introduction:** still guide points; contributions and organisation updated to the new structure; κ.
- **Abstract, Conclusion:** bullets aligned with the revised numbers and findings.
- **Appendix:** renamed symbols; removed the reference to a deleted label; tilde replaces the ambiguous prime.

## Corrections to equations, data or figures (all verified)
| # | Correction | Verification |
|---|---|---|
| E1 | δ_v = 1/Re λ_f (was "real part of 1/λ_f") | `notes/checks/check1_symbolic.py` |
| E2 | "√(μ/ρω) ≈ 8.6 k_p/b, the penetration depth" removed; law stated as Wo_c↓ ≈ 0.116 α_p² and ω ≈ 0.0135 μb²/(ρk_p²) | arithmetic |
| E3 | "C → 0" → vortical field confined to O(\|λ\|⁻¹) layer | check1 (C = −3e^λ/2λ²) |
| E4 | Closure–series agreement restricted to ε ≤ 4 | check2(b) |
| E5 | Unsupported core-slip claim replaced by Table IV | `code/make_results3.py` |
| E6 | Damping "peak at Wo ≈ α_p" → maxima at Wo/α_p = 1.0–2.1, 2.2× rigid at α_p = 50 (was "four times", which compared a non-peak point) | `code/damping_peak.py` |
| E7 | Upper-crossover mechanism: proposed scaling argument **tested and rejected**; text now states only what the data show | `notes/checks/check4_scaling.py` |
| F1 | Figures: κ in legends/titles of Fig. 6; colour-bar label in Fig. 7 | regenerated |

No change to the solver or to previously computed data. New data: Table IV, the gap-independence values, the damping
maxima, the Basset fraction and the Ω² comparison, each from a script in `code/`.

## Findings (blue) — details in `notes/key_findings.md`
1. Low-frequency negative added mass = Basset memory removed by the wall (→ full Basset term as Wo → 0).
2. Dissipation maximum at Wo/α_p ≈ 1–2 (interpretation, stated as such).
3. Gap-independent transparency crossover Wo_c↓ ≈ 0.116 α_p².
4. Soft-shell damping suppression ≈ Ω².

## Remaining `\TODO`s (11)
Author list, affiliation, e-mail, acknowledgements, code repository link; Beavers–Joseph reduction (Remark 1);
asymptotic derivation of the α_p² law; confirm permeability values for glycocalyx/mucus in the frequency example;
finer α_s resolution for the re-entrant parallel windows; acoustic radiation-force coupling; multipole/FEM check at ε = 1.
Introduction prose; abstract and conclusion prose.

## Simulated referee report
1. **Accuracy of the dipolar closure at ε ≈ 1.** "The method misses lubrication and is 5% off at ε = 1; are the crossover
   positions reliable?" — *Fix:* add a full multipole (l ≤ 6) or axisymmetric FEM computation for the normal rigid-wall
   case at ε = 1 and report Wo_c; the closure gives 2.92.
2. **Comparison with Zhang et al. (2023).** "The agreement is only qualitative." — *Fix:* digitise their FEM/asymptotic
   curves (or use their asymptotic formula) for the same ε and overlay them in Fig. 3(a).
3. **The α_p² law lacks a derivation.** "An empirical fit with an unexplained exponent." — *Fix:* asymptotic analysis of
   the reflection coefficients for Wo ≫ α_p; at minimum, show Wo_c↓/α_p² for μ_p ≠ μ and β_p ≠ 0 to establish robustness.
4. **Physiological parameters.** "α_p = 3–100 for the glycocalyx implies micron-scale pores, which is unrealistic for
   micron probes." — *Fix:* tabulate b, k_p and the implied α_p and frequencies separately for mucus (micron probes) and
   glycocalyx (nanocarriers); restrict claims accordingly.
5. **Brinkman viscosity and stress-jump coefficients fixed.** "μ_p/μ = 1 and β_p ∈ [−0.5, 0.5] are arbitrary." — *Fix:* add
   a sensitivity panel for μ_p/μ ∈ {1, 2, 5} and justify β ranges from OTW measurements.
6. **Rigid porous matrices.** "The glycocalyx is poroelastic; at MHz frequencies its deformation matters." — *Fix:*
   estimate the poroelastic relaxation frequency and show where the rigid-matrix assumption holds.
7. **Acoustofluidic application is illustrative.** "No radiation force, no trajectories." — *Fix:* either couple to a
   standard Gor'kov radiation-force model or reduce the claim to the force contrast only.
8. **Rotation.** "Parallel oscillation near a wall couples to rotation." — *Fix:* quantify the torque in the dipolar
   closure, or state the O((b/h)⁴) estimate with a reference.
