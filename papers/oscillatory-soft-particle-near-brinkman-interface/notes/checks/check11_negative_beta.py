"""Admissibility for negative stress-jump coefficients: the OTW jump contributes beta*mu/sqrt(k)*|u_t|^2 to the energy
balance, so beta<0 removes dissipation. Check total damping -Re(F/U) and wall-induced damping for beta in [-1, 0]."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
worst = (np.inf, None)
for bp in [-1.0, -0.5]:
    for ap in [3., 5., 20., 100.]:
        for W in [0.01, 0.3, 3., 30.]:
            for d in 'zx':
                for kw in [dict(gam=1.0), dict(gam=0.7, alpha_s=5., beta_s=-1.0), dict(gam=0.0, alpha_s=2., beta_s=-1.0)]:
                    s = o.Sphere(W, **kw); M = o.reflection_matrix(W, 2.0, d, ap, bp); F, F0 = o.force_M(s, M)
                    tot = -F.real/(6*np.pi); inf = -F0.real/(6*np.pi)
                    if tot < worst[0]: worst = (tot, dict(bp=bp, ap=ap, Wo=W, d=d, **kw), inf)
print('minimum total damping -Re F/(6 pi U) over beta_p, beta_s in {-1,-0.5}:', round(worst[0], 4), worst[1], ' (unbounded part', round(worst[2], 4), ')')
