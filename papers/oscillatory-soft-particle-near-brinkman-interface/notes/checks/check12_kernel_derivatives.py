"""Derivatives of the radial kernels listed in Appendix A (verified symbolically)."""
import sympy as sp
r, L = sp.symbols('r lambda', positive=True)
K = sp.exp(-L*r)/r; I = sp.sinh(L*r)/r
claims = {
 "K'":   (sp.diff(K, r),    -(1+L*r)*sp.exp(-L*r)/r**2),
 "K''":  (sp.diff(K, r, 2), (2+2*L*r+L**2*r**2)*sp.exp(-L*r)/r**3),
 "K'''": (sp.diff(K, r, 3), -(6+6*L*r+3*L**2*r**2+L**3*r**3)*sp.exp(-L*r)/r**4),
 "I'":   (sp.diff(I, r),    (L*r*sp.cosh(L*r)-sp.sinh(L*r))/r**2),
 "I''":  (sp.diff(I, r, 2), ((L**2*r**2+2)*sp.sinh(L*r)-2*L*r*sp.cosh(L*r))/r**3),
 "I'''": (sp.diff(I, r, 3), ((L**3*r**3+6*L*r)*sp.cosh(L*r)-(3*L**2*r**2+6)*sp.sinh(L*r))/r**4),
}
for k, (a, b) in claims.items():
    print(('PASS ' if sp.simplify((a-b).rewrite(sp.exp)) == 0 else 'FAIL ') + k)
