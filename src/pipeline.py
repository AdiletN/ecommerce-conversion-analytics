"""Run the full analysis or a fake offline example."""
from __future__ import annotations
import argparse
from pathlib import Path
import sqlite3
import pandas as pd
from .data import MONTHS, load_sessions, prepare_sessions, download_data
from .demo import synthetic_sessions
from .analysis import make_segments, visitor_hypothesis, ab_plan
from .report import dashboard

ROOT = Path(__file__).resolve().parent.parent


def generate_outputs(s: pd.DataFrame, output: Path, demo: bool = False) -> None:
    if s.empty:
        raise ValueError("No sessions to analyze")
    output.mkdir(parents=True, exist_ok=True)
    s.to_csv(output / "sessions_clean.csv", index=False)
    with sqlite3.connect(output / "conversion_analysis.db") as conn:
        s.to_sql("sessions", conn, if_exists="replace", index=False)
        pd.DataFrame({"month_number": range(1, 13), "month_name": MONTHS}).to_sql(
            "dim_month", conn, if_exists="replace", index=False
        )
        for sql_file in sorted((ROOT / "sql").glob("*.sql")):
            frame = pd.read_sql_query(sql_file.read_text(encoding="utf-8"), conn)
            frame.to_csv(output / f"sql_{sql_file.stem}.csv", index=False)

    segments = make_segments(s)
    for name, tab in segments.items():
        tab.to_csv(output / f"segment_{name}.csv", index=False)

    result = visitor_hypothesis(s)
    pd.DataFrame([result]).to_csv(output / "observational_test.csv", index=False)
    ab_plan(float(s["revenue"].mean())).to_csv(output / "ab_test_plan_NOT_RESULTS.csv", index=False)
    dashboard(s, output / "dashboard.png", demo)

    visitors = "\n".join(
        f"- {row.visitortype.replace('_', ' ')}: {row.sessions:,} sessions; {row.conversion_rate:.2%} conversion"
        for row in segments["visitor"].itertuples()
    )
    origin = "FAKE TEST DATA (not the UCI dataset)" if demo else "UCI DATASET"
    pvalue = f"{result['chi2_pvalue']:.3g}" if result.get("status") == "ok" else "not available"
    interval = (f"[{result['difference_ci95_low_pp']:.2f}, {result['difference_ci95_high_pp']:.2f}] pp"
                if result.get("status") == "ok" else "not available")
    summary = f"""# Run summary

**Data source: {origin}**

This file is created by the Python script each time it runs.
The main business report is saved in `reports/real/FINDINGS.md` and is not changed by the script.

## Main numbers

- Sessions: **{len(s):,}**
- Sessions with a purchase: **{int(s['revenue'].sum()):,}**
- Purchase conversion rate: **{s['revenue'].mean():.2%}**

## Visitor groups
{visitors}

## Statistical check

- Chi-square p-value: **{pvalue}**.
- 95% confidence interval for (returning minus new) conversion: **{interval}**.
- This is an observational comparison, not a real A/B test.

## Important limits

- `Revenue` shows a purchase, not the amount of money.
- The file has no order prices, so we cannot calculate sales or profit.
- The file has months but no years, so we cannot study long-term trends.
- These results do not prove cause and effect.
"""
    # Keep hand-written business findings safe from future pipeline runs.
    (output / "RUN_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(f"{origin}: {len(s):,} sessions, {int(s['revenue'].sum()):,} purchase sessions, {s['revenue'].mean():.2%} conversion")
    print(f"Files saved in {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="E-commerce session analysis")
    parser.add_argument("--demo", action="store_true", help="Run with fake data for testing")
    parser.add_argument("--input", type=Path, help="Local path to UCI CSV data")
    args = parser.parse_args()
    if args.demo and args.input:
        parser.error("Choose either --demo or --input, not both")
    if args.demo:
        generate_outputs(prepare_sessions(synthetic_sessions()), ROOT / "reports" / "demo", demo=True)
        return
    path = args.input if args.input else ROOT / "data" / "online_shoppers_intention.csv"
    if not path.exists():
        print("Trying to download UCI data...")
        download_data(path)
    generate_outputs(load_sessions(path), ROOT / "reports" / "real")


if __name__ == "__main__":
    main()
