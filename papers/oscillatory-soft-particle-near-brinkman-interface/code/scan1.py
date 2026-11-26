import numpy as np
from osc_solver import force
for d in ['z','x']:
  for eps in [1.0,3.0]:
    print(d,eps)
    for Wo in [0.1,0.3,1,2,3,5,10,20,40]:
        F,F0=force(Wo,eps,d,rigid_wall=True); Fi=F-F0
        print(f"  Wo={Wo:5}: gam_int={-Fi.real/(6*np.pi):+.4f} m_int/mf={Fi.imag/(4/3*np.pi*Wo**2):+.4f}")
h=2.0;print('potential-flow normal expect ~',0.5*3/8/h**3, 'parallel', 0.5*3/16/h**3)
