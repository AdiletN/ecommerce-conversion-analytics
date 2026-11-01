"""Make realistic-looking but fully SYNTHETIC sessions for offline smoke tests."""
from __future__ import annotations
import numpy as np
import pandas as pd


def synthetic_sessions(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    month = rng.choice(["Feb", "Mar", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], n)
    visitor = rng.choice(["Returning_Visitor", "New_Visitor", "Other"], n, p=[.75, .23, .02])
    pages = np.maximum(0, rng.negative_binomial(3, .15, n))
    weekend = rng.random(n) < .28
    traffic = rng.choice([1, 2, 3, 4, 5, 6, 7, 8], n, p=[.2, .23, .14, .13, .1, .1, .05, .05])
    logit = -2.35 + .65 * (visitor == "Returning_Visitor") + .019 * np.minimum(pages, 65) - .15 * weekend + .2 * (month == "Nov")
    prob = 1.0 / (1.0 + np.exp(-logit))
    revenue = rng.random(n) < prob
    bounce = np.clip(.18 * np.exp(-pages / 14) + rng.normal(0, .012, n), 0, .2)
    exit_rate = np.clip(bounce + rng.uniform(0, .04, n), 0, 1)
    return pd.DataFrame({
        "Administrative": rng.poisson(2, n),
        "Administrative_Duration": rng.uniform(0, 400, n),
        "Informational": rng.poisson(1, n),
        "Informational_Duration": rng.uniform(0, 200, n),
        "ProductRelated": pages,
        "ProductRelated_Duration": pages * rng.uniform(8, 70, n),
        "BounceRates": bounce,
        "ExitRates": exit_rate,
        "PageValues": np.where(revenue, rng.uniform(10, 100, n), 0),
        "SpecialDay": rng.choice([0, .2, .4, .6, .8, 1], n, p=[.82, .04, .04, .04, .04, .02]),
        "Month": month,
        "OperatingSystems": rng.integers(1, 6, n),
        "Browser": rng.integers(1, 7, n),
        "Region": rng.integers(1, 10, n),
        "TrafficType": traffic,
        "VisitorType": visitor,
        "Weekend": weekend,
        "Revenue": revenue,
    })
