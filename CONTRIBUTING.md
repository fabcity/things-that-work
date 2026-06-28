# Contributing to Things That Work

Thank you for helping. This project serves people in crisis, so clarity, honesty and
working sources matter more than polish.

There are two ways in:

1. **No code — use the live forms.** The fastest contribution is *five things that work
   from your city*. Go to **ttw.fab.city**, hit **Start**, and use *"Suggest a solution
   / a need"* or *"Share a success"* (Spanish & Indonesian forms work too).
2. **Code/content — a pull request.** Everything below.

## The model (read this first)

The pages are **data‑driven**. You almost never edit HTML to change content:

```
data/  +  data/i18n/   ──(python3 build_dataset.py)──►  dist/ + the page HTML
```

- `data/*.json` — the solutions/entries (schema in **SCHEMA.md**).
- `data/i18n/es.json`, `id.json`, `crisis.es.json`, `crisis.id.json` — translations.
- `template.html` — the main ttw.fab.city page (design + render).
- `template_ve.html` — the **/venezuela** page (design + render). The base copy is
  English; Spanish/Indonesian come from the i18n files. Missing translations fall back
  to English.

## Local setup

```bash
pip install pillow                 # only needed for icon generation
python3 build_dataset.py           # rebuild after editing data/ or a template
python3 -m http.server 8000 --directory deploy   # preview at localhost:8000
```

## Common edits — where to make them

| You want to… | Edit |
|---|---|
| Add a solution to the index | a file in `data/` (follow **SCHEMA.md**); include a real `source_url` |
| Translate / fix wording (ES/ID) | `data/i18n/*.json` |
| Add a crisis card (e.g. a comms tool) | the crisis dataset + i18n; tag its `need` |
| Add a Venezuela resource / WhatsApp group / map | the `venezuela` data (groups, resources, map) |
| Add/replace a printable file | `deploy/files/ferulas/` + the printing data; credit the author |
| Change the look of /venezuela | `template_ve.html` (CSS + render JS) |

> Several Venezuela‑specific additions are applied in a guarded `TTW-VE-ADDITIONS`
> block in `build_dataset.py` — extend that block, or move them into the data files.

## Content rules (important)

- **Cite the source.** Every solution needs a real, linkable `source_url`. No source,
  no merge.
- **Be honest about testing.** Use the `validation` field truthfully — "documented"
  means *published*, not *re‑tested today*.
- **Never invent figures.** The earthquake briefing ("Qué pasó") and any casualty/
  magnitude numbers come **only from official sources** (FUNVISIS, Protección Civil,
  PAHO/OMS, UN OCHA, USGS). When unknown, leave it blank.
- **No unsafe instructions.** Medical/water/sanitation steps must match recognised
  guidance (WHO/CDC/PAHO/Red Cross). Add the caveat where relevant.
- **Trilingual.** Add `es`/`id` where you can; English is the fallback.
- **Respect asset licenses.** 3D files and external designs stay © their authors
  (e.g. Ostec3D). Don't commit anything you don't have the right to share.

## Pull requests

- Branch from `main`, keep PRs small and focused, describe what and why.
- If you changed `data/` or a template, run `python3 build_dataset.py` and confirm the
  page still renders in **all three languages** and **offline** (load over http, then
  reload offline).
- Be kind. See **CODE_OF_CONDUCT.md**.

Questions: **tomas@fab.city**.
