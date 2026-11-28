import time, numpy as np
from fem_axisym import make_mesh, Problem, exact_unbounded
for hmin, hmax, R in [(0.02, 0.4, 30), (0.02, 0.4, 40), (0.02, 0.4, 60)]:
    t=time.time(); mesh, tags, R_ = make_mesh(hmin, hmax, R=R); P = Problem(mesh, tags, R_)
    Wo=3.0; F0=P.force(Wo,0.0); Fw=P.force(Wo,0.0,rigid=True); Fp=P.force(Wo,20.0); ex=exact_unbounded(Wo)
    print(R, P.nu+P.np_, 'err_unb', abs(F0-ex)/abs(ex), 'wall', -(Fw-F0).real/(6*np.pi), (Fw-F0).imag/(6*np.pi), 'perm', -(Fp-F0).real/(6*np.pi), (Fp-F0).imag/(6*np.pi), round(time.time()-t,1), flush=True)
