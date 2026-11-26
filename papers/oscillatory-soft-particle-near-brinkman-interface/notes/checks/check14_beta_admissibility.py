"""Where does a positive stress jump make the model non-dissipative?  Scan of total damping -Re(F/U)/(6 pi):
(a) isolated particle (beta_s) over alpha_s, kappa, Wo;  (b) reported configurations of the paper:
    rigid sphere near layers with beta_p = +0.5 over the crossover-scan range; Table IV soft particle with beta_s = +0.5."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
print('(a) unbounded porous/core-shell particle: min over Wo in [0.01, 200] of -Re F_inf/(6 pi U)')
Wg = np.logspace(-2, np.log10(200), 40)
for bs in [0.25, 0.5, 1.0]:
    for kap in [0.0, 0.7]:
        for a in [2., 5., 20.]:
            v = [-o.Sphere(W, gam=kap, alpha_s=a, beta_s=bs).response()[1][0].real/(6*np.pi) for W in Wg]
            i = int(np.argmin(v)); print(f'   beta_s={bs:4} kappa={kap} alpha_s={a:4}: min={v[i]:+.3f} at Wo={Wg[i]:.1f}')
print('(b1) rigid sphere, beta_p=+0.5, eps=1, normal/parallel: min total and min interaction damping over Wo in [0.05, 250]')
Wg2 = np.logspace(np.log10(0.05), np.log10(250), 50)
for ap in [3., 8.6, 20., 50., 100.]:
    for d in 'zx':
        tot, gi = [], []
        for W in Wg2:
            s = o.Sphere(W); M = o.reflection_matrix(W, 2.0, d, ap, 0.5); F, F0 = o.force_M(s, M)
            tot.append(-F.real/(6*np.pi)); gi.append(-(F-F0).real/(6*np.pi))
        print(f'   alpha_p={ap:5} {d}: min total={min(tot):+.3f}  min gamma_int={min(gi):+.4f} at Wo={Wg2[int(np.argmin(gi))]:.1f}')
print('(b2) Table IV soft particle kappa=0.7, alpha_s=5, beta_s=+0.5, alpha_p=20: min total damping over Wo in [0.05, 50]')
v = []
for W in np.logspace(np.log10(0.05), np.log10(50), 40):
    s = o.Sphere(W, gam=0.7, alpha_s=5., beta_s=0.5); M = o.reflection_matrix(W, 2.0, 'z', 20.0); F, F0 = o.force_M(s, M)
    v.append((-F.real/(6*np.pi), -F0.real/(6*np.pi)))
print('   min total=%.3f, min unbounded=%.3f' % (min(a for a, b in v), min(b for a, b in v)))
