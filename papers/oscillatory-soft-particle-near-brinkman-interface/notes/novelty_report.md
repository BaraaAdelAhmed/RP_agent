# Novelty report — Oscillatory soft particle near a fluid–Brinkman interface

## 1. Idea in one sentence
We compute the frequency-dependent hydrodynamic force (damping, added mass and phase lag) on a soft core–shell sphere (unsteady Brinkman shell, Navier-slip core, Ochoa-Tapia–Whitaker stress-jump surface) that oscillates normal or parallel to a semi-infinite unsteady-Brinkman layer with an interfacial stress jump. We use this to map how layer permeability, the stress jump and particle softness move the Womersley-number crossover of the wall-induced added mass reported by Zhang et al. (2023) for a rigid sphere near a rigid wall.

## 2. Search log (2026-11-26)
Sources: `rp.py search` (OpenAlex + arXiv; Semantic Scholar returned HTTP 429 on some calls), WebSearch, WebFetch (Cambridge abstract page of Zhang et al. 2023).

| # | Query | Filter | Relevant hits |
|---|---|---|---|
| 1 | unsteady drag sphere oscillating near wall added mass | – | Zhang 2023 JFM; Batalha 2026 arXiv |
| 2 | oscillating sphere near porous Brinkman wall | – | Sherwood 2020; Ollila 2012; Algatheem 2025; Daddi-Moussa-Ider 2026 |
| 3 | sphere motion near Brinkman interface stress jump | – | Richardson & Power 1996; porous-shell stress-jump papers |
| 4 | unsteady Stokes flow porous half-space oscillating particle | – | Sherwood 2020 only |
| 5 | soft particle core-shell oscillatory flow drag | – | none relevant |
| 6 | porous sphere unsteady Brinkman oscillation | – | Prakash & Raja Sekhar 2011; Ollila 2012 |
| 7 | glycocalyx hydrodynamics particle near endothelial surface layer | – | Smith et al. 2003 (bio motivation) |
| 8 | particle near fluid-porous interface Beavers-Joseph slip | – | none with a particle |
| 9 | oscillating sphere near permeable interface frequency dependent drag | year ≥ 2021 | El-Sapa 2022 (impermeable slip wall); Algatheem 2025 |
| 10 | particle near porous layer unsteady Stokes Brinkman reflection | year ≥ 2021 | Daddi-Moussa-Ider 2023 (Brinkman plate) |
| 11 | colloidal probe AFM oscillation near soft porous brush layer | year ≥ 2021 | none relevant |
| 12 | acoustofluidic separation circulating tumor cells deformability | year ≥ 2021 | reviews (application context) |
| 13 | (author's own works, title queries) | – | Faltas 2021, Faltas 2024, El-Sayed 2026 |
| W1 | WebSearch: sphere oscillating near porous Brinkman layer unsteady Stokes added mass drag 2024 2025 | – | no paper combining the two |

## 3. Closest prior work
| Citation | What it does | Difference from this work |
|---|---|---|
| Zhang et al. 2023 JFM (`zhang2023unsteady`) | Rigid no-slip sphere oscillating normal to a rigid wall; finite elements, asymptotics and AFM; the resonance-frequency shift crosses from positive to negative as Wo increases | Rigid particle and impermeable wall only. Here the wall is a permeable Brinkman layer with a stress jump, the particle is soft, and both normal and parallel motion are treated |
| Sherwood 2020 JFM (`sherwood2020unsteady`) | 1-D unsteady flow above an oscillating or impulsively started porous wall | No particle, no finite-size interaction force |
| Faltas et al. 2021 EJMB (`faltas2021axisymmetric`) | Steady axisymmetric motion of a slip sphere near a Brinkman interface with stress jump | Steady only, rigid particle. This work is its unsteady generalisation and reduces to its geometry as Wo → 0 |
| Faltas et al. 2024 CJP (`faltas2024oscillations`) | Oscillating sphere near a flat fluid–fluid interface | The second phase is a clear fluid, not porous, and the particle is rigid |
| El-Sayed et al. 2026 Mathematics (`elsayed2026effect`) | Thermocapillary migration of a Brinkman porous sphere with Beavers–Joseph slip | Steady, unbounded, thermally driven; no wall |
| Ollila et al. 2012 JFM; Prakash & Raja Sekhar 2011 | Oscillating porous sphere in unbounded fluid | No interface; core–shell with stress jump and slip core not treated |
| Richardson & Power 1996 | Steady motion of a porous particle near a plane interface | Steady; no porous half-space with stress jump |
| Daddi-Moussa-Ider et al. 2023, 2026 | Brinkman point-force Green's functions near no-slip walls or plates | Point force only, impermeable boundary, no particle response |
| Algatheem et al. 2025; El-Sapa 2022 | Oscillating spheres in a Brinkman medium or near an impermeable slip wall | No fluid–porous interface |
| Batalha et al. 2026 arXiv | Oscillating sphere near an elastic wall, lubrication regime | Elastic (deformable) wall, not a permeable one; near-contact regime only |

## 4. Verdict
**Novel** (confidence: moderate–high). No paper found treats a finite-size particle oscillating near a semi-infinite permeable (Brinkman) half-space, with or without a stress jump. None treats a soft core–shell particle oscillating near any wall. The individual ingredients exist: unsteady porous sphere, steady sphere near a Brinkman interface, rigid sphere oscillating near a rigid wall. Their combination, and the inverse "frequency-sweep signature of a permeable wall", appear to be new. Limits of the search: OpenAlex and arXiv plus one web search; Semantic Scholar was partly rate-limited; very recent conference papers may have been missed.

## 5. Strong point
**A permeable biological layer leaves a distinctive, measurable fingerprint in the frequency-dependent force on a nearby oscillating particle.** The Womersley number at which the wall-induced added mass changes sign shifts with the layer's permeability and stress jump. For sufficiently permeable layers the crossover disappears altogether in normal oscillation. This gives a non-contact spectroscopic route to measuring glycocalyx or mucus permeability.

Contribution bullets:
- Semi-analytical solution of unsteady Stokes–Brinkman flow for a core–shell sphere (Brinkman shell, Navier-slip core, OTW stress jump) oscillating normal or parallel to a Brinkman half-space with stress jump. The method combines exact l = 1 sphere solutions, an exact Fourier-space reflection of the unsteady singularities at the porous interface, and a self-consistent dipolar closure that sums all orders of reflection.
- Validation against the exact unsteady unbounded drag, the Debye–Bueche–Brinkman porous-sphere drag, Brenner's and Faxén's steady wall corrections, and the inviscid image added mass.
- Maps of the interaction damping γ_int, the added-mass shift m_int and the crossover Womersley number Wo_c against α_p, β_p, α_s and γ, for normal and parallel oscillation.
- Bio-relevant consequences: (i) inverse estimation of glycocalyx or mucus permeability; (ii) phase- and amplitude-contrast maps between cell-like particles of different softness near an endothelial-like layer (acoustofluidic sorting); (iii) design guidance for mucus-penetrating vesicles.

## 6. Reviewer risks and answers
1. **"The dipolar (l = 1) closure is not exact at small gaps."** We quantify the error against Brenner's exact solution: about 6 % (normal) and 2 % (parallel) at ε = 1, decaying quickly with ε. We restrict quantitative claims to ε ≥ 1, state that the lubrication regime is out of scope, and leave full multipole collocation as an extension.
2. **"The OTW and Brinkman parameters for the glycocalyx are uncertain."** We use literature ranges (Table 1 of the blueprint) and present trends over the full range. The inverse problem is posed as a proof of concept.
3. **"Sign convention for the added mass."** We define m_int so that F_int = −γ_int U − m_int dU/dt, and relate our sign change explicitly to the frequency-shift crossover measured by Zhang et al.
4. **"Particle deformability (soft = permeable, not elastic)."** The word "soft" here means a hydrodynamically permeable shell (as in electrokinetic soft-particle theory). Elastic deformation is outside the model; we cite Batalha et al. for that.
5. **"Free rotation for parallel oscillation."** The model prescribes translation (as for an AFM probe or an acoustically driven particle). Rotation–translation coupling enters at O((b/h)^4), beyond the dipolar closure.
