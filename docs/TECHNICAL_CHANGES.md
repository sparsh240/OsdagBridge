# Technical Changes — OsdagBridge PDF Report Enhancements

**Date:** 2026-11-20

**Status:** Phase 8 validation complete

**Original baseline:** `validation/Report_Before.pdf` (commit `d74f56d`)

**Final artifact:** `validation/submission/Report_After.pdf` (v5)

## 1. Objective

Improve the clarity and correctness of the generated OsdagBridge PDF report without
changing the design calculations. The implementation intentionally reuses existing
report data and keeps the changes small and review-friendly for a FOSSEE internship
deliverable.

## 2. Phase 6 changes (already committed)

| Area | Before | After |
|---|---|---|
| §3 braking force | Blank in vehicle rows; `N/A` in summary row | `217.39 kN` in all rows, derived from 8 m carriageway → 2 design lanes (IRC 6 Table 6 / Cl. 211.2) |
| §5.5 utilization chart | Deck and End Diaphragms showed `N/A` | Girder / deck / cross bracing / end diaphragm values are populated from report data |
| Table 5.29 ED Moment unit | Displayed `kN` | Displays `kN-m`; values and UR unchanged |
| Long tables | Header rows did not repeat on continuation pages | Repeating headers on all 50 long tables |
| Footers / page layout | Table/footer collision risk | Footer and table regions separated |
| Live-load tables | Vehicle and footpath rows mixed | Separate vehicle and footpath tables |
| Material chart | Not present | Steel / concrete / rebar chart with ED tonnage estimation note |

## 3. Phase 7 fixes (P1/P2/P3)

| Area | Before | After |
|---|---|---|
| Table 2.4 — overall bridge width | `12.649999999999999` | `12.65` (display-only rounding) |
| Table 2.7 — girder dimensions | `1.39 mm`, `0.008 mm`, `0.42 mm, 0.018 mm` | `1390`, `8`, `420, 18` etc. in the mm-labelled columns (display-only conversion from the stored metre values) |
| Table 3.6 — seismic forces | Blank force cells | `687.82 kN` for both longitudinal and transverse forces, with an explicit `N/A` fallback |
| Table 7.1 — crash barrier BOQ | `0.00000 m² × 25.00 m = 0.00001 m³`; zero qty/weight | `0.30228 m² × 25.00 m = 7.55707 m³`; qty `2`; total volume `15.11`; weights `18.89` / `37.79` |
| Table 5.4 — girder shear blocks | A girder's multirow block could split across pages | Intermediate rows use `\\*[6pt]`; `multirow` loaded with its `longtable` option |
| Continuation headers | Caption text was repeated as the continuation head | First head keeps the caption; continuation head shows `(table continued)` plus the real column header |
| Footer / TOC numbering | Cover footer was `Page 1 of 70` while the TOC started at page 2 | Cover `Page 1 of 71`, TOC `Page 2 of 71`, TOC entries start at `3`, last footer `Page 71 of 71` |
| Table 5.11 fatigue note | PDF text extraction showed `¿ 25 mm` | Bare `>` changed to `$> 25$` in math mode; extraction now shows `> 25 mm` |
| Table 3.3 braking note | Awkward `Number of lanes: carriageway width (IRC 6 Table 6)` | Reworded to `The lane count was derived from carriageway width (IRC 6 Table 6).` |
| Load-combination formatter | Could leak unexpected internal labels or malformed factors | Labels are mapped to known IRC aliases; numeric factors are parsed explicitly; unknown names are skipped |
| Table 5.19 punching label | Reported as `URd,c` in an older artifact | Current source and PDF use `$v_{Rd,c}$`; verified as `vRd,c` in extracted text |
| Project Overview | Reported as duplicated | Not present as a duplicate in current source or PDF; no block was removed |

### 3.1 Footer overlap fix (post-P1/P2/P3)

| Area | Before | After |
|---|---|---|
| Software-default note | `foot_vspace_note = "-8pt"` placed `* Software default value` over the body note near the bottom of page 14 | `foot_vspace_note = "2pt"`; the rendered note now sits clear of the body text |
| Multirow table breaks | A plain row ending let longtable split a `multirow` group; label `G6` was stranded in the footer on page 25 | `protect_multirow_breaks()` converts row endings in every longtable to `\*`, keeping each group together |

The multirow fix is central and applies to all current and future longtables, so
no chapter template needs a one-off edit. Keeping groups intact changes pagination
(from 71 to 77 pages) but removes the footer collision. A rendered-PDF geometry
check now asserts zero body/footer word-box intersections.

The crash-barrier fix normalizes `typical_section.crash_barrier.area` once in
`boq_generator.calculate_material_quantities()`. The UI stores this key in m² while
the default library stores mm²; the second division by `1e6` was collapsing the
volume to zero.

The seismic-force fix adds two computed keys in `common.py`, returns the forces from
`BridgeGrillageModel.create_seismic_load_cases()`, stores them in `output_dict`,
merges them into the report payload, and renders them in `chap3.py`.

The PDF font/ToUnicode mapping was the root cause of the extracted `¿ 25 mm`.
The LaTeX source was already correct; math mode avoids the problematic text-font
encoding of `>`.

## 4. Files changed or added

| File | Purpose |
|---|---|
| `src/osdagbridge/core/reports/styles.py` | Centralized LaTeX styles; continuation-head injection, footer note spacing and generic `multirow` break protection. |
| `src/osdagbridge/core/reports/charts.py` | Matplotlib-based utilization-ratio and material charts. |
| `src/osdagbridge/core/reports/chap2.py` | Display fixes for Table 2.4 / 2.7 and explicit continuation head for the restraint table. |
| `src/osdagbridge/core/reports/chap3.py` | Braking population, split live-load tables, seismic force rows, note wording and hardened combination formatter. |
| `src/osdagbridge/core/reports/chap5.py` | UR chart, ED Moment unit, Table 5.4 keep-together and math-mode fatigue note. |
| `src/osdagbridge/core/reports/chap7.py` | Material chart embed and ED tonnage limitation note. |
| `src/osdagbridge/core/reports/report_generator.py` | Chart helpers, payload merge for seismic forces, `multirow` longtable option and page-counter alignment. |
| `src/osdagbridge/core/utils/common.py` | New seismic force keys. |
| `src/osdagbridge/core/bridge_types/plate_girder/analyser.py` | Returns computed seismic forces. |
| `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py` | Stores computed seismic forces in `output_dict`. |
| `src/osdagbridge/core/boq/boq_generator.py` | Numeric BOQ fields and crash-barrier area normalization. |
| `src/osdagbridge/core/utils/codes/irc6_2017.py` | Fixed `cl_211_2_braking_force()`, which previously raised `UnboundLocalError`. |
| `docs/ENVIRONMENT.md` | Verified versions, LaTeX packages and PySide6 caveat. |
| `docs/TECHNICAL_CHANGES.md` | This document. |
| `validation/README.md` | Validation artifact index and verified values. |

Generated clutter removed during the final cleanup pass: Python `__pycache__`
trees and `*.pyc` files, the editable-install `src/osdagbridge.egg-info/`
metadata, and the two runtime log directories (`ResourceFiles/` and
`src/ResourceFiles/`), which contained only duplicate Osdag log files. Tracked
validation artifacts and the runtime `weather.sqlite` database were retained.

## 5. Verification

### 5.1 Before/after artifacts

- `validation/Report_Before.pdf` — baseline report regenerated headlessly from
  original commit `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3` using the same `inputs.osi`.
- `validation/submission/Report_After.pdf` — final v5 report (77 pages).
- `validation/submission/Report_After.tex` — matching LaTeX source.
- `validation/submission/inputs.osi` — matching input file.

The final headless generation reuses the GUI-rendered figures from the previous
submission so that figure placement stays unchanged. The page count rose from 71
to 77 because `multirow` groups are now kept together instead of being split
across pages.

### 5.2 Report checks

| Measure | Result |
|---|---|
| PDF pages | `77` |
| `longtable` count | `50` |
| `endfirsthead` / `endhead` | `50 / 50` |
| Missing headers | `0` |
| Continuation notes | `49` (one complex table keeps its bespoke two-row head) |
| Repeated caption heads | `0` |
| Protected multirow row endings | `384` starred endings |
| Footer/body word-box intersections | `0` (full `pdftotext -bbox` scan) |
| Cover / TOC / last footer | `Page 1 of 77` / `Page 2 of 77` / `Page 77 of 77` |
| TOC first entry | `Executive Summary 3` |

Verified rendered values:

- Table 2.4: `12.65`; Table 2.7: `1390`, `8`, `420`, `18`.
- Table 3.3 braking: `217.39 kN`.
- Table 3.6 seismic forces: `687.82 kN` longitudinal and transverse.
- Table 5.11 fatigue note extracts as `plate thickness > 25 mm`.
- Table 5.19 punching label extracts as `vRd,c`.
- Table 5.29 ED Moment: `kN-m`; cross bracing and ED shear remain `kN`.
- Table 7.1 crash barrier: `0.30228 m² × 25.00 m = 7.55707 m³`, qty `2`, total `15.11`, weights `18.89` / `37.79`.
- Braking remains `217.39 kN`; environment values (wind `39 m/s`, zone `III`, shade temperatures) render from the detailed `project.location` block.

### 5.3 GUI restart check

- The desktop GUI was restarted in offscreen mode after the code changes. The
  main window was created with fresh modules and the `PlateGirderBridge` backend.
- A full click-through report generation was not feasible in this container:
  keeping the Qt/OCCT GUI resident while running the design exhausted the host
  memory. The final report was therefore generated headlessly with the same core
  and the GUI-rendered figures from the prior validated submission.

### 5.4 Code checks

- `python -m py_compile ...` passed for all modified modules.
- `git diff --check` passed.
- `/tmp/opencode/smoke_report.py` generated a PDF successfully: `longtable: 50`,
  `endfirsthead: 50`, `endhead: 50`, missing headers: `0`. The smoke recompile only
  reported missing images in its temporary verification directory and pre-existing
  overfull hboxes.

### 5.5 UR discrepancy investigation

Earlier v4 artifacts showed an overall UR of `1.92` with a governing fatigue stress
of `177.15 MPa`; v5 showed `1.93` with `178.14 MPa`. To isolate this, the committed
v4 code (worktree at `0ab12eb`) was regenerated with the exact same `inputs.osi`
and the same figure set. It also produced `1.93` / `178.14 MPa`. The difference is
therefore due to the input/UI state used for the earlier v4 run, not to the Phase 7
code changes. No design calculation was altered.

## 6. Scope decisions

- Report metadata remains `Test Rprt` / `Rev 0`.
- GitHub link and collaborator changes were skipped because no replacement values
  were supplied.
- The duplicated Project Overview reported in the issue list could not be
  reproduced; no report block was deleted.
- The garbled Table 3.3 note, malformed Table 3.8 combinations and `URd,c` label
  were not present in current source or artifacts. Defensive formatter/note changes
  were still applied where useful.

## 7. Known limitations

1. Chapter 5 End Diaphragm tables still reuse cross-bracing data
   (`cb_capacity_content`). This is pre-existing; the UR chart deliberately follows
   the printed Table 5.29 value. A proper fix needs real ED design results.
2. Approximately 142 pre-existing `Overfull \hbox` LaTeX warnings remain in the
   headless smoke recompile. They are cosmetic.
3. The environment has PySide6 `6.12.0` installed while `requirements.txt` caps it at
   `6.9.3`. This does not affect the report path and is documented in
   `docs/ENVIRONMENT.md`.
4. End-diaphragm steel tonnage in Chapter 7 is estimated from section properties and
   member lengths; it is not a separate BOQ line item. This is stated below the chart.

## 8. Documentation references

- LaTeX `longtable`: <https://ctan.org/pkg/longtable>
- LaTeX `multirow`: <https://ctan.org/pkg/multirow>
- LaTeX `fancyhdr`: <https://ctan.org/pkg/fancyhdr>
- LaTeX `lastpage`: <https://ctan.org/pkg/lastpage>
- Matplotlib: <https://matplotlib.org/stable/>
- Qt for Python (PySide6): <https://doc.qt.io/qtforpython/>
- IRC 6:2017: <https://law.resource.org/pub/in/bis/S03/is.6.2017.pdf>
