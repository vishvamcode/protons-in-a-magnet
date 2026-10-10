# Learning log

Quiz questions at the end of each stage, my answers, and the grade. Rules: PROJECT_PLAN.md, section 4.

## Stage 1-2 · Install and first Bragg peak (2026-10-09)
1. Physics: why does the dose peak sharply near the end of the range instead of being highest where the protons enter?
   - My answer: *(pending)*

## Stage 3 and 3b · Validation sweep and energy spread (2026-10-10)
1. Physics: why does a higher mean excitation energy I make the protons go deeper?
2. Code: in `analysis/metrics.py`, what does `distal_depth_mm(dd, 0.8)` return, and why does it look beyond the peak?
3. What would break if we compared R80 with PSTAR using the 1 % energy-spread beam instead of the ideal beam?
4. Number: R80 − PSTAR at 150 MeV, and its statistical uncertainty?
- Quiz taught, not tested (2026-10-10): I asked for the answers after one reminder of the rule; Claude explained all four in the project thread. Re-quiz before the explain-it-all session (task 11).

## Stage 4 and 5 · Field on, own model (2026-10-10)
1. Physics: why does most of the sideways bending happen in the last few centimetres?
2. Code: in `analysis/lorentz_ode.py`, what does `curvature = 1.0 / radius_mm(t, field_T)` represent, and which equation uses it?
3. What would break if the field pointed along the beam (z) instead of across it (y)?
4. Number: sideways shift of the Bragg peak at 230 MeV and 1.5 T, and how well does the model agree?
- Quiz taught, not tested (2026-10-10): I asked for the answers after one reminder of the rule; Claude explained all four in the project thread. Re-quiz before the explain-it-all session (task 11).
