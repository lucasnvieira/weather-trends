"""Turn the raw files into the clean tables used by the notebook and the web report.

Inputs (data/raw/ and data/reference/):
    udacity/city_list.csv              city and country list exported from the Udacity database
    berkeley_earth/*.txt               monthly anomalies per grid cell (scripts/download_berkeley_earth.py)
    reference/countries_by_continent.csv
    reference/brazil_cities.csv        coordinates from Excel's Geography data type

Outputs:
    data/processed/annual_temperatures.csv   one row per series and year
    data/processed/cities_by_continent.csv   city list with a standardized country and continent
    data/processed/weather.db                SQLite copy of the Udacity schema, so sql/*.sql can run
    app/data.js                              everything the web report needs, embedded as JavaScript

Usage:
    python scripts/build_dataset.py
"""

import json
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REFERENCE = ROOT / "data" / "reference"
PROCESSED = ROOT / "data" / "processed"
APP = ROOT / "app"

# Same mapping as scripts/download_berkeley_earth.py
CITIES = {
    # city: (country, grid cell)
    "Amsterdam": ("Netherlands", "52.24N-5.26E"),
    "Dublin": ("Ireland", "53.84N-6.82W"),
    "Belo Horizonte": ("Brazil", "20.09S-44.36W"),
    "Campinas": ("Brazil", "23.31S-46.31W"),
    "Colombo": ("Brazil", "24.92S-49.66W"),
    "Curitiba": ("Brazil", "24.92S-49.66W"),
    "Fortaleza": ("Brazil", "4.02S-37.77W"),
    "Guarulhos": ("Brazil", "23.31S-46.31W"),
    "Manaus": ("Brazil", "2.41S-60.27W"),
    "Porto Alegre": ("Brazil", "29.74S-51.69W"),
    "Recife": ("Brazil", "8.84S-34.86W"),
    "Rio de Janeiro": ("Brazil", "23.31S-42.82W"),
    "Salvador": ("Brazil", "13.66S-38.81W"),
}

# City names fixed while cleaning (the Udacity list capitalizes "De").
CITY_SPELLING = {"Rio De Janeiro": "Rio de Janeiro"}

# Country names in the Udacity list that are spelled differently in the continent list.
# In the 2024 version this step was done by hand in Excel before the VLOOKUP.
COUNTRY_ALIASES = {
    "Bolivia": "Bolivia (Plurinational State of)",
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Congo (Democratic Republic Of The)": "Democratic Republic of the Congo",
    "Côte D'Ivoire": "Côte d’Ivoire",
    "Czech Republic": "Czechia",
    "Guinea Bissau": "Guinea-Bissau",
    "Iran": "Iran (Islamic Republic of)",
    "Laos": "Lao People's Democratic Republic",
    "Macedonia": "North Macedonia",
    "Moldova": "Republic of Moldova",
    "Russia": "Russian Federation",
    "South Korea": "Republic of Korea",
    "Syria": "Syrian Arab Republic",
    "Tanzania": "United Republic of Tanzania",
    "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "United States": "United States of America",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
    "Vietnam": "Viet Nam",
}


def read_berkeley(path: Path) -> tuple[float, pd.DataFrame]:
    """Return the 1951-1980 absolute temperature and the monthly anomalies of one file."""
    text = path.read_text(encoding="latin-1")
    baseline = float(re.search(r"Jan 1951-Dec 1980 absolute temperature \(C\):\s+([-\d.]+)", text).group(1))
    rows = [line.split()[:3] for line in text.splitlines() if line.strip() and not line.startswith("%")]
    monthly = pd.DataFrame(rows, columns=["year", "month", "anomaly"]).astype(float)
    monthly[["year", "month"]] = monthly[["year", "month"]].astype(int)
    return baseline, monthly


def annual_series(path: Path) -> pd.DataFrame:
    """Annual mean temperature, kept only for years with all 12 months.

    A year with missing months is biased by the season that is missing (the Udacity
    extract ends in September 2013, so its 2013 value has no spring in Campinas).
    """
    baseline, monthly = read_berkeley(path)
    annual = monthly.groupby("year").agg(anomaly=("anomaly", "mean"), months=("anomaly", "count"))
    annual = annual[annual["months"] == 12].reset_index()
    annual["avg_temp"] = (baseline + annual["anomaly"]).round(2)
    return annual[["year", "avg_temp", "months"]]


def build_annual() -> pd.DataFrame:
    frames = []
    glob = annual_series(RAW / "berkeley_earth" / "global_land.txt")
    frames.append(glob.assign(series="Global", country=None, cell=None))
    for city, (country, cell) in CITIES.items():
        frames.append(annual_series(RAW / "berkeley_earth" / f"{cell}.txt").assign(series=city, country=country, cell=cell))
    annual = pd.concat(frames, ignore_index=True)
    return annual[["series", "country", "cell", "year", "avg_temp"]]


def build_continents() -> pd.DataFrame:
    cities = pd.read_csv(RAW / "udacity" / "city_list.csv")
    cities["city"] = cities["city"].replace(CITY_SPELLING)
    continents = pd.read_csv(REFERENCE / "countries_by_continent.csv")
    cities["country_std"] = cities["country"].replace(COUNTRY_ALIASES)
    merged = cities.merge(continents, left_on="country_std", right_on="country", how="left", suffixes=("", "_ref"))
    missing = merged[merged["continent"].isna()]
    if not missing.empty:
        raise ValueError(f"Countries without a continent: {sorted(missing['country'].unique())}")
    # Same grouping as the 2024 version: North and South America counted together.
    merged["continent_group"] = merged["continent"].replace({"North America": "Americas", "South America": "Americas"})
    return merged[["city", "country", "continent", "continent_group"]]


def build_database(annual: pd.DataFrame, cities: pd.DataFrame) -> None:
    db_path = PROCESSED / "weather.db"
    db_path.unlink(missing_ok=True)
    with sqlite3.connect(db_path) as con:
        cities[["city", "country"]].to_sql("city_list", con, index=False)
        city_data = annual[annual["series"] != "Global"].rename(columns={"series": "city"})
        city_data[["year", "city", "country", "avg_temp"]].to_sql("city_data", con, index=False)
        annual[annual["series"] == "Global"][["year", "avg_temp"]].to_sql("global_data", con, index=False)


def brazil_outline_path() -> dict:
    """Project the Natural Earth outline of Brazil to SVG path data (equirectangular, cos(lat) scaled)."""
    geometry = json.loads((REFERENCE / "brazil_outline.geojson").read_text())["geometry"]
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    lon0, lon1, lat0, lat1 = -74.5, -28.5, -34.5, 6.0
    kx = np.cos(np.radians(-14))
    width = (lon1 - lon0) * kx * 10
    height = (lat1 - lat0) * 10

    def xy(lon, lat):
        return round((lon - lon0) * kx * 10, 1), round((lat1 - lat) * 10, 1)

    parts = []
    for polygon in polygons:
        ring = polygon[0]
        if len(ring) < 8:  # skip tiny islands
            continue
        points = [xy(lon, lat) for lon, lat in ring]
        parts.append("M" + "L".join(f"{x},{y}" for x, y in points) + "Z")
    return {"path": "".join(parts), "width": round(width, 1), "height": round(height, 1),
            "lon0": lon0, "lat1": lat1, "kx": round(float(kx), 5), "scale": 10}


def build_app_data(annual: pd.DataFrame, cities: pd.DataFrame) -> None:
    series = {}
    for name, frame in annual.groupby("series", sort=False):
        series[name] = {
            "country": frame["country"].iloc[0],
            "cell": frame["cell"].iloc[0],
            "years": frame["year"].tolist(),
            "temps": frame["avg_temp"].tolist(),
        }
    brazil = pd.read_csv(REFERENCE / "brazil_cities.csv")
    brazil["cell"] = brazil["city"].map(lambda c: CITIES[c][1])
    stats = (annual[annual["country"] == "Brazil"].groupby("series")["avg_temp"]
             .agg(["min", "max", "mean"]).round(2).rename(columns={"mean": "avg"}))
    brazil = brazil.join(stats, on="city")
    counts = cities["continent_group"].value_counts()
    duplicates = cities[cities["city"].duplicated(keep=False)].sort_values(["city", "country"])
    data = {
        "series": series,
        "brazil": brazil.to_dict(orient="records"),
        "continents": [{"continent": k, "cities": int(v)} for k, v in counts.items()],
        "cityCount": int(len(cities)),
        "cityNames": int(cities["city"].nunique()),
        "countryCount": int(cities["country"].nunique()),
        "duplicates": duplicates[["city", "country"]].to_dict(orient="records"),
        "brazilMap": brazil_outline_path(),
    }
    APP.mkdir(exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (APP / "data.js").write_text(
        "// Generated by scripts/build_dataset.py. Do not edit by hand.\n"
        f"window.WEATHER = {payload};\n",
        encoding="utf-8",
    )


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    annual = build_annual()
    cities = build_continents()
    annual.to_csv(PROCESSED / "annual_temperatures.csv", index=False)
    cities.to_csv(PROCESSED / "cities_by_continent.csv", index=False)
    build_database(annual, cities)
    build_app_data(annual, cities)
    print(f"{annual['series'].nunique()} series, {len(annual)} rows; "
          f"global {annual[annual['series'] == 'Global']['year'].max()}, "
          f"cities {annual[annual['series'] != 'Global']['year'].max()}")
    print(cities["continent_group"].value_counts().to_string())


if __name__ == "__main__":
    main()
