"""Independent axisymmetric finite-element check (normal oscillation, impermeable no-slip sphere, eps = 1).

Unsteady Stokes in z>0 and unsteady Brinkman (mu_p = mu, beta_p = 0) in z<0, solved as ONE domain with a Darcy term
switched on in z<0 (velocity and stress continuity across z=0 are then natural), dimensionless (b = 1, U = 1):
    -i Wo^2 u - lap u + grad p + alpha_p^2 chi(z<0) u = 0,  div u = 0.
Taylor-Hood P2-P1 triangles in the meridian plane (r, z), axisymmetric weak form with weight r.
BCs: u = e_z on the sphere r^2+(z-h)^2=1, u = 0 on the far boundary, u_r = 0 on the axis.
Rigid wall: u = 0 on z <= 0.  Unbounded reference: alpha_p = 0 on the SAME mesh (exact force -6 pi (1+lam+lam^2/9)).
Force: variational (reaction) force = 2 pi * sum of the z-momentum residual over the sphere's u_z dofs.
F_int = F(layer or wall) - F(alpha_p = 0), on the same mesh, so that discretisation errors largely cancel."""
import sys, json, time, numpy as np, scipy.sparse as sps, scipy.sparse.linalg as spl
import gmsh, meshio
from skfem import MeshTri, MeshTri2, Basis, ElementTriP2, ElementTriP1, ElementVector, BilinearForm, asm, bmat
from skfem.helpers import dot, ddot, grad

H = 2.0  # sphere centre height (eps = 1)

def make_mesh(hmin, hmax, R=12.0, dref=1.5, fname='mesh.msh', rcut=None, hif=None):
    gmsh.initialize(); gmsh.option.setNumber('General.Terminal', 0); gmsh.model.add('m')
    occ = gmsh.model.occ
    up = occ.addRectangle(0, 0, 0, R, R); lo = occ.addRectangle(0, -R, 0, R, R)
    disk = occ.addDisk(0, H, 0, 1, 1)
    out, _ = occ.cut([(2, up)], [(2, disk)])
    occ.fragment(out + [(2, lo)], []); occ.synchronize()
    surfs = gmsh.model.getEntities(2)
    upper = [s[1] for s in surfs if gmsh.model.occ.getCenterOfMass(2, s[1])[1] > 0]
    lower = [s[1] for s in surfs if gmsh.model.occ.getCenterOfMass(2, s[1])[1] < 0]
    gmsh.model.addPhysicalGroup(2, upper, 1); gmsh.model.addPhysicalGroup(2, lower, 2)
    curves = gmsh.model.getEntities(1)
    sph, iface = [], []
    for c in curves:
        bb = gmsh.model.getBoundingBox(1, c[1])
        xm, ym = (bb[0]+bb[3])/2, (bb[1]+bb[4])/2
        if abs(np.hypot(xm, ym-H) - 1) < 0.3 and bb[4] > 0.5: sph.append(c[1])
        elif abs(bb[1]) < 1e-9 and abs(bb[4]) < 1e-9: iface.append(c[1])
    f = gmsh.model.mesh.field
    if rcut is None:
        d = f.add('Distance'); f.setNumbers(d, 'CurvesList', sph + iface); f.setNumber(d, 'Sampling', 400)
        t = f.add('Threshold'); f.setNumber(t, 'InField', d); f.setNumber(t, 'SizeMin', hmin); f.setNumber(t, 'SizeMax', hmax)
        f.setNumber(t, 'DistMin', 0.0); f.setNumber(t, 'DistMax', dref)
        f.setAsBackgroundMesh(t)
    else:   # refine the sphere fully, the interface only for r < rcut (where the reflected vorticity lives)
        d = f.add('Distance'); f.setNumbers(d, 'CurvesList', sph); f.setNumber(d, 'Sampling', 600)
        t = f.add('Threshold'); f.setNumber(t, 'InField', d); f.setNumber(t, 'SizeMin', hmin); f.setNumber(t, 'SizeMax', hmax)
        f.setNumber(t, 'DistMin', 0.0); f.setNumber(t, 'DistMax', dref)
        d2 = f.add('Distance'); f.setNumbers(d2, 'CurvesList', iface); f.setNumber(d2, 'Sampling', 2000)
        t2 = f.add('Threshold'); f.setNumber(t2, 'InField', d2); f.setNumber(t2, 'SizeMin', hif or hmin); f.setNumber(t2, 'SizeMax', hmax)
        f.setNumber(t2, 'DistMin', 0.0); f.setNumber(t2, 'DistMax', dref)
        b = f.add('Box'); f.setNumber(b, 'VIn', 1.0); f.setNumber(b, 'VOut', 0.0)
        f.setNumber(b, 'XMin', 0); f.setNumber(b, 'XMax', rcut); f.setNumber(b, 'YMin', -dref); f.setNumber(b, 'YMax', dref)
        mt = f.add('MathEval'); f.setString(mt, 'F', f'F{t2}*F{b} + {hmax}*(1-F{b})')
        mn = f.add('Min'); f.setNumbers(mn, 'FieldsList', [t, mt]); f.setAsBackgroundMesh(mn)
    gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0); gmsh.option.setNumber('Mesh.MeshSizeFromPoints', 0)
    gmsh.option.setNumber('Mesh.Algorithm', 6)
    gmsh.model.mesh.generate(2); gmsh.model.mesh.setOrder(2); gmsh.write(fname); gmsh.finalize()
    m = meshio.read(fname)
    t6 = np.vstack([c.data for c in m.cells if c.type == 'triangle6'])
    tags = np.asarray(m.cell_data_dict['gmsh:physical']['triangle6'])
    allp = m.points[:, :2]
    vert = np.unique(t6[:, :3]); vmap = -np.ones(len(allp), int); vmap[vert] = np.arange(len(vert))
    p = allp[vert].T; t = vmap[t6[:, :3]].T
    mid = {}
    for e_loc, (a, b) in enumerate([(0, 1), (1, 2), (2, 0)]):
        for k in range(t6.shape[0]):
            i0, i1 = t6[k, a], t6[k, b]; mid[(min(i0, i1), max(i0, i1))] = t6[k, 3+e_loc]
    lin = MeshTri(p, t)                       # same facet ordering as MeshTri2 built on the same t
    fmid = np.array([allp[mid[(min(vert[a], vert[b]), max(vert[a], vert[b]))]] for a, b in lin.facets.T]).T
    mesh = MeshTri2(np.hstack([p, fmid]), t)
    return mesh, tags, R

class Problem:
    def __init__(self, mesh, tags, R):
        self.mesh = mesh
        eu = ElementVector(ElementTriP2()); ep = ElementTriP1()
        ub = Basis(mesh, eu, intorder=5); pb = Basis(mesh, ep, intorder=5)
        lower = np.where(tags == 2)[0]
        ubl = Basis(mesh, eu, intorder=5, elements=lower)
        @BilinearForm
        def stiff(u, v, w):
            r = w.x[0]
            return (ddot(grad(u), grad(v))*r + u[0]*v[0]/np.maximum(r, 1e-12))
        @BilinearForm
        def mass(u, v, w):
            return dot(u, v)*w.x[0]
        @BilinearForm
        def div(u, q, w):
            r = w.x[0]
            return -q*(r*(grad(u)[0, 0] + grad(u)[1, 1]) + u[0])
        self.K = asm(stiff, ub); self.M = asm(mass, ub); self.D = asm(mass, ubl)
        self.B = asm(div, ub, pb)
        self.nu = ub.N; self.np_ = pb.N; self.ub, self.pb = ub, pb
        x = ub.doflocs; xp = pb.doflocs
        comp = np.arange(ub.N) % 2        # skfem interleaves vector components (0 = r, 1 = z)
        rr, zz = x[0], x[1]
        on_sph = np.abs(np.hypot(rr, zz-H) - 1) < 1e-6
        far = (rr > R-1e-8) | (np.abs(zz) > R-1e-8)
        axis = rr < 1e-10
        self.sph_z = np.where(on_sph & (comp == 1))[0]
        dir_mask = on_sph | far | (axis & (comp == 0))
        self.dir_base = np.where(dir_mask)[0]
        self.uvals = np.zeros(ub.N); self.uvals[self.sph_z] = 1.0
        self.wall = np.where((zz <= 1e-10) & ~on_sph)[0]
        self.p_fix = np.array([np.argmax(xp[0]**2 + xp[1]**2)])
        self.p_lower_only = np.where(xp[1] < -1e-10)[0]
        self.zp = xp[1]

    def force(self, Wo, ap, rigid=False):
        A = (self.K - 1j*Wo**2*self.M + ap**2*self.D).astype(complex)
        S = bmat([[A, self.B.T.astype(complex)], [self.B.astype(complex), None]], 'csr')
        n = S.shape[0]
        udir = self.dir_base if not rigid else np.unique(np.concatenate([self.dir_base, self.wall]))
        pdir = self.p_fix if not rigid else np.unique(np.concatenate([self.p_fix, self.p_lower_only]))
        dofs = np.concatenate([udir, self.nu + pdir])
        x = np.zeros(n, complex); x[:self.nu] = 0; x[self.sph_z] = 1.0
        free = np.setdiff1d(np.arange(n), dofs)
        rhs = -S[free][:, dofs] @ x[dofs]
        x[free] = spl.spsolve(S[free][:, free].tocsc(), rhs)
        res = S @ x
        return -2*np.pi*res[self.sph_z].sum()   # force exerted by the fluid on the sphere (sign fixed by the exact check)

def exact_unbounded(Wo):
    lam = np.sqrt(-1j*Wo**2 + 0j)
    return -6*np.pi*(1 + lam + lam**2/9)
