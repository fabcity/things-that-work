#!/usr/bin/env python3
"""
Fetch printforhelp.org/centers and update data/printforhelp_centers.json.
Run from the repo root:  python3 scripts/sync_printforhelp.py
"""
import json, re, datetime, sys
from pathlib import Path
try:
    import urllib.request
    from html.parser import HTMLParser
except ImportError:
    sys.exit("Python 3 required")

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
URL  = "https://printforhelp.org/centers"
OUT  = DATA / "printforhelp_centers.json"

class CenterParser(HTMLParser):
    """Parse center links from printforhelp.org/centers SSR HTML."""
    def __init__(self):
        super().__init__()
        self.centers = []
        self._in_link = False
        self._href = ""
        self._buf = []
        self._count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            d = dict(attrs)
            href = d.get("href", "")
            if "/centers/" in href and href != "/centers/new":
                self._in_link = True
                self._href = href
                self._buf = []

    def handle_endtag(self, tag):
        if tag == "a" and self._in_link:
            self._in_link = False
            text = "".join(self._buf).strip()
            if text:
                # Text looks like: "NameCity, State, COUNTRY"
                # Split on first occurrence of a city pattern
                self.centers.append({"raw": text, "url": self._href})

    def handle_data(self, data):
        if self._in_link:
            self._buf.append(data)


def parse_center(raw: str) -> dict:
    """Extract name, city, country from raw link text."""
    # Raw text: "NameCity, ST, COUNTRY" (no separator between name and city)
    # Countries at end: USA / MX / Venezuela
    for country in ("Venezuela", "USA", "MX"):
        if country in raw:
            # Everything after country tag is noise (phone/hours/verified)
            idx = raw.index(country)
            location = raw[idx:].split()[0]  # "Venezuela" / "USA" / "MX"
            # City is just before country — grab last comma-segment before it
            before = raw[:idx].strip().rstrip(",").strip()
            # Name heuristic: ends at first digit or known city pattern
            # Just store the full text cleaned; display is handled by the card
            return {"raw": raw, "country": location}
    return {"raw": raw, "country": "?"}


def main():
    print(f"Fetching {URL} …")
    req = urllib.request.Request(URL, headers={"User-Agent": "ttw-sync/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html_bytes = r.read()
    except Exception as e:
        sys.exit(f"Fetch failed: {e}")

    html = html_bytes.decode("utf-8", errors="replace")

    # Count
    m = re.search(r'(\d+)\s+centros de acopio', html)
    count = int(m.group(1)) if m else 0

    # Countries from filter UI
    countries_raw = re.findall(r'<li>\s*(MX|USA|Venezuela)\s*</li>', html)
    countries = list(dict.fromkeys(countries_raw))  # dedupe preserving order

    # Centers via parser
    parser = CenterParser()
    parser.feed(html)
    centers = [parse_center(c["raw"]) for c in parser.centers]

    out = {
        "updated":   datetime.date.today().isoformat(),
        "count":     count or len(centers),
        "countries": countries or ["USA", "MX", "VE"],
        "centers":   centers,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"Saved {out['count']} centers ({', '.join(out['countries'])}) → {OUT}")


if __name__ == "__main__":
    main()
