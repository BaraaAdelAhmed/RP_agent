import numpy as np, json, warnings
from scipy.optimize import brentq
import osc_solver as o
warnings.filterwarnings('ignore')
R = {}
def Fint(Wo, eps, d, sph_kw={}, ap=1e6, bp=0.0, mp=1.0, rigid=False):
    s = o.Sphere(Wo, **sph_kw)
    M = o.reflection_matrix(Wo, 1+eps, d, ap, bp, mp, rigid_wall=rigid)
    F, F0 = o.force_M(s, M)
    return F - F0, F0
def coeffs(*a, **k):
    Fi, F0 = Fint(*a, **k)
    return -Fi.real/(6*np.pi), Fi.imag/(6*np.pi), F0
def Woc(eps, d, lo=0.05, hi=60, **k):
    g = np.logspace(np.log10(lo), np.log10(hi), 28)
    v = [coeffs(W, eps, d, **k)[1] for W in g]
    for i in range(len(g)-1):
        if v[i] < 0 <= v[i+1]:
            return brentq(lambda W: coeffs(W, eps, d, **k)[1], g[i], g[i+1], xtol=1e-4)
    return np.nan

# 1. validation: steady (extrapolated) vs Brenner / Faxen series
def brenner(h):
    a = np.arccosh(h); n = np.arange(1, 60)
    t = n*(n+1)/((2*n-1)*(2*n+3))*((2*np.sinh((2*n+1)*a)+(2*n+1)*np.sinh(2*a))/(4*np.sinh((n+.5)*a)**2-(2*n+1)**2*np.sinh(a)**2)-1)
    return 4/3*np.sinh(a)*t.sum()
eps_v = np.array([0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5])
val = {'eps': eps_v.tolist(), 'normal': [], 'parallel': [], 'brenner': [], 'faxen': [], 'refl_n': []}
for e in eps_v:
    x = 1/(1+e)
    for d, key in [('z', 'normal'), ('x', 'parallel')]:
        r = []
        for W in [0.01, 0.02]:
            F, F0 = Fint(W, e, d, rigid=True); r.append(((F+F0)/F0).real)
        val[key].append(2*r[0]-r[1])
    val['brenner'].append(brenner(1+e) if e < 4.5 else np.nan)
    val['faxen'].append(1/(1-9/16*x+x**3/8-45/256*x**4-x**5/16))
    val['refl_n'].append(1/(1-9/8*x+x**3/2))
R['validation_steady'] = val
# high-Wo inviscid image check
hv = {'Wo': [5, 10, 20, 40, 80, 160], 'eps': 1.0}
for d in ['z', 'x']:
    hv[d] = [Fint(W, 1.0, d, rigid=True)[0].imag/(4/3*np.pi*W**2) for W in hv['Wo']]
x = 0.5
hv['pot_z'] = 0.5*(3/8*x**3); hv['pot_x'] = 0.5*(3/16*x**3)
R['validation_inviscid'] = hv
print('validation done', flush=True)

# 2. rigid sphere: spectra vs Wo for several alpha_p (beta_p=0), eps=1
Wg = np.logspace(-1.3, 1.7, 46).tolist()
sp_ = {'Wo': Wg}
for d in ['z', 'x']:
    for ap in ['wall', 50, 20, 10, 5]:
        kk = dict(rigid=True) if ap == 'wall' else dict(ap=float(ap))
        c = [coeffs(W, 1.0, d, **kk)[:2] for W in Wg]
        sp_[f'{d}_{ap}'] = [[a, b] for a, b in c]
R['spectra_ap'] = sp_
print('spectra done', flush=True)

# 3. critical Womersley vs alpha_p for beta_p
aps = np.logspace(np.log10(3), np.log10(300), 11).tolist()
wc = {'ap': aps}
for d in ['z', 'x']:
    wc[f'{d}_wall'] = Woc(1.0, d, rigid=True)
    for bp in [-0.5, 0.0, 0.5]:
        wc[f'{d}_{bp}'] = [Woc(1.0, d, ap=a, bp=bp) for a in aps]
        print(d, bp, wc[f'{d}_{bp}'], flush=True)
R['Woc_ap'] = wc

# 4. soft particle near glycocalyx-like layer (ap=20): spectra vs alpha_s, and Woc vs alpha_s, gamma
ss = {'Wo': Wg}
for d in ['z', 'x']:
    for As in [2, 5, 10, 'rigid']:
        kw = dict(gam=1.0) if As == 'rigid' else dict(gam=0.7, alpha_s=float(As))
        ss[f'{d}_{As}'] = [list(coeffs(W, 1.0, d, sph_kw=kw, ap=20.0)[:2]) for W in Wg]
R['spectra_soft'] = ss
als = [1, 2, 3, 5, 8, 12, 20, 35, 50]
ws = {'alpha_s': als}
for d in ['z', 'x']:
    for gm in [0.0, 0.5, 0.8, 0.95]:
        ws[f'{d}_{gm}'] = [Woc(1.0, d, sph_kw=dict(gam=gm, alpha_s=float(a)), ap=20.0) for a in als]
        print(d, gm, ws[f'{d}_{gm}'], flush=True)
    ws[f'{d}_rigid'] = Woc(1.0, d, sph_kw=dict(gam=1.0), ap=20.0)
R['Woc_soft'] = ws

# 5. steady normalised resistance vs eps (Wo->0), effect of ap, bp  (rigid & soft)
eg = np.linspace(1.0, 5.0, 17).tolist()
st = {'eps': eg}
for d in ['z', 'x']:
    for lab, kk in [('wall', dict(rigid=True)), ('ap50', dict(ap=50.)), ('ap10', dict(ap=10.)),
                    ('ap10_bpm', dict(ap=10., bp=-0.5)), ('ap10_bpp', dict(ap=10., bp=0.5))]:
        v = []
        for e in eg:
            r = [((lambda F: (F[0]+F[1])/F[1])(Fint(W, e, d, **kk))).real for W in [0.01, 0.02]]
            v.append(2*r[0]-r[1])
        st[f'{d}_{lab}'] = v
R['steady'] = st
print('steady done', flush=True)

# 6. Acoustofluidic contrast: CTC-like vs leukocyte-like near endothelium (ap=20, bp=0)
#    CTC: larger stiffer, gam=0.9, alpha_s=20; WBC: gam=0.7, alpha_s=5 (same outer radius scaling)
eg2 = np.linspace(1.0, 4.0, 13).tolist(); Wg2 = np.logspace(-1, 1.5, 21).tolist()
ac = {'eps': eg2, 'Wo': Wg2}
for lab, kw in [('ctc', dict(gam=0.9, alpha_s=20.)), ('wbc', dict(gam=0.7, alpha_s=5.))]:
    for d in ['z', 'x']:
        P = np.zeros((len(eg2), len(Wg2))); A = np.zeros_like(P)
        for i, e in enumerate(eg2):
            for j, W in enumerate(Wg2):
                Fi, F0 = Fint(W, e, d, sph_kw=kw, ap=20.0)
                F = Fi + F0
                P[i, j] = np.degrees(np.angle(-F)); A[i, j] = abs(F)/(6*np.pi)
        ac[f'{lab}_{d}_phase'] = P.tolist(); ac[f'{lab}_{d}_amp'] = A.tolist()
R['acoustic'] = ac
json.dump(R, open('results.json', 'w'))
print('ALL DONE')
