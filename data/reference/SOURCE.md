# Reference data: sources

## `pstar_water_liquid.txt` (primary reference)

| Field | Value |
|---|---|
| Quantity | stopping powers (electronic, nuclear, total; MeV cm²/g), CSDA and projected range (g/cm²) of protons in liquid water, 1 keV to 10 GeV |
| Source | NIST PSTAR database, material "Water, Liquid": https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html (M. J. Berger, J. S. Coursey, M. A. Zucker, J. Chang, ESTAR, PSTAR and ASTAR, NIST) |
| Date accessed | 2026-10-10 (table saved by hand from the web page; the build machine cannot reach NIST) |
| Used in | `analysis/reference.py`: CSDA range at the validation energies (compared with R80) and the stopping power for the Lorentz-force model |
| Checks | 132 rows; total = electronic + nuclear within 0.06 %; projected/CSDA equals the detour column within 0.0007 |
| Note | Ranges at energies between grid points (here only 230 MeV) are the tabulated range at 225 MeV plus the integral of 1/S from 225 to 230 MeV. The table gives 4 significant figures, so ranges carry about ±0.05 mm of rounding |

CSDA ranges used for Stage 3 (mm, density 1 g/cm³): 70 MeV 40.80 · 100 MeV 77.18 · 150 MeV 157.70 · 200 MeV 259.60 · 230 MeV 329.47.

## History

On 9-10 Oct the reference values were first read from the UCL Proton Beam Therapy wiki
(https://www.hep.ucl.ac.uk/pbt/wiki/Proton_ranges), which quotes PSTAR. They agree with the NIST table to 0.03 mm
(the UCL 230 MeV value was 329.50 mm), so the Stage 3 conclusions did not change. The UCL file was removed.

---

# Literature: magnetic-field deflection

## `schellhammer2018_table_d5.csv`

| Field | Value |
|---|---|
| Citation | S. M. Schellhammer, S. Gantz, A. Lühr, B. M. Oborn, M. Bussmann, A. L. Hoffmann, "Dosimetric evidence confirms computational model for magnetic field induced dose distortions of therapeutic proton beams", arXiv:1709.00373 (published in Phys. Med. Biol. 2018) |
| URL | https://arxiv.org/abs/1709.00373 (full text: https://arxiv.org/pdf/1709.00373) |
| Date accessed | 2026-10-10 |
| Table | Appendix D, Table D.5: lateral deflection Δy80 and range retraction ΔR80, measured (film) and simulated (Geant4) |
| Set-up | PMMA phantom, ρ = 1.186 g/cm³, 30 × 15 × 3 cm³, in the gap of a permanent magnet, B0 = 0.95 T (not uniform; fringe field upstream). Energies are nominal; fitted mean energies are 1-2 MeV higher (their Table B.2) |
| How it is used here | A check of the Lorentz-force model (`analysis/lorentz_ode.py`) with the stopping power of water scaled by an assumed PMMA relative stopping power of 1.165 (typical literature value, not taken from this paper; UNVERIFIED) and B = 0.95 T uniform in the phantom only. Not a like-for-like comparison: their field also acts in air before the phantom |

## `wang2021_table2_depth_shortening_1p5T.csv`

| Field | Value |
|---|---|
| Citation | X. Wang, H. Pan, Q. Cheng, X. Wang, W. Xu, "Dosimetric Deviations of Bragg-Peak Position Shifts in Uniform Magnetic Fields for Magnetic Resonance Imaging-Guiding Proton Radiotherapy: A Monte Carlo Study", Front. Public Health 9:641915 (2021), doi:10.3389/fpubh.2021.641915 |
| URL | https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2021.641915/pdf |
| Date accessed | 2026-10-10 |
| Table | Table 2, 1.5 T column: shortening of the Bragg-peak depth in water (FLUKA 2011.2x, ideal uniform field, 20 × 20 × 35 cm³ water phantom). Values are given to 0.2 mm |
| Note | The paper's lateral deflections are only shown graphically (its Fig. 2B), so they are not used |
