-- Step 1: what is in the database?
-- Runs on data/processed/weather.db (SQLite). The same queries ran on the Udacity workspace (PostgreSQL).

-- name: distinct_cities
SELECT DISTINCT city, country
FROM city_list;

-- name: list_size
SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT city) AS city_names,
    COUNT(DISTINCT country) AS countries
FROM city_list;

-- name: duplicate_city_names
-- Same city name in more than one country. Filtering by city alone would mix them up.
SELECT city, country
FROM city_list
WHERE city IN (
    SELECT city
    FROM city_list
    GROUP BY city
    HAVING COUNT(*) > 1
)
ORDER BY city, country;
