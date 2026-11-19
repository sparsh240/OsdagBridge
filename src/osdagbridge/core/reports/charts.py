# =============================================================================
# OsdagBridge — report charts (matplotlib, Agg backend)
# =============================================================================
# Charts are rendered headlessly to temporary PNG files during report assembly
# and embedded as LaTeX figures. All colours, sizes and DPI come from
# reports/styles.py.
#
# Documentation references:
#   Matplotlib pyplot : https://matplotlib.org/stable/api/pyplot_summary.html
#   Axes.bar          : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.bar.html
#   Axes.axhline      : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.axhline.html
#   Agg backend       : https://matplotlib.org/stable/users/explain/backends.html
# =============================================================================

import matplotlib
matplotlib.use("Agg")          # headless: safe from the GUI worker thread
import matplotlib.pyplot as plt

from osdagbridge.core.reports.styles import CHART


def ur_summary_chart(entries, path):
    """Bar chart of utilization ratios; entries = [(label, ur_or_None), ...].

    A red dashed reference line at UR = 1.0 separates passing from failing
    checks. See the Matplotlib documentation links in the module docstring.
    """
    labels = [str(name) for name, _ in entries]
    values = []
    available = []
    for _, value in entries:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0
        values.append(number)
        available.append(value is not None and str(value) not in ("", "---", "N/A"))

    fig, ax = plt.subplots(figsize=CHART["figsize"])
    colors = [CHART["palette"][i % len(CHART["palette"])] for i in range(len(values))]
    bars = ax.bar(labels, values, color=colors, alpha=CHART["bar_alpha"], width=0.58)

    ax.axhline(1.0, color=CHART["threshold_color"],
               linestyle=CHART["threshold_style"],
               linewidth=CHART["threshold_width"],
               label="UR = 1.0 (limit)")

    upper = max([1.0] + values)
    ax.set_ylim(0, max(1.25, upper * 1.18))
    ax.set_ylabel("Utilization Ratio (Demand / Capacity)")
    ax.set_title("Overall Design Check — Utilization Ratio")
    ax.grid(axis="y", alpha=CHART["grid_alpha"], linestyle=":")
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize="small")

    for bar, value, ok in zip(bars, values, available):
        text = f"{value:.2f}" if ok else "N/A"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + upper * 0.02,
                text, ha="center", va="bottom", fontsize="small", fontweight="bold")

    fig.tight_layout()
    fig.savefig(path, dpi=CHART["dpi"], bbox_inches="tight")
    plt.close(fig)
    return path


def material_quantity_chart(steel_tonnes, concrete_m3, rebar_mt, path):
    """Two-panel chart: structural steel tonnage and concrete vs rebar.

    ``steel_tonnes`` is a dict with keys 'girders', 'cross_bracing',
    'end_diaphragms'. Concrete and reinforcement use different units, so each
    bar is labelled with its own unit to avoid an ambiguous shared Y axis.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.6))

    steel_labels = ("Girders", "Cross\nBracing", "End\nDiaphragms")
    steel_keys = ("girders", "cross_bracing", "end_diaphragms")
    steel_values = [float(steel_tonnes.get(k) or 0.0) for k in steel_keys]
    bars = ax1.bar(steel_labels, steel_values,
                   color=CHART["palette"][:3], alpha=CHART["bar_alpha"], width=0.6)
    ax1.set_title("Structural Steel (MT)")
    ax1.set_ylabel("Mass (MT)")
    ax1.grid(axis="y", alpha=CHART["grid_alpha"], linestyle=":")
    ax1.set_axisbelow(True)
    for bar, value in zip(bars, steel_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{value:.2f}", ha="center", va="bottom", fontsize="small")

    other_labels = ("Concrete\nDeck", "Reinforcement\nSteel")
    other_values = [float(concrete_m3 or 0.0), float(rebar_mt or 0.0)]
    units = ("m³", "MT")
    colors = (CHART["palette"][1], CHART["palette"][2])
    bars2 = ax2.bar(other_labels, other_values, color=colors,
                    alpha=CHART["bar_alpha"], width=0.6)
    ax2.set_title("Concrete Volume vs Rebar Weight")
    ax2.set_ylabel("Quantity (m³ / MT)")
    ax2.grid(axis="y", alpha=CHART["grid_alpha"], linestyle=":")
    ax2.set_axisbelow(True)
    for bar, value, unit in zip(bars2, other_values, units):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{value:.2f} {unit}", ha="center", va="bottom", fontsize="small")

    fig.tight_layout()
    fig.savefig(path, dpi=CHART["dpi"], bbox_inches="tight")
    plt.close(fig)
    return path
