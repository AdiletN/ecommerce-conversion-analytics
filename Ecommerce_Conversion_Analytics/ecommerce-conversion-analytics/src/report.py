"""A polished PNG dashboard suitable for GitHub README and screenshots."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
from .analysis import make_segments

INK = "#172B4D"
MID = "#42617C"
TEAL = "#0EA5A0"
LIME = "#A6E3D9"
GRID = "#E6EBF2"
BG = "#F5F7FB"


def dashboard(s: pd.DataFrame, dest: Path, demo: bool = False) -> None:
    segs = make_segments(s)
    fig = plt.figure(figsize=(15, 10), facecolor=BG)
    gs = GridSpec(3, 2, figure=fig, height_ratios=[.75, 2.5, 2.5], hspace=.46, wspace=.22,
                  left=.07, right=.95, top=.89, bottom=.08)
    fig.text(.07, .95, "ECOMMERCE  /  CONVERSION INTELLIGENCE", fontweight="bold", fontsize=21, color=INK)
    fig.text(.07, .921, "Session performance • visitor segments • engagement • acquisition sources", fontsize=11, color=MID)
    if demo:
        fig.text(.95, .926, "SYNTHETIC DEMO · NOT REAL RESULTS", fontsize=10,
                 fontweight="bold", ha="right", color="#B42318")

    total = len(s)
    buys = int(s["revenue"].sum())
    cards = [("SESSIONS", f"{total:,}"), ("PURCHASE SESSIONS", f"{buys:,}"),
             ("CONVERSION RATE", f"{100 * buys / total:.2f}%"),
             ("AVG PRODUCT PAGES", f"{s['productrelated'].mean():.1f}")]
    axc = fig.add_subplot(gs[0, :]); axc.set_axis_off()
    for i, (lab, value) in enumerate(cards):
        x0 = i / 4 + .006
        axc.add_patch(plt.Rectangle((x0, .08), .234, .86, transform=axc.transAxes,
                                    facecolor="white", edgecolor=GRID, linewidth=.8))
        axc.text(x0 + .018, .75, lab, transform=axc.transAxes, fontsize=9, color=MID, weight="bold")
        axc.text(x0 + .018, .31, value, transform=axc.transAxes, fontsize=23, color=INK, weight="bold")

    def style(ax, title):
        ax.set_facecolor("white")
        ax.set_title(title, loc="left", color=INK, fontsize=13, fontweight="bold", pad=18)
        for edge in ax.spines.values(): edge.set_visible(False)
        ax.tick_params(colors=MID, labelsize=9, length=0)
        ax.grid(axis="y", color=GRID, alpha=.9)
        ax.set_axisbelow(True)

    ax1 = fig.add_subplot(gs[1, 0]); style(ax1, "Conversion by visitor type")
    v = segs["visitor"].sort_values("conversion_rate")
    bars = ax1.barh(v["visitortype"].str.replace("_", " "), v["conversion_rate"] * 100, color=TEAL)
    ax1.grid(axis="x", color=GRID); ax1.grid(axis="y", visible=False)
    ax1.set_xlim(0, max(1.0, v["conversion_rate"].max() * 135))
    ax1.set_xlabel("Conversion rate (%)", color=MID)
    for bar, val, n in zip(bars, v["conversion_rate"], v["sessions"]):
        ax1.text(bar.get_width() + .35, bar.get_y() + bar.get_height()/2,
                 f"{val*100:.1f}% (n={n:,})", va="center", color=INK, fontsize=9)

    ax2 = fig.add_subplot(gs[1, 1]); style(ax2, "Monthly conversion (not year-over-year)")
    m = segs["month"]
    ax2.plot(m["month"], m["conversion_rate"] * 100, marker="o", lw=2.7, color=TEAL)
    ax2.fill_between(range(len(m)), m["conversion_rate"] * 100, alpha=.09, color=TEAL)
    ax2.set_ylabel("Conversion rate (%)", color=MID)
    ax2.tick_params(axis="x", rotation=0)
    ax2.set_ylim(bottom=0)

    ax3 = fig.add_subplot(gs[2, 0]); style(ax3, "Conversion vs product pages viewed")
    p = segs["product_pages"]
    ax3.bar(p["product_page_bucket"], p["conversion_rate"] * 100, color=TEAL)
    ax3.set_xlabel("Product pages during session", color=MID)
    ax3.set_ylabel("Conversion rate (%)", color=MID)
    for ix, row in enumerate(p.itertuples()):
        ax3.text(ix, row.conversion_rate * 100 + 0.35, f"n={row.sessions:,}",
                 ha="center", va="bottom", color=MID, fontsize=8)
    ax3.set_ylim(0, max(1, p["conversion_rate"].max() * 130))

    ax4 = fig.add_subplot(gs[2, 1]); style(ax4, "Traffic source mix & conversion")
    t = segs["traffic"].sort_values("sessions", ascending=False).head(6)
    bars = ax4.bar([f"Type {int(x)}" for x in t["traffictype"]], t["sessions"], color=INK)
    ax4.set_ylabel("Sessions", color=MID)
    ax4.tick_params(axis="x", rotation=0)
    for b, rate in zip(bars, t["conversion_rate"]):
        ax4.text(b.get_x() + b.get_width()/2, b.get_height() + 20,
                 f"{rate*100:.1f}%", ha="center", color=MID, fontsize=9)
    ax4.set_ylim(0, t["sessions"].max() * 1.18)
    fig.text(.07, .025,
             "Source: UCI Online Shoppers Purchasing Intention. Revenue = purchase indicator, not currency. "
             "Comparisons are observational, not causal." if not demo else
             "SYNTHETIC DEMO DATA ONLY. Not drawn from the UCI dataset; replace via python -m src.pipeline.",
             fontsize=8.5, color=MID)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
