# Weather Trends

How much warmer is it where I live, compared with the world? A comparison of local and global temperatures from 1854 to 2024, made for the Udacity Data Analyst Nanodegree and updated with current data.

**See the project:** https://lucasnvieira.github.io/weather-trends/ (interactive report)
**Step-by-step analysis:** [notebooks/weather_trends.ipynb](notebooks/weather_trends.ipynb)

## Findings

| Series | 1854–1900 | 1991–2020 | Change |
|---|---|---|---|
| Amsterdam | 8.86 °C | 10.33 °C | +1.47 °C |
| Global (land) | 8.15 °C | 9.49 °C | +1.34 °C |
| Campinas | 19.71 °C | 20.89 °C | +1.18 °C |
| Dublin | 8.50 °C | 9.68 °C | +1.18 °C |

- Campinas is about 11 °C hotter than the global average, but it warmed at a similar pace.
- All four series rose slowly during most of the 20th century and much faster from around 1980. Since 1970, the global land average warmed about 0.3 °C per decade.
- 2024 was the hottest year in the record, 2.27 °C above 1854–1900 on land.
- Two pairs of Brazilian cities in the Udacity database (Campinas/Guarulhos, Colombo/Curitiba) have identical series, because Berkeley Earth assigns each city to a point of a grid and they share a point.

## Structure

```
data/raw/udacity/          CSV exports from the Udacity database
data/raw/berkeley_earth/   monthly files from Berkeley Earth (scripts/download_berkeley_earth.py)
data/reference/            countries by continent, Brazilian city coordinates, outline of Brazil
data/processed/            clean tables and weather.db, a SQLite copy of the Udacity schema
sql/                       the queries of the report, runnable on weather.db
scripts/                   download and cleaning
notebooks/                 the full analysis, with explanations
app/                       the interactive report (plain HTML, CSS and JavaScript)
```

## Data

- **Berkeley Earth**, the source behind the Udacity database. Global land average up to December 2024; city files up to December 2020 (the January 2021 release, the latest available for cities). https://berkeleyearth.org/data/
- **Udacity**, Data Analyst Nanodegree, project "Explore Weather Trends": the city list and the original CSV exports.
- **Statistics Times**, countries by continents: https://statisticstimes.com/geography/countries-by-continents.php
- **Natural Earth**, country boundaries 1:50m (public domain), through the `world-atlas` package.

## Versions

See [CHANGELOG.md](CHANGELOG.md).

## Reproduce it on your computer

Only needed if you want to redo the analysis yourself. To just see the project, open the [interactive report](https://lucasnvieira.github.io/weather-trends/).

```bash
pip install -r requirements.txt
python scripts/download_berkeley_earth.py   # only needed to refresh data/raw/berkeley_earth/
python scripts/build_dataset.py             # raw -> data/processed/ and app/data.js
jupyter notebook notebooks/weather_trends.ipynb
python -m http.server 8765 --directory app  # then open http://localhost:8765 in your browser
```

The SQL files run on `data/processed/weather.db` with any SQLite client, for example `sqlite3 data/processed/weather.db < sql/02_brazil.sql`.

## License

Code (`scripts/`, `app/` except `app/data.js`, `sql/`, `notebooks/`): [MIT](LICENSE). The data in `data/` and `app/data.js` belongs to its sources above and is not covered by the MIT license.
