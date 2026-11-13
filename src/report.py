"""Create a clear four-chart dashboard for the project README."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
from .analysis import make_segments

INK = "#18324B"
MUTED = "#527084"
TEAL = "#128C88"
LIGHT = "#ECF3F5"
BG = "#F6F9FB"


def dashboard(s: pd.DataFrame, dest: Path, demo: bool = False) -> None:
    if s.empty:
        raise ValueError("Cannot draw a dashboard from empty data")
    segs = make_segments(s)
    fig = plt.figure(figsize=(15, 10.4), facecolor=BG)
    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.8, 2.6, 2.6], hspace=.52,
                  wspace=.30, left=.145, right=.95, top=.87, bottom=.085)

    fig.text(.07, .965, "E-COMMERCE  |  CONVERSION ANALYSIS",
             fontsize=21, weight="bold", color=INK, va="top")
    fig.text(.07, .921, "Who buys, and how do shopping sessions differ?",
             fontsize=12, color=MUTED, va="top")
    if demo:
        fig.text(.94, .923, "FAKE DATA FOR TESTING", ha="right", color="#B42318",
                 fontsize=10.5, weight="bold")

    count = len(s)
    purchases = int(s["revenue"].sum())
    cards = [
        ("SESSIONS", f"{count:,}"),
        ("PURCHASE SESSIONS", f"{purchases:,}"),
        ("CONVERSION RATE", f"{purchases / count:.2%}"),
        ("AVG. PRODUCT PAGES", f"{s['productrelated'].mean():.1f}"),
    ]
    ax_top = fig.add_subplot(gs[0, :]); ax_top.set_axis_off()
    for i, (title, value) in enumerate(cards):
        x = i / 4 + .004
        ax_top.add_patch(plt.Rectangle((x, .08), .24, .83, transform=ax_top.transAxes,
                                        facecolor="white", edgecolor=LIGHT, lw=1.1))
        ax_top.text(x + .018, .73, title, fontsize=8.5, weight="bold",
                    color=MUTED, transform=ax_top.transAxes, va="center")
        ax_top.text(x + .018, .32, value, fontsize=22, weight="bold",
                    color=INK, transform=ax_top.transAxes, va="center")

    def decorate(ax, title):
        ax.set_facecolor("white")
        ax.set_title(title, loc="left", fontsize=12.5, weight="bold", pad=13, color=INK)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis="both", labelsize=9, labelcolor=MUTED, length=0)
        ax.grid(axis="y", color=LIGHT)
        ax.set_axisbelow(True)

    # Chart 1. Show the sample size to avoid over-reading the 'Other' group.
    ax1 = fig.add_subplot(gs[1, 0]); decorate(ax1, "Conversion by visitor type")
    visitors = segs["visitor"].sort_values("conversion_rate")
    bars = ax1.barh(visitors["visitortype"].str.replace("_", " "),
                    visitors["conversion_rate"] * 100, color=TEAL)
    ax1.grid(axis="y", visible=False)
    ax1.grid(axis="x", color=LIGHT)
    ax1.set_xlim(0, max(5, visitors["conversion_rate"].max() * 145))
    ax1.set_xlabel("Conversion rate (%)", color=MUTED, fontsize=9)
    for bar, row in zip(bars, visitors.itertuples()):
        ax1.text(bar.get_width() + .45, bar.get_y() + bar.get_height()/2,
                 f"{row.conversion_rate:.1%} | n={row.sessions:,}", va="center",
                 fontsize=8.4, color=INK)

    # Chart 2. Each month is a category. The source has no year field.
    ax2 = fig.add_subplot(gs[1, 1]); decorate(ax2, "Conversion by month (year not given)")
    months = segs["month"]
    ax2.bar(months["month"], months["conversion_rate"] * 100, color=TEAL)
    ax2.set_ylabel("Conversion rate (%)", color=MUTED, fontsize=9)
    ax2.set_ylim(0, max(5, months["conversion_rate"].max() * 125))
    ax2.tick_params(axis="x", rotation=0)

    ax3 = fig.add_subplot(gs[2, 0]); decorate(ax3, "Product pages viewed and conversion")
    pages = segs["product_pages"]
    ax3.bar(pages["product_page_bucket"], pages["conversion_rate"] * 100, color=TEAL)
    ax3.set_xlabel("Product pages in session", color=MUTED, fontsize=9)
    ax3.set_ylabel("Conversion rate (%)", color=MUTED, fontsize=9)
    for index, row in enumerate(pages.itertuples()):
        ax3.text(index, row.conversion_rate * 100 + .45, f"n={row.sessions:,}",
                 ha="center", va="bottom", fontsize=8.3, color=MUTED)
    ax3.set_ylim(0, max(5, pages["conversion_rate"].max() * 136))

    ax4 = fig.add_subplot(gs[2, 1]); decorate(ax4, "Main traffic types: sessions and conversion")
    traffic = segs["traffic"].sort_values("sessions", ascending=False).head(6)
    bars = ax4.bar([f"Type {int(x)}" for x in traffic["traffictype"]],
                   traffic["sessions"], color=INK)
    ax4.set_ylabel("Sessions", fontsize=9, color=MUTED)
    for bar, rate in zip(bars, traffic["conversion_rate"]):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(1, .012*traffic["sessions"].max()),
                 f"{rate:.1%}", ha="center", fontsize=8.5, color=MUTED)
    ax4.set_ylim(0, traffic["sessions"].max() * 1.2)

    source_note = ("FAKE TEST DATA. Do not use these numbers in a CV." if demo else
                   "Source: UCI Online Shoppers dataset | Revenue = purchase (yes/no), not money.")
    fig.text(.07, .04, source_note, color=MUTED, fontsize=9)
    fig.text(.07, .02, "These are links in the data, not proof that one thing causes another.",
             color=MUTED, fontsize=8.5)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
