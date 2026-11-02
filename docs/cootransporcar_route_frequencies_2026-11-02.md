# COOTRANSPORCAR — frequenties, trajectwijzigingen en besluitketen

**Onderzoeksdatum:** 2 november 2026. **Bron:** de vier officiële AMB-PDF's uit GitHub Actions-run `41480204032`, artifact `amb-pdf-COOTRANSPORCAR` (`13159308204`). Alle vier zijn technisch succesvol verwerkt: **6 + 8 + 10 + 14 = 38 PDF-pagina's**. De besluiten uit 2010 zijn met Spaanse OCR geëxtraheerd; 2017 en 2025 via tekstextractie. **De beschikkende tabellen zijn aanvullend op de pagina-afbeeldingen gecontroleerd** (281-2010 p8, 492-2010 p13, 170-2017 p7, 389-2025 p5). De officiële [AMB-bedrijfspagina](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootransporcar/) vermeldt dezelfde vier resoluties.

**Belangrijkste resultaat:** **C8-4139** is de enige route in deze bedrijfsregistratie. De laatst aangetroffen vergunning, **389-2025**, autoriseert **3 minuten spits / 5 minuten dal**, **45–53 Grupo C-voertuigen**, en een rondrit van **40,8 km**. Voor 2017 gold **5/8 minuten**, **33–40 voertuigen**, **40,1 km**. Deze intervallen zijn **juridische vergunningwaarden**; de werkelijke dienstregeling en spits-/daltijdvakken zijn onbekend.

## 1. Gecontroleerde parameters per besluit

| Besluit | Datum | Route | Spits | Dal | Voertuigen min–max | Lengte | Bron |
|---|---|---|---:|---:|---:|---:|---|
| **281-2010** | 6 juli 2010 | C8 (historische benaming Colectivo–Cootransporcar) | **5 min** | **8 min** | **29–35** | onbekend | art. 1 p7–8, scan p8 |
| **492-2010** | 25 oktober 2010 | C8; *gedeeltelijke herroeping* van 281-2010 | **5 min (overgenomen)** | **8 min (overgenomen)** | **33–40** | onbekend | art. 1 p13, scan p13; **492 formuleert geen nieuw zelfstandig spits-/dalinterval** |
| **170-2017** | 7 april 2017 | **C8-4139** | **5 min** | **8 min** | **33–40** | **40,1 km** | art. 1 p6–7, scan p7 |
| **389-2025** | **9 oktober 2025** | **C8-4139** | **3 min** | **5 min** | **45–53** | **40,8 km** | art. 1 p4–5, **scan p5**; tabel en capaciteit in paragraaf 1 |

**Verandering 170-2017 → 389-2025:**
- Spitsinterval: **5 → 3 min** (−2 min, **40% korter**); theoretisch **12 → 20 vertrekken per uur** als het hele spitsuur continu wordt gereden.
- Dalinterval: **8 → 5 min** (−3 min, **37,5% korter**); theoretisch **7,5 → 12 vertrekken per uur** bij continue bediening.
- Minimaal aantal voertuigen: **33 → 45** (+12).
- Maximaal aantal voertuigen: **40 → 53** (+13).
- Routeafstand: **40,1 → 40,8 km** (+0,7 km).
- Klasse blijft **Grupo C (Busetón/Buseta)**.
- Overlap Transmetro troncal: **10,46% → 10,8%**; overlap alimentador: **47,31% → 53,8%** (percentages uit respectievelijke routebladen p7 en p5).

**Interpretatievoorbehoud:** die theoretische ritten per uur zijn slechts de rekenkundige implicatie van het vergunde interval, geen bewijs van gerealiseerde departures en geen bron voor `stop_times.txt`.

## 2. Traject: wat is veranderd?

### 281-2010 → 492-2010
- **281-2010, art. 1 p7–8:** route **Rebolo – La Concepción – Circular**, met terminal **Carrera 23 nr. 23-56**, onder meer via Calle 17, Avenida Calle 30, Calle 72 en Vía 40. Het besluit geeft **5/8 min** en **29–35 busetas**.
- **281-2010, art. 2 p8:** verklaart oudere vergunningen voor dezelfde route vervallen en definieert het nieuwe routebesluit als juridisch titelbewijs; art. 5 p8–9 stelt invoering afhankelijk van een **kennisgeving door AMB** in relatie tot de start van Transmetro.
- **492-2010, art. 1 p13:** verklaart **gedeeltelijke directe herroeping** van 281-2010 (*revocatoria directa parcial*), **wijzigt de straatroute** en bepaalt nu **33–40 voertuigen**. Artikel 2 (p14) **wijst de overige verzoeken af**. **Dit is géén volledige intrekking van C8.**
- De route in 492 wordt via onder meer Calle 17, Carrera 10, Boulevard Simón Bolívar, Calle 24B, Avenida Calle 30, Calle 72, Carrera 58, Calle 77 en Vía 40 gelegd. Exacte geordende segmenten: art. 1 p13.
- Omdat art. 1 van 492 geen afzonderlijk nieuw interval specificeert, blijft **5/8 uit 281** een historische afleiding, in het CSV expliciet als `inherited_from_281_2010` gemarkeerd (geen direct uit 492 geverifieerde nieuwe intervalwaarde).

### 492-2010 → 170-2017
- **170-2017, art. 1 p6–7:** route wordt aangeduid als **C8-4139** en krijgt de naam **Las Nieves – Rebolo – Calle 72 – La Concepción – Villa Carolina – Circular**. De route loopt tot Villa Carolina via Vía 40, Calle 85, Carrera 76, Calle 88/87, Carrera 75A, Calle 93, enzovoort. 
- Terminal blijft **Carrera 23 nr. 23-56**.
- Voertuigtype **Grupo C**, 40,1 km, intervallen **5/8** en capaciteit **33–40**. Het routeblad heeft een kaart, maar die is **historisch** en mag niet zonder kaartcontrole voor de situatie na 2025 worden hergebruikt.
- Het besluit is dus primair een **route-/geometriewijziging**, niet een nieuwe frequentieverhoging.

### 170-2017 → 389-2025
- **389-2025, art. 1 p4–5:** behoudt de routecode **C8-4139** en de algemene naam **Las Nieves – Rebolo – Calle 72 – La Concepción – Villa Carolina – Circular**, maar publiceert een **nieuw volledig straatverloop**.
- Nieuw beschreven traject vertrekt van **Carrera 23 / Calle 23**, gaat langs onder meer **Calle 17, Calle 19/Simón Bolívar, Carrera 4B, Calle 24B, Carrera 5, Calle 27B, Carrera 6A, Calle 26, Carrera 21B, Avenida Calle 30, Calle 37, Carrera 21, Calle 57, Carrera 27, Calle 70B, Calle 72, Vía 40, Calle 85, Carrera 76, Calle 88, Carrera 75A, Calle 92/93, Carrera 73/71**, en keert over onder andere **Vía 40, Calle 72, Carrera 35B, Calle 71, Carrera 27, Calle 57, Calle 36/36B, Calle 30, Simón Bolívar** terug.
- Het oorspronkelijke routeblad van 2017 noemt op delen andere straten (**Calle 71/Vía 40** en **Carrera 59/Calle 70/Carrera 58**, andere draaipunten rond Villa Carolina). Het gaat dus om gewijzigde segmentvolgorde, **niet enkel een nieuwe frequentie**.
- Nieuwe vergunningsparameters op de scan van **p5**: **3/5 min**, **40,8 km**, **45–53 voertuigen**; de operator moet volgens paragraaf 2 **SIBUS RCC** gebruiken (onder verwijzing naar resolutie **197-2021**).
- De technische motivering op **p2–3** vermeldt capaciteitsaanpassing vanwege hogere vraag rond **Carrera 21, Calle 72, Villa Carolina en Río Alto** en verminderde commerciële snelheid.

**Routegeometrie:** het volledige nieuwe straatverloop is bronmatig aanwezig, maar er is nog geen tegen OSM/haltes gecontroleerde polyline of stopvolgorde. Een oude [AMB-KMZ voor C8-4139 (archiefbestand uit 2022)](https://www.ambq.gov.co/test2.ambq.gov.co/rutas-de-buses/COOTRANSPORCAR/C8-4139.kmz) kan voor vergelijking dienen, maar **niet** als automatisch geldige 2025-shape.

## 3. Interpretatie en juridische status

1. **Laatste bedrijfsspecifieke besluit op officiële AMB-index:** 389-2025. De index vermeldt alle vier geregistreerde PDF's, geen bedrijfsspecifiek besluit uit 2026. Dit bewijst niet dat een onbekend algemeen of nieuw besluit onmogelijk bestaat.
2. **492-2010:** *gedeeltelijke herroeping* betekent wijziging van rechtsgevolgen; de route is niet afgeschaft.
3. **170-2017:** verandert het traject, met dezelfde 33–40 capaciteit en 5/8 min.
4. **389-2025:** past **frequentie, routegeometrie en totale capaciteit** aan. De nieuwste artikelen geven 45–53; er is geen intern geconstateerd tegenstrijdig getal zoals bij COOTRANSCO.
5. **00:00–24:00** verschijnt als voorwaardelijk mogelijk venster *afhankelijk van de vraag*, **niet** als bewezen nachtelijke exploitatie.
6. **Geen spits/dal-kloktijden:** het besluit noemt relatieve dienstintensiteit maar geen exacte uren van die periodes; ook geen werkdagen-/weekend-/feestdagrooster.

## 4. Verplichte vervolgacties

| ID | Prioriteit | Te verrichten | Afsluitcriterium |
|---|---|---|---|
| **CPOR-01** | Hoog | Werkelijke C8-exploitatie in 2026 en eventuele AMB-besluiten na 389-2025 vaststellen | Onafhankelijke recente exploitatiebron / opvolgingsbesluit |
| **CPOR-02** | Hoog | 389-2025 p5 volledige straatvolgorde aan OSM en haltegegevens koppelen; verifiëren of enkele straten éénrichtingsverkeer zijn | Bewezen shape, richting en stopvolgorde |
| **CPOR-03** | Hoog | Tijdvakken van *hora pico* en *hora valle*, werkelijke start/eindtijden en week-/feestdagbediening | Onderbouwde `calendar`, `frequencies`, `trips` en `stop_times` |
| **CPOR-04** | Middel | Bevestig feitelijke implementatie na kennisgeving Transmetro voor 281-2010 en daarna 492-2010 | Historische inwerkingtreding, eventueel GTFS-historie |
| **CPOR-05** | Middel | 2022-KMZ versus 2025-nieuwe geometrie vergelijken | Exacte gewijzigde segmenten/kaartdiff, niet hergebruik van oude shape |
| **CPOR-06** | Middel | Vervoercijfers SIBUS / metingen rapport 010-2025 proberen te verkrijgen voor empirische frequenties | Afleidbare realistische intervalvensters met meet-/dienstregelbron |

**Geen aparte OCR-blokkade:** alle numerieke tabellen van 281, 492, 170 en 389 zijn op de originele PDF-pagina's leesbaar en gecontroleerd. Oudere OCR-straatnamen (vooral 281/492) vergen bij historische shape-reconstructie wel scancontrole.

## 5. Opgeslagen machineleesbare bestanden

- `sources/amb/cootransporcar_latest_route_parameters_2026-11-02.csv`: **4 routegebonden records**, bronpagina's, spits/dal, capaciteit, lengte, historische status en `gtfs_ready=no`.
- `sources/amb/cootransporcar_resolution_legal_index_2026-11-02.csv`: **4 juridische records** inclusief PDF SHA-256, art. 1/2/5, historisch wijzigingstype en open werk.
- `sources/amb/company_completion_backlog_2026-11-02.csv`: COOTRANSPORCAR in centrale voortgangsregistratie.
- **GTFS-status: `no`.** Vergunde frequenties zijn bruikbaar als *onderzoeks-/modelinput*, niet rechtstreeks als garantie voor actuele `stop_times.txt` of `frequencies.txt`.

### Primaire PDF-bronnen
- [389-2025 (laatste)](https://www.ambq.gov.co/wp-content/uploads/2025/10/Resolucion-Metropolitana-No.-389-2025-OPERACION-DE-RUTA-C8-4139-COOTRANSPORCAR.pdf)
- [170-2017](https://www.ambq.gov.co/wp-content/uploads/2017/12/RESOLUCIOIN-170-17-COOTRANSPORCAR.pdf)
- [281-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSPORCAR/COOTRANSPORCAR-C8-Resolucion-281-10.pdf)
- [492-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSPORCAR/COOTRANSPORCAR-C8-Resolucion-492-10.pdf)
