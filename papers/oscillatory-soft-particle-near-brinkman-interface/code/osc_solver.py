"""
Oscillatory translation of a core-shell (soft) sphere near a fluid--Brinkman
interface with stress jump.  Unsteady (frequency-domain) Stokes/Brinkman flow.

Units: lengths scaled by outer radius b, viscosity by mu, velocity by |U|,
force by mu*b*|U|.  Time dependence exp(-i omega t).  Wo^2 = rho*omega*b^2/mu.

Method: exact l=1 solution of the core-shell sphere (Bessel-type functions) +
exact reflection of the sphere's exterior singularities (potential dipole +
unsteady Stokeslet-type vortical dipole) by the planar Brinkman interface via
2-D Fourier transforms; self-consistent l=1 (dipolar) closure of the
reflections (all orders of reflection retained in the l=1 sector).
"""
import numpy as np
import sympy as sp

# ---------------------------------------------------------------- radial blocks
_r, _lam, _r0 = sp.symbols('r lam r0')

def _vort_block(g):
    Ur = sp.diff(g, _r, 2) - _lam**2*g
    V = -sp.diff(g, _r)/_r + _lam**2*g
    return [sp.lambdify((_r, _lam, _r0), e, 'numpy') for e in
            (Ur, sp.diff(Ur, _r), V, sp.diff(V, _r))]

# decaying (outer) and regular (inner) Helmholtz kernels, scaled to avoid overflow
_H = _vort_block(sp.exp(-_lam*(_r - _r0))/_r)                       # ~ e^{-lam r}/r
_I = _vort_block((sp.exp(_lam*(_r-_r0)) - sp.exp(-_lam*(_r+_r0)))/(2*_r))             # ~ sinh(lam r)/r


def _blk_uniform(r):     # phi = r cos(theta)
    return dict(Ur=1.0+0j, dUr=0j, V=-1.0+0j, dV=0j, Phi=r)

def _blk_dipole(r):      # phi = d/dz (1/r) = -cos/r^2
    return dict(Ur=2/r**3+0j, dUr=-6/r**4+0j, V=1/r**3+0j, dV=-3/r**4+0j, Phi=-1/r**2)

def _blk_vort(K, r, lam, r0):
    Ur, dUr, V, dV = (f(r, lam, r0) for f in K)
    return dict(Ur=Ur, dUr=dUr, V=V, dV=dV, Phi=0j)


class Sphere:
    """Core-shell sphere, outer radius 1, core radius gam.
    gam = 1 -> rigid (impermeable) sphere with Navier slip ell on r=1.
    gam = 0 -> homogeneous porous (Brinkman) sphere.
    Shell: permeability ks = 1/alpha_s^2, Brinkman viscosity ratio ms = mu_s/mu,
    OTW stress-jump coefficient beta_s on r=1, Navier slip ell on core r=gam.
    """
    def __init__(self, Wo, gam=1.0, alpha_s=10.0, beta_s=0.0, ms=1.0, ell=0.0):
        self.Wo, self.gam, self.a_s, self.b_s, self.ms, self.ell = Wo, gam, alpha_s, beta_s, ms, ell
        self.iwr = 1j*Wo**2                                # i*omega*rho (dimensionless)
        self.lamf = np.sqrt(-1j*Wo**2 + 0j)                # fluid
        self.lams = np.sqrt((alpha_s**2 - 1j*Wo**2)/ms + 0j)  # shell
        self._build()

    # exterior block list: (name, block-func at r, pressure coeff multiplier)
    def _ext_blocks(self, r):
        lf = self.lamf
        return {
            'Up': (_blk_uniform(r), self.iwr),
            'D':  (_blk_vort(_I, r, lf, 1.0), 0.0),     # scaled: physical D = D_s*e^{-lam}
            'B':  (_blk_dipole(r), self.iwr),
            'C':  (_blk_vort(_H, r, lf, 1.0), 0.0),     # scaled: physical C = C_s*e^{lam}
        }

    def _shell_blocks(self, r):
        ls, g = self.lams, self.gam
        cp = self.iwr - self.a_s**2
        out = {'E': (_blk_uniform(r), cp),
               'G': (_blk_vort(_I, r, ls, 1.0), 0.0)}
        if g > 0:
            out['F'] = (_blk_dipole(r), cp)
            out['H'] = (_blk_vort(_H, r, ls, g), 0.0)
        return out

    @staticmethod
    def _amps(blk, cp, mu_eff, r):
        Ur, dUr, V, dV, Phi = blk['Ur'], blk['dUr'], blk['V'], blk['dV'], blk['Phi']
        P = cp*Phi
        Srr = -P + 2*mu_eff*dUr
        Srt = mu_eff*(dV - V/r - Ur/r)
        return np.array([Ur, V, Srr, Srt], dtype=complex)

    def _build(self):
        """Solve for scattered/shell coefficients for unit U, Up, D_s inputs."""
        g = self.gam
        ext1 = {k: self._amps(b, cp, 1.0, 1.0) for k, (b, cp) in self._ext_blocks(1.0).items()}
        self.ext1 = ext1
        unk_ext = ['B', 'C']
        if g >= 1.0:   # rigid sphere with slip ell on r=1
            # rows: Ur(1) = U ;  V(1) + U = ell*Srt(1)
            def rows(col):
                a = ext1[col]
                return np.array([a[0], a[1] - self.ell*a[3]])
            A = np.column_stack([rows(c) for c in unk_ext])
            rhs = {'U': np.array([1.0, -1.0]),           # Ur - U = 0 ; V + U - ell Srt = 0
                   'Up': -rows('Up'), 'D': -rows('D')}
            unk = unk_ext
        else:
            sh1 = {k: self._amps(b, cp, self.ms, 1.0) for k, (b, cp) in self._shell_blocks(1.0).items()}
            unk_sh = list(sh1.keys())
            unk = unk_ext + unk_sh
            n = len(unk)
            def col_ext(c):
                a = ext1[c]
                v = [a[0], a[1], a[2], -a[3] - self.b_s*self.a_s*a[1]]
                return np.array(v + [0]*(n - 4))
            def col_sh(c):
                a = sh1[c]
                v = [-a[0], -a[1], -a[2], a[3]]
                if g > 0:
                    ag = self._amps(self._shell_blocks(g)[c][0], 0.0, self.ms, g)
                    v += [ag[0], ag[1] - self.ell*ag[3]/self.ms]
                return np.array(v)
            A = np.column_stack([col_ext(c) for c in unk_ext] + [col_sh(c) for c in unk_sh])
            # uniform U part of shell: Ur=1, V=-1, pressure iwr*r -> Srr=-iwr, Srt=0
            # appears in r=1 continuity (moved to rhs) and in stress-jump (V_ext+U)
            rU = np.zeros(n, complex)
            rU[0] = 1.0; rU[1] = -1.0; rU[2] = -self.iwr
            rU[3] = self.b_s*self.a_s*1.0          # +beta*alpha*(V+U): U part -> rhs = -(...)
            rhs = {'U': rU,
                   'Up': -col_ext('Up'), 'D': -col_ext('D')}
        X = {k: np.linalg.solve(A, v) for k, v in rhs.items()}
        self.coef = {k: dict(zip(unk, X[k])) for k in X}
        self.unk = unk

    def response(self):
        """Return matrices for inputs (U, Up, w0) [w0 = centre value of regular
        vortical incident field]:  [B, C]_phys = SB @ inp ;  F = SF @ inp."""
        lf = self.lamf
        Dfac = -3.0/(2*lf**3)*np.exp(lf)   # D_s per unit w0 (D_phys = D_s e^{-lam})
        SB = np.zeros((2, 3), complex); SF = np.zeros(3, complex)
        for j, key in enumerate(['U', 'Up', 'D']):
            c = self.coef[key]
            scale = Dfac if key == 'D' else 1.0
            Bp = c['B']*scale
            Cp = c['C']*np.exp(lf)*scale
            SB[:, j] = [Bp, Cp]
            # force = 4pi/3 (Srr - Srt) at r=1 (exterior), incl. incident
            S = c['B']*self.ext1['B'] + c['C']*self.ext1['C']
            if key == 'Up': S = S + self.ext1['Up']
            if key == 'D':  S = S + self.ext1['D']
            SF[j] = 4*np.pi/3*(S[2] - 2*S[3])*scale
        return SB, SF


# ------------------------------------------------------------- reflection
def _gl(n, a, b):
    x, w = np.polynomial.legendre.leggauss(n)
    return 0.5*(b-a)*x + 0.5*(b+a), 0.5*(b-a)*w

def reflection_matrix(Wo, h, direction, alpha_p, beta_p=0.0, mp=1.0, rigid_wall=False,
                      nk=64, npanel=None, ntheta=8):
    """2x2 matrix M: [Up, w0] (e-components of reflected potential velocity and
    regular vortical velocity at the sphere centre (0,0,h)) = M @ [B, C]."""
    lf = np.sqrt(-1j*Wo**2 + 0j)
    lp = np.sqrt((alpha_p**2 - 1j*Wo**2)/mp + 0j)
    cpf = 1j*Wo**2
    cpp = 1j*Wo**2 - alpha_p**2
    e = np.array([0, 0, 1.0]) if direction == 'z' else np.array([1.0, 0, 0])
    # k quadrature: panels in t = k*h
    base = np.array([0.5, 1, 2, 4, 7, 11, 16, 24, 36, 50]) / h
    kl = min(abs(lf), abs(lp), 1.0/h)
    fine = kl*np.logspace(-4, 0.5, 14)
    extra = np.array([abs(lf), abs(lp)])*np.array([[0.5], [1], [2], [4]])
    edges = np.unique(np.concatenate([[0], fine, base, extra.ravel()]))
    edges = edges[edges <= base[-1]]
    ks, wk = [], []
    for a_, b_ in zip(edges[:-1], edges[1:]):
        x, w = _gl(nk, a_, b_); ks.append(x); wk.append(w)
    ks = np.concatenate(ks); wk = np.concatenate(wk)
    th = 2*np.pi*np.arange(ntheta)/ntheta; wth = 2*np.pi/ntheta
    M = np.zeros((2, 2), complex)
    for k, w in zip(ks, wk):
        q = np.sqrt(k**2 + lf**2); qp = np.sqrt(k**2 + lp**2)
        for t in th:
            kx, ky = k*np.cos(t), k*np.sin(t)
            def pot(s):  return np.array([1j*kx, 1j*ky, s], complex)
            def pol(s):  return np.array([1j*kx*s, 1j*ky*s, k**2], complex)
            tor = np.array([1j*ky, -1j*kx, 0], complex)
            def stress(u, s, p, mu):
                return np.array([mu*(s*u[0] + 1j*kx*u[2]), mu*(s*u[1] + 1j*ky*u[2]),
                                 -p + 2*mu*s*u[2]])
            # unknown columns: velocity (3) & stress (3) at z=0
            cols_u, cols_s = [], []
            for u, s, p in [(pot(-k), -k, cpf), (pol(-q), -q, 0), (tor, -q, 0)]:
                cols_u.append(u); cols_s.append(stress(u, s, p, 1.0))
            colsT_u, colsT_s = [], []
            if rigid_wall:
                A = np.column_stack(cols_u)
            else:
                for u, s, p in [(pot(k), k, cpp), (pol(qp), qp, 0), (tor, qp, 0)]:
                    colsT_u.append(u); colsT_s.append(stress(u, s, p, mp))
                A = np.zeros((6, 6), complex)
                for j in range(3):
                    # velocity continuity: R - T = -inc
                    A[0:3, j] = cols_u[j]; A[0:3, 3+j] = -colsT_u[j]
                    # normal stress: R - T = -inc
                    A[3, j] = cols_s[j][2]; A[3, 3+j] = -colsT_s[j][2]
                    # tangential: T_s - R_s - bp*ap*R_u = inc_s + bp*ap*inc_u
                    A[4:6, j] = -cols_s[j][0:2] - beta_p*alpha_p*cols_u[j][0:2]
                    A[4:6, 3+j] = colsT_s[j][0:2]
            for jsrc in range(2):
                gk = pot(k)
                if jsrc == 0:   # B: potential dipole
                    phi = (gk @ e)*2*np.pi/k*np.exp(-k*h)
                    uinc = gk*phi; sinc = stress(uinc, k, cpf*phi, 1.0)
                    # pressure of potential mode is cp*phi; stress() takes p directly
                else:           # C: vortical
                    gq = np.array([1j*kx, 1j*ky, q])
                    uinc = (gq*(gq @ e) - lf**2*e)*2*np.pi/q*np.exp(-q*h)
                    sinc = stress(uinc, q, 0.0, 1.0)
                if rigid_wall:
                    rhs = -uinc
                else:
                    rhs = np.concatenate([-uinc, [-sinc[2]],
                                          sinc[0:2] + beta_p*alpha_p*uinc[0:2]])
                sc = np.linalg.norm(A, axis=0)
                x = np.linalg.solve(A/sc, rhs)/sc
                upot = x[0]*pot(-k)*np.exp(-k*h)
                uvort = (x[1]*pol(-q) + x[2]*tor)*np.exp(-q*h)
                fac = w*k*wth/(4*np.pi**2)
                M[0, jsrc] += fac*(upot @ e)
                M[1, jsrc] += fac*(uvort @ e)
    return M


def force(Wo, eps, direction='z', sphere=None, alpha_p=1e6, beta_p=0.0, mp=1.0,
          rigid_wall=False, **sk):
    """Return (F_total, F_inf) per unit velocity amplitude (complex, units mu*b*U)."""
    sph = sphere if sphere is not None else Sphere(Wo, **sk)
    SB, SF = sph.response()
    h = 1.0 + eps
    M = reflection_matrix(Wo, h, direction, alpha_p, beta_p, mp, rigid_wall=rigid_wall)
    # [B,C] = SB[:,0] U + SB[:,1:] [Up,w0] ;  [Up,w0] = M [B,C]
    A = np.eye(2) - SB[:, 1:] @ M
    BC = np.linalg.solve(A, SB[:, 0])
    inc = M @ BC
    F = SF[0] + SF[1:] @ inc
    return F, SF[0]


# ------------------------------------------------- vectorised reflection (fast)
def reflection_matrix_fast(Wo, h, direction, alpha_p, beta_p=0.0, mp=1.0,
                           rigid_wall=False, nk=64, ntheta=8):
    lf = np.sqrt(-1j*Wo**2 + 0j)
    lp = np.sqrt((alpha_p**2 - 1j*Wo**2)/mp + 0j)
    cpf = 1j*Wo**2; cpp = 1j*Wo**2 - alpha_p**2
    e = np.array([0, 0, 1.0]) if direction == 'z' else np.array([1.0, 0, 0])
    base = np.array([0.5, 1, 2, 4, 7, 11, 16, 24, 36, 50]) / h
    kl = min(abs(lf), abs(lp), 1.0/h)
    fine = kl*np.logspace(-4, 0.5, 14)
    extra = np.array([abs(lf), abs(lp)])*np.array([[0.5], [1], [2], [4]])
    edges = np.unique(np.concatenate([[0], fine, base, extra.ravel()]))
    edges = edges[edges <= base[-1]]
    ks, wk = [], []
    for a_, b_ in zip(edges[:-1], edges[1:]):
        x, w = _gl(nk, a_, b_); ks.append(x); wk.append(w)
    ks = np.concatenate(ks); wk = np.concatenate(wk)
    th = 2*np.pi*np.arange(ntheta)/ntheta
    K, TH = np.meshgrid(ks, th, indexing='ij'); W = np.repeat(wk[:, None], ntheta, 1)
    K, TH, W = K.ravel(), TH.ravel(), W.ravel()*2*np.pi/ntheta
    N = K.size
    kx, ky = K*np.cos(TH), K*np.sin(TH)
    q = np.sqrt(K**2 + lf**2); qp = np.sqrt(K**2 + lp**2)
    Z = np.zeros(N, complex)
    pot = lambda s: np.stack([1j*kx, 1j*ky, s + 0j], -1)
    pol = lambda s: np.stack([1j*kx*s, 1j*ky*s, K**2 + 0j], -1)
    tor = np.stack([1j*ky, -1j*kx, Z], -1)
    def stress(u, s, p, mu):
        return np.stack([mu*(s*u[:, 0] + 1j*kx*u[:, 2]), mu*(s*u[:, 1] + 1j*ky*u[:, 2]),
                         -p + 2*mu*s*u[:, 2]], -1)
    R = [(pot(-K), -K, cpf), (pol(-q), -q, 0), (tor, -q, 0)]
    T = [(pot(K), K, cpp), (pol(qp), qp, 0), (tor, qp, 0)]
    if rigid_wall:
        A = np.stack([u for u, s, p in R], -1)
    else:
        A = np.zeros((N, 6, 6), complex)
        for j in range(3):
            uR, sR, pR = R[j]; uT, sT, pT = T[j]
            SR = stress(uR, sR, pR, 1.0); ST = stress(uT, sT, pT, mp)
            A[:, 0:3, j] = uR; A[:, 0:3, 3+j] = -uT
            A[:, 3, j] = SR[:, 2]; A[:, 3, 3+j] = -ST[:, 2]
            A[:, 4:6, j] = -SR[:, 0:2] - beta_p*alpha_p*uR[:, 0:2]
            A[:, 4:6, 3+j] = ST[:, 0:2]
    sc = np.linalg.norm(A, axis=1, keepdims=True)
    As = A/sc
    gk = pot(K)
    M = np.zeros((2, 2), complex)
    for jsrc in range(2):
        if jsrc == 0:
            phi = (gk @ e)*2*np.pi/K*np.exp(-K*h)
            uinc = gk*phi[:, None]; sinc = stress(uinc, K, cpf*phi, 1.0)
        else:
            gq = np.stack([1j*kx, 1j*ky, q], -1)
            uinc = (gq*(gq @ e)[:, None] - lf**2*e)*(2*np.pi/q*np.exp(-q*h))[:, None]
            sinc = stress(uinc, q, 0.0, 1.0)
        if rigid_wall:
            rhs = -uinc
        else:
            rhs = np.concatenate([-uinc, -sinc[:, 2:3],
                                  sinc[:, 0:2] + beta_p*alpha_p*uinc[:, 0:2]], -1)
        x = np.linalg.solve(As, rhs[..., None])[..., 0]/sc[:, 0, :]
        upot = x[:, 0:1]*pot(-K)*np.exp(-K*h)[:, None]
        uv = (x[:, 1:2]*pol(-q) + x[:, 2:3]*tor)*np.exp(-q*h)[:, None]
        fac = W*K/(4*np.pi**2)
        M[0, jsrc] = np.sum(fac*(upot @ e)); M[1, jsrc] = np.sum(fac*(uv @ e))
    return M

reflection_matrix_slow = reflection_matrix
reflection_matrix = reflection_matrix_fast


def force_M(sph, M):
    SB, SF = sph.response()
    BC = np.linalg.solve(np.eye(2) - SB[:, 1:] @ M, SB[:, 0])
    return SF[0] + SF[1:] @ (M @ BC), SF[0]
