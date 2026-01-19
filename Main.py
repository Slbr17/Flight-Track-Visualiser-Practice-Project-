"""
Main UI entry point.

Flow:
1) User pastes a FlightAware track log URL.
2) Playwright loads the page (so JS-rendered content is included).
3) Save fully-rendered HTML to flightData.html.
4) Import Scalp -> creates Data.xlsx from flightData.html
5) Import display -> creates map.html from Data.xlsx and opens it
6) Import timeInEachCountry -> prints time-by-country summary from Data.xlsx
7) Cleanup temp files
"""

from os import remove
from playwright.sync_api import sync_playwright
import tkinter as tk
from tkinter import messagebox

def start_program_with_url(url):
    """
    Runs the full pipeline using the provided URL.

    Note: this disables UI controls while running so the user can't re-trigger it.
    """

    url_entry.config(state="disabled")
    send_button.config(state="disabled")

    print("Program started with URL:", url)

    # Use Playwright to load the page and wait until network is idle
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()

    # Save the rendered HTML for the next stage (Scalp.py) to parse
    with open("flightData.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved rendered HTML")

    # Importing these modules executes their top-level code immediately.
    # In this project, each module "does its job" at import time.
    import Scalp                # parses flightData.html -> writes Data.xlsx
    import display              # reads Data.xlsx -> writes map.html and opens it
    import timeInEachCountry    # reads Data.xlsx -> prints time-by-country

    # Cleanup generated files.
    remove("Data.xlsx")
    remove("flightData.html")
    remove("map.html")

    messagebox.showinfo("Progam Done", "The program has finished")
    root.destroy()

def on_send():
    """
    Handler for the "Done" button.
    Validates URL and starts the pipeline.
    """
    url = url_entry.get().strip()
    
    if not url:
        messagebox.showwarning("Input Error", "Please enter a URL.")
        return
    
    start_program_with_url(url)
    

# Tkinter UI setup

root = tk.Tk()
root.title("URL Input")
root.geometry("400x200")

# Description label
description_label = tk.Label(
    root,
    text="Please got to FlightAware.com and get a Flight Track Log.\nThen copy the url and paste it down below.",
    wraplength=350,
    justify="center"
)
description_label.pack(pady=15)

# URL entry box
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

# Done button
send_button = tk.Button(root, text="Done", command=on_send)
send_button.pack(pady=10)

root.mainloop()
