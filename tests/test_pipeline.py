"""Check the key calculations with fake data, without internet access."""
from pathlib import Path
import sqlite3
import pandas as pd
import pytest

from src.data import prepare_sessions, binary
from src.demo import synthetic_sessions
from src.analysis import metric_table, visitor_hypothesis, sample_size_per_variant, wilson_interval
from src.pipeline import generate_outputs


def test_conversion_and_rows():
    raw = synthetic_sessions(1000)
    data = prepare_sessions(raw)
    assert data.session_id.is_unique
    assert len(data) == len(raw)
    assert set(data.revenue.unique()).issubset({0, 1})
    table = metric_table(data, "visitortype")
    assert table.sessions.sum() == len(data)
    assert table.purchases.sum() == data.revenue.sum()
    assert abs(data.revenue.mean() - table.purchases.sum() / table.sessions.sum()) < 1e-12


def test_same_values_are_not_deleted():
    raw = synthetic_sessions(10)
    two_identical_rows = pd.concat([raw.iloc[[0]], raw.iloc[[0]]], ignore_index=True)
    assert len(prepare_sessions(two_identical_rows)) == 2


def test_wrong_data_is_rejected():
    with pytest.raises(ValueError):
        binary(pd.Series(["YES", "FALSE"]), "Revenue")
    raw = synthetic_sessions(20)
    raw.loc[0, "Month"] = "NotAMonth"
    with pytest.raises(ValueError):
        prepare_sessions(raw)


def test_statistics_and_ab_plan():
    data = prepare_sessions(synthetic_sessions(2000))
    result = visitor_hypothesis(data)
    assert result["status"] == "ok"
    assert 0 <= result["chi2_pvalue"] <= 1
    low, high = wilson_interval(15, 100)
    assert low < .15 < high
    assert sample_size_per_variant(.15, .1) > sample_size_per_variant(.15, .2)
    with pytest.raises(ValueError):
        sample_size_per_variant(.5, 1.5)


def test_sql_outputs_match_python_and_report_is_safe(tmp_path: Path):
    data = prepare_sessions(synthetic_sessions(1400))
    hand_written_report = tmp_path / "FINDINGS.md"
    hand_written_report.write_text("My business report must stay safe", encoding="utf-8")
    generate_outputs(data, tmp_path, demo=True)
    with sqlite3.connect(tmp_path / "conversion_analysis.db") as db:
        overview = pd.read_sql_query("SELECT COUNT(*) AS n, SUM(revenue) AS p FROM sessions", db).iloc[0]
        cross = pd.read_sql_query("""
            SELECT visitortype AS visitor_type, traffictype AS traffic_type,
                   COUNT(*) AS sessions, SUM(revenue) AS purchases
            FROM sessions
            WHERE visitortype IN ('New_Visitor', 'Returning_Visitor')
            GROUP BY visitortype, traffictype
            HAVING COUNT(*) >= 100
        """, db)
    assert overview["n"] == len(data)
    assert overview["p"] == int(data.revenue.sum())
    results = pd.read_csv(tmp_path / "sql_06_visitor_traffic.csv")
    cross = cross.sort_values(["visitor_type", "traffic_type"]).reset_index(drop=True)
    results = results.sort_values(["visitor_type", "traffic_type"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(results[cross.columns], cross, check_dtype=False)
    assert (results.sessions >= 100).all()
    assert (tmp_path / "sql_01_overview.csv").exists()
    assert (tmp_path / "sql_03_monthly.csv").exists()
    assert (tmp_path / "sql_04_traffic_rank.csv").exists()
    assert (tmp_path / "observational_test.csv").exists()
    assert (tmp_path / "ab_test_plan_NOT_RESULTS.csv").exists()
    assert (tmp_path / "dashboard.png").stat().st_size > 10000
    assert "FAKE TEST DATA" in (tmp_path / "RUN_SUMMARY.md").read_text(encoding="utf-8")
    assert hand_written_report.read_text(encoding="utf-8") == "My business report must stay safe"


def test_empty_input_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        generate_outputs(pd.DataFrame(), tmp_path, demo=True)
