"""
Reads "flightData.html" and extracts a sequence of:
- time
- latitude
- longitude

Then writes them to Data.xlsx for later steps.

Current approach:
- Finds which weekday string (Mon/Tue/...) appears most often and uses those match
  positions as "row anchors".
- From each anchor, slices fixed offsets from the HTML to get time/lat/lon.

Important:
This is a is very brittle!
If the HTML shifts, offsets will need adjusting.
I am just not farmilar enough with HTML to solve it another way.
"""

from pathlib import Path
import re
from openpyxl import Workbook


HTML_PATH = "flightData.html"

# How many characters to capture for each field after jumping to a position.
TIME = 8      # e.g. "01:53:18"
TO_LAT = 116  # number of chars to jump from end of time to latitude start
LAT = 7       # number of chars to capture for latitude
TO_LONG = 114 # jump to longitude start
LONG = 8      # number of chars to capture for longitude

# Read the HTML that Playwright saved
html = Path(HTML_PATH).read_text(encoding="utf-8", errors="ignore")

# -------------------------------------------------------------------
# Find the "best" weekday anchor list
# -------------------------------------------------------------------
# We look for every occurrence of each weekday label (Mon/Tue/...).
# Then we pick the day with the most matches — assuming that's the
# current flight row marker in the log.
daysOfWeek = {
    "Mon": 0, 
    "Tue": 0, 
    "Wed": 0, 
    "Thu": 0, 
    "Fri": 0, 
    "Sat": 0, 
    "Sun": 0
}

for day in daysOfWeek.keys():
    matches = list(re.finditer(re.escape(day), html))
    daysOfWeek[day] = matches

# Pick the weekday that occurred the most in the HTML
matches = max(daysOfWeek.values(), key=len)

# -------------------------------------------------------------------
# Write output to Excel
# -------------------------------------------------------------------
wb = Workbook()
ws = wb.active
ws.title = "Extracted"
ws.append(["time", "latitude", "longitude"])

# For each weekday anchor occurrence, slice out time/lat/lon
for i, m in enumerate(matches, start=1):
    # Capture time right after the weekday marker
    start = m.end() + 1
    end = start + TIME
    time = html[start:end]

    # Jump forward to latitude and slice it
    start = end + TO_LAT
    end = start + LAT
    latitude = html[start:end]

    # Jump forward to longitude and slice it
    start = end + TO_LONG
    end = start + LONG
    longitude = html[start:end]

    # Cleanup artifacts from HTML tags that sometimes get caught
    longitude = longitude.replace("<", "").replace("/", "")


    ws.append([time, latitude, longitude])

wb.save("Data.xlsx")
