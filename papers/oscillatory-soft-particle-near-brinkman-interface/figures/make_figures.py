"""Generate all figures at printed size (text width 396 pt = 5.48 in, single-column REVTeX layout).
Data: code/results.json (validation points), code/results2.json (crossovers), code/results4.json (dense curves)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker as mt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from pathlib import Path

H = Path(__file__).resolve().parent
C0 = H.parent / 'code'
R = json.load(open(C0 / 'results.json'))
R2 = json.load(open(C0 / 'results2.json'))
R4 = json.load(open(C0 / 'results4.json'))
TW = 5.4                                         # printed width (in)
plt.rcParams.update({'font.size': 8.5, 'axes.labelsize': 8.5, 'legend.fontsize': 7.5, 'xtick.labelsize': 7.5,
                     'ytick.labelsize': 7.5, 'axes.titlesize': 8.5, 'lines.linewidth': 1.3, 'savefig.bbox': 'tight',
                     'mathtext.fontset': 'cm', 'font.family': 'serif', 'legend.frameon': False})
# Okabe-Ito palette (colour-blind safe); one colour + line style per parameter value, reused across figures
OI = ['#000000', '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9']
STY = {'wall': (OI[0], '-'), '50': (OI[1], '--'), '20': (OI[2], '-.'), '10': (OI[3], ':'), '5': (OI[4], (0, (5, 1, 1, 1)))}
LAB = {'wall': 'rigid wall', '50': r'$\alpha_p=50$', '20': r'$\alpha_p=20$', '10': r'$\alpha_p=10$', '5': r'$\alpha_p=5$'}

def panel(ax, s):
    ax.text(0.0, 1.03, s, transform=ax.transAxes, va='bottom', ha='left', fontsize=8.5)

def logfmt(ax, axis='x'):
    a = ax.xaxis if axis == 'x' else ax.yaxis
    a.set_major_formatter(mt.LogFormatterMathtext())

# ---------------------------------------------------------------- Fig. 1 schematic
fig, ax = plt.subplots(figsize=(3.6, 3.0))
ax.add_patch(Rectangle((-3, -1.7), 6, 1.7, facecolor='#E8D9BF', edgecolor='none'))
rng = np.random.default_rng(1)
for _ in range(260):
    x, y = rng.uniform(-2.95, 2.95), rng.uniform(-1.65, -0.05)
    ax.add_patch(Circle((x, y), 0.035, color='#9C7B4B', lw=0))
ax.plot([-3, 3], [0, 0], color='k', lw=0.8)
zc, b, a = 2.0, 1.0, 0.62
ax.add_patch(Circle((0, zc), b, facecolor='#BFDDF2', edgecolor='#0072B2', lw=0.8))
for _ in range(60):
    rr, th = np.sqrt(rng.uniform(a**2+0.02, b**2-0.02)), rng.uniform(0, 2*np.pi)
    ax.add_patch(Circle((rr*np.cos(th), zc+rr*np.sin(th)), 0.025, color='#0072B2', lw=0))
ax.add_patch(Circle((0, zc), a, facecolor='#1F4E79', edgecolor='none'))
# axes and origin
ax.annotate('', (2.6, 0), (2.0, 0), arrowprops=dict(arrowstyle='->', lw=0.8))
ax.annotate('', (2.0, 0.6), (2.0, 0), arrowprops=dict(arrowstyle='->', lw=0.8))
ax.text(2.62, 0.05, r'$x$'); ax.text(2.05, 0.62, r'$z$'); ax.plot([0], [0], 'ko', ms=2.5); ax.text(0.06, -0.22, r'$O$')
# radii
ax.plot([0, -a*np.cos(0.9)], [zc, zc-a*np.sin(0.9)], color='w', lw=0.8); ax.text(-0.42, zc-0.2, r'$a$', color='w', fontsize=8)
ax.plot([0, -b*np.cos(0.6)], [zc, zc+b*np.sin(0.6)], color='k', lw=0.8); ax.text(-1.05, zc+0.62, r'$b$')
# height and gap
ax.annotate('', (-1.55, zc), (-1.55, 0), arrowprops=dict(arrowstyle='<->', lw=0.7)); ax.text(-1.8, 0.95, r'$h$')
ax.plot([-1.62, 0], [zc, zc], 'k:', lw=0.6)
ax.annotate('', (0.0, zc-b), (0.0, 0), arrowprops=dict(arrowstyle='<->', lw=0.7, color='#D55E00'))
ax.text(0.08, 0.38, r'$\varepsilon b$', color='#D55E00')
# motion
ax.annotate('', (0, zc+b+0.55), (0, zc+b+0.05), arrowprops=dict(arrowstyle='<->', lw=1.1, color='#D55E00'))
ax.text(0.1, zc+b+0.3, r'$U\mathbf{e}_z e^{-i\omega t}$', color='#D55E00', fontsize=8)
ax.annotate('', (b+0.6, zc), (b+0.05, zc), arrowprops=dict(arrowstyle='<->', lw=1.1, color='#009E73'))
ax.text(b+0.1, zc+0.12, r'$U\mathbf{e}_x e^{-i\omega t}$', color='#009E73', fontsize=8)
ax.text(-2.95, 3.35, r'fluid $(\rho,\mu)$', fontsize=8)
ax.text(0.55, zc-b-0.15, r'shell $(k_s,\mu_s)$', fontsize=7.5, color='#0072B2')
ax.text(-2.95, -1.5, r'porous layer $(k_p,\mu_p)$', fontsize=8)
ax.set_xlim(-3, 3); ax.set_ylim(-1.7, 3.7); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(H/'fig1_schematic.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 2 validation
v = R['validation_steady']; e9 = np.array(v['eps']); V4 = R4['validation']
ed = np.logspace(np.log10(0.25), np.log10(5), 400); xd = 1/(1+ed)
def brenner(h):
    al = np.arccosh(h); n = np.arange(1, 80)
    with np.errstate(over='ignore', invalid='ignore'):
        t = n*(n+1)/((2*n-1)*(2*n+3))*((2*np.sinh((2*n+1)*al)+(2*n+1)*np.sinh(2*al))/(4*np.sinh((n+.5)*al)**2-(2*n+1)**2*np.sinh(al)**2)-1)
    return 4/3*np.sinh(al)*np.nansum(t)
fig, axs = plt.subplots(1, 2, figsize=(TW, 2.3))
a = axs[0]
a.plot(ed, [brenner(1+e) for e in ed], color=OI[0], label='Brenner (exact), normal')
a.plot(ed, 1/(1-9/8*xd+xd**3/2), color=OI[0], ls=':', label=r'reflection series $O(x^3)$, normal')
a.plot(V4['eps'], V4['z'], color=OI[1], label='present, normal')
a.plot(ed, 1/(1-9/16*xd+xd**3/8-45/256*xd**4-xd**5/16), color=OI[2], ls=':', label=r'Faxén series $O(x^5)$, parallel')
a.plot(V4['eps'], V4['x'], color=OI[2], ls='--', label='present, parallel')
a.set_xscale('log'); a.set_xticks([0.25, 0.5, 1, 2, 5]); a.xaxis.set_major_formatter(mt.ScalarFormatter()); a.xaxis.set_minor_formatter(mt.NullFormatter())
a.set_xlabel(r'$\varepsilon=(h-b)/b$'); a.set_ylabel(r'$F/F_\infty$ ($\mathrm{Wo}\to0$)'); panel(a, '(a)')
a = axs[1]; hv = R['validation_inviscid']
a.plot(V4['Wo'], V4['m_z'], color=OI[1]); a.plot(hv['Wo'], hv['z'], 'o', color=OI[1], ms=3.5, label='present, normal')
a.plot(V4['Wo'], V4['m_x'], color=OI[2], ls='--'); a.plot(hv['Wo'], hv['x'], 's', color=OI[2], ms=3.5, label='present, parallel')
a.axhline(hv['pot_z'], color=OI[1], ls=':', lw=1, label=r'image $3b^3/16h^3$')
a.axhline(hv['pot_x'], color=OI[2], ls=':', lw=1, label=r'image $3b^3/32h^3$')
a.set_xscale('log'); logfmt(a); a.set_xlabel(r'$\mathrm{Wo}$'); a.set_ylabel(r'$m_{\rm int}/m_f$ ($\varepsilon=1$)'); panel(a, '(b)')
h1, l1 = axs[0].get_legend_handles_labels(); h2, l2 = axs[1].get_legend_handles_labels()
fig.legend(h1+h2, l1+l2, loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=3, columnspacing=1.2)
fig.tight_layout(); fig.savefig(H/'fig2_validation.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 3 spectra vs alpha_p
S = R4['spectra_ap']
fig, axs = plt.subplots(2, 2, figsize=(TW, 4.2), sharex=True)
for j, d in enumerate('zx'):
    for k in ['wall', '50', '20', '10', '5']:
        c, ls = STY[k]; dd = S[f'{d}_{k}']
        axs[0, j].plot(dd['Wo'], dd['gam'], color=c, ls=ls, label=LAB[k])
        axs[1, j].plot(dd['Wo'], dd['chi'], color=c, ls=ls)
    Wb = np.logspace(np.log10(0.05), np.log10(0.6), 100)
    axs[1, j].plot(Wb, -Wb/np.sqrt(2), color='0.45', lw=2.2, alpha=0.45, label=r'$-\mathrm{Wo}/\sqrt{2}$ (Basset, $\mathrm{Wo}\to0$)')
    axs[1, j].axhline(0, color='0.6', lw=0.5); axs[1, j].set_yscale('symlog', linthresh=1e-2, linscale=0.6)
    axs[1, j].set_xscale('log'); logfmt(axs[1, j]); axs[1, j].set_xlabel(r'$\mathrm{Wo}$')
    panel(axs[0, j], '(a) normal' if d == 'z' else '(b) parallel'); panel(axs[1, j], '(c) normal' if d == 'z' else '(d) parallel')
axs[0, 0].set_ylabel(r'$\hat\gamma_{\rm int}$'); axs[1, 0].set_ylabel(r'$\hat\chi_{\rm int}$')
h, l = axs[0, 0].get_legend_handles_labels(); h2, l2 = axs[1, 0].get_legend_handles_labels(); h += h2; l += l2
fig.tight_layout(); fig.subplots_adjust(top=0.88)
fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.5, 0.925), ncol=3); fig.savefig(H/'fig3_spectra.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 4 steady resistance
st = R4['steady']; eg = np.array(st['eps'])
fig, axs = plt.subplots(1, 2, figsize=(TW, 2.2))
SS = {'wall': (OI[0], '-', 'rigid wall'), 'ap50': (OI[1], '--', r'$\alpha_p=50$'), 'ap10': (OI[3], ':', r'$\alpha_p=10$'),
      'ap10_bpm': (OI[5], '-.', r'$\alpha_p=10,\ \beta_p=-0.5$'), 'ap10_bpp': (OI[4], (0, (5, 1, 1, 1)), r'$\alpha_p=10,\ \beta_p=0.5$')}
for j, d in enumerate('zx'):
    for k, (c, ls, lab) in SS.items():
        axs[j].plot(eg, st[f'{d}_{k}'], color=c, ls=ls, label=lab)
    axs[j].set_xlabel(r'$\varepsilon$'); panel(axs[j], '(a) normal' if d == 'z' else '(b) parallel')
axs[0].set_ylabel(r'$F/F_\infty$ ($\mathrm{Wo}\to0$)')
h, l = axs[0].get_legend_handles_labels()
fig.tight_layout(); fig.subplots_adjust(top=0.8)
fig.legend(h, l, loc='lower center', bbox_to_anchor=(0.5, 0.88), ncol=5, columnspacing=1.0); fig.savefig(H/'fig5_steady.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 5 regime map (sign of chi_int) + crossovers
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
R5 = json.load(open(C0 / 'results5.json')); mp = R5['map']; Wm = np.array(mp['Wo']); am = np.array(mp['ap'])
c = R2['cross_ap']; ap = np.array(c['ap'])
BS = {'-0.5': (OI[5], 0.96), '0.0': (OI[1], 1.0), '0.5': (OI[4], 1.04)}
fig, axs = plt.subplots(1, 2, figsize=(TW, 2.7))
for j, d in enumerate('zx'):
    a = axs[j]; ch = np.array(mp[d])
    a.contourf(am, Wm, (ch.T > 0).astype(float), levels=[-0.5, 0.5, 1.5], colors=['#F2F2F2', '#D6E6F5'])
    a.contour(am, Wm, ch.T, levels=[0], colors='k', linewidths=0.6)
    for bp, (col, off) in BS.items():
        for x, L in zip(ap*off, c[f'{d}_{bp}']):
            for W, sg in L:
                a.plot(x, W, 'o' if sg > 0 else '^', mfc=col if sg > 0 else 'none', mec=col, ms=3.2, mew=0.8)
    aa = np.logspace(np.log10(2), 2, 200)
    a.plot(aa, aa**2/(6*np.sqrt(2)), '--', color=OI[2], lw=1.1)
    a.plot(aa, aa, ':', color='0.35', lw=0.9)
    a.text(45, 0.45, r'$m_{\rm int}<0$', fontsize=7.5); a.text(40, 12, r'$m_{\rm int}>0$', fontsize=7.5, color='#1F4E79')
    a.text(2.4, 60, 'transparent\n' + r'$m_{\rm int}<0$', fontsize=7.5)
    a.set_xscale('log'); a.set_yscale('log'); a.set_xlim(2, 100); a.set_ylim(0.2, 250); logfmt(a); logfmt(a, 'y')
    a.set_xlabel(r'$\alpha_p=b/\sqrt{k_p}$'); panel(a, '(a) normal' if d == 'z' else '(b) parallel')
axs[0].set_ylabel(r'$\mathrm{Wo}$')
hd = [Line2D([], [], color=BS[k][0], marker='s', ls='none', ms=4, label=rf'$\beta_p={float(k):g}$') for k in BS] + \
     [Line2D([], [], color='k', marker='o', ls='none', ms=4, label=r'$\mathrm{Wo}_c^{\uparrow}$'),
      Line2D([], [], color='k', marker='^', mfc='none', ls='none', ms=4, label=r'$\mathrm{Wo}_c^{\downarrow}$'),
      Line2D([], [], color=OI[2], ls='--', label=r'$\alpha_p^2/(6\sqrt{2})$'), Line2D([], [], color='0.35', ls=':', label=r'$\mathrm{Wo}=\alpha_p$')]
fig.tight_layout(); fig.subplots_adjust(top=0.8)
fig.legend(handles=hd, loc='lower center', bbox_to_anchor=(0.5, 0.86), ncol=4); fig.savefig(H/'fig6_regime_map.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 6 soft particles
s4 = R4['spectra_soft']; cs = R2['cross_soft']; als = np.array(cs['alpha_s'])
SA = {'2': (OI[2], '-.', r'$\alpha_s=2$'), '5': (OI[3], ':', r'$\alpha_s=5$'), '10': (OI[1], '--', r'$\alpha_s=10$'),
      'rigid': (OI[0], '-', 'impermeable')}
KA = {'0.0': (OI[2], 0.94), '0.5': (OI[4], 0.98), '0.8': (OI[3], 1.02), '0.95': (OI[1], 1.06)}
fig, axs = plt.subplots(2, 2, figsize=(TW, 4.4))
for k, (col, ls, lab) in SA.items():
    dd = s4[f'z_{k}']
    axs[0, 0].plot(dd['Wo'], dd['gam'], color=col, ls=ls, label=lab); axs[0, 1].plot(dd['Wo'], dd['chi'], color=col, ls=ls)
for a in axs[0]:
    a.set_xscale('log'); logfmt(a); a.set_xlabel(r'$\mathrm{Wo}$')
axs[0, 1].set_yscale('symlog', linthresh=1e-2, linscale=0.6); axs[0, 1].axhline(0, color='0.6', lw=0.5)
axs[0, 0].set_ylabel(r'$\hat\gamma_{\rm int}$'); axs[0, 1].set_ylabel(r'$\hat\chi_{\rm int}$')
panel(axs[0, 0], r'(a) $\kappa=0.7$'); panel(axs[0, 1], r'(b) $\kappa=0.7$')
hs, ls_ = axs[0, 0].get_legend_handles_labels()
for j, d in enumerate('zx'):
    a = axs[1, j]
    for g, (col, off) in KA.items():
        for x, L in zip(als*off, cs[f'{d}_{g}']):
            for W, sg in L:
                a.plot(x, W, 'o' if sg > 0 else '^', mfc=col if sg > 0 else 'none', mec=col, ms=3.5)
    for W, sg in cs[f'{d}_rigid']:
        a.axhline(W, color=OI[0], ls='--', lw=0.8)
    a.set_xscale('log'); a.set_yscale('log'); logfmt(a); a.yaxis.set_major_formatter(mt.ScalarFormatter())
    a.yaxis.set_minor_formatter(mt.NullFormatter()); a.set_yticks([1, 2, 5, 10, 20, 50])
    a.set_xlabel(r'$\alpha_s=b/\sqrt{k_s}$'); panel(a, '(c) normal' if d == 'z' else '(d) parallel')
axs[1, 0].set_ylabel(r'crossover $\mathrm{Wo}$')
hd = [Line2D([], [], color=KA[k][0], marker='s', ls='none', ms=4, label=rf'$\kappa={float(k):g}$') for k in KA] + \
     [Line2D([], [], color=OI[0], ls='--', label='impermeable')]
fig.tight_layout(h_pad=1.5); fig.subplots_adjust(top=0.91, bottom=0.14)
fig.legend(hs, ls_, loc='lower center', bbox_to_anchor=(0.5, 0.95), ncol=4)
fig.legend(handles=hd, loc='upper center', bbox_to_anchor=(0.5, 0.045), ncol=5); fig.savefig(H/'fig7_soft.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 7 acoustofluidic contrast
ac = R4['acoustic']; Wl = np.array(ac['Wo_line']); e2 = np.array(ac['eps']); W2 = np.array(ac['Wo'])
fig = plt.figure(figsize=(TW, 2.3))
gs = fig.add_gridspec(1, 4, width_ratios=[1.15, 1, 1, 0.06], wspace=0.45)
a = fig.add_subplot(gs[0])
for lab, col, nm in [('ctc', OI[2], 'CTC-like'), ('wbc', OI[1], 'leukocyte-like')]:
    a.plot(Wl, ac[f'{lab}_phase_eps1'], color=col, label=nm + r', $\varepsilon=1$')
    a.plot(Wl, ac[f'{lab}_phase_eps4'], color=col, ls=':', label=nm + r', $\varepsilon=4$')
a.set_xscale('log'); logfmt(a); a.set_xlabel(r'$\mathrm{Wo}$'); a.set_ylabel(r'$\arg(-F_z/U_z)$ (deg)'); panel(a, '(a)')
a.legend(loc='lower center', bbox_to_anchor=(1.75, 1.13), ncol=4, columnspacing=1.0)
lev = np.linspace(1.2, 2.8, 17)
for j, d in enumerate('zx'):
    a = fig.add_subplot(gs[j+1])
    r = np.array(ac[f'ctc_{d}_absFint'])/np.array(ac[f'wbc_{d}_absFint'])
    cf = a.contourf(W2, e2, r, levels=lev, cmap='cividis', extend='both')
    cl = a.contour(W2, e2, r, levels=[1.5, 2.0, 2.5], colors='w', linewidths=0.6); a.clabel(cl, fontsize=6.5, fmt='%.1f')
    a.set_xscale('log'); logfmt(a); a.set_xlabel(r'$\mathrm{Wo}$'); a.set_ylabel(r'$\varepsilon$')
    panel(a, '(b) normal' if d == 'z' else '(c) parallel')
cax = fig.add_subplot(gs[3]); fig.colorbar(cf, cax=cax, label=r'$|F^{\rm CTC}_{\rm int}|/|F^{\rm WBC}_{\rm int}|$', ticks=[1.2, 1.6, 2.0, 2.4, 2.8])
fig.savefig(H/'fig8_acoustic.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 8 flow fields
R6 = json.load(open(C0 / 'results6.json')); xg = np.array(R6['x']); zg = np.array(R6['z'])
fig, axs = plt.subplots(2, 2, figsize=(TW, 4.6), sharex=True, sharey=True)
labs = [('wall_lo', '(a) rigid wall, $\\mathrm{Wo}=0.5$'), ('perm_lo', '(b) $\\alpha_p=5$, $\\mathrm{Wo}=0.5$'),
        ('wall_hi', '(c) rigid wall, $\\mathrm{Wo}=10$'), ('perm_hi', '(d) $\\alpha_p=5$, $\\mathrm{Wo}=10$')]
for a, (k, t) in zip(axs.ravel(), labs):
    ux = np.array(R6[k]['ux'], dtype=float); uz = np.array(R6[k]['uz'], dtype=float); sp_ = np.hypot(ux, uz)
    cf = a.pcolormesh(xg, zg, np.log10(np.clip(sp_, 1e-4, 1)), cmap='cividis', vmin=-4, vmax=0, shading='auto')
    a.streamplot(xg, zg, np.nan_to_num(ux), np.nan_to_num(uz), color='w', linewidth=0.5, density=1.1, arrowsize=0.5)
    a.add_patch(Circle((0, 2.0), 1.0, facecolor='0.85', edgecolor='k', lw=0.6, zorder=3))
    a.axhline(0, color='w', lw=0.8, ls='--')
    if 'perm' in k: a.text(-3.85, -2.3, 'porous layer', color='w', fontsize=7.5)
    else: a.add_patch(Rectangle((-4, -2.5), 8, 2.5, facecolor='0.55', edgecolor='none', zorder=2))
    a.set_aspect('equal'); a.set_xlim(-4, 4); a.set_ylim(-2.5, 4.5); panel(a, t)
for a in axs[1]: a.set_xlabel(r'$x/b$')
for a in axs[:, 0]: a.set_ylabel(r'$z/b$')
fig.tight_layout(); fig.subplots_adjust(right=0.86)
cax = fig.add_axes([0.89, 0.15, 0.022, 0.7]); fig.colorbar(cf, cax=cax, label=r'$\log_{10}|\mathrm{Re}\,\mathbf{u}|/U$')
fig.savefig(H/'fig4_flow_fields.pdf'); plt.close(fig)

# ---------------------------------------------------------------- Fig. 9 error analysis (appendix)
qc = R5['quad']; tr = R5['trunc']
fig, axs = plt.subplots(1, 2, figsize=(TW, 2.3))
lab9 = {'0.05_z_1000000.0': 'rigid wall, Wo = 0.05, normal', '3.0_x_10.0': r'$\alpha_p=10$, Wo = 3, parallel', '30.0_z_20.0': r'$\alpha_p=20$, Wo = 30, normal'}
for (k, v), col in zip([(k, v) for k, v in qc.items() if k != 'nk'], OI[1:]):
    axs[0].semilogy(qc['nk'], np.maximum(v, 1e-17), 'o-', color=col, ms=3.5, label=lab9.get(k, k))
axs[0].set_xscale('log', base=2); axs[0].set_xlabel('Gauss nodes per panel'); axs[0].set_ylabel(r'relative change of $\mathsf{M}$')
axs[0].legend(loc='upper right', fontsize=6.5); panel(axs[0], '(a) quadrature')
x = np.array(tr['x']); er = np.array(tr['err'])
axs[1].loglog(x, er, 'o-', color=OI[1], ms=3.5, label='closure vs Brenner (normal)')
xx = np.array([0.15, 0.6]); axs[1].loglog(xx, 0.3*xx**4, '--', color='0.4', label=r'slope 4')
axs[1].set_xticks([0.15, 0.2, 0.3, 0.5, 0.8]); axs[1].xaxis.set_major_formatter(mt.ScalarFormatter()); axs[1].xaxis.set_minor_formatter(mt.NullFormatter()); axs[1].set_xlabel(r'$x=b/h$'); axs[1].set_ylabel('relative error ($\\mathrm{Wo}\\to0$)'); axs[1].legend(loc='upper left', fontsize=6.5)
panel(axs[1], '(b) dipolar truncation')
fig.tight_layout(); fig.savefig(H/'fig9_error_analysis.pdf'); plt.close(fig)
print('figures written')
