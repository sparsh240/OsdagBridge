# =============================================================================
# OsdagBridge — Centralized report styling (single source of truth)
# =============================================================================
# Every formatting decision used by the PDF report lives here: colours, page
# geometry, table padding/rules, header/footer theme, figure sizes and chart
# palette.  Chapter modules must import from this module instead of hardcoding
# LaTeX values.
#
# Documentation references for the technologies used here:
#   LaTeX longtable : https://ctan.org/pkg/longtable
#   LaTeX geometry  : https://ctan.org/pkg/geometry
#   LaTeX fancyhdr  : https://ctan.org/pkg/fancyhdr
#   LaTeX needspace : https://ctan.org/pkg/needspace
#   TeX Live 2025   : https://tug.org/texlive/doc.html
#   Python re       : https://docs.python.org/3.12/library/re.html
# =============================================================================

import re

# ---------------------------------------------------------------------------
# Colour palette (pdflatex xcolor / matplotlib hex)
# ---------------------------------------------------------------------------
GREEN_HEX = "91B014"          # Osdag brand green
FAIL_HEX = "D32F2F"           # red used for FAIL / threshold line

COLORS = {
    "green": GREEN_HEX,
    "fail": FAIL_HEX,
    "green_latex": "osdagGreen",
}

# ---------------------------------------------------------------------------
# Global document / page settings (LaTeX geometry + fancyhdr)
# ---------------------------------------------------------------------------
PAGE = {
    "margin": "1in",
    "bottom": "1.15in",       # extra room so table rows cannot reach the footer
    "footskip": "30pt",
    "headsep": "10pt",
    "stretch": "1.15",
    "headrule_width": "1pt",
    "footrule_width": "1pt",
}

HEADER_FOOTER = {
    "left_text": "Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay",
    "head_vspace": "2pt",
    "foot_vspace_no_note": "0pt",   # was -8pt; caused rows to bleed into footer
    "foot_vspace_note": "2pt",      # keep the software-default note below the text block
    "foot_final_vspace": "6pt",
}

# ---------------------------------------------------------------------------
# Table layout — padding, row height, rules, page-break safety
# ---------------------------------------------------------------------------
TABLE = {
    "tabcolsep": "4pt",       # keeps 5.5cm + 10cm tables inside the text block
    "arraystretch": "1.12",
    "extrarowheight": "0.8pt",
    "arrayrulewidth": "0.5pt",
    "ltpre": "0pt",
    "ltpost": "6pt",
    "needspace": "6\\baselineskip",   # min room before starting a longtable
    "row_pad": "[6pt]",               # default \\ row padding in report tables
}

# ---------------------------------------------------------------------------
# Figures and charts
# ---------------------------------------------------------------------------
FIGURE = {
    "chart_width": "0.92\\textwidth",
    "general_width": "0.9\\textwidth",
}

CHART = {
    "palette": ("#2E7D32", "#1565C0", "#EF6C00", "#6A1B9A"),
    "threshold_color": "#" + FAIL_HEX,
    "threshold_style": "--",
    "threshold_width": 1.6,
    "dpi": 180,
    "figsize": (7.2, 3.4),
    "bar_alpha": 0.88,
    "grid_alpha": 0.25,
}

# ---------------------------------------------------------------------------
# Shared LaTeX helpers
# ---------------------------------------------------------------------------

# A header row in the generated tables is a line containing \textbf{...} that
# ends with \\ or \\[6pt] (see report_utils and chapter modules).
_HEADER_RE = re.compile(r"\\textbf\{")
_ROW_END_RE = re.compile(r"\\\\(?:\[[^\]]*\])?\s*$")
_MULTIROW_RE = re.compile(r"\\multirow\{(\d+)\}")


def protect_multirow_breaks(lines):
    r"""Keep each ``\multirow`` block on one page in a longtable.

    A plain ``\\`` lets longtable split between the rows of a multirow
    group; the row label is then stranded at the bottom of a page and can
    collide with the footer. ``\\*`` forbids that break. The replacement is
    anchored to the actual row terminator so ``\\`` inside ``\\makecell`` is
    left untouched.
    """
    remaining = 0
    for i, line in enumerate(lines):
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line

        if remaining == 0:
            match = _MULTIROW_RE.search(body)
            if match:
                remaining = max(1, int(match.group(1)))

        if remaining > 0 and _ROW_END_RE.search(body):
            def _star(row_match):
                return "\\\\*" + (row_match.group(1) or "") + (row_match.group(2) or "")

            body = re.sub(r"\\\\(\[[^\]]*\])?(\s*)$", _star, body)
            lines[i] = body + newline
            remaining -= 1
    return lines


def inject_longtable_headers(tex: str) -> str:
    """Add ``\\endfirsthead`` / ``\\endhead`` to longtables that lack them.

    The report chapters build tables as raw LaTeX strings, so applying one
    centralized pass after assembly is simpler and less error-prone than
    editing every table.  The caption stays in the first head; subsequent
    pages get a short "(table continued)" note followed by the real column
    header row.

    Docs: https://ctan.org/pkg/longtable
    """
    out = []
    pos = 0
    begin_re = re.compile(r"\\begin\{longtable\}")

    while True:
        match = begin_re.search(tex, pos)
        if not match:
            out.append(tex[pos:])
            break

        out.append(tex[pos:match.start()])
        end = tex.find(r"\end{longtable}", match.end())
        if end == -1:                      # malformed / unfinished table
            out.append(tex[match.start():])
            break

        block = tex[match.start():end]
        lines = protect_multirow_breaks(block.splitlines(keepends=True))

        # longtable requires \\ after \caption; several chapter templates omit
        # it, which produces "Misplaced \noalign" errors. Normalize centrally.
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(r"\caption{") and not _ROW_END_RE.search(stripped):
                newline = "\n" if line.endswith("\n") else ""
                lines[i] = line.rstrip("\r\n") + r" \\" + newline

        if r"\endfirsthead" in block:      # already has explicit headers
            out.append("".join(lines))
            pos = end
            continue

        # Captions are often written as \caption{\textbf{Title}} \\, so a
        # caption must not be mistaken for the column-header row.
        header_idx = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(r"\caption{"):
                continue
            if _HEADER_RE.search(stripped) and _ROW_END_RE.search(stripped):
                header_idx = i
                break

        if header_idx is None:
            # Fallback for tables without a bold header: keep the header-token
            # pair by repeating the caption instead of silently omitting it.
            for i, line in enumerate(lines):
                if line.strip().startswith(r"\caption{"):
                    header_idx = i
                    break

        if header_idx is None:
            out.append("".join(lines))     # no header/caption to repeat
            pos = end
            continue

        rule_idx = header_idx + 1
        while rule_idx < len(lines) and not lines[rule_idx].strip():
            rule_idx += 1
        if rule_idx >= len(lines) or lines[rule_idx].strip() != r"\hline":
            out.append("".join(lines))     # unexpected layout; leave untouched
            pos = end
            continue

        header_line = lines[header_idx]
        if not header_line.endswith("\n"):
            header_line += "\n"
        indent = header_line[:len(header_line) - len(header_line.lstrip())]
        ncols = len(re.findall(r"(?<!\\)&", header_line)) + 1
        note = longtable_header_note(ncols) if ncols > 1 else ""
        repeated = (
            indent + r"\endfirsthead" + "\n"
            + indent + r"\hline" + "\n"
            + indent + note
            + header_line
            + indent + r"\hline" + "\n"
            + indent + r"\endhead" + "\n"
        )
        lines.insert(rule_idx + 1, repeated)
        out.append("".join(lines))
        pos = end

    return "".join(out)


def longtable_header_note(ncols: int) -> str:
    """Optional '(table continued)' line for the repeated head of a longtable."""
    return (
        r"\multicolumn{" + str(ncols) + r"}{c|}{\footnotesize\textit{(table continued)}} \\" + "\n"
        + r"\hline" + "\n"
    )
