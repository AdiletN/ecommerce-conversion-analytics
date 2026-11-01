import sqlite3
import pandas as pd
import pytest
from pathlib import Path

from src.data import prepare_sessions, binary
from src.demo import synthetic_sessions
from src.analysis import metric_table, visitor_hypothesis, sample_size_per_variant, wilson_interval
from src.pipeline import generate_outputs


def test_conversion_and_row_integrity():
    raw = synthetic_sessions(1000)
    s = prepare_sessions(raw)
    assert s.session_id.is_unique
    assert len(s) == len(raw)
    assert set(s.revenue.unique()).issubset({0, 1})
    table = metric_table(s, "visitortype")
    assert table.sessions.sum() == len(s)
    assert table.purchases.sum() == s.revenue.sum()
    assert abs(s.revenue.mean() - table.purchases.sum() / table.sessions.sum()) < 1e-12


def test_does_not_wrongly_deduplicate():
    raw = synthetic_sessions(10)
    doubled = pd.concat([raw.iloc[[0]], raw.iloc[[0]]], ignore_index=True)
    s = prepare_sessions(doubled)
    assert len(s) == 2


def test_bad_bool_rejected():
    with pytest.raises(ValueError):
        binary(pd.Series(["YES", "FALSE"]), "Revenue")


def test_invalid_month_rejected():
    raw = synthetic_sessions(20)
    raw.loc[0, "Month"] = "Smarch"
    with pytest.raises(ValueError):
        prepare_sessions(raw)


def test_hypothesis_ci_and_planner():
    s = prepare_sessions(synthetic_sessions(2000))
    result = visitor_hypothesis(s)
    assert result["status"] == "ok"
    assert 0 <= result["chi2_pvalue"] <= 1
    low, high = wilson_interval(15, 100)
    assert low < .15 < high
    assert sample_size_per_variant(.15, .1) > sample_size_per_variant(.15, .2)
    with pytest.raises(ValueError):
        sample_size_per_variant(.5, 1.5)


def test_sql_matches_pandas_and_all_files_exist(tmp_path: Path):
    s = prepare_sessions(synthetic_sessions(1400))
    generate_outputs(s, tmp_path, demo=True)
    with sqlite3.connect(tmp_path / "conversion_analysis.db") as conn:
        result = pd.read_sql_query("SELECT COUNT(*) AS n, SUM(revenue) AS buys FROM sessions", conn).iloc[0]
    assert result["n"] == len(s)
    assert result["buys"] == s["revenue"].sum()
    assert (tmp_path / "sql_01_overview.csv").exists()
    assert (tmp_path / "sql_03_monthly.csv").exists()
    assert (tmp_path / "sql_04_traffic_rank.csv").exists()
    assert (tmp_path / "observational_test.csv").exists()
    assert (tmp_path / "ab_test_plan_NOT_RESULTS.csv").exists()
    assert (tmp_path / "dashboard.png").stat().st_size > 10000
    assert "SYNTHETIC" in (tmp_path / "FINDINGS.md").read_text(encoding="utf-8")
