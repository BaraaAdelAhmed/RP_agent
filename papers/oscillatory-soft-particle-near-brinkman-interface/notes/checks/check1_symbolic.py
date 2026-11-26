"""Symbolic checks of the formulation and the sphere solution (sympy)."""
import sympy as sp
x, y, z, lam, r, th = sp.symbols('x y z lam r theta', positive=True)
R = sp.sqrt(x**2+y**2+z**2)
grad = lambda f: sp.Matrix([sp.diff(f, v) for v in (x, y, z)])
lap = lambda f: sum(sp.diff(f, v, 2) for v in (x, y, z))
def curl(F): return sp.Matrix([sp.diff(F[2], y)-sp.diff(F[1], z), sp.diff(F[0], z)-sp.diff(F[2], x), sp.diff(F[1], x)-sp.diff(F[0], y)])
ez = sp.Matrix([0, 0, 1])
out = []
# 1. vortical block curl curl(e_z h), h = exp(-lam R)/R : divergence-free, Helmholtz, radial form (eq. vort_radial)
h = sp.exp(-lam*R)/R
w = curl(curl(ez*h))
div = sp.simplify(sum(sp.diff(w[i], v) for i, v in enumerate((x, y, z))))
helm = sp.simplify((lap(w[2]) - lam**2*w[2]))
pt = {x: r*sp.sin(th), y: 0, z: r*sp.cos(th)}
er = sp.Matrix([sp.sin(th), 0, sp.cos(th)]); et = sp.Matrix([sp.cos(th), 0, -sp.sin(th)])
g = sp.exp(-lam*r)/r
ur = sp.simplify((w.subs(pt).dot(er)) - (sp.diff(g, r, 2) - lam**2*g)*sp.cos(th))
ut = sp.simplify((w.subs(pt).dot(et)) - (lam**2*g - sp.diff(g, r)/r)*sp.sin(th))
out.append(('curlcurl(e h): div=0, Helmholtz, u_r and u_theta of eq.(vort_radial)', div == 0 and helm == 0 and ur == 0 and ut == 0))
# 2. potential dipole grad(d/dz 1/R): u_r = f'', u_theta = -f'/r
d = grad(sp.diff(1/R, z)).subs(pt)
out.append(('dipole radial forms', sp.simplify(d.dot(er) - 2*sp.cos(th)/r**3) == 0 and sp.simplify(d.dot(et) - sp.sin(th)/r**3) == 0))
# 3. force integral: F = int (Srr cos^2 - Srt sin^2) dS = 4pi/3 (Srr - 2 Srt)
Srr, Srt = sp.symbols('Srr Srt')
F = 2*sp.pi*sp.integrate((Srr*sp.cos(th)**2 - Srt*sp.sin(th)**2)*sp.sin(th), (th, 0, sp.pi))
out.append(('force = 4pi/3 (Srr - 2 Srt)', sp.simplify(F - sp.Rational(4, 3)*sp.pi*(Srr - 2*Srt)) == 0))
# 4. rigid no-slip sphere closed forms (Prop. rigid): solve u_r=1, u_theta=-1 at r=1
B, C = sp.symbols('B C'); L = sp.symbols('L')
gL = sp.exp(-L*r)/r
Ur = B*2/r**3 + C*(sp.diff(gL, r, 2) - L**2*gL)
V = B/r**3 + C*(L**2*gL - sp.diff(gL, r)/r)
sol = sp.solve([Ur.subs(r, 1) - 1, V.subs(r, 1) + 1], [B, C], dict=True)[0]
okB = sp.simplify(sol[B] - (3+3*L+L**2)/(2*L**2)) == 0
okC = sp.simplify(sol[C] + 3*sp.exp(L)/(2*L**2)) == 0
# traction (mu=1), pressure p = i Wo^2 Phi = -L^2 Phi (since L^2 = -i Wo^2), Phi_dipole = -1/r^2
P = -L**2*(-B/r**2)
Srr_e = -P + 2*sp.diff(Ur, r); Srt_e = sp.diff(V, r) - V/r - Ur/r
Fz = sp.Rational(4, 3)*sp.pi*(Srr_e - 2*Srt_e)
okF = sp.simplify(Fz.subs(r, 1).subs(sol) + 6*sp.pi*(1 + L + L**2/9)) == 0
out.append(('rigid sphere: B, C, Z_U of eqs.(rigid_BC)', okB and okC and okF))
# 5. Steady limit: B + C -> -1/4 ;  inviscid: B -> 1/2
out.append(('B+C -> -1/4 as L->0 (dipole part of Stokes solution)', sp.limit(sol[B] + sol[C], L, 0) == sp.Rational(-1, 4)))
out.append(('B -> 1/2 as L->oo', sp.limit(sol[B], L, sp.oo) == sp.Rational(1, 2)))
# 6. Z_w = 6 pi e^L from Mazur-Bedeaux with mean values of modified Helmholtz
Zw = 6*sp.pi*((1+L)*sp.sinh(L)/L + L**2/3*3*(L*sp.cosh(L) - sp.sinh(L))/L**3)
out.append(('Z_w = 6 pi e^lambda', sp.simplify((Zw - 6*sp.pi*sp.exp(L)).rewrite(sp.exp)) == 0))
# 7. mean-value theorem: surface average of sinh(L r)/r-type field centred elsewhere -> check numerically
# 8. w0 = -2/3 lam^3 D : centre value of curlcurl(e_z sinh(lam R)/R)
wi = curl(curl(ez*sp.sinh(lam*R)/R))
c0 = sp.limit(wi[2].subs({x: 0, y: 0}), z, 0)
out.append(('w0 = -(2/3) lam^3 D', sp.simplify(c0 + sp.Rational(2, 3)*lam**3) == 0))
# 9. lambda_f b = e^{-i pi/4} Wo and penetration depth
Wo = sp.symbols('Wo', positive=True)
lf = sp.sqrt(-sp.I)*Wo
import cmath
out.append(('lambda_f b = e^{-i pi/4} Wo (numeric, principal branch, Wo=3)', abs(cmath.sqrt(-1j*9) - cmath.exp(-1j*cmath.pi/4)*3) < 1e-14))
reinv = sp.simplify(sp.re(1/sp.expand_complex(lf)))
out.append(('Re(1/lambda_f) == sqrt(2)/Wo ?  (paper claims delta_v = Re(1/lambda_f))', sp.simplify(reinv - sp.sqrt(2)/Wo) == 0))
out.append(('1/Re(lambda_f) == sqrt(2)/Wo  (correct statement)', sp.simplify(1/sp.re(sp.expand_complex(lf)) - sp.sqrt(2)/Wo) == 0))
# 10. m_int/m_f = 9/2 chi/Wo^2 ; Froude-Krylov fraction 2/9
mu, b, rho, om, chi = sp.symbols('mu b rho omega chi', positive=True)
m = chi*6*sp.pi*mu*b/om
out.append(('m_int/m_f = (9/2) chi / Wo^2', sp.simplify(m/(sp.Rational(4, 3)*sp.pi*rho*b**3) - sp.Rational(9, 2)*chi*mu/(rho*om*b**2)) == 0))
# 11. inviscid image values (Prop. inviscid)
hh = sp.symbols('h', positive=True)
Up_n = -sp.Rational(1, 2)*2/(2*hh)**3     # opposite-sign mirror dipole, on-axis gradient 2/d^3
Up_x = sp.Rational(1, 2)*(-1)/(2*hh)**3    # same-sign mirror dipole, transverse field -1/d^3
for lab, Up, ref in [('normal', Up_n, sp.Rational(3, 16)), ('parallel', Up_x, sp.Rational(3, 32))]:
    Fint = 2*sp.pi*(-sp.I*Wo**2)*Up
    mm = sp.Rational(9, 2)*sp.im(Fint)/(6*sp.pi)/Wo**2
    out.append((f'inviscid m_int/m_f {lab} = {ref}/h^3', sp.simplify(mm - ref/hh**3) == 0))
for k, v in out: print(('PASS ' if v else 'FAIL ') + k)
