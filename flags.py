"""Module providing a functionality to web scrape Czech wikipedia page with flags."""

import os
import csv
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

# Constants
URL = "https://cs.wikipedia.org/wiki/Seznam_vlajek_st%C3%A1t%C5%AF_sv%C4%9Bta"
WIKI_BASE = "https://cs.wikipedia.org"
OUTPUT_DIR = "flags"
CSV_FILENAME = "flags.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    """Main method"""
    # Download the page
    response = requests.get(URL, timeout=1)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Go through all relevant tables
    tables = soup.select("table.wikitable")
    print(f"Found {len(tables)} wikitable(s).")
    flag_entries = process_wiki_table(tables[0])

    # Save CSV mapping
    csv_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["State", "Filename"])
        writer.writerows(flag_entries)

    print(f"\nCSV mapping saved to: {csv_path}")

def process_wiki_table(table):
    """Reads wikitable and returns list of flags associated country."""
    flag_entries = []
    for row in table.select("tr"):
        cells = row.find_all("td")
        if len(cells) >= 3:
            img_tag = cells[0].find("img")  # image is in the first <td>
            state_name = cells[2].get_text(strip=True)  # 3rd cell (index 2)

            if img_tag and img_tag.get("src"):
                img_src = img_tag["src"]
                if img_src.startswith("//"):
                    img_url = "https:" + img_src
                else:
                    img_url = urljoin(WIKI_BASE, img_src)

                # Clean filename
                extension = os.path.splitext(img_url)[-1]
                safe_name = state_name.replace(" ", "_").replace("/", "_").replace("-", "_")
                filename = unidecode(f"{safe_name}{extension}".lower())
                filepath = os.path.join(OUTPUT_DIR, filename)

                # Download image
                try:
                    img_data = requests.get(img_url, timeout=1).content
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    print(f"Saved: {filename}")
                    flag_entries.append((state_name, filename))
                except IOError as e:
                    print(f"Failed to download {img_url}: {e}")
    return flag_entries


if __name__ == "__main__":
    main()
