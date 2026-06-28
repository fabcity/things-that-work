# Schema — "Things That Work"

One record = one **thing that works for people**. The schema fuses the Whole Earth
Catalog's *access to tools* (what is it, what's it made of, where do I get it) with
Ernesto Oroza's *technological disobedience* (what authority of the object does it
refuse, and how). The goal is a repository you can query — not a pile of PDFs.

## Entry object

| field | type | notes |
|---|---|---|
| `id` | string | unique kebab-case slug |
| `title` | string | concise English title |
| `title_original` | string | original Spanish/French name (`""` if none) |
| `summary` | string | one sentence — what it is |
| `how_it_works` | string | 2–4 concrete sentences, grounded in the source |
| `type` | enum | `tool` · `repair` · `repurposing` · `substitution` · `technique` · `system` · `knowledge-resource` |
| `disobedience_move` | enum[] | one or more of the nine moves (below) |
| `domain` | enum[] | `food` · `agriculture` · `energy` · `water` · `shelter` · `transport` · `health-veterinary` · `fabrication-tools` · `communication` · `materials` · `household` |
| `problem` | string | the scarcity / constraint it answers |
| `materials` | string[] | inputs, feedstock, parts |
| `origin` | string | e.g. `Cuba (Special Period, 1990s)`, `USA (counterculture)` |
| `era` | string | e.g. `1990s`, `1968-1972` |
| `source` | string | source body + issue |
| `source_ref` | string | page / issue reference |
| `source_url` | string | canonical link (issue page or original article) |
| `validation` | enum | `documented` · `widely-practiced` · `anecdotal` · `needs-testing` — honest about whether it's been re-tested today, not just published |
| `fabcity_relevance` | string | one sentence: how it lands for distributed manufacturing / a fab lab / a city |
| `tags` | string[] | 2–5 short tags |
| `source_body` | string | set at build time: `con_nuestros` · `libro_familia` · `wholeearth` |
| `n` | int | display order, set at build time |

## The nine disobedience moves

The verbs the repository is organised around — extended from the language the Cuban
manuals and Oroza actually use:

- **repair** — fix what broke; restore function instead of replacing.
- **repurpose** — use an object for a purpose other than its designed one.
- **refunctionalize** — strip an object to its raw capacities and rebuild it into something new.
- **recover-reuse** — harvest still-good materials or parts from dead objects.
- **substitute** — replace a scarce part/input/product with an available local one.
- **bypass** — design around (or ignore) a missing component, gatekeeper, or rule.
- **replicate** — make a tool/part/consumable locally instead of importing it.
- **augment** — extend or upgrade an object beyond its original spec.
- **scavenge** — source feedstock/materials from waste streams or the environment.

## Whole Earth issue object (`issues[]`)

| field | type | notes |
|---|---|---|
| `collection` | string | one of the six Whole Earth collections |
| `label` | string | issue date label |
| `year` | int / null | parsed from label |
| `slug` | string | wholeearth.info slug |
| `url` | string | `https://wholeearth.info/p/<slug>` |
| `archive_id` | string / null | Internet Archive identifier (where the scan + OCR live) |
| `ia_details` / `ia_pdf` / `ia_fulltext` | string / null | Archive detail page, PDF, OCR text |

`archive_id` is filled for issues confirmed in-session; `ia_pipeline.py resolve`
fills the rest from the live site.
