"""
extract_2024_networks.py
------------------------
Extract per-city 2024 cycling network data from the national CCND geopackage
and save as parquet files matching the format of the existing 2019 files.

Input:
    data/raw/canadian_cycling_network_database/cycle_network_2024.gpkg

Output:
    data/processed/victoria_2024.parquet
    data/processed/montreal_2024.parquet
    data/processed/toronto_2024.parquet
"""

from pathlib import Path
import geopandas as gpd

RAW = Path("data/raw/canadian_cycling_network_database/cycle_network_2024.gpkg")
OUT = Path("data/processed")

CITIES = {
    "victoria": "Victoria",
    "montreal": "Montreal",
    "toronto":  "Toronto",
}

KEEP_COLS = ["source_class", "municipality", "canbics_class", "year", "geometry"]

def main():
    print(f"Loading {RAW.name}...", end=" ", flush=True)
    gdf = gpd.read_file(RAW)
    gdf["year"] = 2024
    print(f"{len(gdf)} total segments.")

    for slug, name in CITIES.items():
        city_gdf = gdf[gdf["municipality"] == name][KEEP_COLS].reset_index(drop=True)
        out_path = OUT / f"{slug}_2024.parquet"
        city_gdf.to_parquet(out_path)
        print(f"  {name}: {len(city_gdf)} segments → {out_path.name}")

if __name__ == "__main__":
    main()
