"""Independent checks of the asymptotic transparency law Wo_c(down) = alpha_p^2/(6 sqrt 2) (Sec. V B).
(a) R_Phi of the full 6x6 interface system at k = O(1/h) << Wo vs (c3-c1)/(c3+c1) and its expansion.
(b) Symbolic expansion of Z_p B for large Wo.
(c) Balance of the two reactive terms -> prefactor 1/(6 sqrt 2).
(d) Computed Wo_c(down) (results2.json, normal and parallel) vs the law, as alpha_p grows."""
import sys, json, warnings, numpy as np, sympy as sp
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
# (a) numerical reflection coefficient of the potential mode, normal incidence of a potential mode, rigid-free Brinkman layer
def R_phi(Wo, ap, k=0.5):
    lf = np.sqrt(-1j*Wo**2); lp = np.sqrt(ap**2 - 1j*Wo**2); cpf = 1j*Wo**2; cpp = 1j*Wo**2 - ap**2
    kx, ky = k, 0.0; q = np.sqrt(k**2+lf**2); qp = np.sqrt(k**2+lp**2)
    pot = lambda s: np.array([1j*kx, 1j*ky, s], complex); pol = lambda s: np.array([1j*kx*s, 1j*ky*s, k**2], complex)
    tor = np.array([1j*ky, -1j*kx, 0], complex)
    def st(u, s, p, mu): return np.array([mu*(s*u[0]+1j*kx*u[2]), mu*(s*u[1]+1j*ky*u[2]), -p+2*mu*s*u[2]])
    R = [(pot(-k), -k, cpf), (pol(-q), -q, 0), (tor, -q, 0)]; T = [(pot(k), k, cpp), (pol(qp), qp, 0), (tor, qp, 0)]
    A = np.zeros((6, 6), complex)
    for j in range(3):
        uR, sR, pR = R[j]; uT, sT, pT = T[j]; SR = st(uR, sR, pR, 1); ST = st(uT, sT, pT, 1)
        A[0:3, j] = uR; A[0:3, 3+j] = -uT; A[3, j] = SR[2]; A[3, 3+j] = -ST[2]; A[4:6, j] = -SR[0:2]; A[4:6, 3+j] = ST[0:2]
    ui = pot(k); si = st(ui, k, cpf, 1)          # unit incident potential mode at z=0
    rhs = np.concatenate([-ui, [-si[2]], si[0:2]])
    x = np.linalg.solve(A, rhs); return x[0]
print('(a) R_Phi: full system vs (c3-c1)/(c3+c1) vs two-term expansion')
for Wo, ap in [(50, 10), (100, 20), (200, 20), (300, 30)]:
    c1, c3 = 1j*Wo**2, 1j*Wo**2-ap**2
    print(f'   Wo={Wo:4d} ap={ap:3d}: full={R_phi(Wo, ap):.3e}  ratio-form={(c3-c1)/(c3+c1):.3e}  expansion={1j*ap**2/(2*Wo**2)+ap**4/(4*Wo**4):.3e}')
# (b) Z_p B large-Wo expansion
L, W = sp.symbols('lambda W', positive=True)
Zp = 6*sp.pi*(1+L+L**2/3); B = (3+3*L+L**2)/(2*L**2)
ser = sp.series(sp.expand(Zp*B/(sp.pi*L**2)), L, sp.oo, 3).removeO()
print('(b) Z_p B /(pi lambda^2) =', sp.simplify(ser), ' -> with lambda = e^{-i pi/4} Wo: 1 + 6/lambda = 1 + 3 sqrt2 (1+i)/Wo:',
      sp.simplify(6/(sp.exp(-sp.I*sp.pi/4)*W) - 3*sp.sqrt(2)*(1+sp.I)/W) == 0)
# (c) balance -> prefactor
a = sp.symbols('alpha', positive=True)
sol = sp.solve(sp.Eq(a**4/(4*W**4), 3*sp.sqrt(2)*a**2/(2*W**3)), W)
print('(c) balance gives Wo =', sol, '=', [sp.nsimplify(s/a**2) for s in sol], '~', [float(s/a**2) for s in sol])
# (d) computed crossovers vs the law
R2 = json.load(open('../../code/results2.json'))['cross_ap']
print('(d) computed Wo_c(down) / (alpha_p^2/(6 sqrt2)), beta_p=0:')
for d in 'zx':
    out = []
    for ap, L_ in zip(R2['ap'], R2[f'{d}_0.0']):
        dn = [w for w, s in L_ if s < 0 and w > 5]
        if dn: out.append((round(ap, 1), round(dn[-1]/(ap**2/(6*np.sqrt(2))), 4)))
    print('   ', d, out)
