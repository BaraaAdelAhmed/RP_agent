"""Mechanism of the multiple parallel windows: split F_int = Z_p U_p + Z_w w0 (self-consistent closure) into the
potential-image part (Z_p U_p) and the vortical-reflection part (Z_w w0); reactive parts /(6 pi)."""
import sys, warnings, numpy as np
sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import osc_solver as o
for ap, rigid in [(1e6, True), (10.0, False)]:
    print('rigid wall' if rigid else f'alpha_p={ap}', ' parallel, eps=1:  Wo | chi_pot | chi_vort | chi_total')
    for W in [0.7, 1.0, 1.5, 2.0, 2.9, 3.5, 5.0, 8.0, 12.0]:
        s = o.Sphere(W); SB, SF = s.response(); M = o.reflection_matrix(W, 2.0, 'x', ap, rigid_wall=rigid)
        BC = np.linalg.solve(np.eye(2) - SB[:, 1:] @ M, SB[:, 0]); inc = M @ BC
        cp, cv = (SF[1]*inc[0]).imag/(6*np.pi), (SF[2]*inc[1]).imag/(6*np.pi)
        print(f'   {W:5.1f} | {cp:+.4f} | {cv:+.4f} | {cp+cv:+.4f}')
