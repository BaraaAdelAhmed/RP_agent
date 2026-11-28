# Independent finite-element check (normal oscillation, impermeable sphere, eps = 1)

- `fem_axisym.py`: axisymmetric Taylor–Hood (P2 velocity / P1 pressure) solver on an isoparametric quadratic mesh
  (gmsh + scikit-fem), complex unsteady Stokes in z > 0 and unsteady Brinkman (mu_p = mu, beta_p = 0) in z < 0 as one
  domain; rigid wall = zero velocity on z <= 0; F_int = F(layer or wall) - F(alpha_p = 0) on the same mesh.
- `sweep_low.py` -> `sweep_low.json`: Wo = 2.8-3.8, rigid wall and alpha_p = 20.
  Mesh: h = 0.02 b at the sphere and the interface, graded to 0.4 b at distance 1.5 b; domain r <= 30 b, |z| <= 30 b;
  127,330 unknowns. Unbounded force on the same mesh matches -6 pi (1 + lambda + lambda^2/9) to 1e-4.
- `refine_study.py` -> `refine_study.json` (mesh refinement at Wo = 3) and `domain_study_R30_R40_R60.txt`
  (domain size at Wo = 3): halving h changes gamma_int by < 0.001; R = 30 -> 60 changes gamma_int by < 0.001 and
  chi_int by < 2e-4.
- Results: Wo_c (rigid wall) = 3.04; Wo_c^up (alpha_p = 20) = 3.16; gamma_int(Wo = 3, alpha_p = 20) = 0.284.
- `hi_conv.py`, `hi_sweep.py` (and their json): high-frequency runs for alpha_p = 20 (mesh h = 0.005 b, R = 30 b);
  downward crossover between Wo = 44 (chi = +0.0046) and 48 (chi = -0.0043), i.e. about 46.
