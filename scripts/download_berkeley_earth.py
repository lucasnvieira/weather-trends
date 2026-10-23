"""Download the Berkeley Earth files used in this project into data/raw/berkeley_earth/.

Berkeley Earth is the original source of the Udacity database. Its city series are
not measured at the city itself: they are samples of a gridded temperature field,
so each city is mapped to the grid cell the Udacity/Kaggle extract used.

Usage:
    python scripts/download_berkeley_earth.py
"""

from pathlib import Path
from urllib.request import urlopen

BASE_URL = "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "berkeley_earth"

# Global land average (same series as Udacity's global_data table), updated monthly.
GLOBAL_FILE = "Global/Complete_TAVG_complete.txt"

# Grid cell of each city. Two pairs share a cell, which explains why their series
# are identical in the Udacity database (Campinas/Guarulhos and Colombo/Curitiba).
CITY_CELLS = {
    "Amsterdam": "52.24N-5.26E",
    "Dublin": "53.84N-6.82W",
    "Belo Horizonte": "20.09S-44.36W",
    "Campinas": "23.31S-46.31W",
    "Colombo": "24.92S-49.66W",
    "Curitiba": "24.92S-49.66W",
    "Fortaleza": "4.02S-37.77W",
    "Guarulhos": "23.31S-46.31W",
    "Manaus": "2.41S-60.27W",
    "Porto Alegre": "29.74S-51.69W",
    "Recife": "8.84S-34.86W",
    "Rio de Janeiro": "23.31S-42.82W",
    "Salvador": "13.66S-38.81W",
}


def download(remote_path: str, local_name: str) -> None:
    target = OUT_DIR / local_name
    if target.exists():
        print(f"skip  {local_name} (already downloaded)")
        return
    with urlopen(f"{BASE_URL}/{remote_path}", timeout=60) as response:
        target.write_bytes(response.read())
    print(f"saved {local_name}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    download(GLOBAL_FILE, "global_land.txt")
    for cell in sorted(set(CITY_CELLS.values())):
        download(f"Local/TAVG/Text/{cell}-TAVG-Trend.txt", f"{cell}.txt")


if __name__ == "__main__":
    main()
