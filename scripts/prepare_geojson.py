"""Inspect geographic datasets before converting them to GeoJSON."""

from pathlib import Path
import zipfile
import geopandas as gpd
from tempfile import TemporaryDirectory

# Find the data directory relative to this script.
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

print(f"Looking for geographic files in: {DATA_DIR}\n")

# Find standalone shapefiles and ZIP archives.
shapefiles = sorted(DATA_DIR.rglob("*.shp"))
archives = sorted(DATA_DIR.rglob("*.zip"))

if not shapefiles and not archives:
    print("No shapefiles or ZIP archives found.")

# Inspect standalone shapefiles.
for path in shapefiles:
    print(f"Shapefile: {path.relative_to(ROOT)}")

# Inspect ZIP archives without extracting them.
for path in archives:
    print(f"\nArchive: {path.relative_to(ROOT)}")

    with zipfile.ZipFile(path) as archive:
        for filename in archive.namelist():
            if filename.lower().endswith(".shp"):
                print(f"  Contains shapefile: {filename}")



# Create a folder for the converted GeoJSON files.
OUTPUT_DIR = DATA_DIR / "geojson"
OUTPUT_DIR.mkdir(exist_ok=True)

for archive_path in archives:
    # Extract and read each shapefile.
    with TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(temp_dir)

        shp_path = next(Path(temp_dir).rglob("*.shp"))
        gdf = gpd.read_file(shp_path)

        # Keep only the relevant geographic attributes.
        if "budomr" in gdf.columns:
            gdf = gdf[["budomr", "geometry"]].copy()

            # Normalize "NO 1" to "NO1" for matching with NVE data.
            gdf["region"] = gdf["budomr"].str.replace(
                " ", "", regex=False
            )
            gdf = gdf[["region", "geometry"]]
            filename = "price_areas.geojson"

        elif "REGION" in gdf.columns:
            gdf = gdf[["REGION", "REGIONNAVN", "geometry"]].copy()
            gdf = gdf.rename(columns={
                "REGION": "region",
                "REGIONNAVN": "name"
            })
            filename = "nve_admin_regions.geojson"

        else:
            print(f"Skipping unrecognized file: {archive_path.name}")
            continue

        # Convert projected coordinates to longitude/latitude.
        gdf = gdf.to_crs(epsg=4326)

        # Export polygons and their region identifiers.
        output_path = OUTPUT_DIR / filename
        gdf.to_file(output_path, driver="GeoJSON", index=False)

        print(f"Created: {output_path.relative_to(ROOT)}")
        print(f"Regions: {gdf['region'].tolist()}\n")

