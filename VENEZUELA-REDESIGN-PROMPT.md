# /venezuela redesign — prompt for Claude (design)

Copy everything between the lines into a new Claude chat (claude.ai, desktop or
web — it will return an HTML **artifact** you can preview live). Optionally attach
2–4 reference images first to steer it (see "How to use" below). Iterate, then
paste the final artifact code back into the Cowork session and I'll re-sync it
into the real page.

---------------------------------------------------------------------------------

You are designing a single web page: the **Venezuela emergency-response page** of
"Things That Work" (ttw.fab.city/venezuela). It is used by Venezuelans living
through the June 2026 earthquake on top of years of degraded services. Most arrive
on a **phone, on a poor connection**. The page must lead them **straight to
action**, calmly and with dignity.

Design it as an **icon of progress and hope for Venezuela** — not a disaster
bulletin. The emotional reference is the **Caracas Metro of 1983**: when it opened
it was a symbol of order, modernity and civic pride. Channel that feeling.

## The design language — synthesize these three, do not pick one

1. **IKEA assembly-manual clarity.** Numbered steps. Wordless-where-possible
   pictograms. Generous whitespace. Calm, friendly, anyone-can-follow. The "how to
   fit a splint / purify water / hang an IV bag" content should read like a
   furniture instruction sheet: simple flat line figures, 1-2-3 sequence, almost no
   prose. Reassuring, never frightening.

2. **Caracas Metro wayfinding (MetroDiseño, early 1980s).** A rigorous modernist
   grid. Bold **color-coding per section**, the way Metro lines and stations are
   colour-keyed. A **unique geometric pictogram for each "need"/section** (water,
   power, medical, sanitation, shelter, comms, food, report, print, contribute) —
   in the Lance-Wyman / International-Typographic-Style tradition: instantly
   legible, geometric, wordless. High-legibility grotesque/geometric sans, strong
   type hierarchy, signage-like section headers. Order, clarity, civic dignity.

3. **Tropicália warmth (Brazil, late 1960s — Oiticica, Veloso).** Stop it from
   being cold or austere. A **warm, saturated, tropical accent palette** used as
   energy and optimism — hopeful yellow, tropical green, coral/magenta, a deep
   confident blue. Colour as hope. You may nod subtly to the Venezuelan flag
   (yellow/blue/red) but do **not** make it nationalistic or flag-kitsch.

The synthesis: a **calm instructional page on a clean warm-paper background**, with
**bold colour-coded "stations" each carrying a geometric pictogram and a number**,
**IKEA-style numbered steps** inside, **warmed by tropical accent colour** so the
whole thing feels like a hopeful civic instrument.

## Hard constraints (do not break these)

- **One self-contained HTML file.** All CSS inline in a `<style>` block; all icons
  **inline SVG** (no icon fonts, no image requests). No external JS/CSS/CDN, no web
  fonts — use a **system font stack** so it loads instantly offline and on 2G. It
  must open correctly from a local file with no network.
- **Mobile-first.** Design for a ~360px phone first; large tap targets (min 44px);
  single column; desktop is a graceful widening. Small total payload.
- **Accessible.** WCAG-AA contrast, semantic HTML (`<header><main><section>`),
  works without JavaScript for all core reading; visible focus states; real text,
  not text-in-images.
- **Trilingual, Spanish first.** Spanish is the default; provide an EN/ES/ID
  language switch in the header. Write the visible copy in **Spanish** (I will
  supply EN/ID). Keep text in clearly-marked spots so it can be swapped.
- **No tracking, no cookies, no popups, no autoplay.** Calm and quiet.
- **Avoid the generic-AI look.** No purple gradients, no glassmorphism, no
  drop-shadow soup, no emoji as icons, no hero stock-photo, no dark "dashboard."
  Commit to the IKEA × Caracas-Metro × Tropicália synthesis with real drawn
  pictograms and a deliberate grid. If a choice could come from any prompt, reject
  it and go more specific.

## The content / sections — keep all of these, in this order

The page leads with ACTION; the news/context goes at the FOOT.

1. **Header** — wordmark "Cosas que sirven · Venezuela", EN/ES/ID switch, a small
   contact (envelope → email). One short orienting line: *"Una página para actuar:
   reporta, imprime y contribuye. Qué pasó está al final."*
2. **Act now (the two alert actions).** Two big buttons → "Reportar persona
   desaparecida" and "Reportar edificio dañado" (external links). A small share row
   (WhatsApp / Telegram / X / copy link).
3. **Respuesta con impresión 3D (the heart).** "¿Tienes una impresora 3D? Súmate":
   two WhatsApp maker-group buttons. A grid of **downloadable files** (splints
   S/M/L, fitting guide, identifier — each a download card). A short **IKEA-style
   numbered fitting sequence** (protect → warm → mould → fix → check) with a safety
   caveat. A catalogue of tested printable designs (name · material · print-time ·
   OSHWA), grouped by category. The collection-centres list (collapsible).
4. **Qué ayuda en los días después (the playbook).** Crisis solutions grouped by
   scenario (water when the tap is cut, light in a blackout, etc.) — each a card
   with a pictogram, a one-line summary, and a source.
5. **Del archivo — según lo que falla.** The wider archive organised by failure
   mode (Agua potable, Energía y luz, Comida, Saneamiento, Salud, Refugio,
   Comunicación) — each a colour-coded "station" with a count and a few links.
6. **Contribuye.** Two cards → "Propón una necesidad / solución" and "Comparte un
   éxito" (each opens an embedded form).
7. **Qué pasó (the briefing, at the foot).** The earthquake summary + key figures +
   the compound-crisis context. This is reference, not the lead.
8. **Footer** — live/official sources, the credit line ("curated by Tomas Diez, Fab
   City Foundation"), contact email, and a line: *"La capa de respuesta comunitaria
   de PLANETAI."*

Use realistic **placeholder** content for each (a few sample cards per section) so
the layout is fully shown — I will wire in the real data afterward. Make the
pictograms a coherent set (same stroke weight, same grid).

Deliver the page as a single HTML artifact. Then offer 2–3 quick variations of the
**colour system** (which tropical accents, how bold the Metro colour-coding) so I
can choose.

---------------------------------------------------------------------------------

## How to use this prompt

1. Open a **new chat in Claude** (claude.ai). Paste the block above.
2. **Optional but powerful — attach 2–4 reference images** so it locks the look:
   - a Caracas Metro **signage / pictogram** photo (wayfinding, station icons);
   - an **IKEA instruction** page (numbered wordless steps);
   - a **Tropicália** artwork or poster (for the colour energy);
   - (optional) a screenshot of the current /venezuela page so it knows what it's
     replacing.
3. Let it generate the HTML artifact; preview it live in Claude.
4. **Iterate** in plain language: "more Metro colour-coding on the section headers,"
   "the pictograms should be one consistent line weight," "warmer Tropicália yellow,"
   "simpler steps, fewer words," "show me a children's-hospital-safe palette."
5. When you like it, open the artifact's **code view and copy the whole HTML.**

## How to re-sync it here

Paste the final HTML back into this Cowork chat and say "sync this as the new
/venezuela design." I will then:

- lift the new CSS, layout and SVG pictograms into `template_ve.html`;
- re-wire every functional block to the live data (report links, the two WhatsApp
  maker groups, the hosted splint/3MF files, the Field Ready catalogue, the
  collection centres, the playbook, "Del archivo", the two contribute forms, the
  "Qué pasó" briefing with the current 235/4 300/157 figures, sources, footer);
- re-attach the trilingual EN/ES/ID strings, the analytics event hooks, the
  link-preview meta, and the PLANETAI line;
- rebuild, verify it renders in all three languages and stays offline-first, and
  repackage the deploy zip.

Keep the section set and order above intact in the design and the re-sync is clean.
The further the design strays from those blocks, the more re-wiring it needs — so
let it be bold on **look**, conservative on **structure**.
