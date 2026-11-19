# OsdagBridge Report Deliverables — Technical Changes

**Date:** 2026-11-20

**Repository:** <https://github.com/sparsh240/OsdagBridge>  
Python report scripts are under `src/osdagbridge/core/reports/`.

## Deliverables

| File | Description |
|---|---|
| `Report_Before.pdf` | Original output, regenerated from baseline commit `d74f56d` with the same inputs. |
| `Report_After.pdf` | Enhanced output with all validated fixes, including the footer-separation fix. |
| `TECHNICAL_CHANGES.md` | This brief technical note. |
| `inputs.osi` | Design inputs used for both reports. |

The LaTeX source files and the legacy v4 report copies were removed from the
submission set; only the requested PDFs and supporting files are retained.

## 1. Key code and LaTeX modifications

No PyLaTeX dependency was introduced: chapters emit LaTeX source as Python
strings, `report_generator.py` assembles the document, and one centralized pass
in `styles.py` post-processes every longtable.

- **Preamble/page layout:** `geometry` now takes margin, bottom, `footskip` and
  `headsep` from `styles.py`. The bottom margin is `1.15in` with a `30pt`
  footskip so table rows cannot reach the footer.
- **Headers/footers:** `fancyhdr` rules, header/footer text and the
  `* Software default value` note use shared values. The note spacing changed
  from `-8pt` to `2pt`, moving it clear of the body text.
- **Longtables:** `multirow` is loaded with its `longtable` option; tables get
  `\endfirsthead` / `\endhead`, a short `(table continued)` note on continuation
  pages, and caption `\\` normalization. Row endings inside `multirow` groups
  are converted to `\*` so a group cannot split and strand its label in the
  footer.
- **Page numbering:** `titlepage` resets the counter; `\addtocounter{page}{1}`
  keeps cover, TOC and section footers aligned from `Page 1 of 77` onward.
- **Values and units:** display-only rounding for overall width and girder
  dimensions, seismic force rows, braking force, ED moment in `kN-m`, math-mode
  `> 25 mm`, corrected punching label, and normalized crash-barrier BOQ area.
- **Charts:** headless Matplotlib `Agg` renderers generate the utilization-ratio
  and material-quantity charts from the same data used by the report tables.
- **Design calculations:** unchanged. All fixes are formatting, data plumbing
  or presentation fixes.

## 2. Files altered under the report generator

| File | Role in the changes |
|---|---|
| `src/osdagbridge/core/reports/report_generator.py` | Preamble, `fancyhdr` layout, chart-helper/payload wiring, page-counter alignment, and the call to centralized longtable post-processing. |
| `src/osdagbridge/core/reports/styles.py` | New single source of truth for colours, page geometry, table padding/rules, header/footer spacing, figure widths and chart styling; includes `protect_multirow_breaks()` and `inject_longtable_headers()`. |
| `src/osdagbridge/core/reports/charts.py` | New headless UR-summary and material-quantity chart renderers. |
| `src/osdagbridge/core/reports/chap2.py` | Table 2.4 / 2.7 display conversion and explicit restraint-table continuation head. |
| `src/osdagbridge/core/reports/chap3.py` | Braking population, split vehicle/footpath tables, seismic force rows, load-combination formatter hardening and note wording. |
| `src/osdagbridge/core/reports/chap5.py` | UR chart hook, ED moment unit, multirow row protection and math-mode fatigue note. |
| `src/osdagbridge/core/reports/chap7.py` | Material chart embed and end-diaphragm tonnage estimation note. |

Supporting data fixes outside the report package: `common.py`,
`analyser.py`, `plategirderbridge.py`, `boq_generator.py` and `irc6_2017.py`.

## 3. Structure of the centralized formatting configuration module

`src/osdagbridge/core/reports/styles.py` is organized as:

1. **Module header and references** — states that all formatting decisions live
   here and links the relevant LaTeX/Python documentation.
2. **Colour constants** — `GREEN_HEX`, `FAIL_HEX` and `COLORS` for Osdag green,
   failure red and the LaTeX color name.
3. **`PAGE`** — geometry and rule widths: `margin`, `bottom`, `footskip`,
   `headsep`, `stretch`, `headrule_width`, `footrule_width`.
4. **`HEADER_FOOTER`** — footer text and vertical spacing, including
   `foot_vspace_note` and `foot_vspace_no_note`.
5. **`TABLE`** — `tabcolsep`, `arraystretch`, `extrarowheight`,
   `arrayrulewidth`, `LTpre`, `LTpost`, `needspace` and default row padding.
6. **`FIGURE` / `CHART`** — embedded widths, palette, threshold styling, DPI,
   figure size and transparency.
7. **LaTeX helpers** — `_HEADER_RE`, `_ROW_END_RE`, `_MULTIROW_RE`,
   `protect_multirow_breaks()`, `inject_longtable_headers()` and
   `longtable_header_note()`.

Chapter modules import these values instead of hardcoding LaTeX dimensions or
colors, so a styling change is made in one place and reaches all 50 longtables.

## 4. Rationale for architectural and styling choices

- **Single source of truth:** separate chapter templates previously repeated
  spacing and colour literals. Centralizing them prevents drift and makes the
  report theme reviewable in one file.
- **Post-assembly LaTeX pass:** table markup is generated across many chapter
  modules. Applying header injection and multirow protection once to the
  assembled document is safer and smaller than editing every table by hand.
- **Keep raw LaTeX strings:** the existing codebase already builds LaTeX this
  way. Introducing PyLaTeX would add a dependency and a large rewrite without
  improving the validated output.
- **Formatting only:** design calculations were deliberately left untouched.
  Data keys were added only where the report had no value to render.
- **Readability over density:** keeping `multirow` groups intact increases the
  report to 77 pages, but prevents split labels and footer collisions.
- **Reproducible visuals:** headless chart rendering uses the same report data
  and reuses GUI-rendered figures, so the PDF can be regenerated consistently
  in CI or a container.

## 5. Visual enhancements and open polish

- Osdag-green header/footer rules with consistent `12pt` typography and
  `1.15` line stretch.
- Tighter, more even tables: `4pt` tabcolsep, `1.12` arraystretch, `0.5pt`
  rules and `[6pt]` row padding.
- Repeating table heads with an italic `(table continued)` note.
- Separate vehicle and footpath live-load tables; explicit `N/A` fallbacks.
- Color-coded utilization chart with a `1.0` threshold line and a two-panel
  material quantity chart.
- Clearer typography in notes: `kN-m`, `$> 25$ mm`, `v_{Rd,c}`, and reworded
  lane-count and braking notes.
- Remaining cosmetic polish: about 142 pre-existing `Overfull \hbox` warnings
  and Chapter 5 end-diaphragm rows that still reuse cross-bracing data; the
  latter is labelled as an estimate in the chart note.

## 6. Verification summary

- `Report_After.pdf`: 77 pages; 50 longtables; 50/50 repeated heads; 0 repeated
  caption heads; 49 continuation notes.
- Full `pdftotext -bbox` scan: `0` body/footer word-box intersections.
- Footers: `Page 1 of 77`, `Page 2 of 77`, `Page 77 of 77`.
- Smoke compile and module syntax checks passed; only known temporary-image
  warnings and pre-existing overfull hboxes remain.
