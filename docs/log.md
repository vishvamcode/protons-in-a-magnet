# Project log

Newest first. Each entry: what was done, the result, and anything that went wrong.

## 2026-10-10 · Stage 3b set up: realistic energy spread
- Decision (Vishvam, 10 Oct): also model a realistic beam with an energy spread. Kept the 0 % runs as the clean
  comparison with PSTAR and added `E*_B0_s1.txt` with `u:So/Beam/BeamEnergySpread = 1.0` (percent, 1σ; all else equal).
- Expected effect: R80 and the peak barely move; the peak gets lower and broader and R20−R80 grows, most at low
  energy where range straggling is small. Runs pending (`scripts/run_sweep_spread.sh`).

## 2026-10-10 · Stage 3 validation sweep
- Ran 70, 100, 150, 200, 230 MeV (100,000 protons each, seed 1, 12 threads, about 1 minute per energy).
- R80 is 0.22 to 1.45 mm deeper than the PSTAR range (0.42 to 0.59 %), inside the ±1 % acceptance band at every energy
  (`results/stage3/summary.csv`, `figures/fig2_range_validation.png`).
- The offset is systematic, about +0.5 % at every energy. Hypothesis (untested): Geant4's `g4em-standard_opt4` uses
  ICRU Report 90 water data (the log prints "Use ICRU90 data 1"), with a mean excitation energy of 78 eV, while
  PSTAR uses 75 eV. A rough Bethe-formula estimate (stopping number about 8 at 150 MeV, dI/I = 4 %) gives a range
  increase of about 0.5 %, the size seen. To test: rerun with ICRU 90 switched off.
- The quick plot script on the PC printed "0.00 %" uncertainty because an outdated copy was used; the corrected
  calculation (std × √N) is in `analysis/io.py`: 0.21 to 0.39 % at the peaks.
- Reference values are provisional (taken from the UCL table that quotes PSTAR); see `data/reference/SOURCE.md`.

## 2026-10-09 · Install (Stage 1) and first Bragg peak (Stage 2)
- Installed WSL + Docker + OpenTOPAS 4.3.0 image on Windows; downloaded 15 of 16 Geant4 data sets (3.4 GB; LEND not needed).
- Smoke test: OpenTOPAS `examples/Scoring/Dose.txt` ran (100,000 protons, about 1 s, no errors).
- First run `E150_B0.txt`: Bragg peak at 156.75 mm, R80 158.63 mm, 54 s on 12 threads.
- Problems fixed: placeholder path typed literally; download script hid errors; `~/G4DATA` owned by root;
  uncertainty formula misread (TOPAS `Standard_Deviation` is per history).
