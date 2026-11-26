import numpy as np, time
from osc_solver import force
def brenner(h):
    a=np.arccosh(h); n=np.arange(1,200)
    t=n*(n+1)/((2*n-1)*(2*n+3))*((2*np.sinh((2*n+1)*a)+(2*n+1)*np.sinh(2*a))/(4*np.sinh((n+.5)*a)**2-(2*n+1)**2*np.sinh(a)**2)-1)
    return 4/3*np.sinh(a)*t.sum()
import sys; WO=float(sys.argv[1]); t0=time.time()
for eps in [0.5,1,2,4]:
    h=1+eps; x=1/h
    Fz,F0=force(WO,eps,'z',rigid_wall=True)
    Fx,_=force(WO,eps,'x',rigid_wall=True)
    Fb,_=force(WO,eps,'z',alpha_p=1e5)
    print(f"eps={eps}: normal l1={ (Fz/F0).real:.4f} Brinkman-ap1e5={(Fb/F0).real:.4f} series={1/(1-9/8*x+x**3/2):.4f} Brenner={brenner(h):.4f} | parallel l1={(Fx/F0).real:.4f} Faxen={1/(1-9/16*x+x**3/8-45/256*x**4-x**5/16):.4f}")
print(time.time()-t0)
# no interface check
F,F0=force(2.0,1.0,'z',alpha_p=1e-6,beta_p=0.0,mp=1.0); print('transparent',F/F0)
