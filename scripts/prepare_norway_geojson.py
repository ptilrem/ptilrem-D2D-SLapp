"""Prepare a single national NO polygon from the already-generated EL polygons.

Run from the repository root: python scripts/prepare_norway_geojson.py
"""
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
GEOJSON_DIR = ROOT / "data" / "geojson"
price_path = GEOJSON_DIR / "price_areas.geojson"
norway_path = GEOJSON_DIR / "norway.geojson"

# Dissolve the five EL polygons into one (possibly multipart) national shape.
price_areas = gpd.read_file(price_path).to_crs(epsg=4326)
norway = price_areas.dissolve()
norway["region"] = "Norway"
norway[["region", "geometry"]].to_file(norway_path, driver="GeoJSON")

print(f"Created {norway_path} with {len(norway)} feature(s).")
