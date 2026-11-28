import time, json, numpy as np
from fem_axisym import make_mesh, Problem, exact_unbounded
out=[]
for hmin, hif, rcut, hmax, R in [(0.01, 0.01, 5, 0.4, 20), (0.005, 0.005, 5, 0.4, 20), (0.01, 0.01, 5, 0.4, 30), (0.005, 0.005, 8, 0.3, 30)]:
    t=time.time(); mesh, tags, R_ = make_mesh(hmin, hmax, R=R, dref=0.6, rcut=rcut, hif=hif); P = Problem(mesh, tags, R_)
    Wo=44.0; F0=P.force(Wo,0.0); Fp=P.force(Wo,20.0); ex=exact_unbounded(Wo)
    row=dict(hmin=hmin, rcut=rcut, hmax=hmax, R=R, ndof=int(P.nu+P.np_), err_unb=float(abs(F0-ex)/abs(ex)), gam=float(-(Fp-F0).real/(6*np.pi)), chi=float((Fp-F0).imag/(6*np.pi)), sec=round(time.time()-t,1))
    print(row, flush=True); out.append(row)
json.dump(out, open('hi_conv.json','w'), indent=1)
