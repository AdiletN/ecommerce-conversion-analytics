-- Check if the visitor gap looks similar across traffic types.
-- Only show groups with at least 100 sessions.
WITH traffic_groups AS (
    SELECT visitortype AS visitor_type,
           traffictype AS traffic_type,
           COUNT(*) AS sessions,
           SUM(revenue) AS purchases
    FROM sessions
    WHERE visitortype IN ('New_Visitor', 'Returning_Visitor')
    GROUP BY visitortype, traffictype
),
visitor_totals AS (
    SELECT visitortype AS visitor_type,
           COUNT(*) AS total_visitor_sessions,
           ROUND(100.0 * AVG(revenue), 2) AS visitor_conversion_pct
    FROM sessions
    WHERE visitortype IN ('New_Visitor', 'Returning_Visitor')
    GROUP BY visitortype
)
SELECT g.visitor_type, g.traffic_type,
       g.sessions, g.purchases,
       ROUND(100.0 * g.purchases / g.sessions, 2) AS conversion_rate_pct,
       ROUND(100.0 * g.sessions / v.total_visitor_sessions, 2) AS share_of_visitor_sessions_pct,
       v.visitor_conversion_pct
FROM traffic_groups AS g
JOIN visitor_totals AS v ON g.visitor_type = v.visitor_type
WHERE g.sessions >= 100
ORDER BY g.visitor_type, g.sessions DESC, g.traffic_type;
