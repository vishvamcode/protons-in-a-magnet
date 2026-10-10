# Reference ranges: source

**File:** `pstar_range_water_ucl.csv`

| Field | Value |
|---|---|
| Quantity | proton range in liquid water (mm), 70-230 MeV |
| Original source | NIST PSTAR database, material "Water, Liquid" (https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html) |
| Where these numbers were read | UCL Proton Beam Therapy wiki, "Proton ranges": https://www.hep.ucl.ac.uk/pbt/wiki/Proton_ranges |
| Date accessed | 2026-10-09 (150 MeV) and 2026-10-10 (70, 100, 200, 230 MeV) |
| Definition on that page | "projected range" in g/cm², converted to mm with water density 1 g/cm³ |

**Status: PROVISIONAL.** These values are second-hand. The page calls them "projected range", which can differ
slightly from the CSDA range. NIST's site could not be reached from the build environment on these dates.
To do (Stage 3): download the PSTAR table for liquid water directly from NIST, save it here as `pstar_water.txt`
with its own entry in this file, and switch `analysis/reference.py` to it.
