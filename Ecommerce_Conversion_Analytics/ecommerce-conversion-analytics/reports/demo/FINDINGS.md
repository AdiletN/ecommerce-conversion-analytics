# Conversion analysis findings

**SYNTHETIC DEMONSTRATION (NOT REAL UCI RESULTS)**

## Scope & definitions
- Sessions: **5,000**
- Sessions resulting in a purchase: **902**
- Session conversion: **18.04%**
- Metric definition: `purchases / sessions`; `Revenue` is a Boolean purchase flag, not an amount of money.

## Visitors
- Returning_Visitor: 3,816 sessions, 19.97% conversion
- New_Visitor: 1,086 sessions, 11.88% conversion
- Other: 98 sessions, 11.22% conversion

## Statistical check
- Preselected comparison: New vs Returning visitor session conversion.
- Two-group chi-square test p-value: **1.064e-09 (chi-square, association only)**.
- Difference (Returning minus New), 95% CI: **[5.785, 10.395] percentage points**.
- The comparison is observational, **not** an A/B test. No causal effect can be inferred.

## Recommended business follow-up
1. Prioritize diagnostic review of high-volume, low-conversion visitor segments.
2. Examine product page usability and on-site navigation; session engagement may reflect user intent, not cause conversion.
3. Design a **future randomized A/B test** with conversion rate as the primary KPI.
4. Check assignment balance, instrumentation, and revenue/guardrail metrics in a real experiment.

## Limitations
- No prices, amounts, transaction IDs, user IDs or full visit dates. Cannot calculate revenue, AOV, retention, or cohort churn.
- Month has no explicit year; seasonal/temporal claims require caution.
- Metrics such as `PageValues` can reflect purchase outcomes and are inappropriate as pre-experiment targeting evidence.
- No random assignment here. Associations are not causal effects.
- Rows are not automatically deduplicated because identical features can describe different sessions.

## Files
- `dashboard.png`: four-panel chart.
- `sql_*.csv`: SQLite query outputs.
- `segment_*.csv`: Pandas segment tables.
- `observational_test.csv`: statistical comparison.
- `ab_test_plan_NOT_RESULTS.csv`: **sample-size calculations only; no experiment has been run**.
- `sessions_clean.csv`: cleaned input for Power BI.
