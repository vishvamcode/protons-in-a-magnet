# Project plan · Protons in a magnet

*Started Thu 8 Oct 2026. Last updated Sat 10 Oct 2026.*

## 1 · Goal

Build an OpenTOPAS (Geant4) model of a proton pencil beam in water, **validate** it against NIST PSTAR ranges, then
apply a uniform transverse magnetic field of 0.5 / 1.0 / 1.5 T and **measure** the lateral deflection and range
shortening of the Bragg peak. Compare three independent answers:

1. OpenTOPAS Monte Carlo (the "measurement" in this project)
2. My own model: Lorentz force + PSTAR stopping power, integrated as an ODE
3. Literature: Wolf & Bortfeld 2012 (analytical), Schellhammer et al. 2018 (film data, 1 T), Wang et al. 2021
   (FLUKA, 1.5 T)

**Why:** MRI-guided proton therapy needs to predict how the scanner's field bends the beam. PSI builds its
MRI-guided proton dose engine from TOPAS lookup tables of beam rotation angle vs water-equivalent depth at 0.5 and
1.5 T, 70-229 MeV (Duetschler et al., PMB 2023, doi:10.1088/1361-6560/acf90d). This project reproduces that physics
step with open tools. It builds on two things I have done before: tracking charged particles in a magnetic field
(ALICE) and comparing simulation with measurement (my f0(980) thesis).

**Deadline:** freeze **Fri 20 Nov 2026**.

## 2 · Tools

| Tool | Version | Used for |
|---|---|---|
| OpenTOPAS | **v4.3.0** | Monte Carlo transport |
| Geant4 | 11.4.2 + matching data sets (15 of 16; LEND not needed) | physics under OpenTOPAS |
| Docker | image `opentopas/opentopas:v4.3.0-geant4-11.4.2`, inside WSL2 Ubuntu 24.04 on Windows | runs OpenTOPAS without compiling it |
| Python | 3.11+ with numpy, scipy, pandas, matplotlib, pytest | analysis, ODE model, figures, tests |
| NIST PSTAR | liquid water tables | reference ranges and stopping powers |
| git + GitHub | public repo | history and sharing |

## 3 · Timeline so far

| Date | What happened | Stage |
|---|---|---|
| **Thu 8 Oct** | Chose this project; wrote this plan, the stage list and the working rules | Plan |
| **Fri 9 Oct** | Installed WSL2 + Docker + the OpenTOPAS image; downloaded the Geant4 data (3.4 GB). Smoke test with the bundled `Dose.txt` example passed. First own run: 150 MeV, 100,000 protons, Bragg peak at 156.75 mm, R80 158.63 mm, 0.29 % statistical uncertainty at the peak, 54 s on 12 threads | **1 and 2 done** (planned for 12-18 Oct) |
| **Sat 10 Oct** | Ran 70, 100, 150, 200 and 230 MeV with an ideal beam (0 % energy spread). R80 is 0.22-1.45 mm (about +0.5 %) deeper than the reference range at every energy, inside the 1 % threshold. Wrote the analysis package (`analysis/`) with tests, made Fig 1 and Fig 2, put the project on GitHub. Prepared a second sweep with a realistic 1 % energy spread | **3 runs done**; 3b prepared |
| **Sun 11 Oct** (next) | Run the 1 % energy-spread sweep and compare it with the ideal beam. Download the PSTAR table directly from NIST and replace the provisional reference values. Answer the Stage 1-3 quiz. Start the reading for `docs/targets.md` (task 0b) | 3b, 3 close-out |

## 4 · Stages

Each stage ends with a review: a 5-bullet summary and four questions (physics, code reading, "what would break
if…", and a number with its uncertainty), answered without notes and logged in `docs/learning-log.md`. Two or more
wrong answers means revisiting before moving on.

### Plan

| # | Task | Done when | Status |
|---|---|---|---|
| 0a | Physics primer: Bethe-Bloch, range straggling, multiple Coulomb scattering, R80 vs CSDA range, Lorentz force on a slowing proton | 1 page of notes in my own words | to do |
| 0b | Read Duetschler 2023 (abstract + methods), Schellhammer 2018 (arXiv 1709.00373), Wang 2021 (PMC8369236), Wolf & Bortfeld 2012 | `docs/targets.md` lists ≥ 3 target numbers with sources | started; 1 of 4 filled |
| 0c | Choose the install route | decision written in README | **done 9 Oct** (WSL2 + Docker) |

### Build

| # | Stage | Planned | Done when | Status |
|---|---|---|---|---|
| 1 | **Install + smoke test**: OpenTOPAS runs the bundled `Dose.txt` example | 12-18 Oct | example output exists; versions in README | **done 9 Oct** |
| 2 | **First Bragg peak**: 40 × 40 × 40 cm water box, 150 MeV pencil beam, depth dose in 0.5 mm bins with mean + standard deviation | by 18 Oct | curve plotted; statistical uncertainty < 1 % in the peak bins | **done 9 Oct** (0.29 %) |
| 3 | **Validation sweep**: 70, 100, 150, 200, 230 MeV. R80, R90, peak depth, distal fall-off (R20 − R80); compare R80 with PSTAR | 19-25 Oct | **Fig 1** + table; \|R80 − PSTAR\| ≤ 1 mm or ≤ 1 % of range, or the gap explained, never tuned | runs and figures **done 10 Oct**; open: PSTAR from NIST directly, test the ICRU 90 explanation of the +0.5 % offset |
| 3b | **Realistic beam**: the same sweep with a 1 % (1σ) energy spread | added 10 Oct | effect on peak height, R80 and fall-off quantified against the ideal beam | run files ready; run on 11 Oct |
| ⛔ | **GATE, Sun 25 Oct**: no validated Fig 1 → switch to the backup project (FLASH data re-analysis, Python only) and continue this one after the application | | decision logged | on track |
| 4 | **Field on**: `DipoleMagnet` on the phantom, field ⟂ beam, 0.5 / 1.0 / 1.5 T at 100, 150, 200, 230 MeV. Score 3D dose; dose-weighted lateral centroid per depth slice → trajectory x(z) | 26 Oct - 1 Nov (can start once Stage 3 is closed) | **Fig 3**: trajectories; table of lateral shift at the Bragg peak and range shortening | not started |
| 5 | **My own model**: direction from dp⃗/ds = q (v̂ × B⃗), magnitude from PSTAR dE/dx, integrated with `scipy.integrate.solve_ivp`. Tests: B = 0 gives a straight line; radius at constant energy matches p/(qB) | 2-8 Nov | **Fig 4**: TOPAS vs ODE vs Wolf-Bortfeld vs Wang 2021 / Schellhammer 2018. Agreement stated in mm | not started |
| 6 | **Lookup table**: incremental rotation angle vs water-equivalent depth, Duetschler-style | by 8 Nov | **Fig 5** | not started |
| 7 | *(stretch, only if 1-6 are done by Thu 12 Nov)* `ProtonLET` along depth, 0 T vs 1.5 T | 12-15 Nov | Fig 6 | optional |

### Review

| # | Task | Planned | Done when |
|---|---|---|---|
| 8 | Clean repo: one command regenerates all figures from saved results; tests pass; seeds fixed | 9-13 Nov | `python -m analysis.figures` works on a fresh clone |
| 9 | 2-page write-up: question, method, validation, results, **limitations**, references | by 15 Nov | `docs/writeup.md` + PDF |
| 10 | README with the results figure at the top, how to reproduce, versions | ongoing | renders on GitHub |
| 11 | Explain-it-all session: mock interview on every file and figure, answered without notes | 16-19 Nov | every "I don't know" fixed before the freeze |
| 12 | Freeze: tag `v1.0`, add to CV | Fri 20 Nov | tag exists, link works logged out |

## 5 · Milestones

| Date | Milestone | Status |
|---|---|---|
| Sun 11 Oct | Plan done, targets started | in progress |
| Sun 18 Oct | First Bragg peak | **reached 9 Oct** |
| **Sun 25 Oct** | **Fig 1 validated (gate)** | runs pass; reference to be confirmed from NIST |
| Sun 1 Nov | Fig 3 (deflection) | |
| Sun 8 Nov | Figs 4 + 5 | |
| Sun 15 Nov | Write-up draft | |
| **Fri 20 Nov** | **Freeze** | |

## 6 · Definition of done

- [ ] Fig 1: R80 for 5 energies agrees with PSTAR within the threshold, or the gap is explained (*runs pass; PSTAR still provisional*)
- [ ] Fig 4: lateral Bragg-peak shift at 1.5 T, TOPAS vs my ODE model, agreement stated in mm, plus the literature points with their sources
- [ ] Every reference number in `data/reference/` has a `SOURCE.md` (citation, URL, date accessed, page/figure)
- [x] `pytest` passes; figures regenerate from one command
- [ ] 2-page write-up with a limitations section
- [ ] `docs/learning-log.md` has a review quiz for every stage, answered by me
- [ ] I can explain every line of every file and every figure without notes
- [x] Repo public on GitHub (*10 Oct*); tag `v1.0` and CV link at the freeze

## 7 · Risks

| Risk | Sign | Response |
|---|---|---|
| Install takes > 1 week | no `Dose.txt` run by Wed 14 Oct | *Resolved: installed 9 Oct* |
| Runs too slow | > 30 min per run | fewer histories for sweeps, more only for final figures; coarser lateral bins. *So far about 1 min per run* |
| Mismatch with PSTAR I can't explain | > 2 mm | check physics list, energy spread, bin size *before* changing anything. *Current offset ≤ 1.45 mm, ICRU 90 hypothesis* |
| Courses squeeze time | 2 stages late | drop Stage 7, then Stage 6. Stages 1-5 are the minimum |
| I can't explain a part | weak quiz answer | stop building; rework the explanation first |
