# Protons in a magnet

**How much does an MRI scanner's magnetic field bend a proton therapy beam?** This project answers that with a
Monte Carlo simulation (OpenTOPAS / Geant4). First it shows that the simulated beam stops where reference data say
it should. Then it turns on a magnetic field and measures how far the Bragg peak moves.

![Depth-dose curves for 70 to 230 MeV protons in water](figures/fig1_depth_dose_all_energies.png)

> **Current result (10 Oct 2026):** at five clinical energies from 70 to 230 MeV, the simulated proton range lands
> within **0.6 %** of the NIST PSTAR reference. That is inside the 1 % acceptance threshold set before the runs.
> The magnetic-field stage starts next.

**Contents:** [Background](#background) · [Method](#method) · [Results](#results) · [Reproduce](#reproduce) ·
[Repository layout](#repository-layout) · [Roadmap](#roadmap) · [Versions](#versions)

## Background

Proton therapy puts most of its dose in a sharp peak (the **Bragg peak**) at a depth set by the beam energy, and
almost nothing beyond it. That makes it precise, but only if you know exactly where the protons stop. Treating
inside an MRI scanner would let clinicians *see* the tumour during treatment. However, the scanner's 0.5-1.5 T
field bends the charged proton beam sideways and shifts the peak. Treatment planning has to predict that shift.

This project rebuilds that prediction with open tools, step by step:

1. **Validate** a proton pencil beam in water against reference ranges (NIST PSTAR).
2. **Deflect** it with a uniform transverse field of 0.5, 1.0 and 1.5 T and measure the lateral shift and range
   change of the Bragg peak.
3. **Cross-check** against an independent Lorentz-force model and published results (Wolf & Bortfeld 2012,
   Schellhammer et al. 2018, Wang et al. 2021).

The approach follows the lookup-table method PSI uses for its MRI-guided proton dose engine (Duetschler et al.,
*Phys. Med. Biol.* 2023, doi:10.1088/1361-6560/acf90d). Full plan and timeline: [PROJECT_PLAN.md](PROJECT_PLAN.md).

## Method

| | |
|---|---|
| **Geometry** | 40 × 40 × 40 cm block of `G4_WATER` in vacuum; dose scored in 800 depth slices of 0.5 mm |
| **Beam** | proton pencil beam, Gaussian spot σ = 3 mm, parallel, on the phantom axis. Stage 3: no energy spread (ideal beam, clean comparison with PSTAR). Stage 3b: 1 % (1σ) energy spread, closer to a clinical beam |
| **Physics** | OpenTOPAS default list: `g4em-standard_opt4`, `g4h-phy_QGSP_BIC_HP`, `g4decay`, `g4ion-binarycascade`, `g4h-elastic_HP`, `g4stopping` |
| **Statistics** | 100,000 protons per run, fixed random seed, 12 threads, about 1 minute per run |
| **Range metrics** | R80, R90 and R20 (depths beyond the peak where the dose falls to 80/90/20 % of its maximum), found by linear interpolation between slices; distal fall-off = R20 − R80 |
| **Uncertainty** | OpenTOPAS reports the standard deviation per proton; the uncertainty of the summed dose is that × √N |

Run files: [topas/runs/](topas/runs/). Analysis code: [analysis/](analysis/), with tests in [tests/](tests/).

## Results

### Stage 3: range validation (10 Oct 2026)

![R80 minus reference range at five energies](figures/fig2_range_validation.png)

| Energy (MeV) | Peak depth (mm) | R80 (mm) | PSTAR range (mm) | R80 − PSTAR (mm) | Fall-off R20−R80 (mm) | Stat. unc. at peak |
|---|---|---|---|---|---|---|
| 70 | 40.75 | 41.02 | 40.80 | +0.22 (0.5 %) | 0.72 | 0.21 % |
| 100 | 76.75 | 77.59 | 77.18 | +0.41 (0.5 %) | 1.23 | 0.24 % |
| 150 | 156.75 | 158.63 | 157.70 | +0.93 (0.6 %) | 2.30 | 0.29 % |
| 200 | 258.25 | 260.70 | 259.60 | +1.10 (0.4 %) | 3.71 | 0.35 % |
| 230 | 327.75 | 330.95 | 329.50 | +1.45 (0.4 %) | 4.63 | 0.39 % |

100,000 protons per energy. Full table: [results/stage3/summary.csv](results/stage3/summary.csv).

**What the numbers say**

- **Every energy passes** the threshold of ≤ 1 mm or ≤ 1 % of the range.
- **The offset is the same in percent (about +0.5 %), not in millimetres.** A geometry or binning error would shift
  every energy by the same number of millimetres. A small difference in the stopping power of water scales with
  the distance travelled. A likely cause (hypothesis, not yet tested): Geant4's `g4em-standard_opt4` uses ICRU
  Report 90 water data (mean excitation energy 78 eV), while PSTAR uses 75 eV. A rough Bethe-formula estimate gives
  a range increase of about 0.5 %.
- **The fall-off grows with energy** (0.7 mm at 70 MeV to 4.6 mm at 230 MeV, about 1.5 % of the range), as expected
  from range straggling.
- **The peak stands out less at high energy** (peak-to-entry ratio 5.7 at 70 MeV, 4.4 at 230 MeV), because more
  protons are lost to nuclear reactions on the longer path.

**Caveat:** the PSTAR values were read from a secondary table and are provisional until the NIST table is
downloaded directly ([data/reference/SOURCE.md](data/reference/SOURCE.md)).

## Reproduce

You need Docker and the Geant4 11.4.2 data sets (3.4 GB). Step-by-step guide for Windows (WSL2 + Docker):
[docs/setup-windows.md](docs/setup-windows.md).

```bash
git clone https://github.com/vishvamcode/protons-in-a-magnet.git && cd protons-in-a-magnet
bash scripts/get_g4data.sh              # once: Geant4 data into ~/G4DATA
pip install -r requirements.txt

scripts/run.sh topas/runs/E150_B0.txt   # one run -> results/E150_B0/
scripts/run_sweep.sh                    # stage 3: five energies -> results/stage3/, then table + figures
scripts/run_sweep_spread.sh             # stage 3b: same with 1 % energy spread -> results/stage3_spread1/

python -m analysis.summarize            # table from saved results (no simulation needed)
python -m analysis.figures              # figures from saved results
pytest -q                               # tests
```

Every run uses a fixed random seed, so it gives the same numbers each time.

## Repository layout

```
topas/runs/        OpenTOPAS parameter files: E{MeV}_B{tesla}.txt (_s1 = 1 % energy spread)
scripts/           run.sh (one run in Docker), run_sweep*.sh, get_g4data.sh, plot_depth_dose.py
analysis/          io.py (read TOPAS output), metrics.py (R80 etc.), reference.py, summarize.py, figures.py
data/reference/    reference ranges, each with a SOURCE.md
results/stage3/    raw OpenTOPAS output of the validation sweep + summary.csv
figures/           figures made by analysis/figures.py
tests/             pytest on synthetic curves with known answers
docs/              setup guide, project log, targets, learning log
```

## Roadmap

| Stage | What | Status |
|---|---|---|
| 1 | Install OpenTOPAS (Docker), smoke test | ✅ 9 Oct |
| 2 | First Bragg peak, 150 MeV | ✅ 9 Oct |
| 3 | Range validation, 70-230 MeV, against PSTAR | ✅ runs pass (10 Oct); PSTAR to be confirmed from NIST |
| 3b | Same with a realistic 1 % energy spread | ⏳ run files ready |
| 4 | Magnetic field on: 0.5 / 1.0 / 1.5 T, lateral shift and range change | planned from late Oct |
| 5 | Own Lorentz-force ODE model vs simulation vs literature | planned |
| 6 | Rotation-angle lookup table (PSI-style) | planned |

Day-by-day notes: [docs/log.md](docs/log.md).

## Versions

OpenTOPAS 4.3.0 · Geant4 11.4.2 (geant4-11-04-patch-02) · Docker image `opentopas/opentopas:v4.3.0-geant4-11.4.2`
(published 2026-09-18) · Python 3 with numpy, scipy, pandas, matplotlib, pytest.

## About

By Vishvam (BSc Physics, Lund University; MSc Particles and Cosmos, Stockholm University), as a portfolio project
in medical physics. Built with help from Claude (Anthropic) for code and set-up; the physics choices, runs and
interpretation are documented in [docs/log.md](docs/log.md). Licence: MIT.
