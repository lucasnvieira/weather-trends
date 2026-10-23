-- Step 3: local and global trends.

-- name: summary_by_series
SELECT
    'Global' AS series,
    MIN(avg_temp) AS min_temp,
    MAX(avg_temp) AS max_temp,
    ROUND(AVG(avg_temp), 2) AS avg_temp,
    MIN(year) AS min_year,
    MAX(year) AS max_year,
    COUNT(avg_temp) AS non_null_years
FROM global_data
UNION ALL
SELECT
    city,
    MIN(avg_temp),
    MAX(avg_temp),
    ROUND(AVG(avg_temp), 2),
    MIN(year),
    MAX(year),
    COUNT(avg_temp)
FROM city_data
WHERE city IN ('Campinas', 'Amsterdam', 'Dublin')
GROUP BY city;

-- name: moving_average
-- 4-year moving average with a window function, the step the 2024 version did in Excel.
-- The CASE keeps the first three years empty, as a 4-year average needs 4 values.
SELECT
    c.year,
    c.city,
    c.avg_temp,
    CASE WHEN COUNT(*) OVER w = 4 THEN ROUND(AVG(c.avg_temp) OVER w, 2) END AS ma_4_years
FROM city_data AS c
WHERE c.city = 'Campinas' AND c.year >= 1854
WINDOW w AS (ORDER BY c.year ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
ORDER BY c.year;

-- name: change_vs_1854_1900
-- How much warmer each series was in 1991-2020 (the latest 30 years with data for all
-- of them) than in 1854-1900. Comparing the same years keeps the comparison fair.
WITH all_series AS (
    SELECT 'Global' AS series, year, avg_temp FROM global_data
    UNION ALL
    SELECT city, year, avg_temp FROM city_data WHERE city IN ('Campinas', 'Amsterdam', 'Dublin')
),
baseline AS (
    SELECT series, AVG(avg_temp) AS base_temp
    FROM all_series
    WHERE year BETWEEN 1854 AND 1900
    GROUP BY series
),
recent AS (
    SELECT series, AVG(avg_temp) AS recent_temp
    FROM all_series
    WHERE year BETWEEN 1991 AND 2020
    GROUP BY series
)
SELECT
    b.series,
    ROUND(b.base_temp, 2) AS avg_1854_1900,
    ROUND(r.recent_temp, 2) AS avg_1991_2020,
    ROUND(r.recent_temp - b.base_temp, 2) AS change
FROM baseline AS b
JOIN recent AS r USING (series)
ORDER BY change DESC;
