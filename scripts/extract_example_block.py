"""
extract_example_block.py
------------------------
Extract a single dissemination block near downtown Montreal to use as a
concrete example in the method diagram.

Input:
    data/raw/ldb_000b21a_e/ldb_000b21a_e.shp  (EPSG:3347)

Output:
    data/example_block.geojson   (single polygon, EPSG:4326, commits to git)
"""

from pathlib import Path
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point

RAW = Path("data/raw")
OUT = Path("data")

SHP = RAW / "ldb_000b21a_e" / "ldb_000b21a_e.shp"
FILE_CRS = "EPSG:3347"  # NAD83 Statistics Canada Lambert

# Target point on the Plateau, close to the REV on Saint-Denis (EPSG:4326)
TARGET_LON, TARGET_LAT = -73.5838, 45.5230

# Bbox in EPSG:4326 — reprojected to EPSG:3347 for file reading
BBOX_4326 = (-73.60, 45.51, -73.57, 45.54)

HC_CLASSES  = {"cycle_track", "bike_path", "local_street_bikeway"}
SEARCH_M    = 600   # radius for nearby network segments

def main():
    transformer = Transformer.from_crs("EPSG:4326", FILE_CRS, always_xy=True)
    minx, miny = transformer.transform(BBOX_4326[0], BBOX_4326[1])
    maxx, maxy = transformer.transform(BBOX_4326[2], BBOX_4326[3])

    # --- Extract example block ---
    print(f"Loading blocks...", end=" ", flush=True)
    gdf = gpd.read_file(SHP, bbox=(minx, miny, maxx, maxy)).to_crs("EPSG:4326")
    print(f"{len(gdf)} blocks loaded.")

    if gdf.empty:
        raise RuntimeError("No blocks found — check bbox.")

    target = Point(TARGET_LON, TARGET_LAT)
    match = gdf[gdf.geometry.contains(target)]

    if match.empty:
        print("Target not inside any block — using nearest centroid.")
        gdf["dist"] = gdf.geometry.centroid.distance(target)
        match = gdf.nsmallest(1, "dist")

    block = match.iloc[[0]][["geometry"]].reset_index(drop=True)
    block.to_file(OUT / "example_block.geojson", driver="GeoJSON")
    print(f"Saved example_block.geojson  bounds: {block.geometry.iloc[0].bounds}")

    # --- Extract nearby high-comfort segments ---
    block_m  = block.to_crs(FILE_CRS)
    centroid = block_m.geometry.iloc[0].centroid
    search   = centroid.buffer(SEARCH_M)
    print(f"Centroid (EPSG:3347): {centroid.x:.0f}, {centroid.y:.0f}")

    print("Loading Montreal 2024 network...", end=" ", flush=True)
    network = gpd.read_parquet(Path("data/processed/montreal_2019.parquet"))
    print(f"{len(network)} total segments, CRS: {network.crs.to_epsg()}")

    # Force CRS match before intersects — parquet CRS metadata can diverge
    network = network.set_crs(FILE_CRS, allow_override=True)
    network_hc = network[network["canbics_class"].isin(HC_CLASSES)]
    print(f"Sample network bounds: {network_hc.geometry.iloc[0].bounds}")

    nearby = network_hc[network_hc.geometry.intersects(search)].to_crs("EPSG:4326")
    print(f"{len(nearby)} high-comfort segments found within {SEARCH_M} m.")

    nearby[["canbics_class", "geometry"]].to_file(
        OUT / "example_network.geojson", driver="GeoJSON"
    )
    print(f"Saved example_network.geojson")

if __name__ == "__main__":
    main()
