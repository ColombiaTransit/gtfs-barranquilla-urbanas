# FLOTA ÁNGULO — alle zes resoluties teruggevonden en geanalyseerd

**Bijgewerkt op 3 november 2026.** Dit document vervangt de eerdere conclusie dat vijf PDF's ontbreken. **Alle zes zijn teruggevonden**, met de verbeterde Ninja Tables-AJAX-bronophaling in [run 41582220020](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41582220020), artifact **13206382827**. **Alle 6 PDF's succesvol gedownload en 65 pagina's geëxtraheerd** (10+10+16+6+10+13); er waren geen PDF-download- of extractiefouten. `232-2025`, `265-2019`, `301-2014` native tekst, en de drie oudere besluiten met Spaanse OCR.

## 1. Nieuwste routevergunning A7-4112: 232-2025

**[Originele PDF 232-2025](https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-M.-232-2025-L.pdf)** — 10 pagina's, SHA-256 `0cddb6778505dcb8f85eb101b368d44d0cbf3367edd56ab354654dccdf600ead`.

**Art. 1 op p. 7–9** wijzigt de vergunning voor de **ene route A7-4112**. Routebenaming volgens art. 1 p. 7: **Barranquillita – Carrera 43 – Miramar – Alameda del Río – La Pradera**. De kaart op p. 8 noemt **Itinerario A**; het besluit levert in dit dossier **geen aparte, volledig geautoriseerde B-variant of B-frequentie** op. Niet zonder nieuwe bron een A/B-dienst opsplitsen.

**Beschikkende routeblad p. 9 — visueel gecontroleerd tegen originele PDF-scan:**
- **Spitsinterval: 3 minuten**.
- **Dalinterval: 5 minuten**.
- **Lengte: 31,4 km**.
- Terminal **Calle 8 nr. 41N-70**.
- Straattraject via o.a. Carrera 43, Carrera 42F, Calle 79B, Calle 84B, Avenida Circunvalar, **Alameda del Río / Carrera 43 / Calle 112 / Calle 114**, verder via La Pradera (Calle 123/Carrera 37/Calle 113) en terug naar Barranquillita. **De volledige volgorde staat op p. 9.**
- Het routeblad vermeldt `00:00–24:00 dependiendo de demanda`, een **voorwaardelijk mogelijk venster**, niet bewezen 24-uursbediening.
- Geen actuele spits/dal-kloktijden en geen kalender/tijdstip van werkelijke vertrekken.
- **GTFS: actuele routegeometrie-kandidaat en vergunde frequentie, maar geen onafhankelijk geverifieerde actuele dienstregeling.**

Het besluit vermeldt SIBUS/RCC registratie (p. 9–10) en geen expliciete datum waarop de exploitant het nieuwe rooster daadwerkelijk is gaan rijden. Voor een route-shape moet de straatvolgorde tegen haltes en OSM worden gecontroleerd.

## 2. Frequente historiek: 2010 → 2025

| Resolutie | Juridische aard | Route A7-4112 spits/dal | Lengte | Bron |
|---|---|---|---|---|
| **157-2010** | Oorspronkelijke A7-herstructurering / Expreso Porvenir | **4/6 min** | onbekend | Art. 1 **p. 7–8**, **p. 8-scan** |
| **242-2012** | **Alleen wijziging van het straattraject** uit 157-2010 | **geen zelfstandige nieuwe intervals** | onbekend | Art. 1 **p. 12–13**, art. 2 **p. 13-scan** |
| **301-2014** | Nieuwe A7-herstructurering | **3/5 min** | **27 km** | Art. 1/2 **p. 13–14**, **p. 14-scan** |
| **265-2019** | Nieuwe A7-herstructurering naar **Alameda del Río** | **3/6 min** | **33,6 km** | Art. 1 **p. 8–10**, **p. 10-tabel** |
| **232-2025** | **Nieuwste bekende vergunning A7-4112** | **3/5 min** | **31,4 km** | Art. 1 **p. 7–9**, **p. 9-scan** |

**Gevolg voor GTFS:** Een feed gebaseerd op 2014 zou **Alameda del Río missen**. Een feed gebaseerd op 2019 zou het dalinterval **6 in plaats van 5 minuten** gebruiken en de langere **33,6 km**-geometrie hanteren. De routeautoriteit heeft in 2025 opnieuw een ander traject en interval vastgesteld. Over dit verschil bestaat na het herlezen van de p. 9-scan geen OCR-onzekerheid.

## 3. Intrekking van andere, historische route: 242-2010

**[242-2010 (route 1302)](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ANGULO/FLOTA-ANGULO-1302-Resolucion-242-10.pdf)** telt 6 gescande OCR-pagina's.

- **Art. 1 p. 5:** **trekt de vergunning voor de historische `Porvenir – Prado`-route in**. De oude route is niet hetzelfde als een extra huidige A7.
- **Art. 2 p. 5:** uitvoering van die intrekking hangt samen met de ingebruikname van Transmetro en kennisgeving door de autoriteit; de besluitdatum is niet automatisch de feitelijke einddatum.
- Het ingetrokken traject mag niet afzonderlijk opnieuw in actuele `routes.txt` worden opgenomen.

## 4. Inhoud 2012: waarom geen nieuwe frequentie

**[242-2012](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ANGULO/FLOTA-ANGULO-A7-Resolucion-242-12.pdf)**: art. 1 p. 12–13 wijzigt het A7-routeverloop naar aanleiding van bereikbaarheid/wensen van bewoners van La Pradera. **Art. 2 p. 13 bevestigt uitdrukkelijk de gedeeltelijke wijziging van 157-2010 ten aanzien van het traject**; geen zelfstandig nieuwe 2012-spits-/dalinterval als uit dit artikel af te leiden. De historische 157-waarden moeten voor zover juridisch van toepassing afzonderlijk worden gereconstrueerd.

## 5. Bronkwaliteit

| Resolutie | Pagina's | Extractie | Kwaliteit |
|---|---:|---|---|
| **232-2025** | 10 | native | **Art. 1 tabel p. 9 visueel geverifieerd**; p. 7 routebenaming |
| **265-2019** | 10 | native | art. 1, p. 8–10 gelezen; 3/6 en 33,6 km |
| **301-2014** | 16 | native | p. 14 eerdere scancontrole: 3/5 en 27 km |
| **242-2010** | 6 | OCR | art. 1/2 p. 5 gelezen, historische intrekking |
| **157-2010** | 10 | OCR | **p. 8-scan** 4/6 bevestigd |
| **242-2012** | 13 | OCR | **p. 13-scan** historische trajectwijziging bevestigd |

**PDF-harvest is nu afgerond: zes van zes.** De verbetering aan `scripts/resolve_amb_flota_links.py` haalt het dynamische WordPress Ninja Tables-`data_request_url` op en schrijft het tabelresultaat als `ninja_table_rows.json` plus een downloadlog weg. De vijf gevonden directe PDF-URL's zijn aan `sources/amb/pdf_manifest.csv` toegevoegd. Een geslaagde download of tekstextractie betekent niet dat een route operationeel is geverifieerd.

## 6. Resterend werk, zonder voertuigcapaciteit

- **FANG-07:** exacte 2025-p. 9 straatvolgorde georefereren naar OSM en haltepunten; de op de kaart gemarkeerde `Itinerario A` op p. 8 vergelijken met de beschreven straatroute. Een aparte B-variant niet verzinnen.
- **FANG-08:** werkelijke exploitatiestatus van A7 in 2026, spits- en daluren, week-/feestdagen, eerste/laatste rit en stopvolgorde onafhankelijk bevestigen.
- **FANG-03:** alleen voor historische GTFS de Transmetro-afhankelijke start/einddatum 2010/2014 en routewijzigingen reconstrueren.
- **FANG-10:** indien nodig geordende polyline-diffs 2014 → 2019 → 2025 met de volledige straatbladen, niet alleen de routelengtes.
- **FANG-01 / 02 / 04 / 05 / 06 / 09: bronophaling afgerond.**

**Voertuigcapaciteit is niet relevant voor onze GTFS en wordt hier bewust buiten beschouwing gelaten.**

**Machineleesbaar:** [`flota_angulo_route_frequency_history_2026-11-03.csv`](../sources/amb/flota_angulo_route_frequency_history_2026-11-03.csv).
