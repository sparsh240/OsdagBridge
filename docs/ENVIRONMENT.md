# Verified development environment

Validated in the active conda environment `osdagbridge-env` on 2026-11-19.

| Component | Declared by project | Verified / chosen | Official documentation |
|---|---|---|---|
| Python | `>=3.11,<3.13` (`pyproject.toml`) | 3.12.16 | https://docs.python.org/3.12/ |
| Conda | — | 26.9.4 | https://docs.conda.io/ |
| PySide6 | `>=6.5.0,<=6.9.3` (`requirements.txt`) | 6.12.0 installed (see note below) | https://doc.qt.io/qtforpython-6/ |
| NumPy | `>=1.21.0` | 2.5.5 | https://numpy.org/doc/stable/ |
| SciPy | `>=1.10.1` | 1.18.1 | https://docs.scipy.org/doc/scipy/ |
| Matplotlib | `>=3.5` | 3.11.2 | https://matplotlib.org/stable/ |
| Pydantic | `>=2.0` | 2.14.3 | https://docs.pydantic.dev/2.x/ |
| OpenSeesPy | `>=3.2.2.6` | 3.8.0.0 | https://opensees.berkeley.edu/wiki/index.php/OpenSeesPy |
| xarray / fiona / shapely / openpyxl | unpinned | 2026.9 / 1.10.1 / 2.2.0 / 3.1.5 | project docs |
| TeX Live / pdflatex | bundled by `osdag_latex_env` 1.0.3 | TeX Live 2025, pdfTeX 1.40.28 | https://tug.org/texlive/doc.html |

Required LaTeX packages were confirmed present: `geometry`, `graphicx`, `amsmath`,
`amssymb`, `booktabs`, `array`, `tabularx`, `float`, `fancyhdr`, `hyperref`,
`xcolor`, `setspace`, `enumitem`, `caption`, `subcaption`, `multirow`,
`colortbl`, `longtable`, `titlesec`, `titletoc`, `lastpage`, `makecell`,
`etoolbox`, `needspace`.

- `longtable` — https://ctan.org/pkg/longtable
- `fancyhdr` — https://ctan.org/pkg/fancyhdr
- `geometry` — https://ctan.org/pkg/geometry
- `needspace` — https://ctan.org/pkg/needspace

## Known environment caveat

The installed PySide6 is 6.12.0 while `requirements.txt` caps it at 6.9.3.
Attempts to downgrade in this workspace were not completed: `pip` cannot
uninstall the conda-installed `shiboken6` (no `RECORD` file), and the conda
solver stalled on the large Qt dependency set. This does **not** affect the
PDF report path — charts are rendered headlessly with Matplotlib's `Agg`
backend and the report generator does not import PySide6. Align the environment
with `requirements.txt` before a final release build of the desktop app.

## Deliberately out of scope

`plotly`, `pygithub`, `pyqt5` and `requests` are reported missing by `pip check`
through conda-only packages, but none are used by the report path. They are left
untouched to avoid pulling PyQt5 alongside PySide6.
