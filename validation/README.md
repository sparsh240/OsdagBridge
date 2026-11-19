# Validation artifacts

This folder keeps the real-PDF validation evidence for the report enhancements.

## Files

- `Report_Before.pdf` / `Report_Before.tex` — baseline regenerated from the original
  commit `d74f56d` using `inputs.osi`.
- `Report_after.pdf` / `Report_after.tex` — legacy v4 after-report, retained for
  visual comparison. The final artifact is the v5 file below.
- `inputs.osi` — design inputs used for the final report.
- `submission/Report_After.pdf` — final v5 report, 71 pages.
- `submission/Report_After.tex` — matching LaTeX source, 50 long tables.
- `submission/inputs.osi` — copy of the final `inputs.osi`.

The final headless generation reuses the GUI-rendered figures from the previous
submission so that figure placement and page count remain unchanged.

## Key verified values

- Braking: `217.39 kN` for 8 m carriageway → 2 design lanes.
- Overall UR: `1.93` with governing fatigue stress `178.14 MPa`. The committed v4
  code produces the same values from this `inputs.osi`; the earlier `1.92` artifact
  came from a different input/UI state, not from a design-code change.
- Table 2.4: `12.65`; Table 2.7: `1390`, `8`, `420`, `18` in the mm-labelled columns.
- Table 3.6 seismic forces: `687.82 kN` longitudinal and transverse.
- Table 5.11 fatigue note extracts as `plate thickness > 25 mm`.
- Table 5.19 punching label extracts as `vRd,c`.
- Table 5.29 ED Moment: `kN-m`; cross bracing and ED shear remain `kN`.
- Table 7.1 crash barrier: `0.30228 m² × 25.00 m = 7.55707 m³`, qty `2`, total
  volume `15.11`, weights `18.89` / `37.79`.
- Repeated longtable headers: `50 / 50`; missing headers: `0`; repeated caption
  heads: `0`; continuation notes: `49`.
- Footer alignment: cover `Page 1 of 71`, TOC `Page 2 of 71`, last `Page 71 of 71`;
  TOC starts with `Executive Summary 3`.
- Centrifugal load: `N/A` by design (no horizontal-curvature input).

See `docs/TECHNICAL_CHANGES.md` for the complete change log.
