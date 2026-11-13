-- Behavioral association only: more pages does not prove higher conversion causally.
SELECT product_page_bucket AS page_bucket, COUNT(*) AS sessions,
       SUM(revenue) AS purchases,
       ROUND(100.0 * AVG(revenue), 2) AS conversion_rate_pct
FROM sessions
GROUP BY product_page_bucket
ORDER BY CASE product_page_bucket WHEN '0' THEN 1 WHEN '1–4' THEN 2
    WHEN '5–14' THEN 3 WHEN '15–29' THEN 4 ELSE 5 END;
