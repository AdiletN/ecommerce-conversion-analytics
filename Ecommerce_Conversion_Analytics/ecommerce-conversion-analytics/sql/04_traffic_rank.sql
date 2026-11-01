WITH traffic AS (
    SELECT traffictype AS traffic_type, COUNT(*) AS sessions,
           SUM(revenue) AS purchases,
           ROUND(100.0 * AVG(revenue), 2) AS conversion_rate_pct
    FROM sessions
    GROUP BY traffictype
)
SELECT *,
       RANK() OVER (ORDER BY conversion_rate_pct DESC) AS conversion_rank
FROM traffic
WHERE sessions >= 100  -- small segments are too noisy for direct ranking
ORDER BY conversion_rank, traffic_type;
