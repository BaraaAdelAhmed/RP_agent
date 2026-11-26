# Outline (target: Physics of Fluids, REVTeX 4-2 / AIP)

## Abstract (guide bullets + commented draft)
Context (oscillating probes and cells near biological porous layers) → gap (only rigid sphere/rigid wall known) → method → key result (Wo_c shift and suppression; damping changes) → implication (non-contact permeability spectroscopy; acoustofluidic contrast).

## I. Introduction (guide points only, author writes prose)
- A. Motivation: glycocalyx, mucus, AFM microrheology, acoustofluidics (Smith 2003; Hossein 2023; Wu 2019; Pangeni 2023)
- B. Unsteady particle–wall hydrodynamics (Zhang 2023; Batalha 2026; El-Sapa 2022; Faltas 2024)
- C. Fluid–porous interfaces and porous particles (Ochoa-Tapia & Whitaker 1995; Sherwood 2020; Faltas 2021; Richardson & Power 1996; Ollila 2012; Prakash 2011; Daddi-Moussa-Ider 2023/2026; El-Sayed 2026)
- D. Gap and contributions (bullets from the novelty report)
- E. Organisation

## II. Problem Formulation (in full)
- A. Geometry and kinematics (core radius a, shell radius b, centre height h, gap ε, normal/parallel oscillation, exp(−iωt), small amplitude)
- B. Governing equations in three domains (unsteady Stokes; unsteady Brinkman in the shell relative to the moving matrix; unsteady Brinkman half-space); screening parameters λ_f, λ_s, λ_p
- C. Boundary and interface conditions (core impermeability + Navier slip; OTW stress jump on r = b; continuity + OTW jump on z = 0; decay)
- D. Dimensionless groups and bio-relevant ranges (table)
- E. Force decomposition and observables: F = F_∞ + F_int; γ_int, m_int (consistent sign convention), phase lag; Wo_c defined by m_int = 0; link to resonance-frequency shift
- Assumptions numbered (linearity, rigid stationary porous layer, homogeneous isotropic media, non-rotating prescribed translation, ε ≥ 1 validity)

## III. Solution Method: Exact Sphere Response and Fourier Reflection at the Porous Interface (in full)
- A. Helmholtz decomposition: potential + vortical fields in each domain; pressures
- B. Exact l = 1 solution for the core–shell sphere (Proposition 1: exterior field = potential dipole + vortical dipole; linear response matrices); closed-form limits (rigid: −6π(1+λ+λ²/9); DBB porous sphere)
- C. Generalised Faxén law (Lemma: force depends only on the centre values of the potential and vortical parts of the incident field)
- D. Reflection of the unsteady singularities at the Brinkman interface: 2-D Fourier representation, 6×6 interface system per wavevector, reflection matrix M(Wo, h; α_p, β_p, μ_p/μ)
- E. Self-consistent dipolar closure (Proposition 2: all orders of reflection in l = 1); algorithm; quadrature and complexity
- F. Limiting cases: α_p → 0 transparent interface (F_int → 0); α_p → ∞ rigid wall; Wo → 0 steady (Faltas 2021 geometry); Wo → ∞ inviscid image added mass

## IV. Results and Discussion (in full, only computed data)
- A. Setup: parameter table, baselines (rigid wall, rigid sphere), accuracy
- **Fig. 1** schematic of the geometry
- **Fig. 2** validation: (a) steady wall correction vs ε, normal and parallel, against Brenner (exact) and Faxén/reflection series; (b) m_int vs Wo at ε = 1 approaching the inviscid image values
- **Fig. 3** spectra for a rigid sphere at ε = 1: γ_int(Wo) and reactive part χ_int(Wo) for rigid wall and α_p = 50, 20, 10, 5; normal and parallel (4 panels)
- **Fig. 4** Wo_c vs α_p for β_p = −0.5, 0, 0.5; normal and parallel; rigid-wall reference line; suppression of the crossover for permeable layers
- **Fig. 5** soft particle near a glycocalyx-like layer (α_p = 20): spectra for α_s = 2, 5, 10 vs rigid (γ = 0.7); Wo_c vs α_s for γ = 0, 0.5, 0.8, 0.95
- **Fig. 6** steady-limit (Wo → 0) resistance vs ε for α_p and β_p (connects to Faltas 2021)
- **Fig. 7** acoustofluidic contrast: phase and amplitude maps (ε, Wo) of a CTC-like vs leukocyte-like particle near an endothelial-like layer
- **Table** selected numerical values (benchmarks)
- G. Biomedical implications: inverse permeability estimation, CTC sorting, mucus-penetrating carriers
- H. Limitations and sensitivity: l = 1 closure accuracy at ε < 1; no lubrication; rigid porous layer; non-rotating particle

## V. Conclusion (guide bullets)

## Appendices (in full)
- A. Radial functions and stress amplitudes
- B. Fourier mode vectors and the 6×6 interface system
