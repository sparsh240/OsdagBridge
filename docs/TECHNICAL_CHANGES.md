# Technical Changes — OsdagBridge PDF Report Enhancements

**Date:** 2026-11-20  
**Status:** Phase 6 packaging  
**Baseline report:** `validation/Report_after.pdf` (v4)

## 1. Objective

Improve the clarity of the generated OsdagBridge PDF report without changing the
design calculations. The implementation intentionally reuses existing report data
and keeps the changes small and review-friendly for a FOSSEE internship deliverable.

## 2. What changed

| Area | Before | After |
|---|---|---|
| §3 braking force | Blank in vehicle rows; `N/A` in summary row | `217.39 kN` in all rows, derived from 8 m carriageway → 2 design lanes (IRC 6 Table 6 / Cl. 211.2) |
| §5.5 utilization chart | Deck and End Diaphragms showed `N/A` | `1.92` girder, `0.94` deck, `0.86` cross bracing, `0.86` end diaphragms |
| Table 5.29 ED Moment unit | Displayed `kN` | Displays `kN-m`; values and UR unchanged |
| Long tables | Header rows did not repeat on continuation pages | Repeating headers on all 50 long tables |
| Footers / page layout | Table/footer collision risk | Footer and table regions separated |
| Live-load tables | Vehicle and footpath rows mixed | Separate vehicle and footpath tables |
| Material chart | Not present | Steel / concrete / rebar chart with ED tonnage estimation note |
| BOQ inputs for charts | Text-formatted values | Numeric fields added |

## 3. Files changed or added

| File | Purpose |
|---|---|
| `src/osdagbridge/core/reports/styles.py` | New centralized LaTeX styles plus repeated-header injection for `longtable`. |
| `src/osdagbridge/core/reports/charts.py` | New Matplotlib-based utilization-ratio and material charts. |
| `src/osdagbridge/core/reports/chap3.py` | Braking population, carriageway-width lane fallback, split live-load tables, updated note. |
| `src/osdagbridge/core/reports/chap5.py` | UR chart embed/caption, repeated-header fixes, ED Moment unit correction. |
| `src/osdagbridge/core/reports/chap7.py` | Material chart embed and ED tonnage limitation note. |
| `src/osdagbridge/core/reports/report_generator.py` | Chart data helpers; deck now reads `deck_report_values` including overhang; ED fallback to Table 5.29 source. |
| `src/osdagbridge/core/utils/codes/irc6_2017.py` | Fixed `cl_211_2_braking_force()`, which previously raised `UnboundLocalError` for every input. |
| `src/osdagbridge/core/boq/boq_generator.py` | Numeric fields for chart generation. |
| `docs/ENVIRONMENT.md` | Verified versions, LaTeX packages, and PySide6 caveat. |
| `docs/TECHNICAL_CHANGES.md` | This document. |

## 4. Verification

### Before/after artifacts

- `validation/Report_Before.pdf` — generated headlessly from original commit
  `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` using the same `inputs.osi`.
- `validation/submission/Report_After.pdf` — final v4 report.

| Measure | Before | After |
|---|---|---|
| PDF pages | 62 | 71 |
| `longtable` count | 49 | 50 |
| Repeating `endfirsthead` / `endhead` | 2 / 2 | 50 / 50 |
| Detailed vehicle braking table | Absent | `217.39 kN` in all rows |
| Utilization-ratio chart | Absent | `1.92 / 0.94 / 0.86 / 0.86` |
| ED Moment unit | Not applicable in summary table | `kN-m` |

### Headless smoke test

- PDF generated successfully.
- `longtable`: `50`; `endfirsthead`: `50`; `endhead`: `50`; missing headers: `0`.

### Real-project v4 check

- Braking: `217.39 kN`.
- Chart: `1.92 / 0.94 / 0.86 / 0.86`.
- ED Moment: `18.33 kN-m / 21.310 kN-m`.
- Cross bracing and ED shear remain in `kN`.
- Centrifugal load remains `N/A` by design: the model has no horizontal-curvature input.

## 5. Known limitations

1. Chapter 5 End Diaphragm tables still reuse cross-bracing data (`cb_capacity_content`).
   This is pre-existing; the UR chart deliberately follows the printed Table 5.29 value.
   A proper fix would need real ED design results, which are not available in this run.
2. Approximately 137 pre-existing `Overfull \hbox` LaTeX warnings remain. They are cosmetic.
3. The environment has PySide6 `6.12.0` installed while `requirements.txt` caps it at
   `6.9.3`. This does not affect the report path and is documented in
   `docs/ENVIRONMENT.md`.
4. End-diaphragm steel tonnage in Chapter 7 is estimated from section properties and
   member lengths; it is not a separate BOQ line item. This is stated below the chart.

## 6. Documentation references

- LaTeX `longtable`: <https://ctan.org/pkg/longtable>
- LaTeX `fancyhdr`: <https://ctan.org/pkg/fancyhdr>
- LaTeX `lastpage`: <https://ctan.org/pkg/lastpage>
- Matplotlib: <https://matplotlib.org/stable/>
- Qt for Python (PySide6): <https://doc.qt.io/qtforpython/>
- IRC 6:2017: <https://law.resource.org/pub/in/bis/S03/is.6.2017.pdf>
