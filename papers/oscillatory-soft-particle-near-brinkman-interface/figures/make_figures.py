"""Generate all figures from code/results.json (produced by code/make_results.py)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from pathlib import Path
H = Path(__file__).resolve().parent
R = json.load(open(H.parent/'code'/'results.json'))
plt.rcParams.update({'font.size': 9, 'axes.labelsize': 10, 'legend.fontsize': 7.5,
                     'figure.dpi': 150, 'savefig.bbox': 'tight', 'mathtext.fontset': 'cm'})
C = ['#1f4e79', '#c0392b', '#2e8b57', '#d68910', '#7d3c98', '#555555']

# Fig 1 schematic
fig, ax = plt.subplots(figsize=(3.4, 2.8))
ax.add_patch(Rectangle((-3, -2.2), 6, 2.2, color='#c8a97e', alpha=.55))
for x in np.linspace(-2.8, 2.8, 30):
    for y in np.linspace(-1.0, -0.1, 5):
        ax.add_patch(Circle((x + 0.1*(y*7 % 2), y), 0.04, color='#8b6b3e'))
ax.add_patch(Circle((0, 1.9), 1.0, color='#9ecae1', alpha=.8))
ax.add_patch(Circle((0, 1.9), 0.65, color='#1f4e79'))
ax.plot([-3, 3], [0, 0], 'k', lw=1)
ax.annotate('', (0, 3.25), (0, 2.65), arrowprops=dict(arrowstyle='<->', lw=1.4, color=C[1]))
ax.annotate('', (1.65, 1.9), (1.05, 1.9), arrowprops=dict(arrowstyle='<->', lw=1.4, color=C[2]))
ax.text(0.12, 3.05, r'$U_z e^{-i\omega t}$', color=C[1]); ax.text(1.1, 2.05, r'$U_x$', color=C[2])
ax.plot([-1.6, -1.6], [0, 1.9], 'k:', lw=.8); ax.text(-1.55, 0.9, r'$h$')
ax.plot([0, 0.65*np.cos(-.6)], [1.9, 1.9+0.65*np.sin(-.6)], 'w', lw=.8); ax.text(0.15, 1.55, r'$a$', color='w')
ax.plot([0, -1.0*np.cos(.5)], [1.9, 1.9+np.sin(.5)], 'k', lw=.8); ax.text(-0.75, 2.35, r'$b$')
ax.text(-2.9, 3.1, r'fluid $(\rho,\mu)$, $z>0$', fontsize=8)
ax.text(-2.9, -1.75, r'Brinkman layer $(k_p,\mu_p)$, $z<0$', fontsize=8)
ax.text(1.2, 0.12, r'interface: stress jump $\beta_p$', fontsize=7)
ax.text(0.85, 0.95, r'shell $(k_s,\mu_s,\beta_s)$', fontsize=7)
ax.text(-0.5, 1.95, 'core', color='w', fontsize=7); ax.text(-0.4, 1.7, r'slip $\ell_c$', color='w', fontsize=6.5)
ax.set_xlim(-3, 3); ax.set_ylim(-2.2, 3.4); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(H/'fig1_schematic.pdf'); plt.close(fig)

# Fig 2 validation
v = R['validation_steady']; e = np.array(v['eps'])
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.6))
a = axs[0]
a.plot(e, v['brenner'], 'k-', label='Brenner (exact), normal')
a.plot(e, v['refl_n'], 'k--', lw=.8, label=r'reflection series $O(x^3)$, normal')
a.plot(e, v['normal'], 'o', color=C[0], ms=4, label='present, normal')
a.plot(e, v['faxen'], '-', color='gray', label=r'Faxén series $O(x^5)$, parallel')
a.plot(e, v['parallel'], 's', color=C[1], ms=4, label='present, parallel')
a.set_xscale('log'); a.set_xticks([0.25, 0.5, 1, 2, 5]); a.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter()); a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a.set_xlabel(r'$\varepsilon=(h-b)/b$'); a.set_ylabel(r'$F/F_\infty$ (steady)')
a.legend(frameon=False); a.set_title('(a)', loc='left')
hv = R['validation_inviscid']; W = np.array(hv['Wo'])
a = axs[1]
a.semilogx(W, hv['z'], 'o-', color=C[0], ms=4, label='present, normal')
a.semilogx(W, hv['x'], 's-', color=C[1], ms=4, label='present, parallel')
a.axhline(hv['pot_z'], color=C[0], ls='--', lw=.8, label='inviscid image, normal')
a.axhline(hv['pot_x'], color=C[1], ls='--', lw=.8, label='inviscid image, parallel')
a.set_xlabel(r'$\mathrm{Wo}$'); a.set_ylabel(r'$m_{\rm int}/m_f$'); a.legend(frameon=False)
a.set_title(r'(b) rigid wall, $\varepsilon=1$', loc='left')
fig.tight_layout(); fig.savefig(H/'fig2_validation.pdf'); plt.close(fig)

# Fig 3 spectra vs alpha_p
S = R['spectra_ap']; W = np.array(S['Wo'])
fig, axs = plt.subplots(2, 2, figsize=(6.8, 4.8), sharex=True)
for j, d in enumerate(['z', 'x']):
    for i, ap in enumerate(['wall', '50', '20', '10', '5']):
        y = np.array(S[f'{d}_{ap}'])
        lab = 'rigid wall' if ap == 'wall' else rf'$\alpha_p={ap}$'
        axs[0, j].semilogx(W, y[:, 0], color=C[i], label=lab)
        axs[1, j].semilogx(W, y[:, 1], color=C[i], label=lab)
    axs[1, j].axhline(0, color='k', lw=.5)
    axs[1, j].set_yscale('symlog', linthresh=1e-2)
    axs[1, j].set_xlabel(r'$\mathrm{Wo}$')
    axs[0, j].set_title(('(a) normal' if d == 'z' else '(b) parallel') + r', $\varepsilon=1$, $\beta_p=0$', loc='left')
axs[0, 0].set_ylabel(r'$\hat\gamma_{\rm int}=-{\rm Re}\,F_{\rm int}/(6\pi\mu bU)$')
axs[1, 0].set_ylabel(r'$\hat\chi_{\rm int}={\rm Im}\,F_{\rm int}/(6\pi\mu bU)$')
axs[0, 0].legend(frameon=False)
fig.tight_layout(); fig.savefig(H/'fig3_spectra_alphap.pdf'); plt.close(fig)

# Fig 4 all crossovers vs alpha_p
R2 = json.load(open(H.parent/'code'/'results2.json'))
c = R2['cross_ap']; ap = np.array(c['ap'])
def scat(a, xs, lists, col, lab):
    first = True
    for x, L in zip(xs, lists):
        for W, sg in L:
            a.plot(x, W, 'o' if sg > 0 else '^', mfc=col if sg > 0 else 'none', mec=col, ms=4,
                   label=lab if first else None); first = False
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.8))
for j, d in enumerate(['z', 'x']):
    for i, bp in enumerate(['-0.5', '0.0', '0.5']):
        scat(axs[j], ap*(1+0.04*(i-1)), c[f'{d}_{bp}'], C[i], rf'$\beta_p={float(bp):g}$')
    for W, sg in c[f'{d}_wall']:
        axs[j].axhline(W, color='k', ls='--', lw=.8, label='rigid wall')
    axs[j].plot(ap, 0.116*ap**2, ':', color='gray', lw=.8, label=r'$\mathrm{Wo}=0.116\,\alpha_p^2$')
    axs[j].set_ylim(0.6, 250)
    axs[j].set_xscale('log'); axs[j].set_yscale('log')
    axs[j].set_xlabel(r'$\alpha_p=b/\sqrt{k_p}$'); axs[j].set_ylabel(r'crossover $\mathrm{Wo}$')
    axs[j].set_title('(a) normal' if d == 'z' else '(b) parallel', loc='left')
axs[0].legend(frameon=False, fontsize=6.5)
fig.tight_layout(); fig.savefig(H/'fig4_Woc_alphap.pdf'); plt.close(fig)

# Fig 5 soft particle
s = R['spectra_soft']; W = np.array(s['Wo']); cs = R2['cross_soft']; als = np.array(cs['alpha_s'])
fig, axs = plt.subplots(2, 2, figsize=(6.8, 4.8))
for i, As in enumerate(['2', '5', '10', 'rigid']):
    y = np.array(s[f'z_{As}'])
    lab = 'rigid sphere' if As == 'rigid' else rf'$\alpha_s={As}$'
    axs[0, 0].semilogx(W, y[:, 0], color=C[i], label=lab)
    axs[0, 1].semilogx(W, y[:, 1], color=C[i], label=lab)
axs[0, 1].set_yscale('symlog', linthresh=1e-2); axs[0, 1].axhline(0, color='k', lw=.5)
axs[0, 0].set_ylabel(r'$\hat\gamma_{\rm int}$'); axs[0, 1].set_ylabel(r'$\hat\chi_{\rm int}$')
for a in axs[0]: a.set_xlabel(r'$\mathrm{Wo}$')
axs[0, 0].legend(frameon=False)
axs[0, 0].set_title(r'(a) normal, $\gamma=0.7$, $\alpha_p=20$', loc='left'); axs[0, 1].set_title('(b)', loc='left')
for j, d in enumerate(['z', 'x']):
    for i, g in enumerate(['0.0', '0.5', '0.8', '0.95']):
        scat(axs[1, j], als*(1+0.05*(i-1.5)), cs[f'{d}_{g}'], C[i], rf'$\gamma={float(g):g}$')
    for Wc, sg in cs[f'{d}_rigid']:
        axs[1, j].axhline(Wc, color='k', ls='--', lw=.8, label='rigid sphere')
    axs[1, j].set_xscale('log'); axs[1, j].set_yscale('log')
    axs[1, j].yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter()); axs[1, j].yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    axs[1, j].set_yticks([1, 2, 5, 10, 20, 50])
    axs[1, j].set_xlabel(r'$\alpha_s=b/\sqrt{k_s}$'); axs[1, j].set_ylabel(r'crossover $\mathrm{Wo}$')
    axs[1, j].set_title(('(c) normal' if d == 'z' else '(d) parallel') + r', $\alpha_p=20$', loc='left')
axs[1, 0].legend(frameon=False, fontsize=6.5, ncol=2)
fig.tight_layout(); fig.savefig(H/'fig5_soft_particle.pdf'); plt.close(fig)

# Fig 6 steady
st = R['steady']; e = np.array(st['eps'])
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.6))
labs = {'wall': 'rigid wall', 'ap50': r'$\alpha_p=50$', 'ap10': r'$\alpha_p=10$',
        'ap10_bpm': r'$\alpha_p=10,\ \beta_p=-0.5$', 'ap10_bpp': r'$\alpha_p=10,\ \beta_p=0.5$'}
for j, d in enumerate(['z', 'x']):
    for i, k in enumerate(labs):
        axs[j].plot(e, st[f'{d}_{k}'], color=C[i], ls='-' if i < 3 else ':', label=labs[k])
    axs[j].set_xlabel(r'$\varepsilon$'); axs[j].set_ylabel(r'$F/F_\infty$ ($\mathrm{Wo}\to0$)')
    axs[j].set_title('(a) normal' if d == 'z' else '(b) parallel', loc='left')
axs[0].legend(frameon=False)
fig.tight_layout(); fig.savefig(H/'fig6_steady.pdf'); plt.close(fig)

# Fig 7 acoustofluidic contrast
ac = R2['acoustic2']; e = np.array(ac['eps']); W = np.array(ac['Wo'])
def get(lab, d):
    Fi = np.array(ac[f'{lab}_{d}_Fint'][0]); Fi = Fi[0] + 1j*Fi[1]
    Fz = np.array(ac[f'{lab}_{d}_Finf']); Fz = Fz[0] + 1j*Fz[1]
    return Fi, Fz
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6), constrained_layout=True)
for lab, col, nm in [('ctc', C[1], 'CTC-like'), ('wbc', C[0], 'leukocyte-like')]:
    Fi, Fz = get(lab, 'z')
    for i, ls in [(0, '-'), (len(e)-1, ':')]:
        axs[0].semilogx(W, np.degrees(np.angle(-(Fz + Fi[i]))), ls, color=col,
                        label=f'{nm}, ' + rf'$\varepsilon={e[i]:g}$')
axs[0].set_xlabel(r'$\mathrm{Wo}$'); axs[0].set_ylabel(r'$\arg(-F_z/U_z)$ (deg)')
axs[0].legend(frameon=False, fontsize=6); axs[0].set_title('(a) normal, phase', loc='left')
for j, d in enumerate(['z', 'x']):
    a = axs[j+1]; Fc, _ = get('ctc', d); Fw, _ = get('wbc', d)
    r = np.abs(Fc)/np.abs(Fw)
    cs_ = a.contourf(W, e, r, levels=np.linspace(0.8, 3.0, 12), cmap='viridis', extend='both')
    a.contour(W, e, r, levels=[1.0, 1.5, 2.0], colors='w', linewidths=.6)
    a.set_xscale('log'); a.set_xlabel(r'$\mathrm{Wo}$'); a.set_ylabel(r'$\varepsilon$')
    a.set_title(('(b) normal' if d == 'z' else '(c) parallel') + r', $|F^{\rm CTC}_{\rm int}|/|F^{\rm WBC}_{\rm int}|$', loc='left', fontsize=7.5)
fig.colorbar(cs_, ax=axs[1:], shrink=.9)
fig.savefig(H/'fig7_acoustic_contrast.pdf'); plt.close(fig)
print('figures written')
