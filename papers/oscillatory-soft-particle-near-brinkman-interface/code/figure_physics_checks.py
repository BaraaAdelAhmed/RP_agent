"""Figure review checks (pass 2 audit).
(a) Fig.3(b): double positive window in parallel oscillation at alpha_p=10 and the bump at alpha_p=5 -- persistence
    under refinement (dense Wo grid, doubled quadrature).
(b) Fig.3: low-Wo universality of chi_int across alpha_p -- and its breakdown as alpha_p -> 0 (transparent limit).
(c) Fig.3 high-Wo rigid-wall damping slope (Stokes-layer dissipation, expect gamma_int ~ Wo^1 asymptotically)."""
import sys, warnings, numpy as np
sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import osc_solver as o
def chi(W, ap, d, rigid=False, **q):
    s = o.Sphere(W); M = o.reflection_matrix(W, 2.0, d, ap, rigid_wall=rigid, **q); F, F0 = o.force_M(s, M)
    return (F-F0)/(6*np.pi)
print('(a) sign changes of chi_int, parallel, eps=1, on 120-point grid Wo in [0.5,20]; base vs doubled quadrature')
for ap in [5.0, 8.59, 10.0]:
    for q in [dict(), dict(nk=128, ntheta=16)]:
        W = np.logspace(np.log10(0.5), np.log10(20), 120); c = np.array([chi(w, ap, 'x', **q).imag for w in W])
        idx = np.where(np.sign(c[:-1]) != np.sign(c[1:]))[0]
        print(f'   alpha_p={ap:5.2f} quad={"x2" if q else "base"}: crossings at Wo~', np.round(np.sqrt(W[idx]*W[idx+1]), 2),
              f' max chi in windows={c.max():+.4f}')
print('(b) -chi_int/(Wo/sqrt2) at Wo=0.01 (normal, eps=1) vs alpha_p')
for ap in [0.1, 0.3, 1.0, 3.0, 5.0, 20.0, 1e6]:
    print(f'   alpha_p={ap:9.1f}: {-chi(0.01, ap, "z").imag/(0.01/np.sqrt(2)):.3f}')
print('(c) rigid-wall damping slope d ln gamma / d ln Wo (normal, eps=1)')
for W in [20, 50, 100, 200]:
    g1 = -chi(W, 1e6, 'z', rigid=True).real; g2 = -chi(1.2*W, 1e6, 'z', rigid=True).real
    print(f'   Wo={W}: gamma_int={g1:.3f}  slope={np.log(g2/g1)/np.log(1.2):.3f}')
