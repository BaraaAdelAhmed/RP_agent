"""Sensitivity to core slip (ell_c) and shell stress jump (beta_s): normal oscillation,
eps=1, alpha_p=20, beta_p=0.  Output: results3.json (Table in Sec. VI A)."""
import numpy as np, json, warnings
from scipy.optimize import brentq
import osc_solver as o
warnings.filterwarnings('ignore')
def F(W, kw):
    s = o.Sphere(W, **kw); M = o.reflection_matrix(W, 2.0, 'z', 20.0); Fz, F0 = o.force_M(s, M); return Fz - F0
def first_up(kw):
    g = np.logspace(np.log10(0.3), np.log10(20), 30); v = [F(W, kw).imag for W in g]
    for i in range(len(g)-1):
        if v[i] < 0 <= v[i+1]: return brentq(lambda W: F(W, kw).imag, g[i], g[i+1], xtol=1e-4)
    return float('nan')
cases = [('rigid, no slip', dict(gam=1.0)), ('rigid, ell=0.25', dict(gam=1.0, ell=0.25)), ('rigid, ell=0.5', dict(gam=1.0, ell=0.5)),
         ('soft, base', dict(gam=0.7, alpha_s=5.)), ('soft, ell=0.5', dict(gam=0.7, alpha_s=5., ell=0.5)),
         ('soft, beta_s=-0.5', dict(gam=0.7, alpha_s=5., beta_s=-0.5)), ('soft, beta_s=0.5', dict(gam=0.7, alpha_s=5., beta_s=0.5))]
out = []
for lab, kw in cases:
    a = F(0.05, kw); b = F(3.0, kw)
    row = dict(case=lab, gam0=-a.real/(6*np.pi), gam3=-b.real/(6*np.pi), chi3=b.imag/(6*np.pi), Woc=first_up(kw))
    out.append(row); print(row, flush=True)
json.dump(out, open('results3.json', 'w'), indent=1)
