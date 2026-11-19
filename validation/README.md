# Validation and submission artifacts

Repository: <https://github.com/sparsh240/OsdagBridge>

The report scripts live under `src/osdagbridge/core/reports/`. This folder keeps
the delivered PDF evidence for the report enhancements.

## Deliverable files

- `submission/Report_Before.pdf` — original output, regenerated from baseline
  commit `d74f56d` using the same inputs.
- `submission/Report_After.pdf` — final enhanced output (77 pages).
- `submission/TECHNICAL_CHANGES.md` — brief technical report covering code and
  LaTeX changes, altered report-generator files, the centralized styling module,
  design rationale, visual enhancements and verification.
- `submission/inputs.osi` — design inputs used for the final report.

The legacy v4 report, duplicate baseline copies and generated LaTeX source files
were removed so the submission contains only the requested reports and their
supporting files.

## Key verified values

- Braking: `217.39 kN` for 8 m carriageway → 2 design lanes.
- Overall UR: `1.93` with governing fatigue stress `178.14 MPa`. The committed v4
  code produces the same values from this `inputs.osi`; the earlier `1.92`
  artifact came from a different input/UI state, not from a design-code change.
- Table 2.4: `12.65`; Table 2.7: `1390`, `8`, `420`, `18` in the mm-labelled columns.
- Table 3.6 seismic forces: `687.82 kN` longitudinal and transverse.
- Table 5.11 fatigue note extracts as `plate thickness > 25 mm`.
- Table 5.19 punching label extracts as `vRd,c`.
- Table 5.29 ED Moment: `kN-m`; cross bracing and ED shear remain `kN`.
- Table 7.1 crash barrier: `0.30228 m² × 25.00 m = 7.55707 m³`, qty `2`, total
  volume `15.11`, weights `18.89` / `37.79`.
- Repeated longtable headers: `50 / 50`; missing headers: `0`; repeated caption
  heads: `0`; continuation notes: `49`.
- Footer alignment: cover `Page 1 of 77`, TOC `Page 2 of 77`, last `Page 77 of 77`;
  TOC starts with `Executive Summary 3`.
- Footer separation: full `pdftotext -bbox` scan reports `0` body/footer word-box
  intersections; `* Software default value` is clear of body text.
- Centrifugal load: `N/A` by design (no horizontal-curvature input).

See `docs/TECHNICAL_CHANGES.md` for the detailed change log and
`submission/TECHNICAL_CHANGES.md` for the brief deliverable report.
