#!/usr/bin/env python3
"""Refresh data/desaparecidos_stats.json from the citizen missing-persons registry API.
Public read-only endpoint. Run: python3 scripts/sync_desaparecidos.py"""
import json, datetime, urllib.request
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "desaparecidos_stats.json"
API = "https://desaparecidos-terremoto-api.theempire.tech/api/metricas"

def main():
    req = urllib.request.Request(API, headers={"User-Agent": "ttw-fabcity-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        g = json.loads(r.read()).get("geo", {})
    nums = {"total": int(g.get("totalPersonas") or 0),
            "sin_contacto": int(g.get("sinContacto") or 0),
            "localizados": int(g.get("localizados") or 0)}
    if nums["total"] == 0:
        print("desaparecidos: empty response, skipping"); return
    prev = {}
    if OUT.exists():
        try: prev = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception: prev = {}
    if all(prev.get(k) == v for k, v in nums.items()):
        print("desaparecidos: no change", nums); return
    out = {"updated": datetime.date.today().isoformat(), "source": API, **nums}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("desaparecidos: updated", out)

if __name__ == "__main__":
    main()
