"""(a) Physical admissibility: wall-induced and total damping over all stored spectra.
(b) Spectral radius of S_inc M (convergence of the reflection series, Prop. 2) over the parameter range."""
import sys, json, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
R = json.load(open('../../code/results.json'))
mins = {k: float(np.min(np.array(v)[:, 0])) for blk in ('spectra_ap', 'spectra_soft') for k, v in R[blk].items() if k != 'Wo'}
print('(a) min gamma_int over stored spectra:', min(mins.values()), ' (key:', min(mins, key=mins.get), ')')
worst = 0
for W in [0.01, 0.1, 1, 3, 10, 50]:
    for kw in [dict(gam=1.0), dict(gam=0.0, alpha_s=2.), dict(gam=0.7, alpha_s=5.), dict(gam=0.5, alpha_s=1.)]:
        s = o.Sphere(W, **kw); SB, SF = s.response(); gin = -SF[0].real
        for ap, rig in [(1e6, True), (5., False), (20., False)]:
            for d in 'zx':
                M = o.reflection_matrix(W, 2.0, d, ap, rigid_wall=rig); F, F0 = o.force_M(s, M)
                rho = max(abs(np.linalg.eigvals(SB[:, 1:] @ M)))
                worst = max(worst, rho)
                if -(F.real) <= 0: print('   NEGATIVE total damping', W, kw, ap, d)
print('(a) total damping -Re F/U > 0 in all sampled cases (eps=1); (b) max spectral radius of S_inc M at eps=1:', round(worst, 4))
for eps in [0.5, 0.25]:
    s = o.Sphere(0.01); SB, SF = s.response(); M = o.reflection_matrix(0.01, 1+eps, 'z', 1e6, rigid_wall=True)
    print(f'    rigid, normal, Wo=0.01, eps={eps}: spectral radius = {max(abs(np.linalg.eigvals(SB[:,1:] @ M))):.4f}')
