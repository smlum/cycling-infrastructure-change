"""
harmonise_montreal.py
---------------------
Reclassify Montreal 2019 and 2024 network data from source_class to a
consistent canbics_class, correcting for the fact that the two source
datasets (PHAC 2019 and StatsCan 2024) applied Can-BICS labels differently.

The 2019 dataset uses numeric source codes; 2024 uses French text.
What 2019 called 'local_street_bikeway' (code 1) corresponds to
'chaussée désignée' in the 2024 source — but StatsCan labelled that
as 'shared_roadway', making a naive comparison invalid.

This script remaps both years from source_class directly, then overwrites
the parquet files so downstream code can treat all cities consistently.

Input / output:
    data/processed/montreal_2019.parquet  (overwritten in place)
    data/processed/montreal_2024.parquet  (overwritten in place)
"""

from pathlib import Path
import geopandas as gpd

DATA = Path("data/processed")

# Canonical source_class → canbics_class mapping for Montreal.
# Covers both the 2019 numeric codes and the 2024 French text labels.
# 'voie partagée bus-vélo' is intentionally omitted (bus-bike shared lane,
# not a cycling-specific facility).
SOURCE_REMAP = {
    # 2019 numeric codes
    "1": "local_street_bikeway",
    "3": "painted_bike_lane",
    "4": "cycle_track",
    "5": "bike_path",
    "6": "cycle_track",
    "7": "multi_use_path",
    # 2024 French source labels
    "chaussée désignée":                    "local_street_bikeway",
    "vélorue":                              "local_street_bikeway",
    "piste cyclable sur rue":               "cycle_track",
    "piste cyclable au niveau du trottoir": "cycle_track",
    "piste cyclable en site propre":        "bike_path",
    "bande cyclable":                       "painted_bike_lane",
    "sentier polyvalent":                   "multi_use_path",
}


def remap(path: Path) -> None:
    gdf = gpd.read_parquet(path)

    before = gdf["canbics_class"].value_counts().to_dict()
    gdf["canbics_class"] = gdf["source_class"].astype(str).map(SOURCE_REMAP)
    after = gdf["canbics_class"].value_counts(dropna=False).to_dict()

    unmapped = gdf["canbics_class"].isna().sum()
    print(f"\n{path.name}")
    print(f"  Before: {before}")
    print(f"  After:  {after}")
    if unmapped:
        missed = gdf.loc[gdf["canbics_class"].isna(), "source_class"].unique()
        print(f"  Unmapped source classes ({unmapped} rows): {list(missed)}")

    gdf.to_parquet(path)
    print(f"  Saved.")


def main():
    for year in [2019, 2024]:
        remap(DATA / f"montreal_{year}.parquet")


if __name__ == "__main__":
    main()
