# FLOTA ÁNGULO — A7-4112, frequenties, routewijzigingen en besluitketen

**Peildatum:** 2 november 2026. **Status:** één van zes officiële resoluties inhoudelijk gecontroleerd, **vijf PDF's niet beschikbaar in de bestaande extractie**. Bewust **niet** gelijkgesteld aan volledige juridische afronding. Een recovery-Action is toegevoegd om de missende PDF-links van AMB terug te halen. **GTFS_READY=no**.

## 1. Bronnen en dekkingsgraad

AMB noemt in zijn [officiële FLOTA ÁNGULO-archief](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-flota-angulo/) zes besluiten voor het bedrijf:

| Besluit | Betrokken route volgens AMB-index | Beschikbaar? | Inhoudelijk resultaat |
|---|---|---|---|
| **232-2025** | A7-4112 | **nee, directe PDF ontbreekt** | Nieuwste vermeld besluit; niet veilig om te veronderstellen welke frequentie of wijziging het vastlegt |
| **265-2019** | A7-4112 | **nee** | AMB-nieuwsbericht verbindt Flota Ángulo aan nieuwe verbindingen met Alameda del Río; de precieze juridische A7-parameters uit dit besluit zijn onbekend |
| **301-2014** | A7-4112 | **ja** | 16 p., oorspronkelijke PDF en p. 14-scan gecontroleerd; historische frequenties en vloot hieronder |
| **242-2010** | 1302 | **nee** | Historische route 1302; juridische functie onbekend, geen route uit afleiden |
| **157-2010** | A7 | **nee** | Historische A7-vergunning, nog niet geanalyseerd |
| **242-2012** | A7 | **nee** | Historische A7-vergunning, nog niet geanalyseerd |

In `sources/amb/flota_angulo_resolution_legal_index_2026-11-02.csv` zijn **alle zes** met een passende verificatie-/blokkeringsstatus opgeslagen.

De bestaande GitHub Actions-extractie, [run 41488216079](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41488216079), artifact `amb-pdf-FLOTA_ANGULO` (ID `13163535622`), bevat uitsluitend **301-2014**, alle 16 pagina's native tekst, zonder PDF-/OCR-fout.

## 2. Vergunningsparameters — resolutie 301-2014

**Datum:** 23 oktober 2014 (p. 16). **Artikel 1 en 2:** ambtshalve herstructurering, bedrijfsroutes worden vervangen door het beschreven traject (p. 13–14). De tabel op **pagina 14** is visueel vergeleken met de originele scan.

| Veld | Waarde | Bewijs |
|---|---|---|
| **Routecode** | **A7-4112** | p. 14 (PDF-scan leest ondubbelzinnig A7; OCR kan Al schrijven) |
| **Routebenaming** | **Barranquillita – La Pradera – Circular** | p. 14 |
| **Spitsinterval** | **3 minuten** | p. 14 |
| **Dalinterval** | **5 minuten** | p. 14 |
| **Minimale vloot** | **33 voertuigen** | p. 14–15 |
| **Maximale vloot** | **40 voertuigen** | p. 14–15 |
| **Lengte** | **27 km** | p. 14 |
| **Voertuigklasse** | **Grupo C (Busetón – Buseta)** | p. 14 |
| **Dispatchterminal** | **Calle 8 No. 41N-70, Barranquillita** | p. 14 |
| **Overlap Transmetro** | **32% troncal / 42% alimentador** | p. 14 |
| **Mogelijk vergunningsvenster** | **00:00–24:00 *afhankelijk van de vraag*** | p. 14; **geen bewezen nacht-/24-uursbediening** |

**Gegeven routeverloop uit 2014 (art. 2 p. 14):** uit Calle 8 naar Carrera 43 / Carrera 42F, Calle 79B / Carrera 42H / Calle 84B, via Calle 96/94, de corridors van Carrera 42C/42B1/42A4, Calle 83/Carrera 38, Calle 100/Carrera 36, Calle 85/Carrera 34, Calle 107A/108 en Avenida Circunvalar; via Carrera 31/Calle 123/Carrera 37/Calle 114 terug naar Barranquillita. **De volledige exacte geordende stratenlijst staat op p. 14** en mag niet uit deze samenvatting als geverifieerde OSM-shape worden gegenereerd. De route is een *circular* met uitgaande en teruggaande segmenten.

**Artikel 3 p. 15:** de uitvoering is **gefaseerd** en afhankelijk van de instroom van nieuwe Transmetro-voertuigen. De autoriteit moet na onherroepelijkheid vooraf de ingangsdatum meedelen, met een kennisgeving niet minder dan drie dagen tevoren. In sommige gevallen verlangt het besluit acht dagen simultane dienst ter informatie van reizigers. **Een besluitdatum is daarom geen bewezen effectieve startdatum**.

**Artikel 7 p. 16:** het besluit herroept/vervangt eerdere strijdige besluiten en verklaart de nieuwe vergunning de basis van de geautoriseerde route op dat moment. **2019 en 2025 kunnen deze parameters later hebben gewijzigd.**

**Officiële PDF:** https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ANGULO/301-14-RESOLUCION-FLOTA-ANGULO.pdf

## 3. Latere aanwijzingen: niet verwarren met de inhoud van ontbrekende besluiten

### 2019 — Alameda del Río
[AMB meldde in oktober 2019](https://www.ambq.gov.co/en-servicio-5-nuevas-rutas-de-buses-para-32-mil-habitantes-de-alameda-del-rio/) dat via resoluties **199, 264, 265 en 266** nieuwe busverbindingen naar **Alameda del Río** waren toegestaan, met onder andere **Flota Ángulo, La Carolina en Transdiaz** als bedrijven. De toen aangekondigde nieuwe routes kregen een algemeen vermeld bedieningsvenster van **05:45–22:00**.

Dit is **bronbewijs van de uitbreiding in 2019**, maar het nieuwsbericht bevat **niet** de oorspronkelijke artikeltabel van **265-2019** voor A7-4112. Daarom kan het exacte nieuwe A7-routeverloop, wagenpark en spits-/dalinterval **niet** veilig uit het artikel worden ingevuld. Het algemene urenvenster is ook **geen vastgesteld 2026-rooster voor A7**.

### 2025 — routecode administratief in gebruik
AMB noemt **A7-4112 van FLOTA ANGULO** in onder meer [Circular 002-2025](https://www.ambq.gov.co/wp-content/uploads/2025/01/Circular-No.-002-de-2025-Cierre-Total-LECTURA-DEL-BANDO.pdf) en [Circular 009-2025](https://www.ambq.gov.co/wp-content/uploads/2025/02/Circular-No.-009-2025-Cierre-Total-GUACHERNA.pdf). Die documenten betreffen **tijdelijke omleidingen** bij evenementen, niet een permanente routewijziging en evenmin een actuele frequentietabel.

De officiële bedrijfsindex vermeldt **232-2025** als nieuwste A7-besluit. Dit is de **primaire ontbrekende bron**. Zonder deze PDF is het niet mogelijk een 2026-geldigheidsclaim voor de 3/5-minutenwaarden te onderbouwen.

### Aanvullende bedrijfsinformatie (secundair)
De [eigen bedrijfspagina van Flota Ángulo](https://www.flotaembusa.net/copia-de-embusa) beschrijft historische routes *Expreso Porvenir* en *Porvenir Prado* en meldt dat na de start van vervoer per Transmetro alleen Expreso Porvenir resteerde. Dit is context, **geen officiële AMB-vergunning of actuele frequentie**.

## 4. Recovery-workflow: missende vijf PDF's

Omdat de officiële AMB-index zes PDF-titels toont terwijl de directe URL van vijf bestanden in de vorige batch niet werd gevonden, is toegevoegd:

- `scripts/resolve_amb_flota_links.py`: leest de officiële archiefpagina, zoekt daadwerkelijke PDF-hrefs/data-links, verifieert de **PDF-byteheader**, en geeft een `resolved_manifest.csv` met **uitsluitend bewezen PDF-links**. Onvindbare URLs worden **niet** geraden.
- `.github/workflows/recover-flota-angulo-pdfs.yml`: automatisch bij push van workflow/script of handmatig via `workflow_dispatch`; gebruikt het bestaande `scripts/extract_amb_pdfs.py` om alle geverifieerde PDF's en Spaanse OCR per pagina te archiveren en publiceert het artifact `amb-flota-angulo-recovered-pdfs`.

**De workflow is aangemaakt; dit rapport claimt niet dat vijf extra PDF's reeds zijn geëxtraheerd.** De daadwerkelijke Action-uitkomst en het artifact dienen eerst te worden gecontroleerd. Geverifieerde nieuwe URL's kunnen daarna in `sources/amb/pdf_manifest.csv` worden overgenomen, waarna 232-2025 en 265-2019 eerst artikel-voor-artikel worden verwerkt.

## 5. Openstaande acties

| ID | Prioriteit | Werk | Afsluitcriterium |
|---|---|---|---|
| **FANG-01** | **Blokkerend** | Officiële PDF **232-2025** ophalen en artikel/routefrequentie/vloot/terminal vastleggen | Originele PDF + bronpagina + geanalyseerde tabel |
| **FANG-02** | **Blokkerend** | PDF **265-2019** (uitbreiding Alameda del Río) ophalen en exact traject/interval vergelijken met 301-2014 | Route-diff en correcte historisch vergunde cijfers |
| **FANG-03** | Hoog | Ingangsdatum en opvolgende juridische status van 301-2014 reconstrueren | Officiële kennisgeving of expliciet geen bewijs |
| **FANG-04** | Hoog | PDF **242-2010** (historische route 1302) vinden en juridische aard bepalen | Gecontroleerde beschikkende artikelen; geen veronderstelde revocatie |
| **FANG-05** | Hoog | PDF **157-2010** (A7) vinden en in historische routeketen opnemen | Betrouwbare PDF-tekst + bron |
| **FANG-06** | Hoog | PDF **242-2012** (A7) vinden en vergelijken met 301-2014 | Route-/frequentievergelijking |
| **FANG-07** | Hoog | Volledige 2025-weggeometrie, haltes en beide rijrichtingen vaststellen; oude 2014-shape niet blind hergebruiken | Gecontroleerde routegeometry en stopvolgorde |
| **FANG-08** | Hoog | Feitelijke 2026-diensturen en spits/dal-vensters onafhankelijk controleren; 2019-vermelding 05:45–22:00 niet automatisch kopiëren | Actuele bron voor GTFS `calendar`, `trips`, `frequencies` en `stop_times` |
| **FANG-09** | Middel | De recovery-Action, linkrapport en OCR-artifacts auditen, URL's in manifest toevoegen, documenten juridisch classificeren | Volledig gedocumenteerde zes-besluitenketen |

## 6. Machineleesbare output / GTFS

- `sources/amb/flota_angulo_route_parameters_2026-11-02.csv` houdt de **geverifieerde 2014-parameters** gescheiden van de nog onbekende 2019-/2025-waarden.
- `sources/amb/flota_angulo_resolution_legal_index_2026-11-02.csv` bevat **zes besluiten met audit-/bronstatus**.
- `sources/amb/flota_angulo_resolutions_register.csv` blijft de URL-zoekwerklijst.
- **A7-4112: `GTFS_READY=no`**. Geen 2014-frequenties als actuele 2026-dienstregeling publiceren en geen fictieve 24-uursrijden claimen.
