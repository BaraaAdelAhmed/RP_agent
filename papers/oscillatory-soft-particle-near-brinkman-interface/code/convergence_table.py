"""Appendix C: quadrature convergence of the reflection matrix and spectral radius of S_inc M."""
import warnings, numpy as np
import osc_solver as o
warnings.filterwarnings('ignore')
rows = [(0.05, 1.0, 'z', 1e6, True), (3.0, 1.0, 'x', 10.0, False), (30.0, 1.0, 'z', 20.0, False), (3.0, 0.25, 'z', 1e6, True), (10.0, 4.0, 'x', 50.0, False)]
for W, eps, d, ap, rig in rows:
    M1 = o.reflection_matrix(W, 1+eps, d, ap, rigid_wall=rig)
    M2 = o.reflection_matrix(W, 1+eps, d, ap, rigid_wall=rig, nk=128, ntheta=16)
    s = o.Sphere(W); SB, SF = s.response()
    rho = max(abs(np.linalg.eigvals(SB[:, 1:] @ M1)))
    print(f'Wo={W:5} eps={eps:4} {d} alpha_p={"wall" if rig else ap}: rel.change={np.abs(M2-M1).max()/np.abs(M1).max():.1e}  rho={rho:.3f}')
