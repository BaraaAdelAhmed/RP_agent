"""Numerical checks with the solver: closure vs classical reflection series (order in x=b/h),
Weyl identity, and the size of effects claimed but not plotted (core slip, beta_s)."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
from scipy.integrate import quad
from scipy.special import j0
# (a) Weyl/Hankel identity: e^{-lam R}/R = int_0^inf (k/q) e^{-q|z|} J0(k rho) dk , check real lam
lam, rho_, zz = 1.3, 0.7, 0.9
lhs = np.exp(-lam*np.hypot(rho_, zz))/np.hypot(rho_, zz)
rhs = quad(lambda k: k/np.sqrt(k*k+lam*lam)*np.exp(-np.sqrt(k*k+lam*lam)*zz)*j0(k*rho_), 0, 200, limit=400)[0]
print(f'(a) Weyl identity: lhs={lhs:.12f} rhs={rhs:.12f}')
# (b) closure vs reflection series 1/(1-9/8x+x^3/2) (normal) and Faxen (parallel); steady (Richardson)
def steady(eps, d):
    v = []
    for W in [0.01, 0.02]:
        s = o.Sphere(W); M = o.reflection_matrix(W, 1+eps, d, 1e6, rigid_wall=True); F, F0 = o.force_M(s, M)
        v.append((F/F0).real)
    return 2*v[0]-v[1]
print('(b) eps, x, closure-normal - series(O x^3), /x^4 ; closure-parallel - Faxen(O x^3 part), /x^4')
for eps in [1, 2, 4, 9, 19]:
    x = 1/(1+eps)
    n = steady(eps, 'z'); p = steady(eps, 'x')
    sn = 1/(1-9/8*x+x**3/2); sx = 1/(1-9/16*x+x**3/8)
    print(f'   {eps:3d} {x:.3f}  {n-sn:+.2e} {(n-sn)/x**4:+.3f}   {p-sx:+.2e} {(p-sx)/x**4:+.3f}')
# (c) effect of core slip and shell stress jump (claimed weaker / not computed)
for lab, kw in [('base gam=0.7 as=5', dict(gam=0.7, alpha_s=5.)), ('ell_c=0.5', dict(gam=0.7, alpha_s=5., ell=0.5)),
                ('beta_s=0.5', dict(gam=0.7, alpha_s=5., beta_s=0.5)), ('beta_s=-0.5', dict(gam=0.7, alpha_s=5., beta_s=-0.5)),
                ('rigid', dict(gam=1.0)), ('rigid ell=0.5', dict(gam=1.0, ell=0.5))]:
    res = []
    for W in [0.05, 3.0]:
        s = o.Sphere(W, **kw); M = o.reflection_matrix(W, 2.0, 'z', 20.0); F, F0 = o.force_M(s, M)
        res.append((-(F-F0).real/(6*np.pi), (F-F0).imag/(6*np.pi)))
    print(f'(c) {lab:18s} gam_int(Wo=.05)={res[0][0]:.4f}  gam_int(Wo=3)={res[1][0]:.4f} chi(Wo=3)={res[1][1]:+.4f}')
