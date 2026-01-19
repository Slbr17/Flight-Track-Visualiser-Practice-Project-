"""
Reads Data.xlsx (time/latitude/longitude) and generates an interactive map.html
using Folium:
- Circle markers for each point
- A polyline connecting points in row order
- Pops open the generated HTML map in the default browser
"""

import pandas as pd
import folium
import webbrowser
from pathlib import Path

EXCEL_FILE = "Data.xlsx"   # your excel file
OUT_HTML = "map.html"      # output map file

# Load spreadsheet
df = pd.read_excel(EXCEL_FILE)

# Clean latitude/longitude:
# - Convert to string
# - Remove anything that isn't a digit, dot, or minus sign
# - Convert to numeric, forcing invalids to NaN
df["latitude"] = pd.to_numeric(df["latitude"].astype(str).str.replace(r"[^0-9\.\-]+", "", regex=True), errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"].astype(str).str.replace(r"[^0-9\.\-]+", "", regex=True), errors="coerce")

# Drop rows where lat/lon couldn't be parsed
df = df.dropna(subset=["latitude", "longitude"])

if df.empty:
    raise SystemExit("No valid latitude/longitude rows found.")

# Center map on the average location
center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

# Add points
for _, row in df.iterrows():
    # Popup uses row.get('time','') in case time column is missing
    popup_text = (
        f"Time: {row.get('time', '')}<br>"
        f"Lat: {row['latitude']}<br>"
        f"Lon: {row['longitude']}"
    )

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=4,
        popup=folium.Popup(popup_text, max_width=300),
        fill=True
    ).add_to(m)

#draws a line connecting points in order
points = df[["latitude", "longitude"]].values.tolist()
folium.PolyLine(points).add_to(m)

# Save the map and open it in the browser
m.save(OUT_HTML)
webbrowser.open(Path(OUT_HTML).resolve().as_uri())
