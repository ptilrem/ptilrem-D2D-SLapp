"""Cache hourly regional ERA5 averages for NO4 and NO5 (2024).

Run once from the repository root:
    python scripts/cache_weather_no4_no5.py

This uses the same 100 sampled coordinates per electricity region as the
Assignment 3 ERA5 caches. The saved files have one row per UTC hour.
"""

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOCATIONS_PATH = DATA_DIR / "region_locations.parquet"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
REGIONS = ("NO4", "NO5")
N_LOCATIONS = 100
BATCH_SIZE = 10


def download_region(region: str, locations: pd.DataFrame) -> pd.DataFrame:
    """Download 2024 ERA5 data and average each hour across 100 locations."""
    points = locations.loc[
        locations["area"] == region, ["latitude", "longitude"]
    ].head(N_LOCATIONS)

    if len(points) != N_LOCATIONS:
        raise ValueError(
            f"Expected {N_LOCATIONS} sampled locations for {region}; "
            f"found {len(points)}."
        )

    frames = []
    for start in range(0, N_LOCATIONS, BATCH_SIZE):
        batch = points.iloc[start : start + BATCH_SIZE]
        params = {
            "latitude": ",".join(batch["latitude"].astype(str)),
            "longitude": ",".join(batch["longitude"].astype(str)),
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "hourly": "temperature_2m,precipitation",
            "models": "era5",
            "timezone": "UTC",
        }

        response = requests.get(API_URL, params=params, timeout=180)
        response.raise_for_status()
        results = response.json()
        if isinstance(results, dict):
            results = [results]
        if len(results) != len(batch):
            raise ValueError(
                f"Unexpected API response: {len(results)} results "
                f"for {len(batch)} locations in {region}."
            )

        frames.extend(pd.DataFrame(result["hourly"]) for result in results)
        print(f"{region}: downloaded {start + len(batch)}/{N_LOCATIONS} locations")

    weather = (
        pd.concat(frames, ignore_index=True)
        .groupby("time", as_index=False)[["temperature_2m", "precipitation"]]
        .mean()
    )
    weather["time"] = pd.to_datetime(weather["time"], utc=True)
    return weather.sort_values("time").reset_index(drop=True)


def main() -> None:
    locations = pd.read_parquet(LOCATIONS_PATH)

    for region in REGIONS:
        output = DATA_DIR / f"weather_{region}_2024_100locations.parquet"
        if output.exists():
            print(f"{region}: already cached, skipping ({output})")
            continue

        weather = download_region(region, locations)
        weather.to_parquet(output, index=False)
        print(f"{region}: saved {len(weather):,} hourly rows to {output}")


if __name__ == "__main__":
    main()
