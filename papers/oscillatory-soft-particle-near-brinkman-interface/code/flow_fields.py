"""Velocity fields of the paper's solution (normal oscillation, impermeable sphere, eps=1) in the plane y=0:
scattered dipoles (B, C) from the self-consistent closure + their full Fourier-reflected field in z>0 + the
transmitted field in the Brinkman layer z<0.  Output: results6.json (real part at phase omega t = 0, U = 1)."""
import json, warnings, numpy as np
import osc_solver as o
warnings.filterwarnings('ignore')

def field(Wo, ap, rigid, X, Z, h=2.0, nk=24, ntheta=48):
    lf = np.sqrt(-1j*Wo**2 + 0j); lp = np.sqrt((ap**2 - 1j*Wo**2) + 0j)
    cpf, cpp = 1j*Wo**2, 1j*Wo**2 - ap**2
    s = o.Sphere(Wo); SB, SF = s.response(); M = o.reflection_matrix(Wo, h, 'z', ap, rigid_wall=rigid)
    B, C = np.linalg.solve(np.eye(2) - SB[:, 1:] @ M, SB[:, 0])
    e = np.array([0, 0, 1.0])
    # --- scattered field (closed form), relative position from the centre
    rx, rz = X, Z - h; r = np.hypot(rx, rz); ct = rz/r
    rh = np.stack([rx/r, np.zeros_like(r), rz/r], -1)
    dip = (-e/r[..., None]**3 + 3*(ct/r**3)[..., None]*rh)               # grad(e . grad 1/r)
    g = np.exp(-lf*r)/r; g1 = -(1+lf*r)*np.exp(-lf*r)/r**2; g2 = (2+2*lf*r+(lf*r)**2)*np.exp(-lf*r)/r**3
    vor = (g2*ct)[..., None]*rh + (g1/r)[..., None]*(e - ct[..., None]*rh) - (lf**2*g)[..., None]*e
    u = B*dip + C*vor
    u[Z < 0] = 0
    # --- reflected / transmitted Fourier field
    base = np.array([0.5, 1, 2, 4, 7, 11, 16, 24, 36, 50]) / h
    edges = np.unique(np.concatenate([[0], min(abs(lf), abs(lp), 1/h)*np.logspace(-4, 0.5, 10), base]))
    ks, wk = [], []
    for a_, b_ in zip(edges[:-1], edges[1:]):
        x_, w_ = o._gl(nk, a_, b_); ks.append(x_); wk.append(w_)
    ks = np.concatenate(ks); wk = np.concatenate(wk)
    th = 2*np.pi*np.arange(ntheta)/ntheta
    K, TH = np.meshgrid(ks, th, indexing='ij'); W = np.repeat(wk[:, None], ntheta, 1)*2*np.pi/ntheta
    K, TH, W = K.ravel(), TH.ravel(), W.ravel()
    kx, ky = K*np.cos(TH), K*np.sin(TH); q = np.sqrt(K**2+lf**2); qp = np.sqrt(K**2+lp**2); N = K.size; Zr = np.zeros(N, complex)
    pot = lambda s_: np.stack([1j*kx, 1j*ky, s_+0j], -1); pol = lambda s_: np.stack([1j*kx*s_, 1j*ky*s_, K**2+0j], -1)
    tor = np.stack([1j*ky, -1j*kx, Zr], -1)
    def stress(uu, s_, p, mu): return np.stack([mu*(s_*uu[:, 0]+1j*kx*uu[:, 2]), mu*(s_*uu[:, 1]+1j*ky*uu[:, 2]), -p+2*mu*s_*uu[:, 2]], -1)
    Rm = [(pot(-K), -K, cpf), (pol(-q), -q, 0), (tor, -q, 0)]; Tm = [(pot(K), K, cpp), (pol(qp), qp, 0), (tor, qp, 0)]
    gk = pot(K); phi = (gk @ e)*2*np.pi/K*np.exp(-K*h)
    uinc = B*gk*phi[:, None]; sinc = B*stress(gk*phi[:, None], K, cpf*phi, 1.0)
    gq = np.stack([1j*kx, 1j*ky, q], -1); uv = (gq*(gq @ e)[:, None] - lf**2*e)*(2*np.pi/q*np.exp(-q*h))[:, None]
    uinc = uinc + C*uv; sinc = sinc + C*stress(uv, q, 0.0, 1.0)
    if rigid:
        A = np.stack([uu for uu, _, _ in Rm], -1); rhs = -uinc
    else:
        A = np.zeros((N, 6, 6), complex)
        for j in range(3):
            uR, sR, pR = Rm[j]; uT, sT, pT = Tm[j]; SR = stress(uR, sR, pR, 1.0); ST = stress(uT, sT, pT, 1.0)
            A[:, 0:3, j] = uR; A[:, 0:3, 3+j] = -uT; A[:, 3, j] = SR[:, 2]; A[:, 3, 3+j] = -ST[:, 2]
            A[:, 4:6, j] = -SR[:, 0:2]; A[:, 4:6, 3+j] = ST[:, 0:2]
        rhs = np.concatenate([-uinc, -sinc[:, 2:3], sinc[:, 0:2]], -1)
    sc = np.linalg.norm(A, axis=1, keepdims=True); xx = np.linalg.solve(A/sc, rhs[..., None])[..., 0]/sc[:, 0, :]
    fac = W*K/(4*np.pi**2)
    Xf, Zf = X.ravel(), Z.ravel(); out = np.zeros((Xf.size, 3), complex)
    for i0 in range(0, Xf.size, 400):
        xs, zs = Xf[i0:i0+400], Zf[i0:i0+400]
        ph = np.exp(1j*np.outer(xs, kx))                                   # y = 0
        up = (zs >= 0)
        eR1, eR2 = np.exp(-np.outer(zs, K)), np.exp(-np.outer(zs, q))
        refl = (ph*fac*xx[:, 0]*eR1)[..., None]*pot(-K)[None] + (ph*fac*eR2)[..., None]*(xx[:, 1:2]*pol(-q) + xx[:, 2:3]*tor)[None]
        res = refl.sum(1)
        if not rigid:
            eT1, eT2 = np.exp(np.outer(np.minimum(zs, 0), K)), np.exp(np.outer(np.minimum(zs, 0), qp))
            tr = (ph*fac*xx[:, 3]*eT1)[..., None]*pot(K)[None] + (ph*fac*eT2)[..., None]*(xx[:, 4:5]*pol(qp) + xx[:, 5:6]*tor)[None]
            res = np.where(up[:, None], res, tr.sum(1))
        else:
            res = np.where(up[:, None], res, 0)
        out[i0:i0+400] = res
    u = u + out.reshape(u.shape)
    inside = np.hypot(X, Z-h) < 1.0
    u[inside] = np.nan
    return u

if __name__ == '__main__':
    x = np.linspace(-4, 4, 121); z = np.linspace(-2.5, 4.5, 106); X, Z = np.meshgrid(x, z)
    R = {'x': x.tolist(), 'z': z.tolist()}
    for lab, Wo, ap, rig in [('wall_lo', 0.5, 1e6, True), ('perm_lo', 0.5, 5.0, False), ('wall_hi', 10.0, 1e6, True), ('perm_hi', 10.0, 5.0, False)]:
        u = field(Wo, ap, rig, X, Z)
        R[lab] = {'ux': np.real(u[..., 0]).tolist(), 'uz': np.real(u[..., 2]).tolist(), 'Wo': Wo, 'ap': ap}
        print(lab, np.nanmax(np.abs(u[..., 2])), flush=True)
    json.dump(R, open('results6.json', 'w'), allow_nan=True); print('ALL DONE')
