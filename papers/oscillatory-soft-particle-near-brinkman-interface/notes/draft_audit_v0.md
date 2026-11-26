# First-draft audit (Pass 1, no edits) — 2026-11-26

Snapshot: `versions/v0/`. Tools run: `rp.py symbols`, `rp.py lint`, `rp.py check` (clean). Independent checks:
`notes/checks/check1_symbolic.py` (sympy), `check2_numeric.py`, `check3_upper_crossover.py`; their outputs are saved next to them.

Severity: **critical** = wrong or undefined; **major** = breaks the reader's flow; **minor** = wording.

---

## 1. Notation table

| Symbol | Meaning | Dim. | Defined | Used | Issue |
|---|---|---|---|---|---|
| a, b | core / outer radius | m | PF:4–5 | PF | – |
| γ = a/b | core ratio | – | PF:5 | everywhere | **critical: clashes with γ_int (damping) and \hat γ_int.** The reader meets "γ = 0.7" and "\hat γ_int" in the same figure |
| γ_int, \hat γ_int | wall-induced damping | kg/s, – | PF:186–190 | Res | see above |
| m_int, m_f | wall-induced added mass; displaced mass | kg | PF:186, 192 | Res | – |
| χ_int, \hat χ_int | reactive coefficient ω m_int/(6πμb) | – | PF:191 | Res, figs | **minor:** written \hat χ_int in figures but χ_int in symbols list; dimensional χ_int never defined. Keep only \hat χ_int |
| ρ, μ | fluid density, viscosity | SI | PF:6 | all | – |
| k_s, μ_s, β_s | shell permeability, Brinkman viscosity, stress jump | SI / – | PF:10, 30 | – | – |
| k_p, μ_p, β_p | layer permeability, viscosity, stress jump | SI / – | PF:8–9, 126 | – | – |
| ℓ_c, \hat ℓ_c | core slip length | m, – | PF:29, Tab. I | – | **minor:** \hat ℓ_c also used as rigid-sphere slip on r = b (PF:118); say so in Tab. I |
| h, ε | centre height; gap (h−b)/b | m, – | PF:11, 14 | all | **major: h also used for the kernel h_j(r)** (An:28). Analysis mixes h (height) and h_f(r) in the same equations (An:51, 145–153) |
| x = b/h | inverse distance | – | An:236 | Res | **minor:** x is also the Cartesian coordinate |
| r, θ, φ | spherical coordinates about x_0 | – | PF:11 | – | **minor:** φ (azimuth, \varphi) vs φ (phase, \phi) — two glyphs of the same letter |
| ω, U, \be, \bU | frequency, velocity amplitude, direction | – | PF:18–19 | – | **minor:** \bU used once, then U\be; drop \bU |
| λ_f, λ_s, λ_p, λ_j | complex screening parameters | 1/m | PF:85–89 | – | **minor:** λ ≡ λ_f b in the analysis (An:3) changes λ from dimensional to dimensionless. State it as "λ ≡ λ_f b" |
| δ_v | viscous penetration depth √(2μ/ρω) | m | PF:93 | Res:136 | **critical:** PF:93 says δ_v = Re(1/λ_f); in fact δ_v = 1/Re λ_f (check1 item 10). Res:136–137 calls √(μ/ρω) "the viscous penetration depth", which is δ_v/√2 |
| Wo, α_s, α_p | dimensionless groups | – | Tab. I | – | **minor:** first used in the Introduction (Intro:11) before definition (allowed in guide points; define on first use in the final intro) |
| Wo_c, Wo_c^↑, Wo_c^↓ | crossover Womersley numbers | – | Def. 1 (PF:206) | – | **minor:** Abstract uses Wo_c for the porous case where Wo_c^↑ is meant |
| \bsig, \bn, \bm\Pi, μ_j | stress, normal, tangential projector | – | PF:97–101 | – | – |
| F, F_∞, F_int, \hat F | force (complex amplitude) | N, – | PF:177 | – | **critical: F also names a shell coefficient** (An:53 "F∇(e·∇1/r)"). In An:91 "F = Z_U U + …" and the shell F appear on one page |
| Φ, \bm w, \bu_rig | potential / vortical / rigid parts | – | An:8 | – | – |
| h_j, i_j | radial Helmholtz kernels | – | An:28 | – | **major: i_j clashes with the imaginary unit i** (e.g. "i_f" next to "iWo²"), and h_j with height h. Propose \mathcal K_j, \mathcal I_j (modified-Bessel style) |
| B, C, D, E, F, G, H | multipole coefficients | – | An:50–54 | – | **critical/major:** F (force), E (vs \be), H (vs h), C (generic). Propose B, C (exterior, keep), D (incident, keep), shell: E_1, E_2, G_1, G_2 |
| U_p, w_0 | centre values of incident potential / vortical velocity | – | An:62–63 | – | – |
| \mathcal U, \mathcal V, \mathcal P, \mathcal S | radial amplitudes | – | An:68–72 | App | **minor:** \mathcal S_rr vs \mathsf S_inc vs surface S |
| \bm s_U, \mathsf S_inc, Z_U, \bm z_inc, Z_p, Z_w | sphere response | – | An:85–90 | – | – |
| \bk, k, q, q_p | wavevector, magnitude, decay rates | – | An:140–142 | App | – |
| R_Φ, R_P, R_T, T_Φ, T_P, T_T | reflected / transmitted amplitudes | – | An:165 | – | **minor:** T also the transpose; R_P (poloidal) vs \mathcal P (pressure) |
| \mathsf A, \bm r, \bM | interface matrix, rhs, reflection matrix | – | An:168–174 | – | **minor:** M* (probe mass, PF:199) vs \bM |
| c_j | pressure coefficient of the potential part | – | App:6 | App | **minor:** defined only in the appendix, but its values appear in Lemma 1. Define in Lemma 1 |
| α_j | – | – | – | An:23 | **minor:** α_j used in the proof of Lemma 1 but never defined (means α_s or α_p; zero in the fluid) |
| N_k, N_θ | quadrature sizes | – | An:260 | – | **minor:** never defined |
| Ω | DBB drag ratio | – | Tab. III caption | Res | – |

Typesetting: vectors consistently \bm; matrices mixed \mathsf / \bm (\bm s_U, \mathsf S_inc). **Minor.**
Dimensional vs dimensionless: PF is dimensional, Analysis dimensionless (b = 1) — stated in An:3 but λ silently changes meaning (above).

## 2. Physical terms

| Term | First use | Defined? | Physical meaning given? |
|---|---|---|---|
| added mass / wall-induced added mass | Abstract, PF:186 | yes, Eq. (decomposition) | **major:** only mathematical; add "inertia of fluid entrained with the particle, changed by the wall" |
| damping coefficient γ_int | PF:186 | yes | partly |
| reactive force / coefficient | Res:99 | via \hat χ_int | **minor:** say "out-of-phase (inertial)" once |
| Womersley number | Tab. I | yes | **minor:** say "particle size over viscous penetration depth" in text, not only the table |
| stress jump (OTW) | PF:30 | equation only | **major:** add a physical sentence (tangential momentum transfer at a porous surface carried by the Brinkman boundary layer) |
| Brinkman (effective) viscosity | PF:8 | name only | **minor** |
| Basset (memory) force | Res:101 | no | **major:** used to explain the low-Wo branch without definition or reference |
| Froude–Krylov force | An:120 | no | **minor** |
| Stokes layer | Res:96 | no | **minor** |
| crossover Womersley number | Def. 1 | yes | yes |
| transparent layer | An:294, Res | Remark 7 | yes |
| soft particle | Assumption 2 | yes | yes |
| poloidal / toroidal | An:131, 165 | no | **minor** |
| Darcy drag | PF:41 | no | **minor** |
| image (dipole) | An:275 | no | **minor** |

## 3. Equation checks

Dimensional consistency of every numbered equation in PF (eqs. 1–14) — **pass** (stress-jump terms μu/√k and slip terms ℓσ/μ have units of stress and velocity). Non-dimensionalisation (PF §F → Analysis) — consistent with the solver (pressures iWo²Φ, (iWo²−α²)Φ; screening (α²−iWo²)/(μ_j/μ)).

Verified independently (check1, sympy; check2, numeric):

| Item | Result |
|---|---|
| curl curl(e h) solenoidal, Helmholtz, radial forms (Eq. vort_radial) | PASS |
| dipole radial forms | PASS |
| force formula F = 4π/3 (S_rr − 2S_rθ) | PASS |
| Prop. 1: B, C, Z_U (rigid no-slip) | PASS (symbolic solve) |
| Prop. 1: Z_w = 6π e^λ via Mazur–Bedeaux | PASS |
| Z_p = 6π(1+λ+λ²/3) | PASS (numeric, earlier, solver vs formula) |
| w_0 = −(2/3)λ³ D | PASS |
| B + C → −1/4 (Stokes limit); B → 1/2 (inviscid) | PASS |
| λ_f b = e^{−iπ/4} Wo | PASS (numeric, principal branch) |
| m_int/m_f = (9/2) \hat χ_int / Wo² | PASS |
| Prop. 4 inviscid image 3/(16h³), 3/(32h³) | PASS |
| Weyl identity (Eq. weyl) | PASS (quadrature, 12 digits) |
| **δ_v = Re(1/λ_f)** (PF:93) | **FAIL — critical.** Correct: δ_v = 1/Re λ_f |
| Prop. 4 proof: "C → 0" (An:118, An:275) | **critical wording error.** C = −3e^λ/(2λ²) grows; it is the vortical *field* C h_f(r) ∝ e^{−λ(r−1)} that is confined to a layer of thickness O(|λ|^{-1}) |
| Remark 3: closure "agrees with the reflection series through O(x³)" | **major (overclaim).** check2(b): closure − series = O(x⁴)·(0.1–0.3) for ε ≤ 4, but for ε ≥ 9 the Richardson extrapolation in Wo is limited by Wo·h (not small), so the order cannot be confirmed numerically there. Rephrase as "numerically consistent with … for ε ≤ 4" |
| Lemma 1 proof, Prop. 3(ii) proof | **minor:** sketches; label them "proof sketch" |
| Limiting cases recovered | rigid exact unsteady drag (machine precision), DBB porous sphere (4–5 digits), Brenner (Tab. III), Faxén series, transparent interface (F_int = 0 to 1e−15), α_p → ∞ = rigid wall (4 digits), inviscid image (Fig. 2b) |

## 4. Reverse outline (core sections)

**Problem Formulation** — A: geometry, coordinates, gap. B: five assumptions. C: governing equations; screening parameters; δ_v. D: boundary conditions + Remark on limits (BJ). E: dimensionless groups, Tab. I, competition Wo vs α. F: force decomposition, observables, sign remark, crossover definition. G: why the problem is hard.
- Jump: §C introduces δ_v and "screening" before the reader knows why they matter (motivated only in §E). Merge C+D (both short) and move the λ discussion next to the dimensionless groups.
- §E (118 words) too thin to stand alone (lint).

**Solution Method** — A: decomposition lemma. B: sphere blocks, fields, tractions, force; response matrices; Prop. 1 rigid closed forms; Lemma 2 (force from centre values). C: Fourier reflection, interface system, reflection matrix, Prop. 3 limits, quadrature. D: closure, Prop. 2 series, accuracy remark, Algorithm 1, complexity. E: limiting regimes (Prop. 4 inviscid, steady remark, transparency remark).
- Lemma 2 (force from centre values) is stated *after* the response matrices that rely on it — reorder (state the lemma first, then the blocks).
- Accuracy remark sits inside the method; it belongs with the validation.
- Section has no opening sentence saying what the reader gets at the end, and no closing sentence.

**Results** — A: setup + Tab. II. B: validation, Tab. III, Fig. 2. C: rigid sphere spectra, Fig. 3 (low-Wo mechanism; three effects of permeability; damping peak). D: crossover map, Fig. 4, three features, β_p, implication. E: steady limit, Fig. 5 (140 words). F: soft particles, Fig. 6, bullet list. G: acoustofluidic contrast, Fig. 7. H: limitations (bullets).
- Results open with validation, which is method quality rather than a result → move to its own section.
- §E steady limit is short and logically belongs to the rigid-sphere discussion (as the Wo → 0 end of Fig. 3).
- Bullet lists in §F and §H must become prose (Pass 4).

## 5. Claim–evidence map

| Claim (location) | Evidence | Status |
|---|---|---|
| Wo_c ≈ 2.9 / 0.95, rigid wall (Abs, Res:98, Concl) | Fig. 3, results.json | supported |
| Consistent with Zhang's frequency-shift crossover (Res:105, Concl) | Remark 2 + Fig. 3 | supported qualitatively; **minor:** say "qualitatively", since we have no quantitative comparison with their data |
| Permeable layer raises Wo_c^↑ (Abs, Res:129) | Fig. 4 | supported |
| Upper crossover Wo ≈ 0.116 α_p² (Abs, Res:133) | Fig. 4, fit exponent 2.08 | supported; **new evidence (check3): it is independent of the gap (34.7–35.5 for ε = 1–3)** — not yet in the paper |
| Mechanism "δ' ≈ 8.6 k_p/b … combines pore scale with √k_p/b" (Res:136–139) | none | **major: unsupported/vague mechanism**; replace (see §9) |
| Window closes α_p ≈ 6–9 normal, 4–6 parallel (Abs, Res, Concl) | Fig. 4 (grid resolution 11 points) | supported; say "between grid points" |
| Damping peak at Wo ≈ α_p "is the frequency at which the Stokes layer matches the Brinkman length" (Res:110) | Fig. 3 only | **major: stated as fact; is an interpretation** → "is consistent with" |
| Low-Wo negative added mass = wall truncation of Basset memory (Res:100–104) | Fig. 3 + reasoning | plausible; **needs an established reference** (wall-modified memory/long-time tail) |
| Steady drag changes only a few per cent (Res:167–170) | Fig. 5, numbers | supported |
| Soft shell lowers damping up to ×4 (Res:186, 209) | Fig. 6(a) | supported |
| Core slip "has a weaker effect when the shell is permeable" (Res:211) | **none in the paper** | **critical: unsupported.** check2(c) shows it is true (rigid: γ_int 0.937 → 0.545 with \hat ℓ_c = 0.5; γ = 0.7, α_s = 5: 0.539 → 0.495), so add these numbers as a small table, or delete the sentence |
| Phase contrast ≤ 13°, force ratio 1.4–2.7 (Res:228–231) | Fig. 7 | supported |
| "Sorting works best at Wo = O(1)" (Res:233) | Fig. 7 + ratio | **minor:** interpretive → "suggests" |
| "favours mucus-penetrating carriers" (Concl, Res:210) | damping only | **minor:** hedge; no penetration model |
| "non-contact spectroscopy of permeability" (Abs, Concl) | Figs. 4, check3 | supported as proposal; keep "could provide" |
| Crossover locations less affected by closure error (Res:247) | none | already hedged with TODO; keep |

## 6. Referencing

- Equations never referenced (lint): eq:gap, eq:kinematics, eq:force, eq:kernels, eq:blocks, eq:weyl, eq:modes, eq:series, eq:first_reflection → reference where used or unnumber. **Minor.**
- Assumptions 1–5 never referenced → reference them where they bite (rotation, thick layer) or keep as an unreferenced list (acceptable). **Minor.**
- Figures: all cited before their float, all discussed; no order problem (lint). Fig. 3 bottom panels plot \hat χ_int on a symlog axis without saying "linear for |·| < 10⁻²" in the caption — **minor**. Fig. 7(b,c) colour bar has no label — **minor**. Fig. 2(a) legend says "Faxén series O(x⁵)" — fine.
- Tab. I lists α_p range 3–300, computations use 3–100 (Fig. 4) and up to 300 in the first sweep — **minor**, make consistent.

## 7. Language

- lint: 209 sentences, mean 24.2 words (good), 0 banned phrases. Most >50-word "sentences" are bullet lists, tables and captions (scanner artefacts). Real long sentences: PF:22 (79 words, "All fields are written …"), An:165–168 (60), Res proposition/claim lines.
- Bullet lists inside Results §F and §H and in "Three features make this hard" (PF:216) → prose.
- Tone: mostly report register; a few teaching phrases ("The negative branch has a simple interpretation", "Three features stand out") → tighten.
- Tense: consistent (present for results, past for computations) — keep.

## 8. Restructuring plan (5 → 7 main sections)

| Old | New |
|---|---|
| I Introduction (guide points) | **I Introduction** (guide points; update contributions/organisation) |
| II A Geometry; B Assumptions | **II Problem Formulation** — A Geometry, kinematics and assumptions |
| II C Governing equations (101 w) + D Boundary conditions | II B Governing equations and interface conditions |
| II E Dimensionless (118 w) + F Observables + G Objective | II C Dimensionless problem, force decomposition and observables (G folded in as the closing paragraph) |
| III A Decomposition + B Sphere response | **III Solution Method** — A Exact response of the core–shell sphere (Lemma 1, Lemma 2 first, then blocks, Prop. 1) |
| III C Reflection | III B Fourier reflection at the Brinkman interface |
| III D Closure + Algorithm + III E Limits | III C Self-consistent dipolar closure and limiting regimes |
| IV B Validation (+ Remark 3 accuracy) | **IV Validation and Accuracy** (Tab. III, Fig. 2, accuracy envelope, convergence) |
| IV A Setup → into IV/V opening; IV C Rigid spectra + IV E Steady limit + IV D Crossover map | **V Rigid Particle near a Permeable Layer: Spectra, Crossovers and Transparency** — A Interaction spectra from the steady to the inertial regime (Fig. 3 + steady Fig. 5); B Crossover map and the transparency law (Fig. 4) |
| IV F Soft particles + IV G Acoustofluidic + IV H Limitations | **VI Soft Particles and Biomedical Implications** — A Shell permeability and core size (Fig. 6, new slip/β_s table); B Acoustofluidic contrast (Fig. 7); C Limitations |
| V Conclusions | **VII Conclusions** (bullets) |
| Appendices A, B | unchanged |

## 9. Candidate physical insights (Pass 4 findings, blue)

1. **Low-frequency negative added mass from wall-truncated hydrodynamic memory.** Evidence: Fig. 3, \hat χ_int < 0 for Wo < Wo_c in every configuration; magnitude ∝ the Basset term 6πλ. Artefact check: present for rigid wall (exact limits verified) and at all α_p; converged. Reference to support the mechanism: established work showing that a wall changes the long-time velocity autocorrelation/memory of a sphere — to search and confirm (e.g. Felderhof's velocity-relaxation-near-a-wall papers; Basset/Maxey–Riley for the memory term).
2. **Gap-independent transparency crossover Wo_c^↓ ≈ 0.116 α_p².** Evidence: Fig. 4 (exponent 2.08), check3 (independent of ε within 2%). Artefact check: brentq-refined roots, quadrature converged, exists for all α_p ≥ 8.6 and all β_p. Proposed mechanism, stated as interpretation: for Wo ≫ α_p the layer differs from the fluid only through the Darcy term, so the inertial (image) reflection scales as α_p²/Wo², and it is overtaken by the O(Wo⁻¹) viscous correction when Wo ∝ α_p². Support: Sherwood (2020) on unsteady flow at a porous wall (penetration and reflection governed by the same competition); Brinkman (1949). `\TODO` for an asymptotic proof.
3. **Dissipation peak at Wo ≈ α_p** (\hat γ_int up to 4× the rigid wall): energy dissipated by Darcy drag inside the layer when the oscillatory penetration depth reaches the Brinkman length. Evidence: Fig. 3. Support: Sherwood (2020). Hedged wording.
4. **Closure of the positive-added-mass window for α_p ≲ 6–9** — a direct consequence of 1 and 2 meeting; no extra reference needed beyond those of 1–2.
5. **Soft shells suppress near-wall damping and the crossover** — mechanism: flow through the shell weakens the scattered dipole (Debye–Bueche–Brinkman). Support: Brinkman (1949), Ollila et al. (2012). Evidence: Fig. 6, check2(c).

Each will be checked again in Pass 4 and recorded in `notes/key_findings.md`.

## 10. Proposed corrections to equations, data or figures

| # | Location | Fix | Verification |
|---|---|---|---|
| E1 | PF:93 | "The real part of 1/λ_f is δ_v" → "δ_v = 1/Re λ_f = √(2μ/ρω)" | check1 item 10 |
| E2 | Res:136–137 | "√(μ/ρω) ≈ 8.6 k_p/b" is δ_v/√2; write δ_v ≈ 12.2 k_p/b, or state the law only as Wo_c^↓ ≈ 0.116 α_p² | arithmetic |
| E3 | An:118, An:275 | "C → 0" → "the vortical scattered field C h_f is confined to a layer of thickness O(\|λ\|⁻¹)" | check1 (C = −3e^λ/2λ²) |
| E4 | An:236 (Remark 3) | weaken to "numerically consistent with the classical series through O(x³) for ε ≤ 4" | check2(b) |
| E5 | Res:211 | add Table (slip and β_s sensitivity, values from check2(c)) or delete the claim | check2(c) |
| E6 | Res:110 | "This is the frequency at which …" → "consistent with …" | – |
| D1 | Fig. 7 | add colour-bar label | – |
| D2 | Fig. 4 caption / text | add gap-independence of Wo_c^↓ (check3), optionally as an inset or one sentence | check3 |

No change to the solver, the computed data or the existing figures' numbers is needed.

## 11. Questions for the author

1. **γ clash:** rename the core ratio (γ = a/b → κ = a/b) or the damping (γ_int → ζ_int)? I recommend κ for the core ratio and keeping γ_int, which matches Zhang et al. (2023) and the AFM literature.
2. **Kernel and shell-coefficient symbols:** OK to rename h_j, i_j → \mathcal K_j, \mathcal I_j and shell coefficients E, F, G, H → E_1, E_2, G_1, G_2?
3. **New table** with core-slip and β_s sensitivity (computed in check2, ~6 rows)? It turns an unsupported sentence into evidence.
4. **Structure:** approve the 7-section plan in §8?
5. **Abstract and Conclusion:** keep as guide bullets (default) or write prose?
