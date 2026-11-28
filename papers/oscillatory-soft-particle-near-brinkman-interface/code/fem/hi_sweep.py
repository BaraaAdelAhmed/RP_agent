"""FEM downward crossover for alpha_p = 20 (normal, eps = 1). Mesh: hmin 0.005 (sphere and interface r<8), hmax 0.3, R 30."""
import json, time, numpy as np
from fem_axisym import make_mesh, Problem, exact_unbounded
mesh, tags, R = make_mesh(0.005, 0.3, R=30, dref=0.6, rcut=8, hif=0.005); P = Problem(mesh, tags, R)
out = {'mesh': dict(hmin=0.005, hif=0.005, rcut=8, hmax=0.3, R=30, ndof=int(P.nu+P.np_)), 'rows': []}
for Wo in [48.0, 52.0]:
    t = time.time(); F0 = P.force(Wo, 0.0); Fp = P.force(Wo, 20.0)
    row = dict(Wo=Wo, err_unb=float(abs(F0-exact_unbounded(Wo))/abs(exact_unbounded(Wo))), gam=float(-(Fp-F0).real/(6*np.pi)), chi=float((Fp-F0).imag/(6*np.pi)))
    out['rows'].append(row); print(row, round(time.time()-t, 1), flush=True)
json.dump(out, open('hi_sweep.json', 'w'), indent=1)
