"""Data download, validation, and reusable session-level features."""
from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen, Request
import pandas as pd
import numpy as np

DATA_URLS = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00468/online_shoppers_intention.csv",
    "https://raw.githubusercontent.com/Bhavya-Chellapandian/online-shoppers-purchasing-intention-dataset/main/online_shoppers_intention.csv",
)
REQUIRED = {
    "Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
    "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates",
    "PageValues", "SpecialDay", "Month", "OperatingSystems", "Browser",
    "Region", "TrafficType", "VisitorType", "Weekend", "Revenue",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PAGE_LABELS = ["0", "1–4", "5–14", "15–29", "30+"]


def download_data(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for url in DATA_URLS:
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 (Data Analyst Portfolio)"})
            with urlopen(request, timeout=30) as response:
                content = response.read()
            if not content.startswith(b"Administrative,") or len(content) < 100000:
                raise ValueError("Unexpected CSV response")
            destination.write_bytes(content)
            return destination
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError(
        "Dataset download failed. Download 'online_shoppers_intention.csv' manually "
        "from https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset "
        f"and save it at {destination}. Details: {' | '.join(errors)}"
    )


def binary(series: pd.Series, field: str) -> pd.Series:
    parsed = series.astype(str).str.strip().str.lower().map({
        "true": 1, "false": 0, "1": 1, "0": 0
    })
    if parsed.isna().any():
        raise ValueError(f"Invalid boolean or missing value in {field}")
    return parsed.astype(int)


def prepare_sessions(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {sorted(missing)}")
    if df[list(REQUIRED)].isna().any().any():
        raise ValueError("Missing values detected. Audit missing data before analysis.")
    s = df.copy().reset_index(drop=True)
    s.columns = [c.lower() for c in s.columns]
    s["revenue"] = binary(s["revenue"], "Revenue")
    s["weekend"] = binary(s["weekend"], "Weekend")
    numbers = ["administrative", "administrative_duration", "informational",
               "informational_duration", "productrelated", "productrelated_duration",
               "bouncerates", "exitrates", "pagevalues", "specialday",
               "operatingsystems", "browser", "region", "traffictype"]
    for c in numbers:
        s[c] = pd.to_numeric(s[c], errors="raise")
    if (s["productrelated"] < 0).any() or (~s["month"].isin(MONTHS)).any():
        raise ValueError("Negative product page count or unexpected month")
    if (~s["bouncerates"].between(0, 1)).any() or (~s["exitrates"].between(0, 1)).any():
        raise ValueError("BounceRates/ExitRates outside 0..1")
    s.insert(0, "session_id", np.arange(1, len(s) + 1))
    s["month_order"] = s["month"].map({v: i + 1 for i, v in enumerate(MONTHS)}).astype(int)
    s["product_page_bucket"] = pd.cut(
        s["productrelated"], bins=[-0.1, 0.5, 4.5, 14.5, 29.5, np.inf],
        labels=PAGE_LABELS
    ).astype(str)
    # Source has one row per session, NOT order amounts or customer purchase history.
    # Do not deduplicate identical feature rows: they may represent distinct sessions.
    return s


def load_sessions(path: Path) -> pd.DataFrame:
    return prepare_sessions(pd.read_csv(path))
