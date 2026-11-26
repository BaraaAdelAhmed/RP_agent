"""Test: the low-Wo negative reactive interaction equals the fraction of the unbounded Basset reactive
term (Im of -6*pi*lambda)/(6*pi) = Wo/sqrt(2) that the wall removes."""
import sys, warnings, numpy as np
sys.path.insert(0, '../../code'); warnings.filterwarnings('ignore')
import osc_solver as o
for d in ['z', 'x']:
    for eps in [1.0, 3.0]:
        row = []
        for W in [0.01, 0.03, 0.1, 0.3, 1.0]:
            s = o.Sphere(W); M = o.reflection_matrix(W, 1+eps, d, 1e6, rigid_wall=True); F, F0 = o.force_M(s, M)
            chi = (F-F0).imag/(6*np.pi); row.append(-chi/(W/np.sqrt(2)))
        print(f'{d} eps={eps}: -chi_int/(Wo/sqrt2) at Wo=.01,.03,.1,.3,1 =', np.round(row, 3))
