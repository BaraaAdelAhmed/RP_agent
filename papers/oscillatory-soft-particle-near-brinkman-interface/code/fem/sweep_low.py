"""FEM sweep near the lower crossover: rigid wall and alpha_p = 20 (beta_p = 0), normal, eps = 1. Mesh: hmin 0.02, hmax 0.4, R 30."""
import json, time, numpy as np
from fem_axisym import make_mesh, Problem, exact_unbounded
mesh, tags, R = make_mesh(0.02, 0.4, R=30); P = Problem(mesh, tags, R)
out = {'mesh': dict(hmin=0.02, hmax=0.4, R=30, ndof=int(P.nu+P.np_)), 'rows': []}
for Wo in [2.8, 3.0, 3.2, 3.4, 3.6, 3.8]:
    t = time.time(); F0 = P.force(Wo, 0.0); Fw = P.force(Wo, 0.0, rigid=True); Fp = P.force(Wo, 20.0)
    row = dict(Wo=Wo, err_unb=float(abs(F0-exact_unbounded(Wo))/abs(exact_unbounded(Wo))),
               wall_gam=float(-(Fw-F0).real/(6*np.pi)), wall_chi=float((Fw-F0).imag/(6*np.pi)),
               p20_gam=float(-(Fp-F0).real/(6*np.pi)), p20_chi=float((Fp-F0).imag/(6*np.pi)))
    out['rows'].append(row); print(row, round(time.time()-t, 1), flush=True)
json.dump(out, open('sweep_low.json', 'w'), indent=1)
