import numpy as np
from osc_solver import Sphere
# rigid sphere unbounded: F = -6pi(1+lam+lam^2/9)
for Wo in [1e-3,0.5,2,10]:
    s=Sphere(Wo,gam=1.0); SB,SF=s.response(); l=s.lamf
    print('rigid',Wo,SF[0], -6*np.pi*(1+l+l**2/9))
# porous sphere steady (Brinkman/Debye-Bueche, beta=0, ms=1)
for a in [1,5,20]:
    s=Sphere(1e-4,gam=0.0,alpha_s=a); SB,SF=s.response()
    t=1-np.tanh(a)/a; Om=2*a**2*t/(2*a**2+3*t)
    print('porous',a,SF[0].real/(-6*np.pi), Om)
# core-shell with stiff shell -> rigid ; Wo>0
for g in [0.5,0.9]:
    s=Sphere(2.0,gam=g,alpha_s=2000.); print('cs->rigid',g,s.response()[1][0])
# uniform potential incident on fixed rigid sphere: F = 6pi(1+lam+lam^2/3)*Up  (Mazur-Bedeaux)
s=Sphere(2.0,gam=1.0); SB,SF=s.response(); l=s.lamf
print('Up resp',SF[1], 6*np.pi*(l**2/3)+0*l, 'check FK + ...')
