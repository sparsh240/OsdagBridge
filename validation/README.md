# Validation artifacts

This folder keeps the real-PDF validation evidence for the report enhancements.

## Files

- `Report_after.pdf` / `Report_after.tex` — final v4 report generated after all fixes.
- `inputs.osi` — design inputs used for the final report.
- `submission/Report_After.pdf` — submission copy of the final report.
- `submission/Report_After.tex` — matching LaTeX source.
- `submission/inputs.osi` — matching input file.
- `Report_Before.pdf` — baseline report regenerated headlessly from original commit `d74f56d`.

## Key verified values

- Braking: `217.39 kN` for 8 m carriageway → 2 design lanes.
- UR chart: `1.92` girder, `0.94` deck, `0.86` cross bracing, `0.86` end diaphragms.
- Table 5.29 ED Moment: `kN-m` units; cross bracing and ED shear remain `kN`.
- Repeated longtable headers: 50 tables, 0 missing.
- Centrifugal load: `N/A` by design (no horizontal-curvature input).

See `docs/TECHNICAL_CHANGES.md` for the complete change log.
