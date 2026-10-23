-- Step 2: Brazilian cities.

-- name: brazil_cities
SELECT city
FROM city_list
WHERE country = 'Brazil'
ORDER BY city;

-- name: brazil_summary
-- The 2024 version filtered with HAVING after the GROUP BY. Filtering with WHERE first does the
-- same job and lets the database skip the other countries before grouping.
SELECT
    city,
    MIN(avg_temp) AS min_temp,
    MAX(avg_temp) AS max_temp,
    ROUND(AVG(avg_temp), 2) AS avg_temp,
    MIN(year) AS min_year,
    MAX(year) AS max_year,
    COUNT(avg_temp) AS non_null_years
FROM city_data
WHERE country = 'Brazil'
GROUP BY city
ORDER BY city;

-- name: identical_series
-- Pairs of cities whose yearly temperatures are equal in every common year.
SELECT
    a.city AS city_a,
    b.city AS city_b,
    COUNT(*) AS common_years,
    SUM(a.avg_temp = b.avg_temp) AS equal_years
FROM city_data AS a
JOIN city_data AS b
    ON a.year = b.year
    AND a.city < b.city
WHERE a.country = 'Brazil' AND b.country = 'Brazil'
GROUP BY a.city, b.city
HAVING SUM(a.avg_temp = b.avg_temp) = COUNT(*);
