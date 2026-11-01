-- JOIN dimension to preserve calendar ordering; year unavailable in source.
SELECT d.month_name AS month,
       COUNT(s.session_id) AS sessions,
       SUM(s.revenue) AS purchases,
       ROUND(100.0 * AVG(s.revenue), 2) AS conversion_rate_pct
FROM sessions AS s
JOIN dim_month AS d ON s.month_order = d.month_number
GROUP BY d.month_number, d.month_name
ORDER BY d.month_number;
