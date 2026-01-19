"""
- Read points from Data.xlsx (time/lat/lon).
- Convert each point to a GeoData.
- Spatial-join points into country polygons (shapefile).
- Sort by time and compute the time delta to the next point.
- Attribute each segment's duration to the starting point's country.
- Sum durations by country and print the totals.

Notes:
- Times appear to be "time of day" only (HH:MM:SS), not full dates.
- If the track crosses midnight, deltas go negative; we fix by +24h.
- Points over ocean or outside polygons are labeled "Offshore".
"""

import pandas as pd
import geopandas as gpd

EXCEL_FILE = "Data.xlsx"

# Path to your shapefile.
# This requires the full shapefile set (.shp + .dbf + .shx + .prj, etc.)
# Downloaded from: https://www.naturalearthdata.com/
COUNTRIES_SHP = r"countries/ne_110m_admin_0_countries.shp"

# Column in the shapefile that holds the country name.
# In Natural Earth, this is often "NAME", but it can vary by dataset.
COUNTRY_COL = "NAME"

# ---------- Load Excel ----------
df = pd.read_excel(EXCEL_FILE)

# Clean time strings (e.g. "01:53:18\r") by stripping whitespace
df["time"] = df["time"].astype(str).str.strip()

# Parse as time-of-day (HH:MM:SS). Invalid parses become NaN.
df["time_dt"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce")

# Clean coordinates
df["latitude"] = pd.to_numeric(
    df["latitude"].astype(str).str.replace(r"[^0-9\.\-]+", "", regex=True),
    errors="coerce"
)
df["longitude"] = pd.to_numeric(
    df["longitude"].astype(str).str.replace(r"[^0-9\.\-]+", "", regex=True),
    errors="coerce"
)

# Removes invalid rows
df = df.dropna(subset=["time_dt", "latitude", "longitude"]).copy()

if df.empty:
    raise SystemExit("No valid rows after cleaning time/lat/long.")

# ---------- Make GeoData points ----------
# Points are created from lon/lat and set to WGS84 (EPSG code = 4326)
points = gpd.GeoData(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326"
)

# ---------- Load countries polygons ----------
countries = gpd.read_file(COUNTRIES_SHP)

# CRS must exist to align coordinates correctly
if countries.crs is None:
    raise ValueError("Countries shapefile CRS is missing (check the .prj file).")

# Reproject countries to match points CRS if needed
if countries.crs != points.crs:
    countries = countries.to_crs(points.crs)

# Assign country to each point
# predicate="within" means point must fall inside a polygon
joined = gpd.sjoin(
    points,
    countries[[COUNTRY_COL, "geometry"]],
    how="left",
    predicate="within"
)

# If no country matched (e.g., over water), label as Offshore
joined["country"] = joined[COUNTRY_COL].fillna("Offshore")


# Sort Data by time
joined = joined.sort_values("time_dt").reset_index(drop=True)

# ---------- Compute time difference between points ----------
# Shift time column to get the next timestamp per row
joined["next_time"] = joined["time_dt"].shift(-1)

# Delta in seconds between current time and next time
joined["delta_sec"] = (joined["next_time"] - joined["time_dt"]).dt.total_seconds()

# If flight crosses midnight, delta becomes negative (e.g., 23:59 -> 00:01).
# Fix by adding 24 hours (assumes only one midnight crossing between samples).
joined.loc[joined["delta_sec"] < 0, "delta_sec"] += 24 * 3600

# Drop the last row (no next point) and any invalid deltas
segments = joined.iloc[:-1].copy()
segments = segments.dropna(subset=["delta_sec"])
segments = segments[segments["delta_sec"] >= 0]

# ---------- Sum time by country ----------
# Group by country, summing segment durations
time_by_country = (
    segments.groupby("country", as_index=False)["delta_sec"].sum()
    .sort_values("delta_sec", ascending=False)
)

# ---------- Output ----------
time_by_country["time_hms"] = pd.to_timedelta(
    time_by_country["delta_sec"], unit="s"
).astype(str)

print(time_by_country)