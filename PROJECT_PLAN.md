# PROJECT_PLAN · Protons in a magnet

*Project 1 of 04-portfolio-projects.md. Written 2026-10-08. Drop this file into the repo root next to CLAUDE.md.*

## 1 · Goal

Build an OpenTOPAS (Geant4) model of a proton pencil beam in water, **validate** it against NIST PSTAR ranges, then apply a uniform transverse magnetic field of 0.5 / 1.0 / 1.5 T and **measure** the lateral deflection and range shortening of the Bragg peak. Compare three independent answers:

1. OpenTOPAS Monte Carlo (the "measurement" in this project)
2. My own model: Lorentz force + PSTAR stopping power, integrated as an ODE
3. Literature: Wolf & Bortfeld 2012 (analytical), Schellhammer et al. 2018 (film data, 1 T), Wang et al. 2021 (FLUKA, 1.5 T)

**Why:** PSI builds its MRI-guided proton dose engine from TOPAS lookup tables of beam rotation angle vs water-equivalent depth at 0.5 / 1.5 T, 70-229 MeV (Duetschler…Zhang, PMB 2023, doi:10.1088/1361-6560/acf90d). This project reproduces that physics step with open tools, and it uses my two strongest skills: tracking charged particles in a field (ALICE) and comparing simulation with measurement (my f0(980) thesis).

**Hard deadline:** freeze **Fri 20 Nov 2026**. The ETH application closes Mon 30 Nov 2026, 11:59 CET.

## 2 · Tools

| Tool | Version | Used for | Where it runs |
|---|---|---|---|
| OpenTOPAS | **v4.3.0** | Monte Carlo transport | Claude Code (install, runs) |
| Geant4 | 11.4.2 (or 11.3.2) + matching data sets | under OpenTOPAS | Claude Code |
| Docker (preferred) | image `opentopas/opentopas:v4.3.0-geant4-11.4.2` | avoids a native build | Claude Code |
| Python | 3.11+ with numpy, scipy, pandas, matplotlib, pytest | analysis, ODE model, figures | Claude Code (code) + Claude app (understanding) |
| NIST PSTAR | web tables, liquid water | ranges + dE/dx | saved to `data/reference/` |
| git + GitHub | any | history, public repo | Claude Code |

## 3 · Repo layout

```
protons-in-a-magnet/
├── CLAUDE.md               # rules for Claude Code (20-60-20)
├── PROJECT_PLAN.md         # this file
├── README.md               # what, why, how to reproduce, results
├── topas/
│   ├── common/             # world, water phantom, beam, physics, scorers (included files)
│   └── runs/               # one small file per run: E{energy}_B{field}.txt
├── scripts/                # run_sweep.sh etc.
├── analysis/               # Python package
│   ├── io.py               # read TOPAS CSV output
│   ├── metrics.py          # R80, R90, peak depth, distal fall-off, lateral centroid
│   ├── lorentz_ode.py      # my own deflection model
│   ├── reference.py        # load PSTAR + digitised literature points
│   └── figures.py          # one function per figure
├── data/reference/         # PSTAR tables, digitised literature, each with SOURCE.md
├── results/                # raw TOPAS output (git-ignored if large)
├── figures/                # final PNG/PDF
├── tests/                  # pytest on synthetic curves
└── docs/
    ├── targets.md          # the numbers I'm trying to reproduce, with sources
    ├── learning-log.md     # quiz questions + my answers, per stage
    └── writeup.md          # 2-page write-up
```

## 4 · Stages (20-60-20)

*Chat = my Claude Project. CC = Claude Code in this repo. Each stage ends with a quiz (see CLAUDE.md) logged in `docs/learning-log.md`.*

### 20 · PLAN (Thu 8 - Sun 11 Oct)

| # | Task | Where | Done when |
|---|---|---|---|
| 0a | Physics primer: Bethe-Bloch, range straggling, multiple Coulomb scattering, R80 vs CSDA range, Lorentz force on a slowing proton | Chat | 1 page of notes in my own words |
| 0b | Read Duetschler 2023 (abstract + methods), Schellhammer 2018 (arXiv 1709.00373), Wang 2021 (PMC8369236), Wolf & Bortfeld 2012 | Chat | `docs/targets.md` lists ≥ 3 target numbers with sources |
| 0c | Choose install route for my OS (Docker vs native) | Chat → CC | decision written in README |

### 60 · BUILD

| # | Stage | Dates | Where | Done when |
|---|---|---|---|---|
| 1 | **Install + smoke test**: OpenTOPAS runs the bundled `Dose.txt` example | Mon 12 - Sun 18 Oct | CC | example output file exists; versions noted in README |
| 2 | **First Bragg peak**: 40×40×40 cm water box, 150 MeV pencil beam along z, depth-dose in 0.5 mm bins, scorer reports mean + standard deviation | by Sun 18 Oct | CC | curve plotted; statistical uncertainty < 1% in the peak bins |
| 3 | **Validation sweep**: 70, 100, 150, 200, 230 MeV. Compute R80, R90, peak depth, distal fall-off (R80-R20). Compare R80 with PSTAR CSDA range | Mon 19 - **Sun 25 Oct** | CC (runs + code), Chat (explain any mismatch) | **Fig 1** + table. |R80 − CSDA| ≤ 1 mm or ≤ 1% of range (my threshold); if not, explained, not tuned |
| ⛔ | **GATE, Sun 25 Oct:** no validated Fig 1 → switch the application project to Project 2 (FLASH, Python-only) and continue this one after 30 Nov | | | decision logged |
| 4 | **Field on**: `DipoleMagnet` on the phantom, field ⟂ beam, 0.5 / 1.0 / 1.5 T at 100, 150, 200, 230 MeV. Score 3D dose; take the dose-weighted lateral centroid per depth slice → trajectory x(z) | Mon 26 Oct - Sun 1 Nov | CC | **Fig 2**: trajectories; table of lateral shift at the Bragg peak + range shortening |
| 5 | **My own model**: direction from dp⃗/ds = q (v̂ × B⃗) (the Lorentz force per unit path length), magnitude from from PSTAR dE/dx, integrated with `scipy.integrate.solve_ivp`. Unit tests: B = 0 gives a straight line; the radius at constant energy matches p/(qB) | Mon 2 - Sun 8 Nov | Chat (derive on paper first) → CC (code + tests) | **Fig 3**: TOPAS vs ODE vs Wolf-Bortfeld vs Wang 2021 / Schellhammer 2018 points. Agreement stated in mm |
| 6 | **Lookup table**: incremental rotation angle vs water-equivalent depth, Duetschler-style | by Sun 8 Nov | CC | **Fig 4** |
| 7 | *(stretch, only if 1-6 are done by Thu 12 Nov)* `ProtonLET` along depth, 0 T vs 1.5 T | Thu 12 - Sun 15 Nov | CC | Fig 5 |

### 20 · REVIEW (Mon 9 - Fri 20 Nov)

| # | Task | Where | Done when |
|---|---|---|---|
| 8 | Clean repo: one command regenerates all figures from saved results; tests pass; seeds fixed | CC | `python -m analysis.figures` works on a fresh clone |
| 9 | 2-page write-up: question, method, validation, results, **limitations**, references | Chat | `docs/writeup.md` + PDF |
| 10 | README with results figure at the top, how to reproduce, versions | CC + Chat | renders on GitHub |
| 11 | **Explain-it-all session**: Claude interviews me on every file and figure; I answer without notes | Chat | all answers logged; any "I don't know" fixed before freeze |
| 12 | Freeze: tag `v1.0-eth`, make repo public, add to CV + motivation letter | CC | tag exists, link works logged out |

## 5 · Milestones

| Date | Milestone | Also feeds |
|---|---|---|
| Sun 11 Oct | Plan done, targets written | - |
| Sun 18 Oct | First Bragg peak | Almhagen / Dasu follow-up email (file 03) |
| **Sun 25 Oct** | **Fig 1 validated (gate)** | Motivation letter v1 can mention the project as "in progress" |
| Sun 1 Nov | Fig 2 (deflection) | eApply opens 1 Nov: enter referees the same day (file 02) |
| Sun 8 Nov | Figs 3 + 4 | CV v2 |
| Sun 15 Nov | Write-up draft | Letter v2 |
| **Fri 20 Nov** | **Freeze, repo public** | Final letter + CV (file 02: submit by Wed 25 Nov) |

## 6 · Definition of done

- [ ] Fig 1: R80 for 5 energies agrees with PSTAR CSDA range within the threshold, or the gap is explained
- [ ] Fig 3: lateral Bragg-peak shift at 1.5 T, TOPAS vs my ODE model, agreement stated in mm, plus the literature points with their sources
- [ ] Every reference number in `data/reference/` has a `SOURCE.md` (citation, URL, date accessed, page/figure)
- [ ] `pytest` passes; figures regenerate from one command
- [ ] 2-page write-up with a limitations section
- [ ] `docs/learning-log.md` has a quiz for every stage, answered by me
- [ ] **I can explain every line of every file and every figure without notes**
- [ ] Repo public, tagged `v1.0-eth`, linked in CV

## 7 · Risks

| Risk | Sign | Response |
|---|---|---|
| Install takes > 1 week | no `Dose.txt` run by Wed 14 Oct | Use the Docker image; if that fails, Geant4's `hadrontherapy` example |
| Runs too slow on laptop | > 30 min per run | fewer histories for sweeps, more only for final figures; coarser lateral bins |
| Mismatch with PSTAR I can't explain | > 2 mm | check the physics list, beam energy spread, scoring bin size *before* changing anything |
| Courses squeeze time | 2 stages late | drop Stage 7, then Stage 6. Stages 1-5 are the minimum |
| I can't explain a part | quiz answer weak | stop building; rework the explanation in chat first |
