"""Second pass: all sign changes of the wall-induced reactive force (multiple crossovers),
and wall-induced force contrast for the acoustofluidic application."""
import numpy as np, json, warnings
from scipy.optimize import brentq
import osc_solver as o
warnings.filterwarnings('ignore')
def chi(W, eps, d, sph_kw={}, ap=1e6, bp=0.0, rigid=False):
    s = o.Sphere(W, **sph_kw); M = o.reflection_matrix(W, 1+eps, d, ap, bp, 1.0, rigid_wall=rigid)
    F, F0 = o.force_M(s, M); return (F-F0).imag/(6*np.pi)
def crossings(eps, d, hi=250., n=70, **k):
    g = np.logspace(np.log10(0.05), np.log10(hi), n); v = np.array([chi(W, eps, d, **k) for W in g])
    out = []
    for i in range(n-1):
        if np.isfinite(v[i]) and np.isfinite(v[i+1]) and np.sign(v[i]) != np.sign(v[i+1]):
            r = brentq(lambda W: chi(W, eps, d, **k), g[i], g[i+1], xtol=1e-4)
            out.append([r, 1 if v[i+1] > 0 else -1])   # +1 : neg->pos, -1 : pos->neg
    return out
R = {}
aps = np.logspace(np.log10(3), np.log10(100), 11).tolist()
c = {'ap': aps}
for d in ['z', 'x']:
    c[f'{d}_wall'] = crossings(1.0, d, rigid=True)
    for bp in [-0.5, 0.0, 0.5]:
        c[f'{d}_{bp}'] = [crossings(1.0, d, ap=a, bp=bp, hi=max(150., 2.5*a)) for a in aps]
        print(d, bp, c[f'{d}_{bp}'], flush=True)
R['cross_ap'] = c
als = [1, 2, 3, 5, 8, 12, 20, 35, 50]
cs = {'alpha_s': als}
for d in ['z', 'x']:
    cs[f'{d}_rigid'] = crossings(1.0, d, sph_kw=dict(gam=1.0), ap=20.0, hi=200.)
    for gm in [0.0, 0.5, 0.8, 0.95]:
        cs[f'{d}_{gm}'] = [crossings(1.0, d, sph_kw=dict(gam=gm, alpha_s=float(a)), ap=20.0, hi=200.) for a in als]
        print(d, gm, cs[f'{d}_{gm}'], flush=True)
R['cross_soft'] = cs
eg2 = np.linspace(1.0, 4.0, 13).tolist(); Wg2 = np.logspace(-1, 1.5, 21).tolist()
ac = {'eps': eg2, 'Wo': Wg2}
for lab, kw in [('ctc', dict(gam=0.9, alpha_s=20.)), ('wbc', dict(gam=0.7, alpha_s=5.))]:
    for d in ['z', 'x']:
        Fi = np.zeros((len(eg2), len(Wg2)), complex); Fz = np.zeros(len(Wg2), complex)
        for j, W in enumerate(Wg2):
            s = o.Sphere(W, **kw)
            for i, e in enumerate(eg2):
                F, F0 = o.force_M(s, o.reflection_matrix(W, 1+e, d, 20.0)); Fi[i, j] = F-F0
            Fz[j] = F0
        ac[f'{lab}_{d}_Fint'] = [[Fi.real.tolist(), Fi.imag.tolist()]]
        ac[f'{lab}_{d}_Finf'] = [Fz.real.tolist(), Fz.imag.tolist()]
R['acoustic2'] = ac
json.dump(R, open('results2.json', 'w')); print('ALL DONE')
