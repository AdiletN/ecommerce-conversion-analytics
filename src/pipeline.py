"""CLI: fetch UCI real data or run a clearly labelled synthetic offline demo."""
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
    output.mkdir(parents=True, exist_ok=True)
    # Flat fact table: importable directly into Power BI, Excel or SQLite.
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

    outcome = visitor_hypothesis(s)
    pd.DataFrame([outcome]).to_csv(output / "observational_test.csv", index=False)
    ab_plan(float(s["revenue"].mean())).to_csv(output / "ab_test_plan_NOT_RESULTS.csv", index=False)
    dashboard(s, output / "dashboard.png", demo)

    total, purchases = len(s), int(s["revenue"].sum())
    vtab = segments["visitor"]
    vtext = "\n".join(f"- {row.visitortype}: {row.sessions:,} sessions, {row.conversion_rate:.2%} conversion"
                       for row in vtab.itertuples())
    label = "SYNTHETIC DEMONSTRATION (NOT REAL UCI RESULTS)" if demo else "REAL UCI SOURCE DATA"
    sig = "not calculated"
    if outcome.get("status") == "ok":
        sig = f"{outcome['chi2_pvalue']:.4g} (chi-square, association only)"
    report = f"""# Conversion analysis findings\n\n**{label}**\n\n## Scope & definitions\n- Sessions: **{total:,}**\n- Sessions resulting in a purchase: **{purchases:,}**\n- Session conversion: **{purchases / total:.2%}**\n- Metric definition: `purchases / sessions`; `Revenue` is a Boolean purchase flag, not an amount of money.\n\n## Visitors\n{vtext}\n\n## Statistical check\n- Preselected comparison: New vs Returning visitor session conversion.\n- Two-group chi-square test p-value: **{sig}**.\n- Difference (Returning minus New), 95% CI: **[{outcome.get('difference_ci95_low_pp', 'NA')}, {outcome.get('difference_ci95_high_pp', 'NA')}] percentage points**.\n- The comparison is observational, **not** an A/B test. No causal effect can be inferred.\n\n## Recommended business follow-up\n1. Prioritize diagnostic review of high-volume, low-conversion visitor segments.\n2. Examine product page usability and on-site navigation; session engagement may reflect user intent, not cause conversion.\n3. Design a **future randomized A/B test** with conversion rate as the primary KPI.\n4. Check assignment balance, instrumentation, and revenue/guardrail metrics in a real experiment.\n\n## Limitations\n- No prices, amounts, transaction IDs, user IDs or full visit dates. Cannot calculate revenue, AOV, retention, or cohort churn.\n- Month has no explicit year; seasonal/temporal claims require caution.\n- Metrics such as `PageValues` can reflect purchase outcomes and are inappropriate as pre-experiment targeting evidence.\n- No random assignment here. Associations are not causal effects.\n- Rows are not automatically deduplicated because identical features can describe different sessions.\n\n## Files\n- `dashboard.png`: four-panel chart.\n- `sql_*.csv`: SQLite query outputs.\n- `segment_*.csv`: Pandas segment tables.\n- `observational_test.csv`: statistical comparison.\n- `ab_test_plan_NOT_RESULTS.csv`: **sample-size calculations only; no experiment has been run**.\n- `sessions_clean.csv`: cleaned input for Power BI.\n"""
    (output / "FINDINGS.md").write_text(report, encoding="utf-8")
    print(f"{label}: {total:,} sessions, {purchases:,} purchases, {purchases / total:.2%} conversion")
    print(f"Outputs saved to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible e-commerce conversion analysis")
    parser.add_argument("--demo", action="store_true", help="Generate synthetic data for offline demonstration")
    parser.add_argument("--input", type=Path, help="Path to an existing UCI CSV")
    args = parser.parse_args()
    if args.demo and args.input:
        parser.error("Choose either --demo or --input, not both")
    if args.demo:
        df = prepare_sessions(synthetic_sessions())
        generate_outputs(df, ROOT / "reports" / "demo", demo=True)
        return
    file = args.input if args.input else ROOT / "data" / "online_shoppers_intention.csv"
    if not file.exists():
        print("Downloading real UCI dataset (internet connection required)...")
        download_data(file)
    df = load_sessions(file)
    generate_outputs(df, ROOT / "reports" / "real")


if __name__ == "__main__":
    main()
