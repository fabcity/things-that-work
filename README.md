# Things That Work

**Open, practical tools for when the services don't work** — drinkable water when the
tap is cut, light in a blackout, a part you can 3D‑print when the supply chain is gone.
A queryable index of working solutions, plus a live **emergency‑response layer** for
Venezuela.

🌐 Live: **https://ttw.fab.city** · Emergency page: **https://ttw.fab.city/venezuela**
A project of the **Fab City Foundation**.

---

## Why this exists

Two traditions reached the same conclusion from opposite ends. The **Whole Earth
Catalog** called it *access to tools*. Cut off after the Soviet collapse, Cubans
practiced what Ernesto Oroza named *technological disobedience*. One pole is abundance
choosing self‑reliance; the other is scarcity forcing it. Both produce the same
artifact: **a thing that works, made or kept alive locally.** That is what this
repository collects — and, since June 2026, puts directly in the hands of Venezuelans
living through an earthquake on top of years of degraded services.

This is not an archive of PDFs. It is a queryable index, tagged by what each solution
does, what it's made of, what scarcity it answers — rendered as calm, mobile‑first,
offline‑capable web pages in **Spanish, English and Indonesian**.

## Repository map

```
repo/
├─ data/                     # ← the content (edit here)
│  ├─ *.json                 #   solution sources (Whole Earth, Cuba, OLIVE, Appropedia, MSF…)
│  └─ i18n/                  #   translations: es.json, id.json, crisis.es.json, crisis.id.json
├─ build_dataset.py          # builds the dataset + pages from data/ → dist/
├─ ia_pipeline.py            # grows the Whole Earth index from the Internet Archive
├─ template.html             # main ttw.fab.city page (data injected at build)
├─ template_ve.html          # the /venezuela page — design + render logic (data‑driven)
├─ deploy/                   # the published site (served by Cloudflare Pages)
│  ├─ index.html             #   built main page
│  ├─ venezuela/             #   built /venezuela page + PWA assets + offline ZIP
│  ├─ files/ferulas/         #   printable splint files (designs © Ostec3D)
│  └─ _headers               #   Cloudflare headers
├─ SCHEMA.md                 # the data model + the nine "disobedience moves"
└─ CONTRIBUTING.md           # how to add solutions, translations, or design changes
```

## Quick start

```bash
# 1. Open the built pages directly — no server, no build, data is baked in:
open deploy/venezuela/index.html        # the Venezuela emergency page
open deploy/index.html                  # the main Things That Work page

# 2. Rebuild after editing data/ or a template (needs Python 3 + Pillow for icons):
pip install pillow
python3 build_dataset.py                # regenerates dist/ (and the page HTML)

# 3. Preview locally over http (service worker / PWA needs http, not file://):
python3 -m http.server 8000 --directory deploy
#   → http://localhost:8000/venezuela/
```

## The /venezuela emergency page

A single, self‑contained, **offline‑first** page, mobile‑first and trilingual,
designed to lead people straight to action with dignity. It is **data‑driven**:
`template_ve.html` (design + render JS) + `data/` + `data/i18n/` are compiled into
`deploy/venezuela/index.html`.

- **Design language** — the graphic world of **Carlos Cruz‑Diez's Maiquetía airport**
  (the kinetic colour stripe) and **Metro de Caracas / MetroDiseño 1983** (the orange
  *M* + downward‑chevron *emblema*, colour‑coded stations, Helvetica signage), with
  **IKEA‑manual** clarity inside (numbered steps, geometric pictograms, lots of air).
  An icon of progress and hope — not a disaster bulletin.
- **Offline / on your phone** — "Descargar esta página" (one self‑contained file to
  share by WhatsApp/Bluetooth), "Instalar como app" (PWA), and a full ZIP with the
  printable files.
- **Sections** — report missing people / damaged buildings · 3D‑printing response
  (splints by **Ostec3D**, maker WhatsApp groups, the live **Ushahidi** map) ·
  what‑helps playbook by scenario · the wider archive by need · contribute · and the
  earthquake briefing at the foot.

To change its content you almost never touch HTML — edit `data/` and `data/i18n/`.
See **CONTRIBUTING.md**.

## Deploy

The site is **Cloudflare Pages** serving the `deploy/` folder, connected directly to this
repository: every push to `main` publishes automatically (output directory `deploy`, no
build command). No CI secrets or workflow files are required.

To publish manually instead, upload `things-that-work-cloudflare.zip` (regenerate it from
`deploy/`) in the Cloudflare dashboard, or run
`npx wrangler pages deploy deploy --project-name=things-that-work`.

## Contributing

The repository is the invitation; the network is what makes it alive. The fastest,
most valuable contribution is **five things that work from your city**. See
**CONTRIBUTING.md** for solutions, translations, and design changes, and **SCHEMA.md**
for the data model.

## Credits & license

Curated by **Tomas Diez**, Fab City Foundation. Splint designs by **Ostec3D**
([ostec3d.com](https://www.ostec3d.com/) · [@ostec3d](https://www.instagram.com/ostec3d/)).
Sources: Whole Earth Catalog, *Con nuestros propios esfuerzos* & *El Libro de la
Familia* (Cuba, via FabLab‑ULB / Ernesto Oroza), OLIVE (Japan), Appropedia, MSF,
Field Ready, CDC, PAHO/OMS, and others credited in‑page.

- **Code** — MIT (`LICENSE`).
- **Content, data & docs** — CC BY‑SA 4.0 (`CONTENT-LICENSE.md`).
- **Third‑party assets** (e.g. the Ostec3D 3D files) remain © their authors; check
  each before reuse.
