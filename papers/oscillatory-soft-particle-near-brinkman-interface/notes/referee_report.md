# Referee report (2nd-draft pass) — 2026-11-27

Manuscript reviewed: the author's third draft (`57d278af-main_3rd_draft.pdf`), ported verbatim into the sources
(snapshot `versions/v3/`). Checks: `notes/checks/check1`–`check15` (outputs saved), `code/*.py`.

## 1. Method sharpness

| Item | Evidence | Verdict |
|---|---|---|
| Closed forms (B, C, Z_U, Z_p, Z_w), force integral, radial forms | sympy re-derivation, `check1` | correct |
| Kernel derivatives (App. A) | sympy, `check12` | correct |
| **New: asymptotic transparency law** Wo_c↓ = α_p²/(6√2) (author's addition) | `check15`: (a) R_Φ from the full 6×6 interface system agrees with (c₃−c₁)/(c₃+c₁) and with iα²/(2Wo²)+α⁴/(4Wo⁴) to 3–4 digits for Wo = 50–300; (b) Z_pB = πλ²(1+6/λ+15/λ²+…), i.e. −iπWo²[1+3√2(1+i)/Wo+…] (the identity 6/λ = 3√2(1+i)/Wo is elementary; sympy failed to simplify it); (c) the balance gives √2/12 = 0.11785; (d) computed crossovers approach the law from below: 0.862, 0.966, 0.982, 0.985, 0.985 (normal) and 0.881, 0.976, 0.991, 0.993, 0.993 (parallel) of the law at α_p = 8.6–35 | **verified**; residual 1–1.5 % plateau (higher-order terms), within the stated 2 % |
| Quadrature | doubling N_k, N_θ changes M by ≤ 9×10⁻¹⁵ (`convergence_table.py`); Gauss panels converge exponentially | converged |
| Reflection series | spectral radius of S_inc M ≤ 0.50 at ε = 1, 0.69 at ε = 0.25 (`check10`) | converges |
| Dipolar truncation | vs Brenner (exact): 5.1 % (ε=1), 0.9 % (2), < 0.3 % (≥ 3); difference from the O(x³) series = (0.29, 0.11, 0.04) x⁴ at x = 1/2, 1/3, 1/5 (`check2`) → observed order 4 | quantified |
| Root finding | Brent, xtol 10⁻⁴; crossovers identical on a 120-point grid with doubled quadrature (`check8`) | converged |
| Classical limits | unsteady drag (machine precision), DBB porous sphere (10⁻⁴), Brenner/Faxén, inviscid image (5 % at Wo = 160, approaching), transparent interface (< 10⁻¹⁴), α_p → ∞ (4 digits) | all recovered |

**Error budget for plotted quantities (ε = 1):** dipolar truncation ≤ 5 % (normal), ≤ 1.5 % (parallel), ≤ 1 % for
ε ≥ 2 — dominant; FEM comparison (author-supplied) 4 % on Wo_c, 3 % on Wo_c↑, 0.4 % on γ̂_int, 10 % on Wo_c↓ at
α_p = 20; quadrature < 10⁻¹³; root finding < 10⁻⁴; Richardson extrapolation of steady values < 10⁻³ for ε ≤ 4.

## 2. Physical soundness of the findings
| Finding | Expected physics | Verdict |
|---|---|---|
| F1 Basset memory removed by the wall | −χ̂_int → Wo/√2 as Wo → 0 for any blocking/screening wall (0.99/0.96 at Wo = 0.01; holds for α_p ≥ 1, weakens to 0.88 at α_p = 0.1 as the Brinkman length exceeds δ_v) — consistent with wall-modified long-time tails (Felderhof 2005; Mo et al. 2015) | sound |
| F2 damping maximum at Wo/α_p ≈ 1–2 | interior maxima, converged; mechanism stated as interpretation | sound as stated |
| F3 transparency law | now derived asymptotically and verified (check15) | sound |
| F4 Ω² scaling | first-reflection argument; computed ratios 5–30 % below Ω² | sound ("approximately") |
| F5 double parallel window | converged; potential/vortical decomposition (check9) | sound |
| Positivity of dissipation | γ̂_int > 0 everywhere; total damping > 0 for all reported cases; β > 0 is an energy source (energy identity, App. C) | sound with the stated β ≤ 0.5 restriction |

## 3. Realistic parameters
| Item | Issue | Severity |
|---|---|---|
| Mucus mapping "pore sizes 100–500 nm ↔ √k_p ≈ 0.1–0.5 µm" | uncited, and equates Darcy length with mesh size | **major** |
| Glycocalyx "√k_p typically 2–3 nm" | uncited (no source found that we could verify) | **major** |
| "Glycocalyx-like" α_p = 20 (Sec. VI, Figs. 6–7) | for micrometre cells α_p ≳ 10³ in the glycocalyx: effectively rigid; α_p = 20 is mucus-like | **major** |
| Small amplitude | AFM thermal amplitudes (nm) and acoustic displacements (nm) ≪ b, ε b ✓ | ok |
| Brinkman/OTW validity | β ranges from OTW; β ≤ 0.5 admissibility | ok |
| Frequencies | Wo_c ≈ 3 → ≈ 14 kHz, Wo_c↓ ≈ 46 → 3.4 MHz for b = 10 µm | ok |

## 4. Scoop check (searches with `--year-from 2026`, plus web)
- **Faltas, Ashmawy, Mahrous, Ragab, El Sayed (2026), "Rectilinear and rotary oscillations of a porous sphere near a
  Brinkman half-space: frequency filtering and interfacial stress-jump effects", Chin. J. Phys. 104, 1193–1223,
  doi:10.1016/j.cjph.2026.10.017** (online 21 Oct 2026). Abstract not accessible (paywall); keywords include porous
  spheres, stress jumps, rotary oscillation, Womersley number, frequency filtering, lubrication, Hankel transform. This
  overlaps the claim "no study treats a particle oscillating near a permeable half-space" → **major**: the claim is no
  longer true.
- Other 2026 hits (El-Sapa 2026, Daddi-Moussa-Ider & Vilfan 2026, Batalha et al. 2026) already cited or not overlapping.
- Novelty after revision: still holds for the core–shell particle with slip core, the added-mass sign structure
  (crossover map, transparency law, window closure, double parallel windows), the Basset-removal mechanism, and the
  Ω² softness scaling — **provided** the 2026 paper does not compute these; the authors must confirm.

## 5. Number consistency
All numbers in the body trace to `code/` outputs (results.json, results2.json, results3.json, results4.json and the
supporting scripts), except:
- FEM benchmark values (Wo_c = 3.04, Wo_c↑ = 3.15, γ̂_int = 0.280, Wo_c↓ = 41.2): author-supplied, no script → **major**
  (reproducibility).
- Abstract/conclusion use 0.116 α_p² and list the asymptotic law as future work, while the body derives 0.1179 α_p²
  → **minor**, fixed in Stage 3.
- "identical for normal and parallel oscillation": computed values differ by ~1 % → minor.

## 6. Reproducibility
All seven figures are produced by `figures/make_figures.py` from `code/results*.json`; Tables III–IV from
`code/make_results*.py`. Not reproducible: the FEM benchmark.

## 7. Verdict
**Before:** major revision (scoop overlap undistinguished; unrealistic/uncited parameter mapping; FEM not
reproducible).

## Responses
| # | Issue | Response |
|---|---|---|
| R1 | Scoop (Faltas et al. 2026) | Cited in the Introduction guide points as the closest prior work; Gap bullet rewritten to state what remains new; `\TODO` for the authors to state that paper's method and observables precisely (abstract inaccessible). Strongest points (Stage 2) avoid any claim the 2026 paper may contain. |
| R2 | Mucus parameters | Rewritten with measured pore sizes (Duncan et al. 2016: 110–930 nm in fresh CF sputum; Suk et al. 2009: 60–300 nm), used only as an upper bound on √k_p; the accessible frequencies follow (≈ 15 kHz and 3.4 MHz at α_p = 20, b = 10 µm). |
| R3 | Glycocalyx | Reframed: for micrometre particles the glycocalyx is effectively rigid (α_p ≳ 10³); only the low-frequency signature applies; value marked `\TODO{citation needed}`. "Glycocalyx-like/endothelial-like" replaced by "permeable layer (mucus-like)" in Sec. VI and Figs. 6–7 captions; Table I range annotated. |
| R4 | FEM reproducibility | Kept as the authors' data; `\TODO` to add script, mesh and output to `code/`. |
| R5 | Consistency of the law in abstract/conclusion | Fixed in Stage 3. |
| R6 | "identical" normal/parallel | Now "at leading order", with the computed 98.5 %/99.3 %. |

**After the fixes (re-run of items 1–6):** method verified; findings sound; parameters realistic and cited (one
citation still needed for the glycocalyx); remaining open items are author actions (scoop distinction, FEM files).
**Verdict: minor revision.**
