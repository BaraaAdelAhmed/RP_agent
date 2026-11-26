"""Test the scaling argument for the upper crossover: for Wo >> alpha_p,
chi_int ~ a*alpha_p^2 - c*Wo  (positive image ~ alpha_p^2, viscous part ~ Wo)."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
for W in [60.0, 120.0]:
    aps = np.array([5., 10., 15., 20.]); chi = []
    for ap in aps:
        s = o.Sphere(W); M = o.reflection_matrix(W, 2.0, 'z', ap); F, F0 = o.force_M(s, M); chi.append((F-F0).imag/(6*np.pi))
    chi = np.array(chi); A = np.vstack([aps**2, np.ones_like(aps)]).T
    coef, res, *_ = np.linalg.lstsq(A, chi, rcond=None)
    print(f'Wo={W}: chi={np.round(chi,4)}  fit chi = {coef[0]:.5f} ap^2 + ({coef[1]:.4f});  rel. resid={np.sqrt(res[0])/np.abs(chi).max() if res.size else 0:.2e}')
