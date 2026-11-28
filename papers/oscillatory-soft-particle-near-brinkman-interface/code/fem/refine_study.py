import time, json, numpy as np
from fem_axisym import make_mesh, Problem, exact_unbounded
out = []
for hmin, hmax, R in [(0.08, 0.8, 12), (0.04, 0.5, 12), (0.02, 0.4, 12), (0.02, 0.4, 20), (0.01, 0.3, 20)]:
    t = time.time(); mesh, tags, R_ = make_mesh(hmin, hmax, R=R); P = Problem(mesh, tags, R_)
    Wo = 3.0; F0 = P.force(Wo, 0.0); Fw = P.force(Wo, 0.0, rigid=True); Fp = P.force(Wo, 20.0)
    ex = exact_unbounded(Wo)
    row = dict(hmin=hmin, hmax=hmax, R=R, ndof=int(P.nu+P.np_), err_unb=float(abs(F0-ex)/abs(ex)),
               wall=[float(((Fw-F0)/(6*np.pi)).real*-1), float(((Fw-F0)/(6*np.pi)).imag)],
               perm20=[float(((Fp-F0)/(6*np.pi)).real*-1), float(((Fp-F0)/(6*np.pi)).imag)], sec=round(time.time()-t, 1))
    print(row, flush=True); out.append(row)
json.dump(out, open('refine_study.json', 'w'), indent=1)
