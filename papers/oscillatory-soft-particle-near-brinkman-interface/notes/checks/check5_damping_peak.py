"""Locate the high-frequency damping maximum for several alpha_p (normal, eps=1, rigid sphere)."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
for ap in [10., 20., 50.]:
    W = np.logspace(0.5, np.log10(6*ap), 40); g = []
    for w in W:
        s = o.Sphere(w); M = o.reflection_matrix(w, 2.0, 'z', ap); F, F0 = o.force_M(s, M); g.append(-(F-F0).real/(6*np.pi))
    g = np.array(g); i = g.argmax()
    sW = o.Sphere(W[i]); Mw = o.reflection_matrix(W[i], 2.0, 'z', 1e6, rigid_wall=True); Fw, F0w = o.force_M(sW, Mw)
    print(f'alpha_p={ap:5.1f}: max gamma_int={g[i]:.3f} at Wo={W[i]:.1f} (Wo/alpha_p={W[i]/ap:.2f}); rigid wall at same Wo: {-(Fw-F0w).real/(6*np.pi):.3f}; edge={i in (0,len(W)-1)}')
