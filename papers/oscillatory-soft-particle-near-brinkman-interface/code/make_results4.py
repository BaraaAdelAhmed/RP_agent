"""Dense data for the print-quality figures (second draft pass). Same model and solver as make_results.py,
denser sampling only:  >= 200 points per curve, refined near sign changes; denser contour grids.
Output: results4.json."""
import json, warnings, numpy as np
from multiprocessing import Pool
from scipy.optimize import brentq
import osc_solver as o
warnings.filterwarnings('ignore')

def fint(args):
    W, eps, d, kw, ap, bp, rigid = args
    s = o.Sphere(W, **kw); M = o.reflection_matrix(W, 1+eps, d, ap, bp, 1.0, rigid_wall=rigid)
    F, F0 = o.force_M(s, M)
    return complex(F-F0), complex(F0)

def refine(grid, vals, f, n_add=6):
    """add points around each sign change of the imaginary part (chi) for smooth crossings"""
    g = list(grid)
    for i in range(len(grid)-1):
        if np.sign(vals[i].imag) != np.sign(vals[i+1].imag):
            g += list(np.logspace(np.log10(grid[i]), np.log10(grid[i+1]), n_add+2)[1:-1])
    return np.array(sorted(g))

def spectrum(pool, d, kw, ap, rigid, bp=0.0, eps=1.0, W=None):
    W = np.logspace(np.log10(0.05), np.log10(50), 220) if W is None else W
    v = pool.map(fint, [(w, eps, d, kw, ap, bp, rigid) for w in W]); Fi = np.array([a for a, _ in v])
    W2 = refine(W, Fi, None)
    v = pool.map(fint, [(w, eps, d, kw, ap, bp, rigid) for w in W2]); Fi = np.array([a for a, _ in v]); F0 = np.array([b for _, b in v])
    return dict(Wo=W2.tolist(), gam=(-Fi.real/(6*np.pi)).tolist(), chi=(Fi.imag/(6*np.pi)).tolist(),
                Finf_re=F0.real.tolist(), Finf_im=F0.imag.tolist(), Fint_re=Fi.real.tolist(), Fint_im=Fi.imag.tolist())

if __name__ == '__main__':
    R = {}
    with Pool(4) as pool:
        # Fig 3: spectra vs alpha_p (rigid sphere)
        R['spectra_ap'] = {f'{d}_{ap}': spectrum(pool, d, dict(gam=1.0), 1e6 if ap == 'wall' else float(ap), ap == 'wall')
                           for d in 'zx' for ap in ['wall', 50, 20, 10, 5]}
        print('spectra_ap', flush=True)
        # Fig 6(a,b): soft particle spectra (normal)
        R['spectra_soft'] = {f'z_{a}': spectrum(pool, 'z', dict(gam=1.0) if a == 'rigid' else dict(gam=0.7, alpha_s=float(a)), 20.0, False)
                             for a in [2, 5, 10, 'rigid']}
        print('spectra_soft', flush=True)
        # Fig 4 (steady): Richardson extrapolation on 200 eps points
        eg = np.linspace(1.0, 5.0, 200); st = {'eps': eg.tolist()}
        cases = {'wall': (1e6, 0.0, True), 'ap50': (50., 0.0, False), 'ap10': (10., 0.0, False),
                 'ap10_bpm': (10., -0.5, False), 'ap10_bpp': (10., 0.5, False)}
        for d in 'zx':
            for lab, (ap, bp, rig) in cases.items():
                r = {}
                for W in (0.01, 0.02):
                    v = pool.map(fint, [(W, e, d, dict(gam=1.0), ap, bp, rig) for e in eg])
                    r[W] = np.array([((a+b)/b).real for a, b in v])
                st[f'{d}_{lab}'] = (2*r[0.01]-r[0.02]).tolist()
        R['steady'] = st; print('steady', flush=True)
        # Fig 2: dense present curves
        ev = np.logspace(np.log10(0.25), np.log10(5.0), 200); val = {'eps': ev.tolist()}
        for d in 'zx':
            r = {}
            for W in (0.01, 0.02):
                v = pool.map(fint, [(W, e, d, dict(gam=1.0), 1e6, 0.0, True) for e in ev]); r[W] = np.array([((a+b)/b).real for a, b in v])
            val[d] = (2*r[0.01]-r[0.02]).tolist()
        Wv = np.logspace(np.log10(3), np.log10(200), 200); val['Wo'] = Wv.tolist()
        for d in 'zx':
            v = pool.map(fint, [(W, 1.0, d, dict(gam=1.0), 1e6, 0.0, True) for W in Wv])
            val[f'm_{d}'] = [a.imag/(4/3*np.pi*W**2) for (a, _), W in zip(v, Wv)]
        R['validation'] = val; print('validation', flush=True)
        # Fig 7: acoustic contrast, dense
        ac = {}
        Wl = np.logspace(-1, 1.5, 200); ac['Wo_line'] = Wl.tolist()
        eg2 = np.linspace(1.0, 4.0, 30); Wg2 = np.logspace(-1, 1.5, 50); ac['eps'] = eg2.tolist(); ac['Wo'] = Wg2.tolist()
        for lab, kw in [('ctc', dict(gam=0.9, alpha_s=20.)), ('wbc', dict(gam=0.7, alpha_s=5.))]:
            for e in (1.0, 4.0):
                v = pool.map(fint, [(W, e, 'z', kw, 20.0, 0.0, False) for W in Wl])
                ac[f'{lab}_phase_eps{e:g}'] = [float(np.degrees(np.angle(-(a+b)))) for a, b in v]
            for d in 'zx':
                v = pool.map(fint, [(W, e, d, kw, 20.0, 0.0, False) for e in eg2 for W in Wg2])
                ac[f'{lab}_{d}_absFint'] = np.abs(np.array([a for a, _ in v])).reshape(len(eg2), len(Wg2)).tolist()
        R['acoustic'] = ac; print('acoustic', flush=True)
    json.dump(R, open('results4.json', 'w')); print('ALL DONE')
