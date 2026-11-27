"""2nd-draft figures: (A) regime map of sign(chi_int) over (Wo, alpha_p) at eps=1, normal and parallel;
(B) error analysis (quadrature convergence of M; dipolar-closure error vs x against Brenner).  -> results5.json"""
import json, warnings, numpy as np
from multiprocessing import Pool
import osc_solver as o
warnings.filterwarnings('ignore')
def chi(args):
    W, ap, d = args
    s = o.Sphere(W); M = o.reflection_matrix(W, 2.0, d, ap); F, F0 = o.force_M(s, M)
    return float((F-F0).imag/(6*np.pi))
def brenner(h):
    al = np.arccosh(h); n = np.arange(1, 200)
    with np.errstate(over='ignore', invalid='ignore'):
        t = n*(n+1)/((2*n-1)*(2*n+3))*((2*np.sinh((2*n+1)*al)+(2*n+1)*np.sinh(2*al))/(4*np.sinh((n+.5)*al)**2-(2*n+1)**2*np.sinh(al)**2)-1)
    return 4/3*np.sinh(al)*np.nansum(t)
if __name__ == '__main__':
    R = {}
    Wg = np.logspace(np.log10(0.2), np.log10(250), 90); ag = np.logspace(np.log10(2), 2, 60)
    R['map'] = {'Wo': Wg.tolist(), 'ap': ag.tolist()}
    with Pool(4) as pool:
        for d in 'zx':
            v = pool.map(chi, [(W, a, d) for a in ag for W in Wg])
            R['map'][d] = np.array(v).reshape(len(ag), len(Wg)).tolist()
            print('map', d, flush=True)
    # quadrature convergence: relative change of M vs nodes per panel (reference nk=128, ntheta=16)
    cases = [(0.05, 'z', 1e6, True), (3.0, 'x', 10.0, False), (30.0, 'z', 20.0, False)]
    qc = {'nk': [2, 4, 8, 16, 32, 64]}
    for W, d, ap, rig in cases:
        ref = o.reflection_matrix(W, 2.0, d, ap, rigid_wall=rig, nk=128, ntheta=16)
        qc[f'{W}_{d}_{ap}'] = [float(np.abs(o.reflection_matrix(W, 2.0, d, ap, rigid_wall=rig, nk=n) - ref).max()/np.abs(ref).max()) for n in qc['nk']]
    R['quad'] = qc
    # truncation: steady closure vs Brenner, normal, x = b/h in [0.1, 0.8]
    xs = np.linspace(0.12, 0.8, 18); err = []
    for x in xs:
        h = 1/x; vv = []
        for W in (0.005, 0.01):
            s = o.Sphere(W); M = o.reflection_matrix(W, h, 'z', 1e6, rigid_wall=True); F, F0 = o.force_M(s, M); vv.append((F/F0).real)
        cl = 2*vv[0]-vv[1]; err.append(abs(cl-brenner(h))/brenner(h))
    R['trunc'] = {'x': xs.tolist(), 'err': err}
    json.dump(R, open('results5.json', 'w')); print('ALL DONE')
