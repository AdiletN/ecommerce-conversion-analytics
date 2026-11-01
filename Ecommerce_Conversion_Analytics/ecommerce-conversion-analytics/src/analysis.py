"""Descriptive comparisons, uncertainty, and a proposed (not conducted) A/B design."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from .data import PAGE_LABELS


def metric_table(s: pd.DataFrame, group: str) -> pd.DataFrame:
    tab = s.groupby(group, dropna=False, observed=True).agg(
        sessions=("session_id", "count"), purchases=("revenue", "sum")
    ).reset_index()
    tab["conversion_rate"] = tab["purchases"] / tab["sessions"]
    return tab


def wilson_interval(successes: int, total: int, confidence: float = .95) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Total must be positive")
    z = norm.ppf(1 - (1 - confidence) / 2)
    p = successes / total
    den = 1 + z**2 / total
    ctr = (p + z**2 / (2 * total)) / den
    half = (z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))) / den
    return ctr - half, ctr + half


def visitor_hypothesis(s: pd.DataFrame) -> dict:
    # Preselected observational comparison of new vs returning visitor sessions.
    pair = s[s["visitortype"].isin(["New_Visitor", "Returning_Visitor"])]
    counts = pd.crosstab(pair["visitortype"], pair["revenue"])
    if len(counts) != 2 or not {0, 1}.issubset(counts.columns):
        return {"test": "New vs Returning (chi-square, observational)", "status": "insufficient variation"}
    chi2, pval, _, expected = chi2_contingency(counts, correction=False)
    new = pair[pair["visitortype"] == "New_Visitor"]["revenue"]
    ret = pair[pair["visitortype"] == "Returning_Visitor"]["revenue"]
    a, b = float(new.mean()), float(ret.mean())
    delta = b - a
    standard_error = math.sqrt(a * (1 - a) / len(new) + b * (1 - b) / len(ret))
    z = norm.ppf(.975)
    return {
        "test": "New vs Returning (chi-square, observational)",
        "status": "ok",
        "new_sessions": int(len(new)), "returning_sessions": int(len(ret)),
        "new_conversion": round(a, 6), "returning_conversion": round(b, 6),
        "difference_percentage_points": round(delta * 100, 3),
        "difference_ci95_low_pp": round((delta - z * standard_error) * 100, 3),
        "difference_ci95_high_pp": round((delta + z * standard_error) * 100, 3),
        "chi2_pvalue": float(pval),
        "min_expected_cell": round(float(expected.min()), 2),
    }


def sample_size_per_variant(p1: float, relative_lift: float, alpha: float = .05, power: float = .8) -> int:
    """Two independent conversion proportions; normal approximation, equal allocation."""
    p2 = p1 * (1 + relative_lift)
    if not (0 < p1 < 1 and 0 < p2 < 1 and 0 < alpha < 1 and 0 < power < 1):
        raise ValueError("Invalid baseline/lift/alpha/power")
    d = p2 - p1
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    pbar = (p1 + p2) / 2
    n = ((z_alpha * math.sqrt(2 * pbar * (1 - pbar)) +
          z_power * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / d) ** 2
    return math.ceil(n)


def ab_plan(baseline: float) -> pd.DataFrame:
    return pd.DataFrame([{
        "baseline_conversion": baseline,
        "minimum_detectable_relative_lift": lift,
        "assumed_target_conversion": baseline * (1 + lift),
        "alpha": .05, "power": .8,
        "estimated_sessions_per_arm": sample_size_per_variant(baseline, lift),
    } for lift in [.10, .15, .20]])


def make_segments(s: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "visitor": metric_table(s, "visitortype").sort_values("sessions", ascending=False),
        "month": metric_table(s, "month").assign(
            month_order=lambda x: x["month"].map({"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"June":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12})
        ).sort_values("month_order"),
        "traffic": metric_table(s, "traffictype").sort_values("sessions", ascending=False),
        "product_pages": metric_table(s, "product_page_bucket").assign(
            sort_key=lambda x: x["product_page_bucket"].map({v:i for i,v in enumerate(PAGE_LABELS)})
        ).sort_values("sort_key"),
        "weekend": metric_table(s, "weekend"),
    }
