#!/usr/bin/env bash
# Build Things That Work — regenerate the pages from data/ and refresh deploy/.
# Usage:  ./build.sh        (requires python3)
set -euo pipefail
cd "$(dirname "$0")"

echo "→ building dataset + pages (build_dataset.py)…"
python3 build_dataset.py

echo "→ syncing built pages into deploy/…"
cp dist/things-that-work.html deploy/index.html
mkdir -p deploy/venezuela
cp dist/venezuela/index.html deploy/venezuela/index.html
_tmp="deploy/venezuela/sw.js.tmp"; sed "s/const CACHE=\"cqs-ve-[^\"]*\"/const CACHE=\"cqs-ve-$(date +%Y%m%d%H%M)\"/" deploy/venezuela/sw.js > "$_tmp" && mv "$_tmp" deploy/venezuela/sw.js  # bump cqs-ve cache version (portable GNU+BSD sed, same-dir temp)

echo "→ regenerating the offline ZIP…"
python3 - <<'PY'
import os, zipfile
v="deploy/venezuela"; fer="deploy/files/ferulas"
lean=["ferula-pequena.3mf","ferula-mediana.3mf","ferula-grande.3mf",
      "ferula-guia-uso.pdf","ferula-identificador.pdf","ferula-instrucciones-ostec.pdf",
      "ferula-corte-laser-s-m-l.pdf",
      "ferula-mascotas.3mf",
      "guia-mascotas.html"]
z=v+"/venezuela-offline.zip"
if os.path.exists(z): os.remove(z)
with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as f:
    f.write(v+"/index.html","index.html")
    for a in ("manifest.webmanifest","sw.js","icon-192.png","icon-512.png","favicon.svg","favicon-32.png","img/quake-sentinel1.jpg"):
        p=os.path.join(v,a)
        if os.path.exists(p): f.write(p,a)
    for a in lean:
        p=os.path.join(fer,a)
        if os.path.exists(p): f.write(p,"files/ferulas/"+a)
print("   offline zip:", round(os.path.getsize(z)/1048576,2), "MB")
PY

echo "→ repackaging the Cloudflare bundle…"
rm -f things-that-work-cloudflare.zip
( cd deploy && zip -qr ../things-that-work-cloudflare.zip . )

echo "✓ done.  Preview:  python3 -m http.server 8000 --directory deploy  →  http://localhost:8000/venezuela/"
