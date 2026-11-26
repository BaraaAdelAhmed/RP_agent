"""Test the mechanism for Wo_c(down) ~ alpha_p^2: if transparency occurs at fixed |lambda_p-lambda_f| h,
then Wo_c(down) ~ alpha_p^2 h / const, i.e. it should scale linearly with h = 1+eps."""
import sys, warnings, numpy as np
sys.path.insert(0, "."); warnings.filterwarnings('ignore')
import osc_solver as o
from scipy.optimize import brentq
def chi(W, eps, ap, d='z'):
    s = o.Sphere(W); M = o.reflection_matrix(W, 1+eps, d, ap); F, F0 = o.force_M(s, M); return (F-F0).imag
for ap in [17.32, 24.6]:
    for eps in [1.0, 2.0, 3.0]:
        g = np.logspace(0.6, 2.6, 40); v = [chi(W, eps, ap) for W in g]
        roots = [brentq(chi, g[i], g[i+1], args=(eps, ap), xtol=1e-4) for i in range(len(g)-1) if v[i] > 0 >= v[i+1]]
        W = roots[-1] if roots else np.nan
        lf = np.sqrt(-1j*W**2); lp = np.sqrt(ap**2 - 1j*W**2)
        print(f'alpha_p={ap:6.2f} eps={eps}: Wo_down={W:8.2f}  Wo_down/(alpha_p^2 h)={W/(ap**2*(1+eps)):.4f}  |lam_p-lam_f| h={abs(lp-lf)*(1+eps):.3f}')
