#!/usr/bin/env python3
"""Refresh data/makers4venezuela_stats.json from the Makers·Venezuela Supabase registry.
Public anon key (read-only dashboard views; safe in repo). Run: python3 scripts/sync_makers4venezuela.py"""
import json, datetime, sys, urllib.request
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "makers4venezuela_stats.json"
BASE = "https://gwydqpbyopmxqjhrfwxi.supabase.co/rest/v1"
KEY = "sb_publishable_y1Dnx36uomXrlGhpkmmytQ_cZSvfrPx"  # public anon key (read-only)

def fetch(view):
    req = urllib.request.Request(f"{BASE}/{view}?select=*",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def main():
    rows = fetch("dashboard_events")  # public view: qty_fabricated, qty_delivered, country, org
    fab = sum(int(r.get("qty_fabricated") or 0) for r in rows)
    ent = sum(int(r.get("qty_delivered") or 0) for r in rows)
    skip = {"", "Otro", "Sin país"}
    countries = len({(r.get("country") or "").strip() for r in rows} - skip)
    orgs = len({(r.get("org") or "").strip() for r in rows} - {""})
    out = {"updated": datetime.date.today().isoformat(),
           "source": "https://makers4venezuela.github.io/dashboard",
           "fabricated": fab, "delivered": ent, "orgs": orgs, "countries": countries}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, out)

if __name__ == "__main__":
    main()
