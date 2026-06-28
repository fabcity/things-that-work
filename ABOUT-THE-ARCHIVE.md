# Things That Work

A repository of solutions that work for people, seeded from two traditions that
reached the same conclusion from opposite ends.

The **Whole Earth Catalog** called it *access to tools*: give people the means and
the knowledge, and they shape their own world. Cut off from supply chains after the
Soviet collapse, Cubans practiced what Ernesto Oroza named *technological
disobedience*: refusing the designed authority of the industrial object — opening it,
repairing it, repurposing it, rebuilding it from whatever was at hand. One pole is
abundance choosing self-reliance; the other is scarcity forcing it. Both produce the
same artifact: a thing that works, made or kept alive locally. That is what this
repository collects.

This is not an archive of PDFs. It is a **queryable index of working solutions**, each
tagged with what it does, what it's made of, what scarcity it answers, and which move
of disobedience it embodies.

## What's in here

```
repo/
├─ dist/
│  ├─ things-that-work.html   ← THE DELIVERABLE: open this in any browser
│  └─ data.json               ← the dataset (entries + Whole Earth issue index)
├─ data/
│  ├─ con_nuestros.json       ← 23 entries — Con nuestros propios esfuerzos (Cuba)
│  ├─ libro_familia.json      ← 10 entries — El Libro de la Familia (Cuba, Oroza/ULB)
│  └─ wholeearth_seed.json    ← 6 entries — Whole Earth Catalog (USA)
├─ build_dataset.py           ← merges data/ + the 147-issue index → dist/
├─ ia_pipeline.py             ← grows it: mines Whole Earth full text via Internet Archive
├─ SCHEMA.md                  ← the data model + the nine disobedience moves
└─ README.md
```

By the numbers: **39 curated solutions** across food, agriculture, energy, water,
shelter, transport, health, fabrication and materials — and the **full 147-issue
Whole Earth index** (1968–2002), each issue linked to its scan on the Internet Archive.

## Open it

Double-click `dist/things-that-work.html`. No server, no build, no internet needed —
the data is baked in. It works from a USB stick or behind GitLab Pages (the same place
the ULB digitized the Cuban manual). Search the solutions, filter by source, by
disobedience move, by domain; flip to the **Whole Earth Index** tab for the issues.

## The key finding about the source

You asked to "download and index all the documents on wholeearth.info." The important
thing we learned: **the documents are not on wholeearth.info.** That site is a
front-end. Every issue resolves to a scan on the **Internet Archive**, which already
holds the full PDFs *and* OCR'd plain text behind a clean, sanctioned API. So the right
way to index at scale is against the Archive — not by scraping image tiles. That is
exactly what `ia_pipeline.py` does.

## Grow it

```bash
python3 ia_pipeline.py all --limit 5     # trial run on 5 issues
python3 ia_pipeline.py resolve           # map all 147 issues → Archive IDs
python3 ia_pipeline.py fetch             # download OCR full text (cached)
python3 ia_pipeline.py extract           # surface candidate tool reviews
```

`extract` is a **candidate generator**, not an oracle: it surfaces likely tool/book
reviews from the OCR for a human (or a follow-up LLM pass) to turn into schema entries
in `data/`. Then re-run `python3 build_dataset.py` to rebuild the page. The Cuban side
grows the same way — the manuals hold hundreds more entries than the 33 seeded here.

## Provenance

- **Whole Earth publications** — [wholeearth.info](https://wholeearth.info/) (Whole
  Earth Index); scans held by the Internet Archive. Published by Stewart Brand / POINT
  Foundation, 1968–2002.
- **Con nuestros propios esfuerzos** — Cuban Special Period inventions compendium,
  digitized & translated by [FabLab-ULB](https://fablab-ulb.gitlab.io/enseignements/2019-2020/fablab-studio/con-nuestros-propios-esfuerzos/).
- **El Libro de la Familia** — Cuban household survival manual, Havana 1991 (Colección
  Verde Olivo, prologue by Vilma Espín); reissued and reframed in 2019 by FabLab-ULB
  with **Ernesto Oroza** as a foundational document of technological disobedience.

## Honest scope

A seed, not a finished archive. The 39 entries were extracted by hand from the primary
sources to prove the schema holds across hardware, food, energy, health and materials.
`validation: documented` means a solution was published in its source — not that it has
been re-tested today; that's a field for the network to fill.

**First move:** put `things-that-work.html` in front of two or three fab labs and ask
each to add five things that work in their own city. The schema is the invitation; the
network is what turns it into something alive.
