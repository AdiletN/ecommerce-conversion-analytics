-- Each row = one session. Revenue is a purchase flag (0/1), NOT a money amount.
SELECT COUNT(*) AS sessions,
       SUM(revenue) AS purchases,
       ROUND(100.0 * SUM(revenue) / NULLIF(COUNT(*), 0), 2) AS conversion_rate_pct,
       ROUND(AVG(productrelated), 2) AS avg_product_pages,
       ROUND(AVG(bouncerates) * 100, 2) AS mean_session_bounce_metric_pct
FROM sessions;
