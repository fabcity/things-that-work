#!/usr/bin/env python3
"""
ia_pipeline.py — Whole Earth full-text mining pipeline
======================================================

wholeearth.info is a front-end. The actual documents live on the Internet
Archive, with full PDFs *and* OCR'd plain text. This pipeline uses the
Archive's sanctioned endpoints (no scraping of image tiles) to:

  resolve   read wholeearth.info, list every issue, and resolve each to its
            Internet Archive identifier              ->  out/issues_resolved.json
  fetch     download the OCR full text (<id>_djvu.txt) for each issue
                                                      ->  out/text/<id>.txt
  extract   scan the OCR text for review-like blocks and emit candidate
            "things that work" for human curation     ->  out/candidates.jsonl
  all       run resolve -> fetch -> extract

Why this and not a scraper: the Archive exposes /metadata/<id> (JSON file
listing) and /download/<id>/<id>_djvu.txt (full OCR). That is the supported,
low-impact path to the text. Be a good citizen: it sleeps between requests
and caches everything, so re-runs are cheap.

Usage:
    python3 ia_pipeline.py all --limit 5      # try it on 5 issues first
    python3 ia_pipeline.py resolve            # just build the id map
    python3 ia_pipeline.py fetch --limit 20
    python3 ia_pipeline.py extract

Stdlib only. Optional: `pip install internetarchive` for heavier work — not
required here. The `extract` stage is deliberately a *candidate generator*:
it surfaces likely tool/book reviews; a human (or a follow-up LLM pass) fills
the schema in data/. Nothing here is auto-promoted to a verified entry.
"""
import argparse, json, re, sys, time, urllib.request, urllib.error, pathlib

HOME = "https://wholeearth.info/"
UA = "FabCity-ThingsThatWork/1.0 (research; contact: tomas@fab.city)"
OUT = pathlib.Path(__file__).parent / "out"
TXT = OUT / "text"
SLEEP = 1.0  # seconds between network calls — be gentle

# ---------------------------------------------------------------------------
def get(url, binary=False, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if a == tries - 1:
                print(f"  ! failed {url}: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (a + 1))

# ---------------------------------------------------------------------------
def resolve():
    """List every issue on wholeearth.info and resolve its Archive identifier."""
    OUT.mkdir(exist_ok=True)
    home = get(HOME)
    if not home:
        sys.exit("could not load wholeearth.info")
    # issue links look like https://wholeearth.info/p/<slug>
    slugs = []
    seen = set()
    for m in re.finditer(r'href="(https://wholeearth\.info)?/p/([a-z0-9\-_]+)"', home):
        slug = m.group(2)
        if slug not in seen:
            seen.add(slug); slugs.append(slug)
    print(f"found {len(slugs)} issue slugs")

    issues = []
    for i, slug in enumerate(slugs, 1):
        url = f"https://wholeearth.info/p/{slug}"
        page = get(url)
        aid = None
        if page:
            m = re.search(r'archive\.org/(?:details|download)/([A-Za-z0-9._\-]+)', page)
            if m:
                aid = m.group(1)
                # strip any trailing file part if matched on a download URL
                aid = aid.split("/")[0]
        pub = None
        if page:
            mp = re.search(r'Published:\s*</?[^>]*>?\s*([A-Za-z]+\s+\d{4}|\d{4})', page)
            if mp:
                pub = mp.group(1).strip()
        issues.append({"slug": slug, "url": url, "archive_id": aid, "published": pub})
        print(f"  [{i}/{len(slugs)}] {slug} -> {aid or 'UNRESOLVED'}")
        time.sleep(SLEEP)

    (OUT / "issues_resolved.json").write_text(
        json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for x in issues if x["archive_id"])
    print(f"\nresolved {ok}/{len(issues)} -> out/issues_resolved.json")
    return issues

# ---------------------------------------------------------------------------
def fetch(limit=None):
    """Download OCR full text for each resolved issue (cached)."""
    TXT.mkdir(parents=True, exist_ok=True)
    src = OUT / "issues_resolved.json"
    if not src.exists():
        issues = resolve()
    else:
        issues = json.loads(src.read_text(encoding="utf-8"))
    todo = [x for x in issues if x["archive_id"]]
    if limit:
        todo = todo[:limit]
    for i, x in enumerate(todo, 1):
        aid = x["archive_id"]
        dest = TXT / f"{aid}.txt"
        if dest.exists() and dest.stat().st_size > 0:
            print(f"  [{i}/{len(todo)}] {aid} cached"); continue
        # confirm the djvu txt exists via metadata, then download it
        meta = get(f"https://archive.org/metadata/{aid}")
        txt_url = f"https://archive.org/download/{aid}/{aid}_djvu.txt"
        if meta:
            try:
                files = json.loads(meta).get("files", [])
                names = [f.get("name", "") for f in files]
                cand = [n for n in names if n.endswith("_djvu.txt")]
                if cand:
                    txt_url = f"https://archive.org/download/{aid}/{cand[0]}"
            except Exception:
                pass
        body = get(txt_url)
        if body:
            dest.write_text(body, encoding="utf-8")
            print(f"  [{i}/{len(todo)}] {aid} -> {len(body):,} chars")
        else:
            print(f"  [{i}/{len(todo)}] {aid} NO TEXT")
        time.sleep(SLEEP)
    print(f"\ntext cached in {TXT}")

# ---------------------------------------------------------------------------
# Candidate extraction. Whole Earth reviews tend to carry a price and/or a
# supplier/"Access" line. We surface those blocks as candidates for curation.
PRICE   = re.compile(r'\$\s?\d[\d,]*(?:\.\d{2})?')
ACCESS  = re.compile(r'\b(postpaid|catalog|from[:]?|Access|per year|each\b)', re.I)
TITLEish = re.compile(r'^[A-Z][A-Za-z0-9][A-Za-z0-9 &\'\-/.,]{2,60}$')

def extract(limit=None, per_issue=60):
    OUT.mkdir(exist_ok=True)
    files = sorted(TXT.glob("*.txt"))
    if limit:
        files = files[:limit]
    if not files:
        sys.exit("no cached text — run `fetch` first")
    out = (OUT / "candidates.jsonl").open("w", encoding="utf-8")
    total = 0
    for f in files:
        aid = f.stem
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        n = 0
        for idx, ln in enumerate(lines):
            if n >= per_issue:
                break
            if PRICE.search(ln) and ACCESS.search(ln):
                # guess a title from the nearest preceding Title-ish line
                title = None
                for back in range(idx - 1, max(idx - 6, -1), -1):
                    if TITLEish.match(lines[back].strip()):
                        title = lines[back].strip(); break
                block = " ".join(l.strip() for l in lines[idx:idx + 4] if l.strip())
                cand = {
                    "candidate_title": title or "(untitled review)",
                    "excerpt": block[:400],
                    "price_hint": (PRICE.search(ln) or [None]) and PRICE.search(ln).group(0),
                    "source": "Whole Earth (OCR)",
                    "archive_id": aid,
                    "ia_details": f"https://archive.org/details/{aid}",
                    "needs_curation": True,
                }
                out.write(json.dumps(cand, ensure_ascii=False) + "\n")
                n += 1; total += 1
        print(f"  {aid}: {n} candidates")
    out.close()
    print(f"\n{total} candidates -> out/candidates.jsonl  (review, then write schema entries into data/)")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Whole Earth full-text mining via the Internet Archive")
    ap.add_argument("stage", choices=["resolve", "fetch", "extract", "all"])
    ap.add_argument("--limit", type=int, default=None, help="cap number of issues (good for a trial run)")
    a = ap.parse_args()
    if a.stage in ("resolve", "all"):
        resolve()
    if a.stage in ("fetch", "all"):
        fetch(limit=a.limit)
    if a.stage in ("extract", "all"):
        extract(limit=a.limit)
