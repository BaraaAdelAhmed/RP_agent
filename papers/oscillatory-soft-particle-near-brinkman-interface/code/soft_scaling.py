"""Check: steady wall-induced damping of a soft particle scales as the square of its own drag ratio
Omega = F_inf/F_inf(rigid) (first-reflection argument). Normal, eps=1, alpha_p=20, Wo=0.05."""
import sys, warnings, numpy as np
sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import osc_solver as o
W = 0.05; M = o.reflection_matrix(W, 2.0, 'z', 20.0)
s = o.Sphere(W, gam=1.0); F, F0r = o.force_M(s, M); g_r = -(F-F0r).real
for kap in [0.0, 0.7]:
    for a in [2., 5., 10., 20.]:
        s = o.Sphere(W, gam=kap, alpha_s=a); F, F0 = o.force_M(s, M)
        Om = (F0/F0r).real; g = -(F-F0).real/g_r
        print(f'kappa={kap} alpha_s={a:4.0f}: Omega={Om:.3f} Omega^2={Om**2:.3f} gamma_int/gamma_int(rigid)={g:.3f}')
