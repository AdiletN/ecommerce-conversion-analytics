SELECT visitortype AS visitor_type,
       COUNT(*) AS sessions,
       SUM(revenue) AS purchases,
       ROUND(100.0 * AVG(revenue), 2) AS conversion_rate_pct
FROM sessions
GROUP BY visitortype
ORDER BY sessions DESC;
