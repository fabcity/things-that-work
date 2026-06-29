#!/usr/bin/env python3
"""
Build the "Things That Work" repository dataset.

Merges the seed entries (mined from Con nuestros propios esfuerzos,
El Libro de la Familia, and the Whole Earth Catalog) with the full
Whole Earth issue index, and produces:

  - dist/data.json                       (the dataset)
  - dist/things-that-work.html           (self-contained browsable page)

Run:  python3 build_dataset.py
"""
import json, datetime, pathlib, html

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Taxonomy — fuses Whole Earth "access to tools" with Oroza's
# technological-disobedience moves. This is the spine of the repository.
# ----------------------------------------------------------------------------
MOVES = [
    ("repair",        "Repair",         "Fix what broke; restore an object to function instead of replacing it."),
    ("repurpose",     "Repurpose",      "Use an object for a purpose other than the one it was designed for."),
    ("refunctionalize","Refunctionalize","Strip an object to its raw capacities and rebuild it into something new."),
    ("recover-reuse", "Recover / reuse","Harvest still-good materials or parts from dead or scrapped objects."),
    ("substitute",    "Substitute",     "Replace a scarce part, input, or product with an available local one."),
    ("bypass",        "Bypass",         "Design around — or simply ignore — a missing component, gatekeeper, or rule."),
    ("replicate",     "Replicate",      "Make a tool, part, or consumable locally instead of importing it."),
    ("augment",       "Augment",        "Extend or upgrade an object beyond its original specification."),
    ("scavenge",      "Scavenge",       "Source feedstock or materials from waste streams or the environment."),
]
TYPES = [
    ("tool","Tool"), ("repair","Repair"), ("repurposing","Repurposing"),
    ("substitution","Substitution"), ("technique","Technique"),
    ("system","System"), ("knowledge-resource","Knowledge resource"),
]
DOMAINS = [
    ("food","Food"), ("agriculture","Agriculture"), ("energy","Energy"),
    ("water","Water"), ("shelter","Shelter"), ("transport","Transport"),
    ("health-veterinary","Health / veterinary"), ("fabrication-tools","Fabrication & tools"),
    ("communication","Communication"), ("materials","Materials"), ("household","Household"),
]

# ----------------------------------------------------------------------------
# Source bodies
# ----------------------------------------------------------------------------
SOURCES = {
    "con_nuestros": {
        "key": "con-nuestros-propios-esfuerzos",
        "name": "Con nuestros propios esfuerzos",
        "label": "Cuban inventions compendium",
        "note": "“With Our Own Efforts.” A compendium of inventions and solutions sent in by Cubans during the post-Soviet Special Period, digitized and translated by FabLab-ULB (Brussels). The scarcity pole of the repository.",
        "origin": "Cuba",
        "url": "https://fablab-ulb.gitlab.io/enseignements/2019-2020/fablab-studio/con-nuestros-propios-esfuerzos/",
    },
    "libro_familia": {
        "key": "el-libro-de-la-familia",
        "name": "El Libro de la Familia",
        "label": "Cuban household survival manual",
        "note": "“The Family Book.” A Cuban household survival manual first published in Havana in 1991 (Colección Verde Olivo, prologue by Vilma Espín), reissued and reframed in 2019 by FabLab-ULB with Ernesto Oroza as a foundational document of technological disobedience.",
        "origin": "Cuba",
        "url": "",
    },
    "wholeearth": {
        "key": "whole-earth",
        "name": "Whole Earth Catalog",
        "label": "Access to tools (USA, 1968–2002)",
        "note": "Stewart Brand's “access to tools” — the North American counterculture pole. Reviewed the best tools, books and practices for self-sufficiency, ecology and do-it-yourself living.",
        "origin": "USA",
        "url": "https://wholeearth.info/",
    },
    "olive": {
        "key": "olive",
        "name": "OLIVE",
        "label": "Japan disaster wisdom (post-2011)",
        "note": "A citizen-built wiki of disaster-survival techniques, created after Japan's 2011 Tōhoku earthquake and tsunami — make-do solutions from everyday materials for water, warmth, light, cooking, sanitation and shelter.",
        "origin": "Japan",
        "url": "https://sites.google.com/site/olivesoce/home",
    },
    "msf": {
        "key": "msf-3dp",
        "name": "MSF — 3D Printing for All",
        "label": "Open hardware for the field (Médecins Sans Frontières)",
        "note": "Médecins Sans Frontières' project to democratize 3D printing in field hospitals: downloadable, locally-printable medical and non-medical parts — oxygen accessories, lab adapters, spares — where supply chains fail.",
        "origin": "MSF field projects",
        "url": "https://www.printables.com/@3Dprintingforall",
    },
    "appropedia": {
        "key": "appropedia",
        "name": "Appropedia",
        "label": "Appropriate-technology wiki (open)",
        "note": "The largest open wiki of appropriate technology and sustainability — community-documented, buildable how-tos for water, energy, sanitation, food, shelter and materials.",
        "origin": "Global (open wiki)",
        "url": "https://www.appropedia.org/",
    },
    "fieldready": {
        "key": "field-ready",
        "name": "Field Ready",
        "label": "Humanitarian open hardware (field-tested)",
        "note": "Field Ready's portfolio of locally-manufacturable humanitarian hardware — medical, water/sanitation, shelter and workshop parts made by 3D printing, moulding or welding where supply chains fail. Each design carries a field-readiness rating and, for many, an OSHWA certification.",
        "origin": "Field Ready (humanitarian field projects)",
        "url": "https://wikifactory.com/+FieldReady/",
    },
    "ferulas": {
        "key": "ferulas-ve",
        "name": "Férulas Venezuela",
        "label": "3D-printed thermoformable splints (Venezuela)",
        "note": "A Venezuelan volunteer network printing thermoformable splints (férulas) as medical donations after the June 2026 earthquake — reheated in hot water, moulded to the limb, and dropped at collection centers across the country.",
        "origin": "Venezuela",
        "url": "https://chat.whatsapp.com/DaseixyFONlH0xIpXCaGyW",
    },
    "vzla_makers": {
        "key": "vzla-makers",
        "name": "Venezuela Makers",
        "label": "Community designs for the 2026 earthquake response",
        "note": "Open 3D-printable designs Venezuelans are sharing for the June 2026 earthquake response — IV-bag hooks for improvised wards, a cervical brace, splint fitting guides, ready-to-print bundles — published on MakerWorld, Printables and through the Ferulas 3D Venezuela maker community.",
        "origin": "Venezuela",
        "url": "https://bio.capasup.xyz/ferulas",
    },
}

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

entries = []
for fname, sbody in [("con_nuestros.json","con_nuestros"),
                     ("libro_familia.json","libro_familia"),
                     ("wholeearth_seed.json","wholeearth")]:
    for e in load(fname):
        e["source_body"] = sbody
        e["source_key"] = SOURCES[sbody]["key"]
        entries.append(e)

for i, e in enumerate(entries, 1):
    e["n"] = i

# ----------------------------------------------------------------------------
# Whole Earth issue index — every issue listed on wholeearth.info, grouped by
# collection. archive_id filled where verified in-session; the rest are
# resolved by ia_pipeline.py (which reads each issue page on wholeearth.info).
# ----------------------------------------------------------------------------
CONFIRMED_IA = {
    "whole-earth-catalog-fall-1968": "wholeearthcatalo00unse_8",
    "whole-earth-catalog-spring-1969": "wholeearthcatalo00unse_10",
    "difficult-but-possible-supplement-to-the-whole-earth-catalog-july-1969": "difficultbutposs00unse",
    "whole-earth-catalog-fall-1969": "wholeearthcatalo00unse_7",
    "difficult-but-possible-supplement-to-the-whole-earth-catalog-september-1969": "difficultbutposs00unse_0",
    "difficult-but-possible-supplement-to-the-whole-earth-catalog-january-1970": "wholeearthcatalo00unse_6",
    "whole-earth-catalog-spring-1970": "wholeearthcatalo00unse_1",
}

ISSUES_RAW = {
"Whole Earth Catalogs": [
    ("Fall 1968","whole-earth-catalog-fall-1968"),
    ("Spring 1969","whole-earth-catalog-spring-1969"),
    ("July 1969","difficult-but-possible-supplement-to-the-whole-earth-catalog-july-1969"),
    ("Fall 1969","whole-earth-catalog-fall-1969"),
    ("September 1969","difficult-but-possible-supplement-to-the-whole-earth-catalog-september-1969"),
    ("January 1970","difficult-but-possible-supplement-to-the-whole-earth-catalog-january-1970"),
    ("Spring 1970","whole-earth-catalog-spring-1970"),
    ("March 1970","difficult-but-possible-supplement-to-the-whole-earth-catalog-march-1970"),
    ("July 1970","difficult-but-possible-supplement-to-the-whole-earth-catalog-july-1970"),
    ("Fall 1970","whole-earth-catalog-fall-1970"),
    ("September 1970","difficult-but-possible-supplement-to-the-whole-earth-catalog-september-1970"),
    ("January 1971","the-last-whole-earth-catalog-january-1971"),
    ("January 1971","difficult-but-possible-supplement-to-the-whole-earth-catalog-january-1971"),
    ("March 1971","the-last-supplement-to-the-whole-earth-catalog-march-1971"),
    ("April 1974","whole-earth-epilog-teaser"),
    ("October 1974","whole-earth-epilog-october-1974"),
    ("June 1975","the-updated-last-whole-earth-catalog-june-1975"),
    ("Fall 1980","the-next-whole-earth-catalog-fall-1980"),
    ("September 1986","the-essential-whole-earth-catalog-september-1968"),
    ("1988","signal-communication-tools-for-the-information-age"),
    ("1989","the-fringes-of-reason"),
    ("1990","whole-earth-ecolog"),
    ("December 1994","the-millennium-whole-earth-catalog-december-1994"),
    ("Winter 1998","whole-earth-catalog-30th-anniversary-winter-1998"),
],
"CoEvolution Quarterly": [
    ("Spring 1974","coevolution-quarterly-spring-1974"),
    ("Summer 1974","coevolution-quarterly-summer-1974"),
    ("Fall 1974","coevolution-quarterly-fall-1974"),
    ("Winter 1974","coevolution-quarterly-winter-1974"),
    ("Spring 1975","coevolution-quarterly-spring-1975"),
    ("Summer 1975","coevolution-quarterly-summer-1975"),
    ("Fall 1975","coevolution-quarterly-fall-1975"),
    ("Winter 1975","coevolution-quarterly-winter-1975"),
    ("Spring 1976","coevolution-quarterly-spring-1976"),
    ("Summer 1976","coevolution-quarterly-summer-1976"),
    ("Fall 1976","coevolution-quarterly-fall-1976"),
    ("Winter 1976","coevolution-quarterly-winter-1976-1977"),
    ("Spring 1977","coevolution-quarterly-spring-1977"),
    ("Summer 1977","coevolution-quarterly-summer-1977"),
    ("Fall 1977","coevolution-quarterly-fall-1977"),
    ("Winter 1977","coevolution-quarterly-winter-1978"),
    ("Spring 1978","coevolution-quarterly-spring-1978"),
    ("Summer 1978","coevolution-quarterly-summer-1978"),
    ("Fall 1978","coevolution-quarterly-fall-1978"),
    ("Winter 1978","coevolution-quarterly-whole-earth-jamboree-1968-1978"),
    ("Spring 1979","coevolution-quarterly-spring-1979"),
    ("Summer 1979","coevolution-quarterly-summer-1979"),
    ("Fall 1979","coevolution-quarterly-fall-1979"),
    ("Winter 1979","coevolution-quarterly-winter-1979"),
    ("Spring 1980","coevolution-quarterly-spring-1980"),
    ("Summer 1980","coevolution-quarterly-summer-1980"),
    ("Winter 1980","coevolution-quarterly-winter-1980"),
    ("Spring 1981","coevolution-quarterly-spring-1981"),
    ("Summer 1981","coevolution-quarterly-summer-1981"),
    ("Fall 1981","coevolution-quarterly-fall-1981"),
    ("Winter 1981","coevolution-quarterly-winter-1981"),
    ("Spring 1982","coevolution-quarterly-spring-1982"),
    ("Summer 1982","coevolution-quarterly-summer-1982"),
    ("Fall 1982","coevolution-quarterly-fall-1982"),
    ("October 1982","coevolution-catalog-october-1982"),
    ("Winter 1982","coevolution-quarterly-winter-1982"),
    ("Spring 1983","coevolution-quarterly-spring-1983"),
    ("Summer 1983","coevolution-quarterly-summer-1983"),
    ("Fall 1983","coevolution-quarterly-fall-1983"),
    ("Winter 1983","coevolution-quarterly-winter-1983"),
    ("Spring 1984","coevolution-quarterly-spring-1984"),
    ("Summer 1984","coevolution-quarterly-summer-1984"),
    ("Fall 1984","coevolution-quarterly-fall-1984"),
],
"Whole Earth Software Review": [
    ("Spring 1984","whole-earth-software-review-no-1-spring-1984"),
    ("Summer 1984","whole-earth-software-review-no-2-summer-1984"),
    ("June 1984","whole-earth-software-catalog-june-1984"),
    ("Fall 1984","whole-earth-software-review-no-3-fall-1984"),
    ("Fall 1985","whole-earth-software-catalog-2_0-fall-1985"),
],
"Whole Earth Review": [
    ("January 1985","whole-earth-review-january-1985"),
    ("March 1985","whole-earth-review-march-1985"),
    ("May 1985","whole-earth-review-may-1985"),
    ("July 1985","whole-earth-review-july-1985"),
    ("Fall 1985","whole-earth-review-fall-1985"),
    ("Winter 1985","whole-earth-review-winter-1985"),
    ("Spring 1986","whole-earth-review-spring-1986"),
    ("Summer 1986","whole-earth-review-summer-1986"),
    ("Fall 1986","whole-earth-review-fall-1986"),
    ("Winter 1986","whole-earth-review-winter-1986"),
    ("Spring 1987","whole-earth-review-spring-1987"),
    ("Summer 1987","whole-earth-review-summer-1987"),
    ("Fall 1987","whole-earth-review-fall-1987"),
    ("Winter 1987","whole-earth-review-winter-1987"),
    ("Spring 1988","whole-earth-review-spring-1988"),
    ("Summer 1988","whole-earth-review-summer-1988"),
    ("Fall 1988","whole-earth-review-fall-1988"),
    ("Winter 1988","whole-earth-review-winter-1988"),
    ("Spring 1989","whole-earth-review-spring-1989"),
    ("Summer 1989","whole-earth-review-summer-1989"),
    ("Fall 1989","whole-earth-review-fall-1989"),
    ("Winter 1989","whole-earth-review-winter-1989"),
    ("Spring 1990","whole-earth-review-spring-1990"),
    ("Summer 1990","whole-earth-review-summer-1990"),
    ("Fall 1990","whole-earth-review-fall-1990"),
    ("Winter 1990","whole-earth-review-winter-1990"),
    ("Spring 1991","whole-earth-review-spring-1991"),
    ("Summer 1991","whole-earth-review-summer-1991"),
    ("Fall 1991","whole-earth-review-fall-1991"),
    ("Winter 1991","whole-earth-review-winter-1991"),
    ("Spring 1992","whole-earth-review-spring-1992"),
    ("Summer 1992","whole-earth-review-summer-1992"),
    ("Fall 1992","whole-earth-review-fall-1992"),
    ("Winter 1992","whole-earth-5-year-index-1988-1992"),
    ("Winter 1992","whole-earth-review-winter-1992"),
    ("Spring 1993","whole-earth-review-spring-1993"),
    ("Summer 1993","whole-earth-review-summer-1993"),
    ("Fall 1993","whole-earth-review-fall-1993"),
    ("Winter 1993","whole-earth-review-winter-1993"),
    ("Spring 1994","whole-earth-review-spring-1994"),
    ("Summer 1994","whole-earth-review-summer-1994"),
    ("Winter 1994","whole-earth-review-winter-1994"),
    ("Spring 1995","whole-earth-review-spring-1995"),
    ("Summer 1995","whole-earth-review-summer-1995"),
    ("Fall 1995","whole-earth-review-fall-1995"),
    ("Winter 1995","whole-earth-review-winter-1995"),
    ("Spring 1996","whole-earth-review-spring-1996"),
],
"Whole Earth Magazine": [
    ("Summer 1997","whole-earth-summer-1997"),
    ("Winter 1997","whole-earth-winter-1997"),
    ("Spring 1998","whole-earth-spring-1998"),
    ("Summer 1998","whole-earth-summer-1998"),
    ("Fall 1998","whole-earth-fall-1998"),
    ("Spring 1999","whole-earth-spring-1999"),
    ("Summer 1999","whole-earth-summer-1999"),
    ("Fall 1999","whole-earth-fall-1999"),
    ("Winter 1999","whole-earth-winter-1999"),
    ("Spring 2000","whole-earth-spring-2000"),
    ("Summer 2000","whole-earth-summer-2000"),
    ("Fall 2000","whole-earth-fall-2000"),
    ("Winter 2000","whole-earth-winter-2000"),
    ("Spring 2001","whole-earth-spring-2001"),
    ("Summer 2001","whole-earth-summer-2001"),
    ("Winter 2001","whole-earth-winter-2001"),
    ("Spring 2002","whole-earth-spring-2002"),
    ("Summer 2002","whole-earth-summer-2002"),
    ("Fall 2002","whole-earth-fall-2002"),
    ("Winter 2002","whole-earth-winter-2002"),
],
"Special Publications": [
    ("Spring 1970","domebook-1"),
    ("Summer 1970","big-rock-candy-mountain"),
    ("January 1974","ii-cybernetic-frontiers-january-1974"),
    ("1974","energy-primer-solar-water-wind-biofuels"),
    ("December 1977","space-colonies-december-1977"),
    ("Spring 1978","soft-tech-spring-1978"),
    ("1986","10-years-of-coevolution-quarterly-news-that-stayed-news-1986"),
    ("Spring 1991","helping-nature-heal-spring-1991"),
],
}

def year_of(label):
    for tok in label.replace("-", " ").split():
        if tok.isdigit() and len(tok) == 4:
            return int(tok)
    return None

issues = []
for collection, items in ISSUES_RAW.items():
    for label, slug in items:
        aid = CONFIRMED_IA.get(slug)
        issues.append({
            "collection": collection,
            "label": label,
            "year": year_of(label),
            "slug": slug,
            "url": f"https://wholeearth.info/p/{slug}",
            "archive_id": aid,
            "ia_details": f"https://archive.org/details/{aid}" if aid else None,
            "ia_pdf": f"https://archive.org/download/{aid}/{aid}.pdf" if aid else None,
            "ia_fulltext": f"https://archive.org/download/{aid}/{aid}_djvu.txt" if aid else None,
        })

dataset = {
    "meta": {
        "title": "Things That Work",
        "subtitle": "A repository of access to tools and technological disobedience",
        "description": ("Solutions that work for people, drawn from Stewart Brand's Whole Earth "
                        "Catalog (“access to tools”) and from how Cubans, cut off from supply "
                        "chains, disobeyed the designed authority of industrial objects — repairing, "
                        "repurposing, and rebuilding to survive."),
        "generated": datetime.date.today().isoformat(),
        "entry_count": len(entries),
        "issue_count": len(issues),
        "issues_with_archive_id": sum(1 for i in issues if i["archive_id"]),
    },
    "taxonomy": {
        "moves": [{"key": k, "label": l, "desc": d} for k, l, d in MOVES],
        "types": [{"key": k, "label": l} for k, l in TYPES],
        "domains": [{"key": k, "label": l} for k, l in DOMAINS],
        "sources": SOURCES,
    },
    "entries": entries,
    "issues": issues,
}

# ----------------------------------------------------------------------------
# i18n — Spanish & Indonesian. Entry-field translations come from data/i18n/;
# UI, taxonomy and framing strings are authored here for register/quality.
# ----------------------------------------------------------------------------
MOVE_I18N = {  # key: (label_es, label_id, desc_es, desc_id)
 "repair":("Reparar","Memperbaiki","Arreglar lo que se rompió; devolver la función a un objeto en vez de reemplazarlo.","Memperbaiki yang rusak; memulihkan fungsi sebuah benda alih-alih menggantinya."),
 "repurpose":("Reutilizar","Mengalihfungsikan","Usar un objeto para un fin distinto al que fue diseñado.","Memakai sebuah benda untuk tujuan selain yang dirancang baginya."),
 "refunctionalize":("Refuncionalizar","Memfungsikan ulang","Despojar un objeto hasta sus capacidades básicas y reconstruirlo en algo nuevo.","Melucuti benda hingga kapasitas dasarnya dan membangunnya kembali menjadi sesuatu yang baru."),
 "recover-reuse":("Recuperar / reusar","Memulihkan / pakai ulang","Cosechar materiales o piezas aún útiles de objetos muertos o desechados.","Memanen material atau komponen yang masih baik dari benda mati atau rongsokan."),
 "substitute":("Sustituir","Menyubstitusi","Reemplazar una pieza, insumo o producto escaso por uno local disponible.","Mengganti komponen, bahan, atau produk yang langka dengan yang tersedia secara lokal."),
 "bypass":("Sortear","Menyiasati","Diseñar sorteando —o simplemente ignorando— un componente que falta, un guardián o una regla.","Merancang untuk mengakali — atau sekadar mengabaikan — komponen yang hilang, penjaga gerbang, atau aturan."),
 "replicate":("Replicar","Mereplikasi","Fabricar una herramienta, pieza o consumible localmente en vez de importarlo.","Membuat perkakas, komponen, atau barang habis pakai secara lokal alih-alih mengimpornya."),
 "augment":("Aumentar","Meningkatkan","Extender o mejorar un objeto más allá de su especificación original.","Memperluas atau meningkatkan sebuah benda melampaui spesifikasi aslinya."),
 "scavenge":("Rebuscar","Memulung","Obtener insumos o materiales de los flujos de desecho o del entorno.","Mendapatkan bahan baku atau material dari aliran limbah atau lingkungan."),
}
DOMAIN_I18N = {  # key: (es, id)
 "food":("Alimentación","Pangan"),"agriculture":("Agricultura","Pertanian"),"energy":("Energía","Energi"),
 "water":("Agua","Air"),"shelter":("Vivienda","Hunian"),"transport":("Transporte","Transportasi"),
 "health-veterinary":("Salud y veterinaria","Kesehatan & veteriner"),"fabrication-tools":("Fabricación y herramientas","Fabrikasi & perkakas"),
 "communication":("Comunicación","Komunikasi"),"materials":("Materiales","Material"),"household":("Hogar","Rumah tangga"),
}
TYPE_I18N = {  # key: (es, id)
 "tool":("Herramienta","Perkakas"),"repair":("Reparación","Perbaikan"),"repurposing":("Reutilización","Alih fungsi"),
 "substitution":("Sustitución","Substitusi"),"technique":("Técnica","Teknik"),"system":("Sistema","Sistem"),
 "knowledge-resource":("Recurso de conocimiento","Sumber pengetahuan"),
}
SOURCES_I18N = {
 "con_nuestros":{"label_es":"Compendio de inventos cubanos","label_id":"Kompendium penemuan Kuba",
   "note_es":"“Con nuestros propios esfuerzos.” Compendio de inventos y soluciones enviados por cubanos durante el Período Especial posterior a la URSS, digitalizado y traducido por FabLab-ULB (Bruselas). El polo de la escasez del repositorio.",
   "note_id":"“Con nuestros propios esfuerzos” (Dengan Upaya Kita Sendiri). Kompendium penemuan dan solusi yang dikirim warga Kuba selama Periode Khusus pasca-Soviet, didigitalkan dan diterjemahkan oleh FabLab-ULB (Brussels). Kutub kelangkaan dari repositori ini."},
 "libro_familia":{"label_es":"Manual cubano de supervivencia doméstica","label_id":"Manual bertahan hidup rumah tangga Kuba",
   "note_es":"“El Libro de la Familia.” Manual cubano de supervivencia doméstica publicado en La Habana en 1991 (Colección Verde Olivo, prólogo de Vilma Espín), reeditado y reenmarcado en 2019 por FabLab-ULB con Ernesto Oroza como documento fundacional de la desobediencia tecnológica.",
   "note_id":"“El Libro de la Familia” (Kitab Keluarga). Manual bertahan hidup rumah tangga Kuba, pertama terbit di Havana pada 1991 (Colección Verde Olivo, kata pengantar oleh Vilma Espín), diterbitkan ulang dan dibingkai ulang pada 2019 oleh FabLab-ULB bersama Ernesto Oroza sebagai dokumen fondasi pembangkangan teknologi."},
 "wholeearth":{"label_es":"Acceso a herramientas (EE. UU., 1968–2002)","label_id":"Akses ke perkakas (AS, 1968–2002)",
   "note_es":"El “acceso a herramientas” de Stewart Brand — el polo de la contracultura norteamericana. Reseñaba las mejores herramientas, libros y prácticas para la autosuficiencia, la ecología y el “hazlo tú mismo”.",
   "note_id":"“Akses ke perkakas” ala Stewart Brand — kutub kontra-budaya Amerika Utara. Mengulas perkakas, buku, dan praktik terbaik untuk kemandirian, ekologi, dan “kerjakan sendiri”."},
 "olive":{"label_es":"Sabiduría de desastres de Japón (post-2011)","label_id":"Kearifan bencana Jepang (pasca-2011)",
   "note_es":"Una wiki ciudadana de técnicas de supervivencia ante desastres, creada tras el terremoto y tsunami de Tōhoku de 2011 en Japón — soluciones improvisadas con materiales cotidianos para agua, calor, luz, cocina, saneamiento y refugio.",
   "note_id":"Wiki warga berisi teknik bertahan hidup saat bencana, dibuat setelah gempa dan tsunami Tōhoku 2011 di Jepang — solusi seadanya dari bahan sehari-hari untuk air, kehangatan, cahaya, memasak, sanitasi, dan hunian."},
 "msf":{"label_es":"Hardware abierto para el terreno (Médecins Sans Frontières)","label_id":"Perangkat keras terbuka untuk lapangan (Médecins Sans Frontières)",
   "note_es":"El proyecto de Médecins Sans Frontières para democratizar la impresión 3D en hospitales de campaña: piezas médicas y no médicas descargables e imprimibles localmente — accesorios de oxígeno, adaptadores de laboratorio, repuestos — donde fallan las cadenas de suministro.",
   "note_id":"Proyek Médecins Sans Frontières untuk mendemokratisasi pencetakan 3D di rumah sakit lapangan: komponen medis dan non-medis yang dapat diunduh dan dicetak secara lokal — aksesori oksigen, adaptor lab, suku cadang — ketika rantai pasok gagal."},
 "appropedia":{"label_es":"Wiki de tecnología apropiada (abierta)","label_id":"Wiki teknologi tepat guna (terbuka)",
   "note_es":"La mayor wiki abierta de tecnología apropiada y sostenibilidad — guías construibles y documentadas por la comunidad para agua, energía, saneamiento, alimentación, vivienda y materiales.",
   "note_id":"Wiki terbuka terbesar tentang teknologi tepat guna dan keberlanjutan — panduan yang dapat dibuat dan didokumentasikan komunitas untuk air, energi, sanitasi, pangan, hunian, dan material."},
 "fieldready":{"label_es":"Hardware humanitario abierto (probado en terreno)","label_id":"Perangkat keras kemanusiaan terbuka (teruji di lapangan)",
   "note_es":"El portafolio de Field Ready de hardware humanitario fabricable localmente — piezas médicas, de agua y saneamiento, refugio y taller hechas por impresión 3D, moldeo o soldadura donde fallan las cadenas de suministro. Cada diseño lleva una calificación de madurez de terreno y, muchos, una certificación OSHWA.",
   "note_id":"Portofolio Field Ready berisi perangkat keras kemanusiaan yang dapat dibuat lokal — komponen medis, air & sanitasi, hunian, dan bengkel yang dibuat dengan cetak 3D, cetakan, atau las ketika rantai pasok gagal. Tiap desain punya peringkat kesiapan lapangan dan, banyak di antaranya, sertifikasi OSHWA."},
 "ferulas":{"label_es":"Férulas termoformables impresas en 3D (Venezuela)","label_id":"Bidai termoform cetak 3D (Venezuela)",
   "note_es":"Una red de voluntarios venezolanos que imprime férulas termoformables como donación médica tras el terremoto de junio de 2026 — se recalientan en agua caliente y se moldean al miembro, y se entregan en centros de acopio por todo el país.",
   "note_id":"Jaringan relawan Venezuela yang mencetak bidai termoform sebagai donasi medis setelah gempa Juni 2026 — dipanaskan ulang dalam air panas, dibentuk pada anggota tubuh, lalu diantar ke pusat pengumpulan di seluruh negeri."},
 "vzla_makers":{"label_es":"Diseños comunitarios para la respuesta al terremoto de 2026","label_id":"Desain komunitas untuk respons gempa 2026",
   "note_es":"Diseños abiertos imprimibles en 3D que los venezolanos comparten para la respuesta al terremoto de junio de 2026 — ganchos para bolsas de suero en hospitales improvisados, un rigidizador de cuello, guías de colocación de férulas, paquetes listos para imprimir — publicados en MakerWorld, Printables y a través de la comunidad de makers Férulas 3D Venezuela.",
   "note_id":"Desain 3D terbuka yang dibagikan warga Venezuela untuk respons gempa Juni 2026 — pengait kantong infus untuk bangsal darurat, penyangga leher, panduan pemasangan bidai, paket siap cetak — dipublikasikan di MakerWorld, Printables, dan melalui komunitas maker Ferulas 3D Venezuela."},
}
UI = {
 "en":{
  "tagline":"Things That Work — a Fab City repository","rev":"rev. ",
  "subtitle":"A repository of access to tools and technological disobedience",
  "manifesto":'A repository of solutions that <b>actually work for people</b> — built from two traditions that reached the same conclusion from opposite ends. The <b style="color:var(--wec)">Whole Earth Catalog</b> called it <i>access to tools</i>: give people the means and they shape their own world. In Cuba, cut off from supply chains, people practiced what Ernesto Oroza named <b style="color:var(--cuba)">technological disobedience</b>: refusing the designed authority of the industrial object — repairing it, repurposing it, rebuilding it. The more you can make what you need, the freer you are.',
  "c_entries":"solutions indexed","c_cuba":"Cuban disobedience","c_wec":"access to tools","c_issues":"Whole Earth issues",
  "tab_repo":"The Repository","tab_index":"Whole Earth Index",
  "search_ph":"Search solutions — try “feed”, “repair”, “water”, “salvage”, “coffee”…",
  "f_source":"Source","f_move":"Move","f_domain":"Domain","f_type":"Type",
  "reset":"clear all filters ✕","filter":"filter","filters":"filters",
  "empty":"No solutions match these filters.","empty_clear":"clear filters",
  "pill_wec":"Access to tools","pill_cuba":"Technological disobedience","relevance":"Why it lands for Fab City",
  "val_documented":"documented","issues_word":"issues","open_link":"open ↗",
  "index_intro":'The full run of Whole Earth publications, 1968–2002, as catalogued at <a href="https://wholeearth.info/" target="_blank" rel="noopener">wholeearth.info</a>. Each issue is a front-end to a scan held by the <b>Internet Archive</b> — which is where the documents actually live, with full PDFs and OCR\'d text. The mining pipeline (<span class="mono">ia_pipeline.py</span>) resolves every issue to its Internet Archive identifier and pulls the full text for extraction. <span class="mono">●</span> marks issues whose Archive ID is already confirmed; the rest resolve when the pipeline runs.',
  "about_summary":"About this repository — the two poles & the nine moves",
  "about_p1":'Every entry is a <b>thing that works</b>: a tool, a repair, a repurposing, a substitution, a technique, a system, or a knowledge resource. Each is tagged with the <b>disobedience move(s)</b> it embodies — the verbs Oroza and the Cuban manuals use for refusing an object\'s designed fate, extended to cover the Whole Earth "access to tools" logic.',
  "about_moves_h":"The nine moves","about_sources_h":"Sources","about_scope_h":"Honesty about scope",
  "about_scope_p":'This is a <b>seed</b>, not the finished archive. The entries here were extracted by hand from the primary sources to prove the schema holds across hardware, food, energy, health and materials. The full-text mining pipeline is built to grow it across the entire Whole Earth corpus and the rest of the Cuban manuals. Validation is marked honestly: <b>documented</b> means it was published in its source, not that it has been re-tested today.',
  "footer_line":'<b>Things That Work</b> · seeded from <i>Whole Earth Catalog</i>, <i>Con nuestros propios esfuerzos</i>, and <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza). Built for Fab City.',
 },
 "es":{
  "tagline":"Things That Work — un repositorio de Fab City","rev":"rev. ",
  "subtitle":"Un repositorio de acceso a herramientas y desobediencia tecnológica",
  "manifesto":'Un repositorio de soluciones que <b>de verdad funcionan para la gente</b>, construido desde dos tradiciones que llegaron a la misma conclusión por caminos opuestos. El <b style="color:var(--wec)">Whole Earth Catalog</b> lo llamó <i>acceso a herramientas</i>: dale a la gente los medios y dará forma a su propio mundo. En Cuba, cortada de las cadenas de suministro, la gente practicó lo que Ernesto Oroza llamó <b style="color:var(--cuba)">desobediencia tecnológica</b>: negarse a la autoridad de diseño del objeto industrial — repararlo, reutilizarlo, reconstruirlo. Mientras más puedas hacer lo que necesitas, más libre eres.',
  "c_entries":"soluciones indexadas","c_cuba":"desobediencia cubana","c_wec":"acceso a herramientas","c_issues":"números de Whole Earth",
  "tab_repo":"El repositorio","tab_index":"Índice de Whole Earth",
  "search_ph":"Busca soluciones — prueba “pienso”, “reparar”, “agua”, “chatarra”, “café”…",
  "f_source":"Fuente","f_move":"Gesto","f_domain":"Dominio","f_type":"Tipo",
  "reset":"limpiar todos los filtros ✕","filter":"filtro","filters":"filtros",
  "empty":"Ninguna solución coincide con estos filtros.","empty_clear":"limpiar filtros",
  "pill_wec":"Acceso a herramientas","pill_cuba":"Desobediencia tecnológica","relevance":"Por qué aterriza para Fab City",
  "val_documented":"documentado","issues_word":"números","open_link":"abrir ↗",
  "index_intro":'La colección completa de las publicaciones de Whole Earth, 1968–2002, según el catálogo de <a href="https://wholeearth.info/" target="_blank" rel="noopener">wholeearth.info</a>. Cada número es una fachada de un escaneo alojado en el <b>Internet Archive</b> — que es donde viven de verdad los documentos, con PDF completos y texto OCR. El pipeline de minería (<span class="mono">ia_pipeline.py</span>) resuelve cada número a su identificador de Internet Archive y extrae el texto completo. <span class="mono">●</span> marca los números cuyo ID de Archive ya está confirmado; el resto se resuelve al correr el pipeline.',
  "about_summary":"Acerca de este repositorio — los dos polos y los nueve gestos",
  "about_p1":'Cada entrada es una <b>cosa que funciona</b>: una herramienta, una reparación, una reutilización, una sustitución, una técnica, un sistema o un recurso de conocimiento. Cada una lleva etiquetado el <b>gesto (o gestos) de desobediencia</b> que encarna — los verbos que Oroza y los manuales cubanos usan para negarse al destino diseñado de un objeto, extendidos a la lógica del “acceso a herramientas” de Whole Earth.',
  "about_moves_h":"Los nueve gestos","about_sources_h":"Fuentes","about_scope_h":"Honestidad sobre el alcance",
  "about_scope_p":'Esto es una <b>semilla</b>, no el archivo terminado. Las entradas se extrajeron a mano de las fuentes primarias para comprobar que el esquema aguanta en hardware, alimentación, energía, salud y materiales. El pipeline de minería de texto completo está hecho para hacerlo crecer por todo el corpus de Whole Earth y el resto de los manuales cubanos. La validación se marca con honestidad: <b>documentado</b> significa que se publicó en su fuente, no que se haya vuelto a probar hoy.',
  "footer_line":'<b>Things That Work</b> · sembrado desde <i>Whole Earth Catalog</i>, <i>Con nuestros propios esfuerzos</i> y <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza). Hecho para Fab City.',
 },
 "id":{
  "tagline":"Things That Work — repositori Fab City","rev":"rev. ",
  "subtitle":"Repositori akses ke perkakas dan pembangkangan teknologi",
  "manifesto":'Sebuah repositori solusi yang <b>benar-benar berhasil untuk masyarakat</b> — dibangun dari dua tradisi yang sampai pada kesimpulan sama dari arah berlawanan. <b style="color:var(--wec)">Whole Earth Catalog</b> menyebutnya <i>akses ke perkakas</i>: beri orang sarananya dan mereka akan membentuk dunianya sendiri. Di Kuba, terputus dari rantai pasok, orang mempraktikkan apa yang dinamai Ernesto Oroza sebagai <b style="color:var(--cuba)">pembangkangan teknologi</b>: menolak otoritas rancangan benda industri — memperbaikinya, mengalihfungsikannya, membangunnya kembali. Semakin banyak yang bisa kamu buat sendiri, semakin bebas kamu.',
  "c_entries":"solusi terindeks","c_cuba":"pembangkangan Kuba","c_wec":"akses ke perkakas","c_issues":"terbitan Whole Earth",
  "tab_repo":"Repositori","tab_index":"Indeks Whole Earth",
  "search_ph":"Cari solusi — coba “pakan”, “perbaikan”, “air”, “rongsokan”, “kopi”…",
  "f_source":"Sumber","f_move":"Tindakan","f_domain":"Domain","f_type":"Jenis",
  "reset":"hapus semua filter ✕","filter":"filter","filters":"filter",
  "empty":"Tidak ada solusi yang cocok dengan filter ini.","empty_clear":"hapus filter",
  "pill_wec":"Akses ke perkakas","pill_cuba":"Pembangkangan teknologi","relevance":"Mengapa ini relevan untuk Fab City",
  "val_documented":"terdokumentasi","issues_word":"terbitan","open_link":"buka ↗",
  "index_intro":'Koleksi lengkap publikasi Whole Earth, 1968–2002, sebagaimana dikatalogkan di <a href="https://wholeearth.info/" target="_blank" rel="noopener">wholeearth.info</a>. Setiap terbitan adalah antarmuka bagi pindaian yang disimpan di <b>Internet Archive</b> — di sanalah dokumen sebenarnya berada, lengkap dengan PDF dan teks hasil OCR. Pipeline penambangan (<span class="mono">ia_pipeline.py</span>) memetakan setiap terbitan ke pengenal Internet Archive-nya dan menarik teks lengkapnya untuk diekstraksi. <span class="mono">●</span> menandai terbitan yang ID Archive-nya sudah dipastikan; sisanya teratasi saat pipeline dijalankan.',
  "about_summary":"Tentang repositori ini — dua kutub & sembilan tindakan",
  "about_p1":'Setiap entri adalah <b>sesuatu yang berhasil</b>: sebuah perkakas, perbaikan, alih fungsi, substitusi, teknik, sistem, atau sumber pengetahuan. Masing-masing ditandai dengan <b>tindakan pembangkangan</b> yang diwujudkannya — kata kerja yang dipakai Oroza dan manual-manual Kuba untuk menolak nasib rancangan sebuah benda, diperluas mencakup logika “akses ke perkakas” ala Whole Earth.',
  "about_moves_h":"Sembilan tindakan","about_sources_h":"Sumber","about_scope_h":"Kejujuran soal cakupan",
  "about_scope_p":'Ini adalah <b>benih</b>, bukan arsip yang sudah jadi. Entri di sini diekstraksi secara manual dari sumber primer untuk membuktikan skema ini bertahan di ranah perangkat keras, pangan, energi, kesehatan, dan material. Pipeline penambangan teks lengkap dibangun untuk menumbuhkannya ke seluruh korpus Whole Earth dan sisa manual-manual Kuba. Validasi ditandai dengan jujur: <b>terdokumentasi</b> berarti hal itu diterbitkan dalam sumbernya, bukan berarti sudah diuji ulang hari ini.',
  "footer_line":'<b>Things That Work</b> · dibenihkan dari <i>Whole Earth Catalog</i>, <i>Con nuestros propios esfuerzos</i>, dan <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza). Dibuat untuk Fab City.',
 },
}

# merge entry-field translations from data/i18n/
_trans = {}
for _lang in ("es", "id"):
    _p = DATA / "i18n" / f"{_lang}.json"
    _trans[_lang] = json.loads(_p.read_text(encoding="utf-8")) if _p.exists() else {}
for e in dataset["entries"]:
    e["i18n"] = {lg: _trans[lg][e["id"]] for lg in ("es", "id") if e["id"] in _trans[lg]}

# new source bodies — OLIVE (Japan disaster wisdom) + MSF (open hardware); entries carry inline i18n
for _fname, _sb in [("olive.json", "olive"), ("msf.json", "msf"), ("appropedia.json", "appropedia")]:
    for _e in load(_fname):
        _e["source_body"] = _sb
        _e["source_key"] = SOURCES[_sb]["key"]
        _e.setdefault("i18n", {})
        dataset["entries"].append(_e)

# --- Field Ready Portfolio → repository entries (all clean records) ---
import re as _re
def _slug(s):
    return _re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "item"
_FR_METHOD_I18N = {
 "3D Printer":("impresión 3D","cetak 3D"), "Welder":("soldadura","pengelasan"),
 "Injection Moulding":("moldeo por inyección","cetakan injeksi"), "Injection Mould":("moldeo por inyección","cetakan injeksi"),
 "Vacuum Former":("termoformado al vacío","pembentukan vakum"), "Laser Cutter":("corte láser","pemotongan laser"),
 "CNC":("CNC","CNC"), "Lathe":("torno","mesin bubut"),
}
def _fr_method(ct, lg):
    ct = (ct or "").strip()
    if ct in _FR_METHOD_I18N: return _FR_METHOD_I18N[ct][0 if lg == "es" else 1]
    return ct
_FR_DOMAIN_RULES = [
 ("health-veterinary", ["brace","splint","otoscope","nebuli","oxygen","ventilat","umbilical","fetoscope","incubator","iv bag","scalpel","kidney tray","forcep","tweezer","sharps","ecg","cardiolog","prosthe","wheelchair","dental","autoclave","centrifuge","steril","face shield","face mask","mask","airway","opa","nasal","limb","calliper","caliper","suction","warmer","specula","needle","sanitiz","sanitis","truss","hearing","ear guard","crutch","x-ray","handrail","ramp","sock assist","fluid warmer","door opener","door handle","height","intubation","goggles","railing"]),
 ("water", ["latrine","handwash","hand-wash","hand wash","tap","faucet","water","hose","pipe","bsp","tri-clamp","triclamp","filter","bucket","jerry","soap","sink","toilet","syphon","siphon","urine","flush","slab","riser","seal","gasket","coupler","barb","manifold","truck clamp"]),
 ("energy", ["solar","wind turbine","cookstove","cook stove","stove","battery","photovolt","iec 309","compressor","panel","charger","dehumidifier","air bottle"]),
 ("shelter", ["bed","crib","chair","furniture","brick","tile","roof","window","privacy screen","partition","container","pallet","floor","play pen","playpen","house","insulation","cupboard","reciproboo","carpet"]),
 ("communication", ["antenna","rfid","yagi","omni"]),
 ("agriculture", ["garden","permacultur","compost","hydroponic","vertical garden"]),
 ("fabrication-tools", ["clamp","wrench","plier","set square","divider","fastener","grip","spreader","shredder","peg","gauge","whistle","coupler","enclosure","junction","collar","cap","fitting","plug","adapter","connector","bracket","lever","handle","knob","screw","hinge","lock","holder"]),
 ("household", ["clothes peg","toy","school bag","writing","cup holder","rat trap","door lock","whistle"]),
]
def _fr_domain(name, desc):
    t = ((name or "") + " " + (desc or "")).lower()
    hits = [dom for dom, kws in _FR_DOMAIN_RULES if any(k in t for k in kws)]
    return (hits[:2] or ["fabrication-tools"])
_DOM_ES = {"food":"Alimentación","agriculture":"Agricultura","energy":"Energía","water":"Agua y saneamiento","shelter":"Vivienda","health-veterinary":"Salud","fabrication-tools":"Fabricación y herramientas","communication":"Comunicación","materials":"Materiales","household":"Hogar"}
_DOM_ID = {"food":"Pangan","agriculture":"Pertanian","energy":"Energi","water":"Air & sanitasi","shelter":"Hunian","health-veterinary":"Kesehatan","fabrication-tools":"Fabrikasi & perkakas","communication":"Komunikasi","materials":"Material","household":"Rumah tangga"}
_fr_seen = set(); _fr_n = 0
for _r in load("fieldready_all.json"):
    _name = (_r.get("name") or "").strip().rstrip(",").strip()
    if not _name or all(c in ") ,(" for c in _name):
        continue
    _desc = (_r.get("description") or "").strip()
    _notes = (_r.get("catalogue_notes") or "").strip()
    _mat = (_r.get("materials") or "").strip()
    _dl = (_r.get("download") or "").strip()
    _osh = (_r.get("oshwa") or "").replace("\t", "").strip()
    _ct = (_r.get("critical_tool") or "").strip()
    _frd = str(_r.get("field_readiness") or "").strip()
    _part = (_r.get("part") or "").strip()
    _eid = "fr-" + _slug((_part + "-" + _name) if _part else _name)
    if _eid in _fr_seen:
        _eid += "-" + str(_fr_n)
    _fr_seen.add(_eid)
    _doms = _fr_domain(_name, _desc)
    _is3dp = "3d printer" in _ct.lower()
    _moves = (["recover-reuse", "replicate"] if ("bottle" in _mat.lower() or "pet " in _mat.lower())
              else ["replicate", "substitute"])
    _en_sum = _desc or ((_name + ": open-hardware part for clinics and relief, made by " + _ct.lower() + ".") if _ct
                        else (_name + ": open-hardware part for clinics and relief."))
    _es_sum = (_DOM_ES.get(_doms[0], "Pieza") + ". Pieza de hardware abierto de Field Ready"
               + ((", fabricación: " + _fr_method(_ct, "es")) if _ct else "")
               + ". Archivo, materiales e instrucciones en la ficha.")
    _id_sum = (_DOM_ID.get(_doms[0], "Komponen") + ". Komponen perangkat keras terbuka dari Field Ready"
               + ((", dibuat dengan " + _fr_method(_ct, "id")) if _ct else "")
               + ". Berkas, material, dan instruksi ada di kartu.")
    _tags = ["field-ready", "open-hardware"]
    if _is3dp: _tags.append("3d-printing")
    if _ct: _tags.append(_ct.lower())
    if _osh: _tags.append(_osh)
    if _frd: _tags.append("readiness " + _frd + "/5")
    _e = {
      "id": _eid, "title": _name, "title_original": "", "summary": _en_sum,
      "how_it_works": _notes, "type": "tool", "disobedience_move": _moves, "domain": _doms,
      "problem": "", "materials": [m.strip() for m in _re.split(r"[,/]| and ", _mat) if m.strip()] if _mat else [],
      "origin": "Field Ready (humanitarian field projects)", "era": "contemporary",
      "source": "Field Ready", "source_ref": "Field Ready Portfolio" + ((" · " + _part) if _part else ""),
      "source_url": (_dl or "https://wikifactory.com/+FieldReady/"),
      "open_hardware": True, "validation": "documented",
      "fabcity_relevance": "A part a local workshop can fabricate on demand instead of importing it; the field-readiness rating and OSHWA reference show how proven it is.",
      "tags": _tags, "source_body": "fieldready", "source_key": "field-ready",
      "i18n": {"es": {"title": _name, "summary": _es_sum, "how_it_works": "", "problem": ""},
               "id": {"title": _name, "summary": _id_sum, "how_it_works": "", "problem": ""}},
    }
    if _osh: _e["oshwa_uid"] = _osh
    if _frd: _e["field_readiness"] = _frd
    if _dl: _e["download_url"] = _dl
    dataset["entries"].append(_e); _fr_n += 1
print("field ready entries:", _fr_n)

# --- Ferulas Venezuela splints → repository entries (EN canonical + es/id) ---
_FER_HOW_ES = "Se imprime en filamento termoformable y se entrega como donación médica. Para colocarla: proteger la piel con venda o capa, calentar la pieza según su guía (agua tibia o 90–100 °C según el material — nunca sobre la piel desnuda), moldear sobre el miembro antes de que enfríe y fijar con venda elástica o velcro. Endurece al enfriar. Archivos (S/M/L), guía de uso y centros de acopio en la página de Venezuela."
_FER_HOW_EN = "Printed in thermoformable filament and given as a medical donation. To fit: protect the skin with a bandage or layer, warm the part per its guide (warm water or 90–100 °C depending on the material — never against bare skin), mould it onto the limb before it cools, and fix with an elastic bandage or velcro. It hardens as it cools. Files (S/M/L), fitting guide and collection centers are on the Venezuela page."
_FER_HOW_ID = "Dicetak dengan filamen termoform dan diberikan sebagai donasi medis. Cara memasang: lindungi kulit dengan perban atau lapisan, panaskan sesuai panduannya (air hangat atau 90–100 °C tergantung material — jangan di atas kulit telanjang), bentuk pada anggota tubuh sebelum dingin, lalu kencangkan dengan perban elastis atau velcro. Mengeras saat dingin. Berkas (S/M/L), panduan, dan pusat pengumpulan ada di halaman Venezuela."
_FER_PROB_ES = "Tras el terremoto faltan férulas e insumos de inmovilización; importarlas es lento y caro."
_FER_PROB_EN = "After the earthquake, splints and immobilisation supplies are scarce; importing them is slow and costly."
_FER_PROB_ID = "Setelah gempa, bidai dan pasokan imobilisasi langka; mengimpor lambat dan mahal."
for _fid, _es_t, _en_t, _id_t, _size in [
  ("ferula-mano-adulto", "Férula de mano (adulto)", "Hand splint (adult)", "Bidai tangan (dewasa)", "grande"),
  ("ferula-mano-infantil", "Férula de mano (infantil)", "Hand splint (child)", "Bidai tangan (anak)", "pequena"),
  ("ferula-antebrazo", "Férula de antebrazo", "Forearm splint", "Bidai lengan bawah", "mediana"),
  ("ferula-pie", "Férula de pie", "Foot splint", "Bidai kaki", "grande"),
  ("ferula-extension-dedo", "Férula de extensión de dedo", "Finger-extension splint", "Bidai ekstensi jari", "pequena"),
]:
    dataset["entries"].append({
      "id": _fid, "title": _en_t, "title_original": _es_t,
      "summary": _en_t + ": 3D-printed thermoformable splint, a medical donation for trauma after the earthquake.",
      "how_it_works": _FER_HOW_EN, "type": "tool", "disobedience_move": ["replicate", "substitute"],
      "domain": ["health-veterinary"], "problem": _FER_PROB_EN,
      "materials": ["thermoformable filament (PLA/PETG)", "elastic bandage or velcro"],
      "origin": "Venezuela", "era": "contemporary", "source": "Férulas Venezuela",
      "source_ref": "Férulas Venezuela", "source_url": "https://ttw.fab.city/venezuela",
      "open_hardware": True, "validation": "documented",
      "fabcity_relevance": "A medical part a volunteer with a printer makes locally and donates, instead of waiting on an import.",
      "tags": ["ferulas", "splint", "3d-printing", "open-hardware", "trauma", "venezuela", "orthotic"],
      "source_body": "ferulas", "source_key": "ferulas-ve", "download_url": "/files/ferulas/ferula-" + _size + ".3mf",
      "i18n": {
        "es": {"title": _es_t, "summary": _es_t + ": férula termoformable impresa en 3D, donación médica para trauma tras el terremoto.", "how_it_works": _FER_HOW_ES, "problem": _FER_PROB_ES},
        "id": {"title": _id_t, "summary": _id_t + ": bidai termoform cetak 3D, donasi medis untuk trauma setelah gempa.", "how_it_works": _FER_HOW_ID, "problem": _FER_PROB_ID},
      },
    })
print("ferulas entries: 5")

# --- Venezuela makers: community designs shared for the 2026 earthquake response ---
_VZLA = [
 {"id":"vm-iv-hook-single","title":"IV-bag hook, single (improvised ward)","title_original":"Gancho para suero (individual)",
  "summary":"A printable hook to hang one IV / saline bag where there is no pole — made to help hospitals and improvised wards after the 2026 Venezuela earthquake. Prints in about an hour (0.2 mm, 2 walls, 15% infill).",
  "how_it_works":"","type":"tool","disobedience_move":["replicate","substitute"],"domain":["health-veterinary"],
  "problem":"Improvised wards after the quake lack IV poles to hang saline and medication bags.",
  "materials":["PLA or PETG"],"origin":"Venezuela","era":"contemporary","source":"Venezuela Makers",
  "source_ref":"MakerWorld · Salvador Aguilera","source_url":"https://makerworld.com/en/models/2984932-hook-for-individual-medical-solution",
  "open_hardware":True,"validation":"documented","fabcity_relevance":"A volunteer with a printer makes a missing hospital fixture in an hour instead of waiting on supply.",
  "tags":["venezuela","medical","iv-hook","hospital","makerworld","3d-printing","earthquake","free file"],
  "source_body":"vzla_makers","source_key":"vzla-makers",
  "i18n":{"es":{"title":"Gancho para suero (individual)","summary":"Un gancho imprimible para colgar una bolsa de suero donde no hay soporte — hecho para ayudar a hospitales y hospitales improvisados tras el terremoto de Venezuela de 2026. Imprime en cerca de una hora (0,2 mm, 2 paredes, 15% de relleno).","how_it_works":"","problem":"Los hospitales improvisados tras el sismo no tienen soportes para colgar las bolsas de suero o medicación."},
          "id":{"title":"Pengait kantong infus (tunggal)","summary":"Pengait cetak untuk menggantung satu kantong infus saat tak ada tiang — dibuat untuk membantu rumah sakit darurat setelah gempa Venezuela 2026.","how_it_works":"","problem":"Bangsal darurat pascagempa tak punya tiang infus."}}},
 {"id":"vm-iv-hook-double","title":"IV-bag hook, double (improvised ward)","title_original":"Gancho para suero (doble)",
  "summary":"A printable hook to hang two IV / saline bags at once where there is no pole — made for hospitals and improvised wards after the 2026 Venezuela earthquake. Prints in about 18 minutes.",
  "how_it_works":"","type":"tool","disobedience_move":["replicate","substitute"],"domain":["health-veterinary"],
  "problem":"Improvised wards after the quake lack IV poles to hang saline and medication bags.",
  "materials":["PLA or PETG"],"origin":"Venezuela","era":"contemporary","source":"Venezuela Makers",
  "source_ref":"MakerWorld · Salvador Aguilera","source_url":"https://makerworld.com/en/models/2984757-hook-for-double-medical-solution",
  "open_hardware":True,"validation":"documented","fabcity_relevance":"Hangs two bags from one printed part — a fast, free fix for a crowded improvised ward.",
  "tags":["venezuela","medical","iv-hook","hospital","makerworld","3d-printing","earthquake","free file"],
  "source_body":"vzla_makers","source_key":"vzla-makers",
  "i18n":{"es":{"title":"Gancho para suero (doble)","summary":"Un gancho imprimible para colgar dos bolsas de suero a la vez donde no hay soporte — hecho para hospitales y hospitales improvisados tras el terremoto de Venezuela de 2026. Imprime en unos 18 minutos.","how_it_works":"","problem":"Los hospitales improvisados tras el sismo no tienen soportes para colgar las bolsas de suero."},
          "id":{"title":"Pengait kantong infus (ganda)","summary":"Pengait cetak untuk menggantung dua kantong infus sekaligus saat tak ada tiang — untuk rumah sakit darurat setelah gempa Venezuela 2026.","how_it_works":"","problem":"Bangsal darurat pascagempa tak punya tiang infus."}}},
 {"id":"vm-neck-splint","title":"Neck splint / cervical brace (S·M·L)","title_original":"Rigidizador de cuello",
  "summary":"A printable cervical brace designed in Venezuela for the 2026 earthquake. Three sizes (children / adults / large), adjustable by scale; print in PETG (2 walls, recommended) or PLA (3 walls) and close with 5 cm (2 in) velcro.",
  "how_it_works":"","type":"tool","disobedience_move":["replicate","substitute"],"domain":["health-veterinary"],
  "problem":"Cervical immobilisation is scarce after the quake; commercial collars are unavailable or unaffordable.",
  "materials":["PETG (recommended) or PLA","velcro 5 cm / 2 in"],"origin":"Venezuela","era":"contemporary","source":"Venezuela Makers",
  "source_ref":"MakerWorld · fernandoarmas","source_url":"https://makerworld.com/en/models/2984480-neck-splint",
  "open_hardware":True,"validation":"documented","fabcity_relevance":"A locally-printable support device for the exact injuries a quake produces, free to anyone with a printer.",
  "tags":["venezuela","medical","neck-splint","cervical","makerworld","3d-printing","earthquake","free file"],
  "source_body":"vzla_makers","source_key":"vzla-makers",
  "i18n":{"es":{"title":"Rigidizador de cuello (férula cervical)","summary":"Una férula cervical imprimible diseñada en Venezuela para el terremoto de 2026. Tres tallas (niños / adultos / grande), ajustable por escala; imprime en PETG (2 paredes, recomendado) o PLA (3 paredes) y cierra con velcro de 5 cm (2 pulg).","how_it_works":"","problem":"La inmovilización cervical escasea tras el sismo; los collarines comerciales no se consiguen o son caros."},
          "id":{"title":"Penyangga leher (cervical)","summary":"Penyangga leher cetak yang dirancang di Venezuela untuk gempa 2026. Tiga ukuran (anak / dewasa / besar); cetak dengan PETG (2 dinding, disarankan) atau PLA, tutup dengan velcro 5 cm.","how_it_works":"","problem":"Imobilisasi leher langka setelah gempa; penyangga komersial sulit didapat."}}},
 {"id":"vm-capasup-ferulas","title":"Ferulas 3D — fitting guide (six splints)","title_original":"Férulas 3D — guía de uso",
  "summary":"A Spanish step-by-step guide to fitting six 3D-printed splints — wrist, finger, finger-extension, pinky + thumb, palm, and big toe (original models by Prusa Research) — each with what it is for and how to secure it, plus a clear medical caveat.",
  "how_it_works":"","type":"knowledge-resource","disobedience_move":["replicate"],"domain":["health-veterinary"],
  "problem":"A printed splint is only useful if people know which model fits which injury and how to secure it without cutting circulation.",
  "materials":[],"origin":"Venezuela","era":"contemporary","source":"CapasUp",
  "source_ref":"bio.capasup.xyz/ferulas","source_url":"https://bio.capasup.xyz/ferulas",
  "open_hardware":True,"validation":"documented","fabcity_relevance":"The human layer on top of the files — a plain-language fitting guide that makes the printed splints safe to actually use.",
  "tags":["venezuela","splint","ferulas","guide","documentation","spanish","wrist","finger"],
  "source_body":"vzla_makers","source_key":"vzla-makers",
  "i18n":{"es":{"title":"Férulas 3D — guía de uso (seis modelos)","summary":"Una guía en español, paso a paso, para colocar seis férulas impresas en 3D — muñeca, dedo, extensión de dedo, meñique y pulgar, palma de la mano y dedo gordo del pie (modelos originales de Prusa Research) — cada una con para qué sirve y cómo fijarla, con un aviso médico claro.","how_it_works":"","problem":"Una férula impresa solo sirve si se sabe qué modelo corresponde a cada lesión y cómo fijarla sin cortar la circulación."},
          "id":{"title":"Bidai 3D — panduan pemakaian (enam model)","summary":"Panduan langkah demi langkah dalam bahasa Spanyol untuk memasang enam bidai cetak 3D — pergelangan, jari, ekstensi jari, kelingking & ibu jari, telapak, dan jempol kaki (model asli Prusa Research).","how_it_works":"","problem":"Bidai cetak hanya berguna bila orang tahu model mana untuk cedera mana dan cara memasangnya."}}},
 {"id":"vm-emergencia-3mf","title":"Emergencia Venezuela — ready-to-print bundle","title_original":"EMERGENCIA VENEZUELA",
  "summary":"A ready-to-print 3MF bundle assembled by the Ferulas 3D Venezuela makers for the earthquake response — medical splints and parts laid out across plates so a printer can run them straight through. Download and open in your slicer.",
  "how_it_works":"","type":"tool","disobedience_move":["replicate","substitute"],"domain":["health-veterinary"],
  "problem":"Makers wanting to help need a single, vetted file they can print without sourcing each model separately.",
  "materials":["PLA or PETG"],"origin":"Venezuela","era":"contemporary","source":"Férulas 3D Venezuela",
  "source_ref":"Férulas 3D Venezuela (WhatsApp)","source_url":"https://chat.whatsapp.com/DaseixyFONlH0xIpXCaGyW",
  "open_hardware":True,"validation":"documented","fabcity_relevance":"One file, many plates — the maker community packaging its own response so anyone with a printer can start in minutes.",
  "tags":["venezuela","ferulas","bundle","3mf","3d-printing","earthquake","medical"],
  "source_body":"vzla_makers","source_key":"vzla-makers","download_url":"/files/ferulas/emergencia-venezuela.3mf",
  "i18n":{"es":{"title":"Emergencia Venezuela — paquete listo para imprimir","summary":"Un paquete 3MF listo para imprimir, armado por los makers de Férulas 3D Venezuela para la respuesta al terremoto — férulas y piezas médicas distribuidas en planchas para imprimir de corrido. Descárgalo y ábrelo en tu slicer.","how_it_works":"","problem":"Quien quiere ayudar necesita un solo archivo confiable para imprimir sin buscar cada modelo por separado."},
          "id":{"title":"Emergencia Venezuela — paket siap cetak","summary":"Paket 3MF siap cetak yang disusun komunitas maker Ferulas 3D Venezuela untuk respons gempa — bidai dan komponen medis tertata di beberapa pelat agar bisa dicetak langsung.","how_it_works":"","problem":"Relawan butuh satu berkas tepercaya untuk dicetak tanpa mencari tiap model satu per satu."}}},
]
for _e in _VZLA: dataset["entries"].append(_e)
print("venezuela makers entries:", len(_VZLA))

# --- Appropedia Category:Projects (filtered scrape) → repository entries ---
_ap_path = DATA / "appropedia_projects.json"
_ap_n = 0
if _ap_path.exists():
    _existing_ids = {e["id"] for e in dataset["entries"]}
    for _r in json.loads(_ap_path.read_text(encoding="utf-8")):
        _title = (_r.get("title") or "").strip()
        _ext = (_r.get("extract") or "").strip()
        if not _title or not _ext:
            continue
        _eid = "ap-" + str(_r.get("pageid") or _slug(_title))
        if _eid in _existing_ids:
            continue
        _existing_ids.add(_eid)
        _dom = _r.get("domain") or "fabrication-tools"
        if _dom == "other":
            _dom = "fabrication-tools"
        _w = _ext.split()
        _sum = " ".join(_w[:60]) + ("…" if len(_w) > 60 else "")
        _es = _DOM_ES.get(_dom, "Proyecto") + ". Proyecto de tecnología apropiada documentado en Appropedia; texto completo y pasos en la fuente (en inglés)."
        _ids = _DOM_ID.get(_dom, "Proyek") + ". Proyek teknologi tepat guna yang didokumentasikan di Appropedia; teks lengkap dan langkah-langkahnya di sumber (bahasa Inggris)."
        dataset["entries"].append({
          "id": _eid, "title": _title, "title_original": "", "summary": _sum,
          "how_it_works": "", "type": ("system" if _dom in ("water", "energy", "food", "shelter") else "tool"),
          "disobedience_move": ["replicate"], "domain": [_dom], "problem": "",
          "materials": [], "origin": "Appropedia (community wiki)", "era": "contemporary",
          "source": "Appropedia", "source_ref": "Appropedia — Category:Projects",
          "source_url": _r.get("url") or "https://www.appropedia.org/",
          "open_hardware": True, "validation": "documented",
          "fabcity_relevance": "A community-documented, buildable project anyone can adapt and make locally.",
          "tags": ["appropedia", "project", "appropriate-technology", _dom],
          "source_body": "appropedia", "source_key": "appropedia",
          "i18n": {"es": {"title": _title, "summary": _es, "how_it_works": "", "problem": ""},
                   "id": {"title": _title, "summary": _ids, "how_it_works": "", "problem": ""}},
        })
        _ap_n += 1
print("appropedia project entries:", _ap_n)

for _i, _e in enumerate(dataset["entries"], 1):
    _e["n"] = _i
dataset["meta"]["entry_count"] = len(dataset["entries"])
_clbl = {"en": ("source traditions", "open-hardware designs"),
         "es": ("tradiciones de fuentes", "diseños de hardware abierto"),
         "id": ("tradisi sumber", "desain perangkat keras terbuka")}
for _lg in ("en", "es", "id"):
    UI[_lg]["c_cuba"] = _clbl[_lg][0]
    UI[_lg]["c_wec"] = _clbl[_lg][1]

# attach localized labels to taxonomy + sources
for m in dataset["taxonomy"]["moves"]:
    le, li, de, di = MOVE_I18N[m["key"]]
    m.update(label_es=le, label_id=li, desc_es=de, desc_id=di)
for d in dataset["taxonomy"]["domains"]:
    d["label_es"], d["label_id"] = DOMAIN_I18N[d["key"]]
for ty in dataset["taxonomy"]["types"]:
    ty["label_es"], ty["label_id"] = TYPE_I18N[ty["key"]]
for k, s in dataset["taxonomy"]["sources"].items():
    s.update(SOURCES_I18N[k])
dataset["ui"] = UI
dataset["meta"]["langs"] = ["en", "es", "id"]
_missing = [e["id"] for e in dataset["entries"] if not e["i18n"].get("es") or not e["i18n"].get("id")]
print("entries missing a translation:", _missing or "none")

# embed real figure scans (base64 data URIs) where we extracted them; the rest
# render a generated SVG emblem in the page.
import base64
IMG = DATA / "images"
_with_scan = 0
for e in dataset["entries"]:
    p = IMG / f'{e["id"]}.jpg'
    if p.exists() and p.stat().st_size > 0:
        e["image"] = "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode("ascii")
        _with_scan += 1
dataset["meta"]["entries_with_scan"] = _with_scan
print("entries with embedded scan:", _with_scan, "| emblems:", len(dataset["entries"]) - _with_scan)

# ---------------------------------------------------------------------------
# Crisis / degraded-services section (dedicated view, VE-grounded, reusable)
# ---------------------------------------------------------------------------
CRISIS_NEEDS = [  # key (also the value stored on entries), label_es, label_id
    ("Water","Agua","Air"), ("Health","Salud","Kesehatan"),
    ("Sanitation","Saneamiento","Sanitasi"), ("Power","Energía","Listrik"),
    ("Food","Alimentación","Pangan"), ("Comms","Comunicaciones","Komunikasi"),
    ("Coordination","Coordinación","Koordinasi"), ("Shelter","Refugio","Hunian"),
]
PHASES = [
    ("acute-72h","First 72 hours","Primeras 72 horas","72 jam pertama"),
    ("days-after","Days after","Días después","Hari-hari setelahnya"),
    ("prolonged","Prolonged","Prolongado","Berkepanjangan"),
]
CRISIS_UI = {
 "en":{
   "crisis_tab":"Crisis","c_crisis":"crisis solutions",
   "crisis_title":"Crisis & degraded services",
   "crisis_intro":'Not just the moment of the shock — the days and weeks after, when the water, the power, the phones and the clinics don\'t work. Written for the Venezuelan reality — the June 2026 Morón earthquake on top of years of <i>apagones</i> and water rationing — but built to serve any Fab City when services fail. Every item is drawn from an authority (WHO, CDC, EPA, the Sphere Handbook, the Red Cross, SODIS) and keeps its real figures.',
   "crisis_safety":'<b>Read first.</b> These are last-resort measures for when normal services fail. They reduce risk but do not replace a working utility or a clinician. Water disinfection does not remove fuel, chemicals or heavy metals. Anyone severely dehydrated, an infant, or a pregnant person needs a health facility wherever one is reachable.',
   "crisis_src":"Source","crisis_caution":"Caution","crisis_oh":"Open hardware",
 },
 "es":{
   "crisis_tab":"Crisis","c_crisis":"soluciones de crisis",
   "crisis_title":"Crisis y servicios degradados",
   "crisis_intro":'No solo el momento del golpe — los días y semanas después, cuando el agua, la luz, el teléfono y los hospitales no funcionan. Escrito para la realidad venezolana — el terremoto de Morón de junio de 2026 sobre años de <i>apagones</i> y racionamiento de agua — pero hecho para servir a cualquier Fab City cuando fallan los servicios. Cada elemento proviene de una autoridad (OMS, CDC, EPA, el Manual Esfera, la Cruz Roja, SODIS) y conserva sus cifras reales.',
   "crisis_safety":'<b>Léelo primero.</b> Son medidas de último recurso para cuando fallan los servicios normales. Reducen el riesgo pero no reemplazan a un servicio público que funcione ni a un médico. La desinfección del agua no elimina combustible, químicos ni metales pesados. Quien esté gravemente deshidratado, un bebé o una persona embarazada necesita un centro de salud donde lo haya.',
   "crisis_src":"Fuente","crisis_caution":"Precaución","crisis_oh":"Hardware abierto",
 },
 "id":{
   "crisis_tab":"Krisis","c_crisis":"solusi krisis",
   "crisis_title":"Krisis & layanan terganggu",
   "crisis_intro":'Bukan hanya saat guncangan terjadi — tetapi hari dan minggu sesudahnya, ketika air, listrik, telepon, dan klinik tidak berfungsi. Ditulis untuk realitas Venezuela — gempa Morón Juni 2026 di atas bertahun-tahun <i>apagones</i> (pemadaman) dan penjatahan air — tetapi dibuat untuk membantu Fab City mana pun saat layanan gagal. Setiap butir bersumber dari otoritas (WHO, CDC, EPA, Buku Panduan Sphere, Palang Merah, SODIS) dan mempertahankan angka aslinya.',
   "crisis_safety":'<b>Baca dulu.</b> Ini adalah langkah upaya terakhir saat layanan normal gagal. Langkah ini mengurangi risiko tetapi tidak menggantikan layanan publik yang berfungsi atau tenaga medis. Disinfeksi air tidak menghilangkan bahan bakar, bahan kimia, atau logam berat. Siapa pun yang dehidrasi berat, bayi, atau orang hamil membutuhkan fasilitas kesehatan bila tersedia.',
   "crisis_src":"Sumber","crisis_caution":"Perhatian","crisis_oh":"Perangkat keras terbuka",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(CRISIS_UI[_lg])

crisis = json.loads((DATA / "crisis.json").read_text(encoding="utf-8"))
_ctrans = {}
for _lg in ("es","id"):
    _cp = DATA / "i18n" / f"crisis.{_lg}.json"
    _ctrans[_lg] = json.loads(_cp.read_text(encoding="utf-8")) if _cp.exists() else {}
for c in crisis:
    c["i18n"] = {lg: _ctrans[lg][c["id"]] for lg in ("es","id") if c["id"] in _ctrans[lg]}
dataset["crisis"] = crisis
dataset["taxonomy"]["needs"] = [{"key":k,"label":k,"label_es":es,"label_id":idn} for (k,es,idn) in CRISIS_NEEDS]
dataset["taxonomy"]["phases"] = [{"key":k,"label":en,"label_es":es,"label_id":idn} for (k,en,es,idn) in PHASES]
dataset["meta"]["crisis_count"] = len(crisis)
_cmiss = [c["id"] for c in crisis if not c["i18n"].get("es") or not c["i18n"].get("id")]
print("crisis entries:", len(crisis), "| missing translation:", _cmiss or "none")

# localized masthead title + Venezuela tab strings (override a few base UI keys)
EXTRA_UI = {
 "en":{"title":"Things That Work","ve_tab":"Venezuela","ve_resources":"Verify with",
   "ve_intro":'A Venezuela-specific playbook for the recurring reality: a multi-day <i>apagón</i>, water that stops or arrives by truck, networks that drop, clinics short on supplies — and, since 24 June 2026, the Morón earthquake on top. The solutions are drawn from the Crisis section and arranged by the situation you are actually in. Figures come from WHO, CDC, EPA, the Sphere Handbook and the Red Cross.',
   "ve_verify":'<b>Verify locally.</b> This is general guidance, not a live local bulletin. For current conditions, shelters and official notices, check the sources below and your municipal Protección Civil.'},
 "es":{"title":"Cosas que sirven",
   "tagline":"Cosas que sirven — un repositorio de Fab City",
   "footer_line":'<b>Cosas que sirven</b> · sembrado desde <i>Whole Earth Catalog</i>, <i>Con nuestros propios esfuerzos</i> y <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza). Hecho para Fab City.',
   "ve_tab":"Venezuela","ve_resources":"Verifica con",
   "ve_intro":'Una guía específica para Venezuela ante la realidad que se repite: un <i>apagón</i> de varios días, el agua que se va o llega por pipa, las redes que se caen, los centros de salud sin insumos — y, desde el 24 de junio de 2026, el terremoto de Morón encima. Las soluciones vienen de la sección de Crisis, ordenadas según la situación en la que de verdad estás. Las cifras son de la OMS, CDC, EPA, el Manual Esfera y la Cruz Roja.',
   "ve_verify":'<b>Verifica localmente.</b> Esto es orientación general, no un boletín local en vivo. Para condiciones actuales, refugios y avisos oficiales, consulta las fuentes de abajo y tu Protección Civil municipal.'},
 "id":{"title":"Hal yang Berfungsi",
   "tagline":"Hal yang Berfungsi — repositori Fab City",
   "footer_line":'<b>Hal yang Berfungsi</b> · dibenihkan dari <i>Whole Earth Catalog</i>, <i>Con nuestros propios esfuerzos</i>, dan <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza). Dibuat untuk Fab City.',
   "ve_tab":"Venezuela","ve_resources":"Verifikasi dengan",
   "ve_intro":'Panduan khusus Venezuela untuk realitas yang berulang: <i>apagón</i> (pemadaman) berhari-hari, air yang berhenti atau datang dengan truk tangki, jaringan yang putus, klinik yang kekurangan pasokan — dan, sejak 24 Juni 2026, gempa Morón di atasnya. Solusi diambil dari bagian Krisis dan disusun menurut situasi yang sedang kamu hadapi. Angka berasal dari WHO, CDC, EPA, Buku Panduan Sphere, dan Palang Merah.',
   "ve_verify":'<b>Verifikasi secara lokal.</b> Ini panduan umum, bukan buletin lokal langsung. Untuk kondisi terkini, tempat penampungan, dan pengumuman resmi, periksa sumber di bawah dan Protección Civil setempat.'},
}
for _lg in ("en","es","id"):
    UI[_lg].update(EXTRA_UI[_lg])

# Venezuela playbook — scenarios reference Crisis entries by id (no data duplication)
VE_SCENARIOS = [
 {"key":"apagon",
  "t":("Power — a multi-day blackout","Apagón — varios días sin luz","Listrik — pemadaman berhari-hari"),
  "n":("Keep light, phones and medical devices alive; protect insulin; save the food in the fridge.",
       "Mantén luz, teléfonos y equipos médicos; protege la insulina; salva la comida del refrigerador.",
       "Jaga lampu, ponsel, dan alat medis; lindungi insulin; selamatkan makanan di kulkas."),
  "items":["crisis-lighting-small-power","crisis-keep-phones-alive","crisis-cold-chain","crisis-food-without-fridge","crisis-cooking-without-gas"]},
 {"key":"agua",
  "t":("Water — the supply stops","Agua — se corta el suministro","Air — pasokan berhenti"),
  "n":("Store what you have safely, make doubtful water drinkable, and ration to survival minimums.",
       "Almacena lo que tienes de forma segura, vuelve potable el agua dudosa y raciona a mínimos de supervivencia.",
       "Simpan air yang ada dengan aman, jadikan air meragukan layak minum, dan jatah ke batas bertahan hidup."),
  "items":["crisis-safe-water-storage","crisis-cloth-prefiltration","crisis-bleach-chlorination-cdc","crisis-sodis-solar","crisis-water-minimums","oshwa-pipe-t-piece"]},
 {"key":"comms",
  "t":("Comms — no signal, no internet","Comunicación — sin señal ni internet","Komunikasi — tanpa sinyal/internet"),
  "n":("Stretch battery, agree a check-in, and use off-grid messaging when the network is down.",
       "Estira la batería, acuerda un punto de contacto y usa mensajería sin red cuando se cae la señal.",
       "Hemat baterai, sepakati titik kontak, dan pakai pesan luring saat jaringan mati."),
  "items":["crisis-keep-phones-alive","crisis-meshtastic","crisis-briar","crisis-ushahidi"]},
 {"key":"salud",
  "t":("Health — clinics short on supplies","Salud — centros sin insumos","Kesehatan — klinik minim pasokan"),
  "n":("Treat dehydration, keep hands and water clean to stop outbreaks, and fabricate the consumables that run out.",
       "Trata la deshidratación, mantén manos y agua limpias para frenar brotes y fabrica los insumos que se agotan.",
       "Atasi dehidrasi, jaga kebersihan tangan dan air untuk cegah wabah, dan buat sendiri bahan habis pakai yang langka."),
  "items":["crisis-ors-home-recipe","crisis-hand-hygiene","crisis-latrine-excreta","crisis-cold-chain","oshwa-umbilical-cord-clamp","oshwa-oxygen-supply-fitting","oshwa-oropharyngeal-airway"]},
 {"key":"sismo",
  "t":("After a quake (Morón, 2026)","Después de un sismo (Morón, 2026)","Setelah gempa (Morón, 2026)"),
  "n":("Check the building before re-entering, secure safe water, and organise the block.",
       "Revisa el edificio antes de volver a entrar, asegura agua potable y organiza la cuadra.",
       "Periksa bangunan sebelum masuk kembali, amankan air bersih, dan organisir lingkungan."),
  "items":["crisis-secure-building-after-quake","crisis-safe-water-storage","crisis-mutual-aid","crisis-keep-phones-alive"]},
]
VE_RESOURCES = [
 {"name":"ReliefWeb — Venezuela","url":"https://reliefweb.int/country/ven"},
 {"name":"PAHO/OPS — Venezuela","url":"https://www.paho.org/en/venezuela"},
 {"name":"UN OCHA — Venezuela","url":"https://www.unocha.org/venezuela"},
 {"name":"Funvisis (sismología)","url":"http://www.funvisis.gob.ve"},
]
dataset["venezuela"] = {
  "scenarios":[{"key":s["key"],"title":s["t"][0],"title_es":s["t"][1],"title_id":s["t"][2],
                "note":s["n"][0],"note_es":s["n"][1],"note_id":s["n"][2],"items":s["items"]} for s in VE_SCENARIOS],
  "resources":VE_RESOURCES,
}
dataset["meta"]["ve_scenario_count"] = len(VE_SCENARIOS)

# --- Venezuela page: lead (current quake), the compound-crisis narrative, principle ---
VE_TEXT = {
 "en":{
  "ve_h_reality":"Not only an earthquake",
  "ve_h_playbook":"What helps in the days after",
  "ve_resources":"Live & official sources",
  "ve_lead":"On 24 June 2026, two earthquakes — magnitude 7.2, then 7.5 some forty seconds later — struck the Caribbean coast near Morón, about 160 km west of Caracas. It is the strongest quake in Venezuela since 1900. As of 26 June the confirmed toll is at least 1,430 dead, thousands injured and some 68,900 missing — and rising, with rescuers still searching some 250 collapsed or damaged buildings; the Altamira and Los Palos Grandes areas of Caracas are among the worst hit. These numbers will be out of date by the time you read them — for the live count and official notices, use the sources below.",
  "ve_reality":"But this quake did not hit a country that was working. It hit one that has been in a humanitarian emergency for the better part of a decade. Nearly 7.9 million Venezuelans have left — the largest displacement in the Western Hemisphere. Around 7.6 million who stayed already needed humanitarian assistance before the ground moved. The national grid collapsed in 2019 and never fully recovered; the Guri dam still carries about 80% of the country's power, and the western states live with daily blackouts. Caracas has rationed water to millions. The hospitals were already short of supplies and staff. For millions of people, “the days after a disaster” is not an event — it is how life has worked for years.",
  "ve_principle":"That is the hard thing to say plainly: many Venezuelans are already experts at this. They have spent years purifying water, nursing a single fridge through blackouts, keeping one phone alive, splitting medicine, feeding a family on less. This page is not disaster theatre and it romanticizes none of it — nobody should have to live this way, and the real answer is relief now and systems that work. Until then these are tools that reduce harm and hold onto dignity: the same technological disobedience the rest of this archive documents, except here it is not history or theory. It is an ordinary week. The more you can make and mend what you need, the less a collapse can take from you.",
  "ve_live":"This page is tools for the days after, not a live bulletin. For the current toll, shelters and official notices, use the sources below and your local Protección Civil.",
 },
 "es":{
  "ve_h_reality":"No solo un terremoto",
  "ve_h_playbook":"Qué ayuda en los días después",
  "ve_resources":"Fuentes en vivo y oficiales",
  "ve_lead":"El 24 de junio de 2026, dos terremotos — magnitud 7,2 y, unos cuarenta segundos después, 7,5 — sacudieron la costa caribeña cerca de Morón, a unos 160 km al oeste de Caracas. Es el sismo más fuerte en Venezuela desde 1900. Al 26 de junio el saldo confirmado es de al menos 1.430 muertos, miles de heridos y unos 68.900 desaparecidos — y sigue subiendo, con rescatistas aún buscando entre unos 250 edificios colapsados o dañados; las zonas de Altamira y Los Palos Grandes en Caracas están entre las más afectadas. Estas cifras estarán desactualizadas cuando las leas — para el conteo en vivo y los avisos oficiales, usa las fuentes de abajo.",
  "ve_reality":"Pero este terremoto no golpeó a un país que funcionaba. Golpeó a uno que lleva casi una década en emergencia humanitaria. Casi 7,9 millones de venezolanos se han ido — el mayor desplazamiento del hemisferio occidental. Unos 7,6 millones de los que se quedaron ya necesitaban ayuda humanitaria antes de que temblara la tierra. La red eléctrica colapsó en 2019 y nunca se recuperó del todo; el Guri todavía carga cerca del 80% de la energía del país, y los estados del occidente viven con apagones diarios. Caracas raciona el agua a millones. Los hospitales ya estaban sin insumos y sin personal. Para millones de personas, “los días después del desastre” no son un evento — son como ha funcionado la vida desde hace años.",
  "ve_principle":"Eso es lo difícil de decir sin rodeos: muchos venezolanos ya son expertos en esto. Llevan años potabilizando agua, cuidando una sola nevera entre apagones, manteniendo vivo un teléfono, partiendo la medicina, dándole de comer a la familia con menos. Esta página no es teatro de catástrofe y no romantiza nada — nadie debería vivir así, y la respuesta de verdad es auxilio ahora y sistemas que funcionen. Mientras tanto, estas son herramientas que reducen el daño y sostienen la dignidad: la misma desobediencia tecnológica que documenta el resto de este archivo, solo que aquí no es historia ni teoría. Es una semana cualquiera. Mientras más puedas hacer y reparar lo que necesitas, menos te puede quitar el colapso.",
  "ve_live":"Esta página son herramientas para los días después, no un boletín en vivo. Para el saldo actual, los refugios y los avisos oficiales, usa las fuentes de abajo y tu Protección Civil.",
 },
 "id":{
  "ve_h_reality":"Bukan hanya gempa",
  "ve_h_playbook":"Yang membantu di hari-hari sesudahnya",
  "ve_resources":"Sumber langsung & resmi",
  "ve_lead":"Pada 24 Juni 2026, dua gempa — magnitudo 7,2, lalu 7,5 sekitar empat puluh detik kemudian — mengguncang pesisir Karibia dekat Morón, sekitar 160 km di barat Caracas. Ini gempa terkuat di Venezuela sejak 1900. Per 26 Juni, korban terkonfirmasi setidaknya 1.430 tewas, ribuan luka, dan sekitar 68.900 hilang — dan terus bertambah, dengan tim penyelamat masih mencari di sekitar 250 bangunan yang runtuh atau rusak; kawasan Altamira dan Los Palos Grandes di Caracas termasuk yang paling parah. Angka-angka ini akan usang saat kamu membacanya — untuk hitungan terkini dan pengumuman resmi, gunakan sumber di bawah.",
  "ve_reality":"Tetapi gempa ini tidak menimpa negara yang berfungsi. Ia menimpa negara yang sudah hampir satu dekade berada dalam darurat kemanusiaan. Hampir 7,9 juta warga Venezuela telah pergi — perpindahan terbesar di Belahan Barat. Sekitar 7,6 juta yang bertahan sudah membutuhkan bantuan bahkan sebelum tanah berguncang. Jaringan listrik nasional runtuh pada 2019 dan tak pernah pulih sepenuhnya; bendungan Guri masih menanggung sekitar 80% listrik negara, dan negara bagian barat hidup dengan pemadaman harian. Caracas menjatah air untuk jutaan orang. Rumah sakit sudah kekurangan pasokan dan tenaga. Bagi jutaan orang, “hari-hari setelah bencana” bukanlah peristiwa — itulah cara hidup berjalan selama bertahun-tahun.",
  "ve_principle":"Itulah yang sulit dikatakan terus terang: banyak warga Venezuela sudah ahli dalam hal ini. Bertahun-tahun mereka memurnikan air, merawat satu kulkas di tengah pemadaman, menjaga satu ponsel tetap hidup, membagi obat, memberi makan keluarga dengan lebih sedikit. Halaman ini bukan pertunjukan bencana dan tidak meromantisasi apa pun — tidak seorang pun seharusnya hidup begini, dan jawaban sebenarnya adalah bantuan sekarang dan sistem yang berfungsi. Sementara itu, ini adalah perkakas yang mengurangi bahaya dan menjaga martabat: pembangkangan teknologi yang sama yang didokumentasikan arsip ini, hanya saja di sini ia bukan sejarah atau teori. Ia adalah minggu biasa. Semakin banyak yang bisa kamu buat dan perbaiki sendiri, semakin sedikit yang bisa direnggut oleh keruntuhan.",
  "ve_live":"Halaman ini berisi perkakas untuk hari-hari sesudahnya, bukan buletin langsung. Untuk korban terkini, tempat penampungan, dan pengumuman resmi, gunakan sumber di bawah dan Protección Civil setempat.",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(VE_TEXT[_lg])

# footer credit (replaces the seeded-from line in all languages)
FOOTER = {
 "en":'<b>Things That Work</b> — curated by Tomas Diez, Fab City Foundation. Based on the Whole Earth Catalog, <i>Con nuestros propios esfuerzos</i> and <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza); crisis guidance from WHO, CDC, EPA, the Sphere Handbook, the Red Cross and Field Ready.',
 "es":'<b>Cosas que sirven</b> — curado por Tomas Diez, Fab City Foundation. Basado en el Whole Earth Catalog, <i>Con nuestros propios esfuerzos</i> y <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza); guía de crisis de la OMS, CDC, EPA, el Manual Esfera, la Cruz Roja y Field Ready.',
 "id":'<b>Hal yang Berfungsi</b> — dikurasi oleh Tomas Diez, Fab City Foundation. Berdasarkan Whole Earth Catalog, <i>Con nuestros propios esfuerzos</i>, dan <i>El Libro de la Familia</i> (FabLab-ULB &amp; Ernesto Oroza); panduan krisis dari WHO, CDC, EPA, Buku Panduan Sphere, Palang Merah, dan Field Ready.',
}
for _lg in ("en","es","id"):
    UI[_lg]["footer_line"] = FOOTER[_lg]

# report links, share, and the participatory "contribute" CTAs
CONTRIB_UI = {
 "en":{
   "report_h":"Report or find someone",
   "report_missing":"Report or find a missing person","report_damage":"Report or find a damaged building",
   "report_note":"Opens a separate citizen tool in a new tab.",
   "share_h":"Share","share_more":"More (Instagram, TikTok…)","share_copy":"Copy link","share_copied":"Link copied",
   "contribute_h":"Add what works",
   "contribute_lead":"Every other site right now is for reporting — who is missing, what collapsed. This page is for doing. If you know something that works, add it. If one of these worked for you, say so — that is how the next family learns it can be done.",
   "cta_suggest":"Suggest a solution","cta_success":"Share a success",
   "cta_soon":"The form is being published. Meanwhile, share your idea by WhatsApp or copy this page and send it.",
 },
 "es":{
   "report_h":"Reportar o buscar a alguien",
   "report_missing":"Reportar o buscar a un desaparecido","report_damage":"Reportar o ver un edificio dañado",
   "report_note":"Abre una herramienta ciudadana aparte en una pestaña nueva.",
   "share_h":"Compartir","share_more":"Más (Instagram, TikTok…)","share_copy":"Copiar enlace","share_copied":"Enlace copiado",
   "contribute_h":"Suma lo que sirve",
   "contribute_lead":"Todas las demás páginas ahora mismo son para reportar — quién falta, qué se cayó. Esta es para hacer. Si sabes algo que sirve, agrégalo. Si alguno de estos te funcionó, dilo — así la próxima familia aprende que se puede.",
   "cta_suggest":"Propón una solución","cta_success":"Comparte un caso que funcionó",
   "cta_soon":"El formulario se está publicando. Mientras tanto, comparte tu idea por WhatsApp o copia esta página y envíala.",
 },
 "id":{
   "report_h":"Laporkan atau cari seseorang",
   "report_missing":"Laporkan atau cari orang hilang","report_damage":"Laporkan atau lihat bangunan rusak",
   "report_note":"Membuka alat warga terpisah di tab baru.",
   "share_h":"Bagikan","share_more":"Lainnya (Instagram, TikTok…)","share_copy":"Salin tautan","share_copied":"Tautan disalin",
   "contribute_h":"Tambahkan yang berhasil",
   "contribute_lead":"Semua situs lain saat ini untuk melaporkan — siapa yang hilang, apa yang runtuh. Halaman ini untuk bertindak. Jika kamu tahu sesuatu yang berhasil, tambahkan. Jika salah satunya berhasil untukmu, katakan — begitulah keluarga berikutnya tahu ini bisa dilakukan.",
   "cta_suggest":"Usulkan solusi","cta_success":"Bagikan keberhasilan",
   "cta_soon":"Formulir sedang dipublikasikan. Sementara itu, bagikan idemu lewat WhatsApp atau salin halaman ini dan kirimkan.",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(CONTRIB_UI[_lg])

# explain the two channels: needs vs. tested solutions
CONTRIB2 = {
 "en":{
   "contribute_need_h":"Need a solution",
   "contribute_need_desc":"Raise a need — a problem people are facing that doesn't have a good answer yet. If you have an idea for solving it, add that too. The network picks these up and works on them.",
   "contribute_success_h":"Tried something that worked?",
   "contribute_success_desc":"Share a solution you've actually tested — in Venezuela or anywhere else — and what happened. Tested solutions are what the next family can trust and reuse.",
 },
 "es":{
   "contribute_need_h":"¿Necesitas una solución?",
   "contribute_need_desc":"Plantea una necesidad — un problema que la gente enfrenta y que todavía no tiene buena respuesta. Si tienes una idea para resolverlo, agrégala también. La red las recoge y trabaja en ellas.",
   "contribute_success_h":"¿Probaste algo que funcionó?",
   "contribute_success_desc":"Comparte una solución que hayas probado de verdad — en Venezuela o en cualquier otro lugar — y qué pasó. Las soluciones probadas son las que la próxima familia puede usar con confianza.",
 },
 "id":{
   "contribute_need_h":"Butuh solusi?",
   "contribute_need_desc":"Sampaikan sebuah kebutuhan — masalah yang dihadapi orang yang belum punya jawaban baik. Jika kamu punya ide untuk menyelesaikannya, tambahkan juga. Jaringan akan menanggapi dan menggarapnya.",
   "contribute_success_h":"Mencoba sesuatu yang berhasil?",
   "contribute_success_desc":"Bagikan solusi yang benar-benar sudah kamu uji — di Venezuela atau di mana pun — dan apa hasilnya. Solusi yang teruji itulah yang bisa dipercaya dan dipakai ulang oleh keluarga berikutnya.",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(CONTRIB2[_lg])
for _lg, _v in {"en": "Open the form", "es": "Abrir el formulario", "id": "Buka formulir"}.items():
    UI[_lg]["open_form"] = _v

# Home / landing + unified finder
HOME_UI = {
 "en":{
   "home_tab":"Start",
   "home_lead":"Solutions that work when the services don't — water, power, food, sanitation, health, shelter. Tell it what you need, or browse the archive.",
   "home_search_ph":"What do you need?  e.g. “the water is cut and I have bleach”, “no power for the fridge”, “no signal”…",
   "home_results":"matches","home_none":"No matches yet — try saying the need in your own words: water, power, cook, toilet, signal, fever, cold…",
   "route_crisis_h":"I'm in a crisis","route_crisis_d":"The days after a disaster — water, power, comms, health and sanitation when services are down.",
   "route_ve_h":"Venezuela","route_ve_d":"The June 2026 quake, on a country already years in survival mode. Report, share, contribute.",
   "route_browse_h":"Browse the archive","route_browse_d":"Every solution across the six traditions — filter by need, source or move.",
   "route_index_h":"Whole Earth Index","route_index_d":"The full 1968–2002 run, each issue linked to the Internet Archive.",
 },
 "es":{
   "home_tab":"Inicio",
   "home_lead":"Soluciones que funcionan cuando los servicios no — agua, luz, comida, saneamiento, salud, refugio. Dile qué necesitas, o explora el archivo.",
   "home_search_ph":"¿Qué necesitas?  p. ej. “se cortó el agua y tengo cloro”, “sin luz para la nevera”, “sin señal”…",
   "home_results":"resultados","home_none":"Sin resultados aún — describe la necesidad con tus palabras: agua, luz, cocinar, baño, señal, fiebre, frío…",
   "route_crisis_h":"Estoy en una crisis","route_crisis_d":"Los días después de un desastre — agua, luz, comunicación, salud y saneamiento cuando fallan los servicios.",
   "route_ve_h":"Venezuela","route_ve_d":"El sismo de junio de 2026, sobre un país que ya llevaba años en modo supervivencia. Reporta, comparte, contribuye.",
   "route_browse_h":"Explorar el archivo","route_browse_d":"Todas las soluciones de las seis tradiciones — filtra por necesidad, fuente o gesto.",
   "route_index_h":"Índice de Whole Earth","route_index_d":"La colección completa 1968–2002, cada número enlazado al Internet Archive.",
 },
 "id":{
   "home_tab":"Mulai",
   "home_lead":"Solusi yang berhasil ketika layanan tidak — air, listrik, pangan, sanitasi, kesehatan, hunian. Sebutkan kebutuhanmu, atau jelajahi arsip.",
   "home_search_ph":"Apa yang kamu butuhkan?  mis. “air mati dan saya punya pemutih”, “tak ada listrik untuk kulkas”, “tak ada sinyal”…",
   "home_results":"hasil","home_none":"Belum ada hasil — sebutkan kebutuhanmu dengan kata-katamu: air, listrik, masak, toilet, sinyal, demam, dingin…",
   "route_crisis_h":"Saya dalam krisis","route_crisis_d":"Hari-hari setelah bencana — air, listrik, komunikasi, kesehatan, dan sanitasi saat layanan mati.",
   "route_ve_h":"Venezuela","route_ve_d":"Gempa Juni 2026, di negara yang sudah bertahun-tahun bertahan hidup. Lapor, bagikan, kontribusi.",
   "route_browse_h":"Jelajahi arsip","route_browse_d":"Semua solusi dari enam tradisi — saring berdasarkan kebutuhan, sumber, atau tindakan.",
   "route_index_h":"Indeks Whole Earth","route_index_d":"Koleksi lengkap 1968–2002, tiap terbitan tertaut ke Internet Archive.",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(HOME_UI[_lg])

dataset["venezuela"]["report"] = {
  "missing":"https://desaparecidosterremotovenezuela.com/",
  "damage":"https://terremotovenezuela.com/",
}
# Airtable form URLs — paste the published form-view share links to enable direct submit.
# Base: "Things That Work — Venezuela" (appzN0sHyXMj2XLTl), Fab City Foundation workspace.
dataset["venezuela"]["forms"] = {
  "solutions": "https://airtable.com/appzN0sHyXMj2XLTl/shraCUyZPfat1knLY",
  "success":   "https://airtable.com/appzN0sHyXMj2XLTl/shr0km0E8NekC6OOp",
}

# --- 3D-printing response (Spanish-priority) ---
PRINT_UI = {
 "en":{
  "print_h":"3D-printing response","print_lead":"If you have a 3D printer you can help now: print splints and orthotics and drop them at a collection center. If you need one and have no printer, ask in the form or find a center below.",
  "print_cta_h":"Have a 3D printer? Join in","print_files_h":"Print files — Ferulas Venezuela","print_download":"Download",
  "print_models_h":"Models (medical donation)","print_use_h":"How to fit it","print_centers_h":"Where to drop off — collection centers","print_centers_all":"Full list of centers (DOCX)",
  "print_designs_h":"More designs & repositories","print_materials_h":"Materials & print settings",
  "print_materials":"Print from the profile already inside the .3mf file (open it in your slicer). These are thermoformable splints: they soften in hot water and are moulded to the limb.",
  "print_caveat":"Medical donation — ideally fitted by or with a health worker; it is not a substitute for professional care. Follow the temperature for YOUR material: the guides differ (warm / never-boiling for some, 90–100 °C for OSTEC). Never overheat against bare skin.",
 },
 "es":{
  "print_h":"Respuesta con impresión 3D","print_lead":"Si tienes una impresora 3D puedes ayudar ahora: imprime férulas y órtesis y déjalas en un centro de acopio. Si necesitas una y no tienes impresora, pídela en el formulario o busca un centro abajo.",
  "print_cta_h":"¿Tienes una impresora 3D? Súmate","print_files_h":"Archivos para imprimir — Férulas Venezuela","print_download":"Descargar",
  "print_models_h":"Modelos (donación médica)","print_use_h":"Cómo colocarla","print_centers_h":"Dónde entregar — centros de acopio","print_centers_all":"Lista completa de centros (DOCX)",
  "print_designs_h":"Más diseños y repositorios","print_materials_h":"Materiales y ajustes de impresión",
  "print_materials":"Imprime con el perfil que ya viene dentro del archivo .3mf (ábrelo en tu slicer). Son férulas termoformables: se reblandecen en agua caliente y se moldean al miembro.",
  "print_caveat":"Donación médica — idealmente colocada por o con personal de salud; no sustituye la atención profesional. Sigue la temperatura indicada para TU material: las guías difieren (agua tibia / nunca hirviendo en unas, 90–100 °C en OSTEC). Nunca recalientes sobre la piel desnuda.",
 },
 "id":{
  "print_h":"Respons cetak 3D","print_lead":"Jika kamu punya printer 3D, kamu bisa membantu sekarang: cetak bidai (splint) dan ortosis lalu antarkan ke pusat pengumpulan. Jika kamu membutuhkannya dan tak punya printer, minta lewat formulir atau cari pusat di bawah.",
  "print_cta_h":"Punya printer 3D? Bergabunglah","print_files_h":"Berkas cetak — Ferulas Venezuela","print_download":"Unduh",
  "print_models_h":"Model (donasi medis)","print_use_h":"Cara memasang","print_centers_h":"Tempat pengantaran — pusat pengumpulan","print_centers_all":"Daftar lengkap pusat (DOCX)",
  "print_designs_h":"Desain & repositori lain","print_materials_h":"Material & pengaturan cetak",
  "print_materials":"Cetak dengan profil yang sudah ada di dalam berkas .3mf (buka di slicer-mu). Ini bidai termoform: melunak di air panas dan dibentuk pada anggota tubuh.",
  "print_caveat":"Donasi medis — sebaiknya dipasang oleh atau bersama tenaga kesehatan; bukan pengganti perawatan profesional. Ikuti suhu untuk materialmu: panduannya berbeda (air hangat / jangan mendidih pada sebagian, 90–100 °C pada OSTEC). Jangan memanaskan berlebihan di atas kulit telanjang.",
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(PRINT_UI[_lg])

# Load live PrintForHelp center count (updated by scripts/sync_printforhelp.py)
_pfh_json = DATA / "printforhelp_centers.json"
_pfh      = json.loads(_pfh_json.read_text()) if _pfh_json.exists() else {"count": 25, "countries": ["USA", "MX", "VE"]}
_pfh_cc   = " · ".join(_pfh.get("countries", ["USA", "MX", "VE"]))
_pfh_n    = _pfh.get("count", 25)

dataset["venezuela"]["printing"] = {
 "groups":[
   {"name":"Férulas Venezuela","url":"https://chat.whatsapp.com/DaseixyFONlH0xIpXCaGyW",
    "note":"Print & donate splints","note_es":"Imprime y dona férulas","note_id":"Cetak & donasikan bidai"},
   {"name":"Maker por Venezuela","url":"https://chat.whatsapp.com/I7IJTKcI54V3Z6GfAkKsCE",
    "note":"Makers network — coordination","note_es":"Red de makers — coordinación","note_id":"Jaringan maker — koordinasi"},
 ],
 "country_groups":[
   {"country":"Argentina","url":"https://chat.whatsapp.com/CjrAqahbgRs6NFAaaoHBBz"},
   {"country":"Bolivia","url":"https://chat.whatsapp.com/EiYvxJcHGL33CMlABLZQjj"},
   {"country":"Chile","url":"https://chat.whatsapp.com/DKzmYSJk5vrIj91OGquJKD"},
   {"country":"Colombia","url":"https://chat.whatsapp.com/LTJXOV0yPP8AzW1sGly2OW"},
   {"country":"Ecuador","url":"https://chat.whatsapp.com/DUx6z330AlmBpacp8DbaAN"},
   {"country":"Spain","country_es":"España","country_id":"Spanyol","url":"https://chat.whatsapp.com/0nXIPG0NBvxK4RQJL1EsxO"},
   {"country":"Mexico","country_es":"México","country_id":"Meksiko","url":"https://chat.whatsapp.com/LFv1BNlvLnsEzom69IWbMl"},
   {"country":"Peru","country_es":"Perú","url":"https://chat.whatsapp.com/HaPFT3jaRhsIZvQUhwmHlJ"},
   {"country":"Brazil","country_es":"Brasil","country_id":"Brasil","url":"https://chat.whatsapp.com/Iewg2qG8WZIIqzVzcqJkIS"},
   {"country":"USA","country_es":"EE. UU.","country_id":"AS","url":"https://chat.whatsapp.com/INOOTwvZand8b1y8drYz3O"},
   {"country":"Venezuela","url":"https://chat.whatsapp.com/G0Zkjv4z8DLJ8yEwOft1RY"},
 ],
 "hubs":[
   {"name":"Impresión 3D Solidaria — Chile",
    "url":"https://cdordelly.notion.site/VE-Impresi-n-3D-Solidaria-Chile-38df19d5427a80c6aa6ec0c102d8b2e0",
    "note":"Chile coordination hub — printers, centers, updates",
    "note_es":"Hub de coordinación Chile — impresoras, centros, novedades",
    "note_id":"Hub koordinasi Chile — printer, pusat, info terkini"},
 ],
 "files":[
   {"label":"Férula pequeña (.3mf)","href":"/files/ferulas/ferula-pequena.3mf"},
   {"label":"Férula mediana (.3mf)","href":"/files/ferulas/ferula-mediana.3mf"},
   {"label":"Férula grande (.3mf)","href":"/files/ferulas/ferula-grande.3mf"},
   {"label":"Identificador de modelos (PDF)","href":"/files/ferulas/ferula-identificador.pdf"},
   {"label":"Guía de uso / colocación (PDF)","href":"/files/ferulas/ferula-guia-uso.pdf"},
   {"label":"Instrucciones OSTEC (PDF)","href":"/files/ferulas/ferula-instrucciones-ostec.pdf"},
 ],
 "models":["Mano (adulto)","Mano (infantil)","Palma y meñique","Pie","Extensión de dedo","Antebrazo (pequeña)","Codo (infantil)"],
 "use_steps":{
   "es":["Proteger: venda o capa sobre la piel.","Calentar el material según su guía (agua tibia o 90–100 °C, según el material).","Moldear sobre el miembro antes de que enfríe.","Fijar con venda elástica o velcro: firme, no apretada.","Verificar la inmovilización; endurece al enfriar."],
   "en":["Protect: bandage or layer over the skin.","Warm the material per its guide (warm water or 90–100 °C, depending on the material).","Mould onto the limb before it cools.","Fix with elastic bandage or velcro: firm, not tight.","Verify immobilisation; it hardens as it cools."],
   "id":["Lindungi: perban atau lapisan di atas kulit.","Panaskan material sesuai panduannya (air hangat atau 90–100 °C, tergantung material).","Bentuk pada anggota tubuh sebelum dingin.","Kencangkan dengan perban elastis atau velcro: kokoh, tidak ketat.","Periksa imobilisasi; mengeras saat dingin."],
 },
 "centers_doc":"/files/ferulas/centros-de-acopio.docx",
 "pfh":{
   "url":"https://printforhelp.org/centers",
   "note":f"{_pfh_n} drop-off centers, part requests & printing tracker ({_pfh_cc})",
   "note_es":f"{_pfh_n} centros de acopio, solicitud de piezas y seguimiento ({_pfh_cc})",
   "note_id":f"{_pfh_n} pusat pengumpulan, permintaan suku cadang & pelacak cetak ({_pfh_cc})",
 },
 "centers":[
   {"city":"Caracas","detail":"Plaza Altamira, frente al obelisco, después de las 10 AM (red de distribución a La Guaira)"},
   {"city":"Maracaibo","detail":"El Tacón · Fabiana Marín +58 424-6857685"},
   {"city":"Mérida","detail":"CUMIS – Colegio de médicos · Grupo de Rescate Andino (Forestal)"},
   {"city":"Maracay","detail":"Teatro Ópera"},
   {"city":"Aragua","detail":"Av. 19 de Abril, C.C. La Capilla, piso 1, local 26"},
   {"city":"Carabobo","detail":"Av. Monseñor Adams, El Viñedo, Edif. Tailandia, mezzanina"},
   {"city":"San Cristóbal","detail":"UCAT (sede vieja) · ULA · UNET (ing. civil) · Rotaract"},
   {"city":"Barquisimeto","detail":"Concesionarios JAC · Anohia Goitia +58 414-5230879"},
   {"city":"Barcelona (Anzoátegui)","detail":"Residencia Los Parques Green (cerca de Puente Real) · Lineth Torres 0414-1986067"},
   {"city":"Barinas","detail":"Ing. Andréa +58 424-5709067"},
   {"city":"Guanare","detail":"PERCHA, Av. Unda entre cra 7 y 8"},
   {"city":"Lechería","detail":"Gianmarco D'Alessandro +58 424-8867167"},
   {"city":"Colombia — Cali","detail":"David Chirinos +57 318-2599037 · Av 2E Norte #52AN-07, Bo. Álamos (FedEx/DHL)"},
   {"city":"Phoenix, USA","detail":"EcoRobotik Learning Center, Glendale AZ 85308 · +1 480-294-5714"},
 ],
 "designs":[
   {"name":"MyOrthotics 2.0 — Adriana Cabrera","url":"https://github.com/AdrianaCabrera/MyOrthotics-2.0",
    "what":"Printable orthotic/splint templates + manual (semi-paralysis, first-aid, temporary).","what_es":"Plantillas de órtesis/férula imprimibles + manual (semiparálisis, primeros auxilios, uso temporal).","what_id":"Templat ortosis/bidai cetak + manual (semi-lumpuh, P3K, sementara)."},
   {"name":"Field Ready (Wikifactory)","url":"https://wikifactory.com/+FieldReady/",
    "what":"Open humanitarian printable hardware (medical, WASH).","what_es":"Hardware humanitario imprimible y abierto (médico, agua/saneamiento).","what_id":"Perangkat keras kemanusiaan terbuka yang dapat dicetak (medis, WASH)."},
   {"name":"MSF — 3D Printing for All","url":"https://www.printables.com/@3Dprintingforall",
    "what":"Printable field-medical parts (also in this archive).","what_es":"Piezas médicas imprimibles para terreno (también en este archivo).","what_id":"Komponen medis lapangan yang dapat dicetak (juga di arsip ini)."},
 ],
}

# --- Field Ready Portfolio (curated, OSHWA-certified, downloadable, 3D-printable) ---
FR_UI = {
 "en":{"fr_h":"Field Ready — tested printable designs","fr_lead":"Open-hardware parts (most OSHWA-certified) for clinics and relief — each with its file, material and print time. Designed in ABS; PLA or PETG can substitute for non-load, non-sterile parts.",
   "fr_note":"Clinical/critical parts must be checked by a health worker before use; printed plastic is not sterile and not a certified medical device. Confirm fit and material for the specific use.",
   "fr_cat_trauma":"Trauma & orthotics","fr_cat_resp":"Respiratory & critical care","fr_cat_infant":"Maternal & infant","fr_cat_clin":"Clinical instruments","fr_cat_water":"Water lines & connectors"},
 "es":{"fr_h":"Field Ready — diseños probados para imprimir","fr_lead":"Piezas de hardware abierto (la mayoría con certificación OSHWA) para clínicas y emergencia — cada una con su archivo, material y tiempo de impresión. Diseñadas en ABS; se puede sustituir por PLA o PETG en piezas sin carga ni esterilidad.",
   "fr_note":"Las piezas clínicas o críticas deben ser revisadas por personal de salud antes de usarse; el plástico impreso no es estéril ni un dispositivo médico certificado. Confirma el ajuste y el material para cada uso.",
   "fr_cat_trauma":"Trauma y órtesis","fr_cat_resp":"Respiratorio y cuidados críticos","fr_cat_infant":"Materno-infantil","fr_cat_clin":"Instrumental clínico","fr_cat_water":"Agua y conexiones"},
 "id":{"fr_h":"Field Ready — desain cetak teruji","fr_lead":"Komponen perangkat keras terbuka (kebanyakan bersertifikat OSHWA) untuk klinik dan tanggap darurat — masing-masing dengan berkas, material, dan waktu cetaknya. Dirancang dalam ABS; PLA atau PETG bisa menggantikan untuk bagian non-beban dan non-steril.",
   "fr_note":"Komponen klinis/kritis harus diperiksa tenaga kesehatan sebelum dipakai; plastik cetak tidak steril dan bukan alat medis bersertifikat. Pastikan kecocokan dan material untuk tiap penggunaan.",
   "fr_cat_trauma":"Trauma & ortotik","fr_cat_resp":"Pernapasan & perawatan kritis","fr_cat_infant":"Ibu & bayi","fr_cat_clin":"Instrumen klinis","fr_cat_water":"Saluran air & sambungan"},
}
for _lg in ("en","es","id"):
    UI[_lg].update(FR_UI[_lg])

def _fr(cat,name,what,mat,time,oshwa,thing):
    return {"cat":cat,"name":name,"what":what,"mat":mat,"time":time,"oshwa":oshwa,
            "url":"https://www.thingiverse.com/thing:"+thing}
dataset["venezuela"]["fieldready"] = {"source_url":"https://wikifactory.com/+FieldReady/","items":[
 _fr("trauma","Finger Brace","Férula de dedo","ABS","1–2 h","US000175","1673843"),
 _fr("trauma","Wrist Brace (small)","Férula de muñeca (pequeña)","ABS","1–2 h","US000216","2443844"),
 _fr("trauma","Wrist Brace (large)","Férula de muñeca (grande)","ABS","2–3 h","US000217","2161679"),
 _fr("resp","Oxygen Supply Fitting","Conector de suministro de oxígeno","ABS","<1 h","US000204","1562079"),
 _fr("resp","Ventilator Connector","Conector de ventilador","ABS","1–2 h","US000211","1618837"),
 _fr("resp","Nebulizer T Fitting","Conexión en T para nebulizador","ABS","2–3 h","US000224","1562031"),
 _fr("resp","Nebulizer Connector","Conector de nebulizador","ABS","<1 h","US000209","1409472"),
 _fr("resp","Vacuum Suction Pump Connector","Conector de bomba de succión","ABS","<1 h","US000213","2449912"),
 _fr("infant","Umbilical Cord Clamp","Pinza de cordón umbilical","ABS","<1 h","US000203","1528789"),
 _fr("infant","Infant Warmer Corner Piece","Pieza de esquina para calentador infantil","ABS","2–3 h","US000223","1562004"),
 _fr("infant","Fetoscope (3DP)","Fetoscopio (estetoscopio fetal)","ABS","3–5 h","US000218","2161652"),
 _fr("clin","Tweezers / Forceps","Pinzas / fórceps","ABS","<1 h","US000212","1727040"),
 _fr("clin","Scalpel Truss Handle","Mango de bisturí","ABS","<1 h","US000206","1479421"),
 _fr("clin","Otoscope Specula","Espéculo de otoscopio","ABS","<1 h","US000208","1618841"),
 _fr("clin","IV Bag Hook","Gancho para bolsa IV","ABS","1–2 h","US000205","1562085"),
 _fr("clin","Kidney Tray","Riñonera (bandeja clínica)","ABS","2–3 h","","2161664"),
 _fr("clin","Heat-Shrunk Sharps Box","Contenedor de objetos punzantes","PET + ABS","2–3 h","","3122937"),
 _fr("clin","ECG Limb Lead","Electrodo de extremidad (ECG)","ABS","<1 h","US000210","1409472"),
 _fr("clin","Medical-Device Switch Handle","Palanca para equipo médico","ABS","1–2 h","US000226","1618845"),
 _fr("water","Water Cap","Tapa para tanque / tubería de agua","ABS","1–2 h","US000176","2464301"),
 _fr("water","Pipe T-Piece","Unión en T para tubería","ABS","<1 h","US000181","1562058"),
 _fr("water","2” Tri-Clamp","Abrazadera tri-clamp de 2”","ABS","5–8 h","US000179","1561955"),
 _fr("water","Hose Clamp","Abrazadera de manguera","ABS","1–2 h","US000180","28447"),
]}

# --- Community designs surfaced prominently in the /venezuela 3D-printing response ---
for _lg,_h,_l in [("en","Community designs","Shared by makers in Venezuela for this response — print and donate."),
                  ("es","Diseños de la comunidad","Compartidos por makers en Venezuela para esta respuesta — imprime y dona."),
                  ("id","Desain komunitas","Dibagikan oleh maker di Venezuela untuk respons ini — cetak dan donasikan.")]:
    UI[_lg]["community_h"]=_h; UI[_lg]["community_lead"]=_l
dataset["venezuela"]["community"] = {"items":[
 {"name":"Férula de corte láser S·M·L","what":"Laser-cut temporary immobilisation splint — 3 mm MDF (also 5 mm, plywood, cardboard). S/M/L sizes with measurements and recommended uses; 100% editable, open Illustrator file.","what_es":"Férula de inmovilización temporal cortada a láser — MDF de 3 mm (también 5 mm, contrachapado, cartón). Tallas S/M/L con medidas y usos recomendados; archivo de Illustrator 100% editable y abierto.","what_id":"Bidai imobilisasi sementara potong laser — MDF 3 mm (juga 5 mm, tripleks, kardus). Ukuran S/M/L dengan ukuran & penggunaan; berkas Illustrator 100% dapat diedit & terbuka.","author":"Carlos Torres · @Cato_dg","download":"/files/ferulas/ferula-corte-laser-s-m-l.pdf","accent":"laser","pill":"LÁSER","span2":True},
 {"name":"Férula corte láser — archivos (Drive)","what":"Drive folder with the laser-cut splint source files (S·M·L) to download and edit.","what_es":"Carpeta de Drive con los archivos fuente de la férula de corte láser (S·M·L) para descargar y editar.","what_id":"Folder Drive berisi berkas sumber bidai potong laser (S·M·L) untuk diunduh dan diedit.","author":"Carlos Torres · @Cato_dg","url":"https://drive.google.com/drive/folders/1n3Np5F3PCvhwVnZ1qS07f8hoiUE3TB7e","tag":"Drive","accent":"laser","pill":"LÁSER"},
 {"name":"Férulas para mascotas (perros/gatos)","what":"Printable splints to immobilise the affected leg of a pet, by size. The thermoformable flat splint prints in PLA (soften in warm water to shape it); the paw-shaped immobilisers in PLA or PETG. ≥30% infill; supports and a brim on open printers. Secure with bandage and straps, ideally with veterinary guidance.","what_es":"Férulas imprimibles para inmovilizar la patita afectada de una mascota, según su tamaño. La férula plana termoformable se imprime en PLA (se ablanda en agua tibia para moldearla); los inmovilizadores con forma de patita, en PLA o PETG. Relleno ≥30%; soportes y brim en impresoras abiertas. Se fija con vendaje y cintas, idealmente con orientación veterinaria.","what_id":"Bidai cetak untuk imobilisasi kaki hewan peliharaan yang cedera, sesuai ukuran. Bidai datar termoform dicetak PLA (lunakkan di air hangat untuk dibentuk); imobilizer bentuk kaki dengan PLA atau PETG. Isian ≥30%; penyangga & brim pada printer terbuka. Kencangkan dengan perban & tali, idealnya dengan panduan dokter hewan.","download":"/files/ferulas/ferula-mascotas.3mf","accent":"pet","pill":"PETS","pill_es":"MASCOTAS","pill_id":"HEWAN","span2":True},
 {"name":"Guía de uso (mascotas)","what":"How to print, thermoform and fit the splints — 6 steps, from identification to the final check.","what_es":"Cómo imprimir, termoformar y colocar las férulas — 6 pasos, de la identificación a la verificación.","what_id":"Cara mencetak, termoform, dan memasang bidai — 6 langkah, dari identifikasi hingga pemeriksaan akhir.","url":"/files/ferulas/guia-mascotas.html","tag":"Guía","accent":"pet","pill":"PETS","pill_es":"MASCOTAS","pill_id":"HEWAN"},
 {"name":"Modelos STL — mascotas (para editar)","what":"The raw STL models behind the pet splints — for editing, resizing, or remixing. To just print, use the 3MF bundle above.","what_es":"Los modelos STL de las férulas para mascotas — para editar, redimensionar o remezclar. Para solo imprimir, usa el paquete 3MF de arriba.","what_id":"Model STL mentah dari bidai hewan peliharaan — untuk diedit, mengubah ukuran, atau memodifikasi. Untuk langsung mencetak, gunakan paket 3MF di atas.","download":"/files/ferulas/ferulas-mascotas-stl.zip","accent":"pet","pill":"PETS","pill_es":"MASCOTAS","pill_id":"HEWAN"},
 {"name":"Emergencia Venezuela — paquete","what":"Ready-to-print bundle of medical parts.","what_es":"Paquete listo para imprimir (varias piezas médicas).","what_id":"Paket siap cetak (beberapa komponen medis).","author":"Férulas 3D Venezuela","download":"/files/ferulas/emergencia-venezuela.3mf","tag":"3MF"},
 {"name":"Gancho para suero (doble)","what":"Hang two IV bags with no pole.","what_es":"Cuelga dos bolsas de suero sin soporte.","what_id":"Gantung dua kantong infus tanpa tiang.","author":"Salvador Aguilera","url":"https://makerworld.com/en/models/2984757-hook-for-double-medical-solution","tag":"MakerWorld"},
 {"name":"Gancho para suero (individual)","what":"Hang one IV bag with no pole.","what_es":"Cuelga una bolsa de suero sin soporte.","what_id":"Gantung satu kantong infus tanpa tiang.","author":"Salvador Aguilera","url":"https://makerworld.com/en/models/2984932-hook-for-individual-medical-solution","tag":"MakerWorld"},
 {"name":"Rigidizador de cuello (S·M·L)","what":"Cervical brace, 3 sizes, PETG + velcro.","what_es":"Férula cervical, 3 tallas, PETG + velcro.","what_id":"Penyangga leher, 3 ukuran, PETG + velcro.","author":"fernandoarmas","url":"https://makerworld.com/en/models/2984480-neck-splint","tag":"MakerWorld"},
 {"name":"Férulas 3D — guía de uso","what":"How to fit six splints, step by step.","what_es":"Cómo colocar seis férulas, paso a paso.","what_id":"Cara memasang enam bidai, langkah demi langkah.","author":"CapasUp","url":"https://bio.capasup.xyz/ferulas","tag":"Guía"},
 {"name":"Anti-Smell Clip","what":"Wearable 95A TPU nose clip for odor protection — sanitation work, rubble clearing, foul environments. Clips over the nose, reusable and washable. 17 min, TPU 95A.","what_es":"Clip nasal de TPU 95A para protección de olores — saneamiento, remoción de escombros, ambientes malolientes. Se coloca sobre la nariz, reutilizable y lavable. 17 min, TPU 95A.","what_id":"Klip hidung TPU 95A untuk perlindungan bau — sanitasi, pembersihan puing, lingkungan berbau. Dipasang di hidung, dapat dipakai ulang dan dicuci. 17 menit, TPU 95A.","author":"ginoadriano","url":"https://makerworld.com/en/models/1614021-anti-smell-clip-wearable-odor-defense-system","tag":"MakerWorld"},
 {"name":"Floating Nose Clip","what":"PLA nose clip that floats if dropped — for wading through flood water or any water contact. Optional lanyard hole. 17 min, PLA.","what_es":"Clip nasal de PLA que flota si se cae — para vadear agua de inundación o cualquier contacto con agua. Agujero para cordón opcional. 17 min, PLA.","what_id":"Klip hidung PLA yang mengapung jika jatuh — untuk menyeberangi air banjir atau kontak air apapun. Lubang tali opsional. 17 menit, PLA.","author":"MadAnt","url":"https://makerworld.com/en/models/2876214-floating-nose-clip","tag":"MakerWorld"},
 {"name":"Fisurometro","what":"Crack gauge — adhesive-mounted to monitor wall fractures after a quake. Mark the date; check weekly or monthly if the crack is displacing.","what_es":"Medidor de grietas — se instala con cinta adhesiva para vigilar si una fisura crece tras un sismo. Anota la fecha y controla semanalmente si la grieta se desplaza.","what_id":"Pengukur retakan — dipasang dengan perekat untuk memantau retak dinding setelah gempa. Tandai tanggal; periksa tiap minggu apakah retakan bergerak.","author":"Masterality","url":"https://www.crealitycloud.com/model-detail/fisurometro","tag":"Creality Cloud"},
 {"name":"Hebilla para correas (buckle)","what":"Printable side-release buckle to fasten splint straps. PETG recommended; print the female part upright with supports.","what_es":"Hebilla de liberación lateral imprimible para sujetar las correas de las férulas. PETG recomendado; imprime la parte hembra de pie y con soportes.","what_id":"Gesper lepas-samping cetak untuk mengencangkan tali bidai. Disarankan PETG; cetak bagian female berdiri dengan penyangga.","author":"Lu_Pi_314","url":"https://makerworld.com/en/models/1170825-buckle","tag":"MakerWorld"},
 {"name":"Identificadores e instrucciones (papel)","what":"Labels and instructions to print on paper: identify each 3D splint and how to fit it.","what_es":"Etiquetas e instrucciones para imprimir en papel: identifica cada férula 3D y cómo colocarla.","what_id":"Label dan instruksi untuk dicetak di kertas: kenali tiap bidai 3D dan cara memasangnya.","download":"/files/ferulas/identificadores-instrucciones-papel.pdf","tag":"PDF"},
]}

VE_CONTEXT = [
 {"v":("M7.2 → M7.5 · 24 Jun 2026","M7,2 → M7,5 · 24 jun 2026","M7,2 → M7,5 · 24 Jun 2026"),
  "n":("Strongest since 1900, near Morón","El más fuerte desde 1900, cerca de Morón","Terkuat sejak 1900, dekat Morón"),
  "url":"https://en.wikipedia.org/wiki/2026_Venezuela_earthquakes"},
 {"v":("≥235 dead · 4,300 injured","≥235 muertos · 4.300 heridos","≥235 tewas · 4.300 luka"),
  "n":("26 Jun 2026; 157 missing, rising","26 jun 2026; 157 desaparecidos","26 Jun 2026; 157 hilang, terus bertambah"),
  "url":"https://reliefweb.int/country/ven"},
 {"v":("7.9M have left Venezuela","7,9M se han ido de Venezuela","7,9 jt telah pergi"),
  "n":("R4V / UNHCR, Nov 2025","R4V / ACNUR, nov 2025","R4V / UNHCR, Nov 2025"),
  "url":"https://www.r4v.info/"},
 {"v":("7.6M need aid inside","7,6M necesitan ayuda dentro","7,6 jt butuh bantuan di dalam"),
  "n":("UN OCHA, 2025 plan","ONU OCHA, plan 2025","UN OCHA, rencana 2025"),
  "url":"https://humanitarianaction.info/"},
 {"v":("Grid collapsed in 2019","La red colapsó en 2019","Jaringan runtuh 2019"),
  "n":("Guri ~80%; daily apagones","Guri ~80%; apagones diarios","Guri ~80%; pemadaman harian"),
  "url":"https://thedialogue.org/analysis/blackouts-in-venezuela-why-the-power-system-failed-and-how-to-fix-it"},
 {"v":("Caracas water rationed","Caracas raciona el agua","Air Caracas dijatah"),
  "n":("~6M, ~3 days/week (2024)","~6M, ~3 días/semana (2024)","~6 jt, ~3 hari/minggu (2024)"),
  "url":"https://www.csis.org/analysis/unraveling-water-crisis-venezuela"},
]
dataset["venezuela"]["context"] = [
  {"value":c["v"][0],"value_es":c["v"][1],"value_id":c["v"][2],
   "note":c["n"][0],"note_es":c["n"][1],"note_id":c["n"][2],"url":c["url"]} for c in VE_CONTEXT]
dataset["venezuela"]["resources"] = [
 {"name":"ReliefWeb — Venezuela","url":"https://reliefweb.int/country/ven"},
 {"name":"UN OCHA — Venezuela","url":"https://www.unocha.org/venezuela"},
 {"name":"PAHO/OPS — Venezuela","url":"https://www.paho.org/en/venezuela"},
 {"name":"USGS — latest earthquakes","url":"https://earthquake.usgs.gov/earthquakes/map/"},
 {"name":"Funvisis","url":"http://www.funvisis.gob.ve"},
]

# --- Venezuela relevance sweep: surface repository solutions by failure-mode ---
FA_UI = {
 "en":{"from_archive_h":"From the archive — by what's broken","from_archive_lead":"Beyond the playbook above, these are buildable solutions from across the whole archive, grouped by the service that has failed. Each opens its source.","from_archive_more":"in the archive"},
 "es":{"from_archive_h":"Del archivo — según lo que falla","from_archive_lead":"Más allá de la guía de arriba, estas son soluciones que puedes construir, de todo el archivo, agrupadas según el servicio que falló. Cada una abre su fuente.","from_archive_more":"en el archivo"},
 "id":{"from_archive_h":"Dari arsip — menurut yang rusak","from_archive_lead":"Selain panduan di atas, ini solusi yang bisa kamu buat dari seluruh arsip, dikelompokkan menurut layanan yang gagal. Masing-masing membuka sumbernya.","from_archive_more":"di arsip"},
}
for _lg in ("en","es","id"):
    UI[_lg].update(FA_UI[_lg])

# --- Canonical positioning: TTW is the response layer of PLANETAI ---
PLANETAI_UI = {
 "en":{
  "about_planetai_h":"Part of PLANETAI — the response layer",
  "about_planetai_p":'Things That Work is the <b>response-template library of PLANETAI</b> — Fab City’s instrument for closing the loop between Earth observation and community-scale response. PLANETAI’s five-tier stack names, at its Bioregion tier, an <b>OSH/OKH response-template library</b>: the catalogue a node draws from when an observation triggers a fabrication response. This is that library, made human. The four action agents — Bali, Barcelona, Santiago, Boston — draft from it; it supplies the <i>fabricate</i> step of the <b>detect → decide → fabricate → deploy → measure</b> loop; and it is what gives <b>ρ</b> (action latency) something to act with. The faster a community can make and mend what it needs, the tighter that loop closes. <a href="https://planetai.fab.city" target="_blank" rel="noopener">planetai.fab.city ↗</a>',
  "planetai_line":'The community-response layer of <a href="https://planetai.fab.city" target="_blank" rel="noopener">PLANETAI</a> — Fab City’s observation-to-fabrication instrument.',
 },
 "es":{
  "about_planetai_h":"Parte de PLANETAI — la capa de respuesta",
  "about_planetai_p":'Cosas que sirven es la <b>biblioteca de plantillas de respuesta de PLANETAI</b> — el instrumento de Fab City para cerrar el ciclo entre la observación de la Tierra y la respuesta a escala comunitaria. La pila de cinco niveles de PLANETAI nombra, en su nivel Biorregión, una <b>biblioteca de plantillas de respuesta OSH/OKH</b>: el catálogo del que un nodo toma cuando una observación dispara una respuesta de fabricación. Esta es esa biblioteca, hecha humana. Los cuatro agentes de acción —Bali, Barcelona, Santiago, Boston— redactan a partir de ella; alimenta el paso <i>fabricar</i> del ciclo <b>detectar → decidir → fabricar → desplegar → medir</b>; y es lo que le da a <b>ρ</b> (latencia de acción) algo con qué actuar. Mientras más rápido una comunidad pueda hacer y reparar lo que necesita, más se cierra ese ciclo. <a href="https://planetai.fab.city" target="_blank" rel="noopener">planetai.fab.city ↗</a>',
  "planetai_line":'La capa de respuesta comunitaria de <a href="https://planetai.fab.city" target="_blank" rel="noopener">PLANETAI</a> — el instrumento de Fab City de la observación a la fabricación.',
 },
 "id":{
  "about_planetai_h":"Bagian dari PLANETAI — lapisan respons",
  "about_planetai_p":'Hal yang Berfungsi adalah <b>pustaka templat respons PLANETAI</b> — instrumen Fab City untuk menutup lingkar antara observasi Bumi dan respons skala komunitas. Tumpukan lima tingkat PLANETAI menyebut, pada tingkat Bioregion-nya, sebuah <b>pustaka templat respons OSH/OKH</b>: katalog yang diambil sebuah node ketika observasi memicu respons fabrikasi. Inilah pustaka itu, dijadikan manusiawi. Keempat agen aksi — Bali, Barcelona, Santiago, Boston — menyusun draf darinya; ia memasok langkah <i>fabrikasi</i> dalam lingkar <b>deteksi → putuskan → fabrikasi → terapkan → ukur</b>; dan ia yang memberi <b>ρ</b> (latensi aksi) sesuatu untuk ditindaklanjuti. Semakin cepat komunitas membuat dan memperbaiki yang dibutuhkannya, semakin rapat lingkar itu menutup. <a href="https://planetai.fab.city" target="_blank" rel="noopener">planetai.fab.city ↗</a>',
  "planetai_line":'Lapisan respons komunitas dari <a href="https://planetai.fab.city" target="_blank" rel="noopener">PLANETAI</a> — instrumen observasi-ke-fabrikasi Fab City.',
 },
}
for _lg in ("en","es","id"):
    UI[_lg].update(PLANETAI_UI[_lg])

# --- Open-source repo link (footer) ---
REPO_UI = {
 "en":'Open source — improve it at <a href="https://github.com/fabcity/things-that-work" target="_blank" rel="noopener">github.com/fabcity/things-that-work</a>.',
 "es":'Código abierto — mejóralo en <a href="https://github.com/fabcity/things-that-work" target="_blank" rel="noopener">github.com/fabcity/things-that-work</a>.',
 "id":'Sumber terbuka — bantu perbaiki di <a href="https://github.com/fabcity/things-that-work" target="_blank" rel="noopener">github.com/fabcity/things-that-work</a>.',
}
for _lg in ("en","es","id"):
    UI[_lg]["repo_line"] = REPO_UI[_lg]

# --- Country maker groups heading ---
for _lg,_t in (("en","Join from your country"),("es","Súmate desde tu país"),("id","Bergabung dari negaramu")):
    UI[_lg]["print_country_h"] = _t

# --- Regional hubs heading (was missing → empty <h3>) ---
for _lg,_t in (("en","Regional hubs"),("es","Hubs regionales"),("id","Hub regional")):
    UI[_lg]["print_hubs_h"] = _t

# --- Standalone /venezuela: action-first hero + "what happened" moved to the foot ---
VE_FOOT_UI = {
 "en":{"ve_help_lead":"Tools and help for the days after — report, print a part, contribute. What happened and the latest figures are at the foot of the page.",
       "ve_what_h":"What happened"},
 "es":{"ve_help_lead":"Herramientas y ayuda para los días después: reporta, imprime una pieza, contribuye. Qué pasó y las cifras más recientes están al final de la página.",
       "ve_what_h":"Qué pasó"},
 "id":{"ve_help_lead":"Perkakas dan bantuan untuk hari-hari sesudahnya — laporkan, cetak komponen, berkontribusi. Apa yang terjadi dan angka terbaru ada di bagian bawah halaman.",
       "ve_what_h":"Apa yang terjadi"},
}
for _lg in ("en","es","id"):
    UI[_lg].update(VE_FOOT_UI[_lg])
_VE_NEEDS = [
 ("water","Drinkable water","Agua potable","Air minum",{"water"},["water","purif","filter","chlorin","sodis","boil","rainwater","well","distill","biosand","ceramic"]),
 ("energy","Power & light","Energía y luz","Listrik & cahaya",{"energy"},["solar","batter","power","generat","charg","invert","lamp","lantern","light","wind turbine","pedal","dynamo"]),
 ("cooking","Cooking & fuel","Cocina y combustible","Memasak & bahan bakar",set(),["stove","cookstove","cooker","biogas","charcoal","briquette","rocket stove"]),
 ("food","Food without a fridge","Comida sin nevera","Pangan tanpa kulkas",{"food","agriculture"},["preserv","ferment","smoke","root cellar","grain","garden","crop","solar dry","drying"]),
 ("sanitation","Sanitation & hygiene","Saneamiento e higiene","Sanitasi & kebersihan",set(),["latrine","toilet","compost","handwash","soap","greywater","sanitation","menstru","sanitary pad","sewage"]),
 ("health","Health & first aid","Salud y primeros auxilios","Kesehatan & P3K",{"health-veterinary"},["medical","first aid","splint","brace","wound","prosthe","wheelchair","oxygen","steriliz","nebuli"]),
 ("shelter","Shelter & repair","Refugio y reparación","Hunian & perbaikan",{"shelter"},["shelter","tarp","tent","roof","repair","brick","earthbag","structural"]),
 ("comms","Communication","Comunicación","Komunikasi",{"communication"},["antenna","radio","mesh","wifi"]),
]
_RANK = {"olive":0,"vzla_makers":0,"ferulas":1,"msf":2,"fieldready":3,"appropedia":4,"con_nuestros":5,"libro_familia":5,"wholeearth":6}
def _ehay(e):
    return " ".join([e.get("title",""), e.get("summary","")] + (e.get("tags") or [])).lower()
_fa_needs = []
for _nk,_en,_es,_idn,_doms,_kws in _VE_NEEDS:
    _matched = []
    for e in dataset["entries"]:
        if e.get("source_body") == "fieldready":
            continue  # Field Ready entries have no source_url → dead links; they live in their own linked block
        _dom = set(e.get("domain") or [])
        if (_doms and (_dom & _doms)) or any(k in _ehay(e) for k in _kws):
            _matched.append(e)
    _matched.sort(key=lambda e: (_RANK.get(e.get("source_body"), 9),
                                 0 if e.get("open_hardware") else 1,
                                 0 if e.get("source_url") else 1,
                                 e.get("title","")))
    _items = [{"id": e["id"], "title": e.get("title",""),
               "title_es": (e.get("i18n",{}).get("es") or {}).get("title", e.get("title","")),
               "title_id": (e.get("i18n",{}).get("id") or {}).get("title", e.get("title","")),
               "source": e.get("source",""), "url": e.get("source_url") or "",
               "oh": bool(e.get("open_hardware")),
               **({"translation_es": e["translation_es"]} if e.get("translation_es") else {})
               } for e in _matched[:10]]
    _fa_needs.append({"key": _nk, "label": _en, "label_es": _es, "label_id": _idn,
                      "count": len(_matched), "items": _items})
dataset["venezuela"]["from_archive"] = {"needs": _fa_needs}
print("VE from_archive:", {n["key"]: n["count"] for n in _fa_needs})

(DIST / "data.json").write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

# Analytics: paste a privacy-first provider's <script> loader here to activate
# metrics (page views + custom events via the track() helper). Empty = no
# tracking (the track() calls become no-ops). Examples:
#   GoatCounter: <script data-goatcounter="https://CODE.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
#   Plausible:   <script defer data-domain="ttw.fab.city" src="https://plausible.io/js/script.manual.js"></script>
ANALYTICS_SNIPPET = '<script data-goatcounter="https://ttwfabcity.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'

# Inject into the HTML template (self-contained, opens offline)
tpl = (ROOT / "template.html").read_text(encoding="utf-8")
payload = json.dumps(dataset, ensure_ascii=False)
out = tpl.replace("/*__DATA__*/null/*__DATA__*/", payload).replace("<!--ANALYTICS-->", ANALYTICS_SNIPPET)
(DIST / "things-that-work.html").write_text(out, encoding="utf-8")

# Standalone /venezuela page — lean, self-contained, served at /venezuela
# --- TTW-VE-ADDITIONS (community + offline; guarded, idempotent) ---
try:
    _ve = dataset["venezuela"]; _ui = dataset["ui"]
    _g3 = "https://chat.whatsapp.com/Fc7e08cW6ubC33GQCNHxME"
    if not any(_g3 in (x.get("url") or "") for x in _ve["printing"]["groups"]):
        _ve["printing"]["groups"].append({"name":"Makers 4 Venezuela","url":_g3,"note":"Maker network for Venezuela","note_es":"Red de makers por Venezuela","note_id":"Jaringan maker untuk Venezuela"})
    _ve["printing"]["map"] = {"url":"https://vzla.ushahidi.io/map","add":"https://vzla.ushahidi.io/map","api":"https://vzla.api.ushahidi.io/api/v5/posts/geojson"}
    _ve["printing"]["credit"] = {"name":"Ostec3D","url":"https://www.ostec3d.com/","ig":"https://www.instagram.com/ostec3d/"}
    if not any("ushahidi.io" in (r.get("url") or "") for r in _ve["resources"]):
        _ve["resources"].insert(0, {"name":"Mapa Ushahidi — impresión, filamento y acopio (Venezuela)","url":"https://vzla.ushahidi.io/"})
    if not any(c.get("id")=="crisis-bitchat" for c in dataset["crisis"]):
        dataset["crisis"].append({"id":"crisis-bitchat","need":"Comms","phase":["acute-72h","days-after","prolonged"],
            "title":"Phone-to-phone messaging, no internet (bitchat)",
            "summary":"A free app that relays encrypted messages phone-to-phone over Bluetooth mesh — no SIM, internet, servers or account.",
            "source":"bitchat (open source)","source_url":"https://github.com/permissionlesstech/bitchat","open_hardware":False,
            "i18n":{"es":{"title":"Mensajería de teléfono a teléfono, sin internet (bitchat)","summary":"App gratuita que pasa mensajes cifrados de teléfono a teléfono por malla Bluetooth — sin SIM, internet, servidores ni cuenta."},
                    "id":{"title":"Pesan antar-ponsel, tanpa internet (bitchat)","summary":"Aplikasi gratis yang meneruskan pesan terenkripsi antar ponsel lewat mesh Bluetooth — tanpa SIM, internet, server, atau akun."}}})
    for _s in _ve["scenarios"]:
        if _s.get("key")=="comms" and "crisis-bitchat" not in _s["items"]:
            _s["items"].append("crisis-bitchat")
    _add = {
      "offline_h":["Use it offline","Úsala sin conexión","Gunakan luring"],
      "offline_lead":["Save it on your phone and share it — it keeps working with no signal.","Guárdala en tu teléfono y compártela — sigue funcionando sin señal.","Simpan di ponsel dan bagikan — tetap berfungsi tanpa sinyal."],
      "offline_save":["Download this page","Descargar esta página","Unduh halaman ini"],
      "offline_install":["Install as app","Instalar como app","Pasang sebagai aplikasi"],
      "offline_zip":["Everything + files (ZIP)","Todo + archivos (ZIP)","Semua + berkas (ZIP)"],
      "offline_hint":["One file. Open it in any browser; share by WhatsApp or Bluetooth.","Un archivo. Ábrelo en cualquier navegador; compártelo por WhatsApp o Bluetooth.","Satu berkas. Buka di peramban mana pun; bagikan via WhatsApp atau Bluetooth."],
      "print_credit":["Splint design by","Diseño de las férulas:","Desain bidai oleh"],
      "print_map":["Live map: printing sites, filament & drop-off","Mapa en vivo: impresión, filamento y acopio","Peta langsung: lokasi cetak, filamen & titik kumpul"],
      "map_loc":["My location","Mi ubicación","Lokasi saya"],
      "map_download":["Download my area (10 km)","Descargar mi zona (10 km)","Unduh area saya (10 km)"],
      "map_add":["Add a point","Añadir un punto","Tambah titik"],
      "fl_h":["Fab labs near you","Fab labs cerca de ti","Fab lab di dekatmu"],
      "fl_lead":["The global fab lab network can print with you. Find the closest ones and write to them.","La red global de fab labs puede imprimir contigo. Encuentra los más cercanos y escríbeles.","Jaringan fab lab global bisa mencetak bersamamu. Temukan yang terdekat dan hubungi mereka."],
      "fl_btn":["Find fab labs near me","Ver fab labs cercanos","Cari fab lab terdekat"],
      "fl_loading":["Searching the global network…","Buscando en la red mundial…","Mencari di jaringan global…"],
      "fl_geoerr":["Location unavailable — allow location and retry.","Ubicación no disponible — permite la ubicación y reintenta.","Lokasi tidak tersedia — izinkan lokasi dan coba lagi."],
      "fl_err":["Could not load the network. Retry with a connection.","No se pudo cargar la red. Reintenta con conexión.","Tidak dapat memuat jaringan. Coba lagi dengan koneksi."],
      "fl_contact":["View / contact","Ver / contactar","Lihat / hubungi"],

      "map_open_hint":["Open the live map: printing sites, filament & drop-off","Abrir el mapa en vivo: impresión, filamento y acopio","Buka peta langsung: lokasi cetak, filamen & titik kumpul"],
      "map_points":["points","puntos","titik"],
      "map_locating":["Locating…","Ubicando…","Mencari lokasi…"],
      "map_nogeo":["Location unavailable","Ubicación no disponible","Lokasi tidak tersedia"],
      "map_dlstart":["Preparing offline area…","Preparando zona sin conexión…","Menyiapkan area luring…"],
      "map_dlprog":["Saving {d}/{t} tiles…","Guardando {d}/{t} mosaicos…","Menyimpan {d}/{t} ubin…"],
      "map_dldone":["Area saved offline ({n} tiles)","Zona guardada sin conexión ({n} mosaicos)","Area tersimpan luring ({n} ubin)"],
      "map_nocache":["Offline cache not available","Caché sin conexión no disponible","Cache luring tidak tersedia"],

    }
    for _k,(_en,_es,_idn) in _add.items():
        _ui["en"].setdefault(_k,_en); _ui["es"].setdefault(_k,_es); _ui["id"].setdefault(_k,_idn)
    _ve["context"] = [
      {"value":"M7.2 → M7.5","value_es":"M7,2 → M7,5","value_id":"M7,2 → M7,5","note":"24 Jun 2026 · Yumare–Morón","note_es":"24 jun 2026 · Yumare–Morón","note_id":"24 Jun 2026 · Yumare–Morón","url":"https://earthquake.usgs.gov/earthquakes/eventpage/us6000t7zp"},
      {"value":"1,430+ dead","value_es":"+1.430 muertos","value_id":"1.430+ tewas","note":"and thousands injured (rising)","note_es":"y miles de heridos (en aumento)","note_id":"dan ribuan terluka (terus bertambah)","url":"https://reliefweb.int/country/ven"},
      {"value":"68,900 missing","value_es":"68.900 desaparecidos","value_id":"68.900 hilang","note":"search ongoing","note_es":"búsqueda en curso","note_id":"pencarian berlangsung","url":"https://reliefweb.int/country/ven"},
      {"value":"Aftershocks to M4.8","value_es":"Réplicas hasta M4,8","value_id":"Gempa susulan hingga M4,8","note":"ongoing seismic series (USGS)","note_es":"serie sísmica en curso (USGS)","note_id":"rangkaian gempa (USGS)","url":"https://earthquake.usgs.gov/earthquakes/eventpage/us6000t7zp"},
      {"value":"US$4.7–8.7 bn","value_es":"US$4,7–8,7 mil M","value_id":"US$4,7–8,7 miliar","note":"estimated damage (UN)","note_es":"daños estimados (ONU)","note_id":"perkiraan kerusakan (PBB)","url":"https://reliefweb.int/country/ven"},
      {"value":"7.9M","value_es":"7,9M","value_id":"7,9 jt","note":"have left Venezuela","note_es":"han dejado Venezuela","note_id":"telah meninggalkan Venezuela","url":"https://www.r4v.info/en/refugeeandmigrants"},
    ]
    print("TTW-VE-ADDITIONS applied")
except Exception as _e:
    print("TTW-VE-ADDITIONS skipped:", _e)
# --- end TTW-VE-ADDITIONS ---

ve_payload = {
    "meta": {"generated": dataset["meta"]["generated"]},
    "ui": dataset["ui"],
    "venezuela": dataset["venezuela"],
    "crisis": dataset["crisis"],
}
ve_tpl = (ROOT / "template_ve.html").read_text(encoding="utf-8")
(DIST / "venezuela").mkdir(exist_ok=True)
(DIST / "venezuela" / "index.html").write_text(
    ve_tpl.replace("/*__VEDATA__*/null/*__VEDATA__*/", json.dumps(ve_payload, ensure_ascii=False)).replace("<!--ANALYTICS-->", ANALYTICS_SNIPPET),
    encoding="utf-8")
print("venezuela page:", round((DIST / "venezuela" / "index.html").stat().st_size/1024), "KB")

print(f"entries: {len(entries)}")
print(f"issues:  {len(issues)}  (with archive_id: {dataset['meta']['issues_with_archive_id']})")
by_src = {}
for e in entries:
    by_src[e["source_body"]] = by_src.get(e["source_body"], 0) + 1
print("by source:", by_src)
by_coll = {}
for i in issues:
    by_coll[i["collection"]] = by_coll.get(i["collection"], 0) + 1
print("issues by collection:", by_coll)
