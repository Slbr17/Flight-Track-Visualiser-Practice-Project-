# Flight Track Visualiser (Practice Project)

> **Important:** This is a **practice / learning project**, not a production-ready tool.  
> If you want **legitimate, supported access** to FlightAware flight data, you should use their official **AeroAPI** service instead of scraping.

---

## Overview

This project is a small end-to-end experiment that:

1. Takes a **FlightAware Flight Track Log URL** from the user.
2. Uses **Playwright** to load the page and save the fully rendered HTML.
3. Scrapes the HTML to extract a sequence of:
   - timestamps  
   - latitude  
   - longitude
4. Saves the extracted data into an Excel file (`Data.xlsx`).
5. Builds an interactive **Folium** map (`map.html`) showing the flight path.
6. Estimates how long the aircraft spent in each country using **GeoPandas** and a country shapefile.

---

## How it works (high-level)

1. **Main.py**
   - Shows a simple Tkinter UI asking for a FlightAware Flight Track Log URL.
   - Uses Playwright to load the page and save `flightData.html`.
   - Calls into the other modules to:
     - parse HTML → `Data.xlsx`
     - create `map.html`
     - print a “time in each country” summary.
   - Cleans up temporary files.

2. **Scalp.py**
   - Reads `flightData.html`.
   - Locates rows using weekday labels (Mon, Tue, Wed, …).
   - Uses fixed character offsets around those labels to “slice out” time / lat / lon.
   - Writes them to `Data.xlsx`.

3. **display.py**
   - Reads `Data.xlsx` with Pandas.
   - Cleans numeric latitude/longitude values.
   - Generates a Folium map:
     - circle markers for each point
     - a polyline connecting them
   - Saves `map.html` and opens it in the browser.

4. **timeInEachCountry.py**
   - Loads `Data.xlsx` into a GeoDataFrame.
   - Runs a spatial join against a world-countries shapefile.
   - Sorts points by time and estimates the time between successive points.
   - Sums durations by country and prints a table.

---

## Requirements

Python dependencies (example):

- `playwright`
- `pandas`
- `openpyxl`
- `folium`
- `geopandas`
- `shapely`
- `tkinter` (usually included with standard Python on many platforms)

You’ll also need:

- A **world countries shapefile**, e.g. from Natural Earth, placed under `countries/`
  - The code expects `countries/ne_110m_admin_0_countries.shp`
  - And a name field called `NAME` (configurable in `timeInEachCountry.py`)
