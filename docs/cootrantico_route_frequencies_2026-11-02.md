# COOTRANTICO — frequenties, vlootverdeling, trajectwijzigingen en juridische keten

**Peildatum:** 2 november 2026. **Gebruikte bronnen:** oorspronkelijke 19 PDF-extracties van `amb-pdf-COOTRANTICO` (GitHub Actions-run `41480204032`, artifact `13158924438`), plus **ontbrekende resolutie 108-2023**, opgespoord via de officiële AMB-website. De 19 geregistreerde extracties omvatten **18 unieke PDF's**: manifestregel `025-2011` downloadt *byte-identiek* de PDF van `331-2010`. Sinds deze controle zijn **20 manifestregels** geregistreerd, en de nieuwe **108-2023 is op 3 november 2026 in een geslaagde Action-run opnieuw geëxtraheerd**.

**Uitkomst:** acht routecodes in de recentste officiële vergunningswijziging **462-2025 van 27 november 2025**, individuele routefrequenties en voertuigcapaciteiten bronmatig aan de juiste PDF-pagina gekoppeld. Alle acht technische tabellen op p. 6, 8, 10, 12, 14, 16, 18, 20 zijn **visueel op de PDF-scans gecontroleerd**. De p. 10/max 28 versus p. 20/max 18 tegenstrijdigheid is **werkelijk aanwezig** en **geen OCR-fout**.

## 1. Laatst aangetroffen vergunning: 462-2025

| Route | Naam / corridor | Spitsinterval | Dalinterval | Min. voertuigen | Max. voertuigen | Lengte | Beschikkende tabel |
|---|---|---:|---:|---:|---:|---:|---|
| **A18-4183** | Barranquillita – Cevillar – Recreo – Universidades – Circular | **8 min** | **10 min** | **14** | **16** | **32,2 km** | Art. 1 **p. 6** |
| **B4-4120** | Barranquillita – Prado – Calle 72 – Nueva Colombia – Cordialidad – Galapa – Circular | **7** | **9** | **26** | **31** | **56,1 km** | **p. 8** |
| **B5-4121** | Barranquillita – Toboganes – Circunvalar – Caribe Verde – Circular | **8** | **10** | **15** | **28 in routetabel; 18 in vlootmatrix** | **37,3 km** | **p. 10 versus p. 20** |
| **B5-B-4190** | Barranquillita – Por Fin – La Manga – Circular | **8** | **10** | **12** | **14** | **27,8 km** | **p. 12** |
| **B6-4122** | Barranquillita – Prado – Circunvalar – Caribe Verde – Circular | **7** | **9** | **22** | **26** | **47,3 km** | **p. 14** |
| **B7-4123** | Barranquillita – Sourdis – El Bosque – Buenavista – Circular | **6** | **8** | **27** | **32** | **50,2 km** | **p. 16** |
| **B20-4180** | Barranquillita – La Pradera – Circular | **7** | **9** | **13** | **15** | **27,3 km** | **p. 18** |
| **B20-B-4191** | Barranquillita – Las Colinas – Circular | **7** | **9** | **15** | **18** | **30,7 km** | **p. 20** |

Voertuigklasse van **alle acht**: **Grupo C (Busetón–Buseta)**. Terminal in de beschikkende straattrajecten: **Calle 5 / Carrera 43, Barranquilla**. Dit is een dispatchterminal, niet automatisch een GTFS-halte. De vergunningsuren `00:00 a 24:00 ... dependiendo de las necesidades de demanda` zijn **voorwaardelijk** en bewijzen **geen** feitelijke nachtdienst.

**Bedrijfscapaciteit:** de samenvattende tabel in artikel 1, paragraaf 1, **p. 20** noemt **144 minimum en 170 maximum voertuigen**, met B5 **15–18**. De acht maxima van die samenvatting tellen exact op tot 170, terwijl gebruik van **28** voor B5 een bedrijfstotaal **180** zou opleveren. **Dus de in p. 10 gedrukte max 28 is een interne rechts-/documenttegenstrijdigheid en mag niet op grond van een rekencontrole stilzwijgend worden gecorrigeerd.** Beide letterlijke waarden blijven in de CSV bewaard.

Het SIBUS/RCC-vereiste is vastgelegd in artikel 1 paragraaf 2 (p. 21). De uitvoering en rijtijden zijn niet onafhankelijk bevestigd.

## 2. Gewijzigde frequenties versus 2018 / 2023 / 2024

### De cruciale B4-ontwikkeling naar Galapa
| Besluit | Routevorm | Spits | Dal | Vloot | Lengte |
|---|---|---:|---:|---|---|
| **388-2018** | Tijdelijke B4 Barranquillita – Cordialidad / Villa de la Cordialidad | **6** | **8** | **16–19** | historische variant |
| **108-2023**, art. 1 | B4-4120, Galapa / Villa Olímpica | **7** | **9** | **16–19** | **48 km** |
| **259-2024**, art. 1 | Twee itinerarios **A/B** naar Galapa en Villa Olímpica | **15 per A/B** | **17 per A/B** | **16–19 totaal** | **A 50,3 km / B 52,9 km** |
| **259-2024**, gemeenschappelijk drukste traject | Twee overlappende itinerarios | **7 effectief** | **9 effectief** | *zelfde vloot* | niet apart |
| **284-2024**, art. 1 | **Tekstcorrectie** in itinerary B: `Villa Cordialidad` moest `Villa Olímpica` zijn | **geen nieuw interval** | **geen nieuw interval** | ongewijzigd | geen nieuw besluit voor vloot |
| **462-2025**, art. 1 | Nieuwe, opnieuw geautoriseerde **enkelvoudige B4-trajectbeschrijving** via Prado / Calle 72 / Galapa | **7** | **9** | **26–31** | **56,1 km** |

**Correct gebruik:** 2024 `15/17` geldt per afzonderlijk itinerary A en B, en `7/9` is het *effectieve* interval op het gedeelde drukste traject. 2025 heeft een nieuw B4-routeblad met **7/9** als **route-interval**. Deze waarden mogen niet zonder patrooncontrole door elkaar worden gehaald.

### B7 en andere routes
- **B7-4123:** 324-2016 p. 15 gaf **7/10 min**, **21–26 voertuigen**. Het later ontdekte **108-2023**, art. 1, gaf **7/9 min**, **23–28 voertuigen**, **53 km**. **462-2025 p. 16** geeft **6/8 min**, **27–32 voertuigen**, **50,2 km**. Verandering **108→462**: spits −1, dal −1 minuut, lengte −2,8 km, minimum +4, maximum +4.
- **B6-4122:** **212-2016** art. 1 p. 7: **4/6 min**, **20–24**, **40,5 km**. 388-2018 tijdelijk **6/8** en **16–19**; 462-2025 geeft **7/9**, **22–26**, **47,3 km**.
- **A18-4183:** **388-2018** tijdelijk **6/8**, **16–19**; **462-2025** **8/10**, **14–16**, **32,2 km**. Dit is een langere vergunde tussenpoos en een kleinere vloot.
- **B20-4180:** **388-2018** tijdelijk **6/8**, **16–19**; **462-2025** **7/9**, **13–15**.
- **B20-B-4191:** **388-2018** tijdelijk **6/8**, **12–15**; **462-2025** **7/9**, **15–18**.
- **B5-4121:** **388-2018** tijdelijk **6/8**, **16–19**; **462-2025** **8/10**, **15–18 volgens bedrijfsmatrix** (*max 28 volgens routetabel*).
- **B5-B-4190:** **388-2018** tijdelijk **6/8**, **12–15**; **462-2025** **8/10**, **12–14**.

De 388-2018-vergunning heeft een **expliciete tijdelijke status**: artikel 3 p. 17 noemt geldigheid tot de implementatie van het SITP. Zonder exacte invoeringsdata en opvolgingsbesluiten mogen de historische waarden niet als een vaste, doorlopende kalender worden gepubliceerd.

### Bijzondere 2013 / 2010 juridische correctie
- **330-2010** trok de historische `RUTA 3 ESTUDIANTES – LOS ANDES` in met een Transmetro-afhankelijke werking.
- **406-2013**, art. 1 **weigert** formeel de gevraagde directe herroeping, **maar artikel 2 verklaart tegelijk het verlies van uitvoerbaarheid** (*pérdida de fuerza ejecutoria*) van **330-2010**, waardoor de oorspronkelijke route als **A18-4183** mag blijven rijden. Deze twee rechtsgevolgen kunnen naast elkaar bestaan en mogen niet geautomatiseerd tot “afgewezen bezwaar = route nog ingetrokken” worden vereenvoudigd.
- **332-2010:** trekt de **andere** historische `LOS ANDES – ESTUDIANTES` in; niet blind gelijkstellen aan `RUTA 3` uit 330.
- **331-2010** trekt `RUTA 2 MANGA NUEVA COLOMBIA` in, onder invoeringsvoorwaarden; geen bewezen relatie met huidige B20/B20-B uit de routecode alleen.
- Het manifestlabel **025-2011** wijst naar precies **dezelfde PDF-bytes** als **331-2010** (beiden SHA-256 prefix `7d1f47ba99930a14`). Er is **geen afzonderlijke resolutie 025-2011** uit die manifestregel onderzocht. Deze bronfout is afzonderlijk vastgelegd.
- **309-2014**, artikelen 1–3 pp. 13–20: herstructureert zes eerdere routes, vloot **121–148**. Artikel 3 koppelt de invoering aan de gefaseerde Transmetro-vlootinstroom. Oude intervallen en capaciteit zijn geen actuele dienstregeling.


### Controle afgerond op 3 november 2026: resolutie 108-2023

De [Action-run 41523797737](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41523797737) heeft **8 van 8 pagina's met Spaanse OCR verwerkt**. De originele PDF-scans **p. 6 (B4)** en **p. 7 (B7)** zijn vervolgens visueel gecontroleerd. **B4-4120 = 7 min spits / 9 min dal / 48 km; B7-4123 = 7/9 min / 53 km.** B4 (art. 1 p5–6) heeft in 2023 een route richting Galapa en Villa Olímpica; B7 (art. 1 p6–7) via Sourdis/El Bosque/Buenavista. Beide zijn historische parameters; latere besluiten uit 2024 en 2025 blijven bepalend voor de nieuwste vergunningen.

[Machineleesbare 2023-routegegevens](../sources/amb/cootrantico_108_2023_historical_route_parameters.csv). **Geen voertuigcapaciteit in GTFS-analyse.**

## 3. Audit van alle resoluties en nieuwe bron
Het bestand `sources/amb/cootrantico_resolution_legal_index_2026-11-02.csv` heeft **20 regels**:
- **19** oorspronkelijk geregistreerde en geëxtraheerde resolutie-items, waarvan **18** unieke PDF's;
- **1** extra officiële resolutie **108-2023**, die eerder ontbrak, toegevoegd aan `sources/amb/pdf_manifest.csv`, en via web-PDF gelezen. **GitHub OCR-artifact 13178511921 van run 41523797737 is nu gegenereerd: alle 8/8 pagina's met Spaanse OCR**.

De andere juridische ketens: **243/450-2010** (B4+B7, gedeeltelijk bevestigde bezwaren), **245/449-2010** (B5-routewijziging), **244-2010 + 149-2011** (B6-routewijziging, behoud oude capaciteit), **150-2015 en 324-2016** (B7), **212-2016** (B6), en **259/284-2024** (B4) zijn geclassificeerd inclusief artikellocaties en OCR-aandachtspunten. Niet alle oude 2010-straatsegmenten zijn visueel overgetekend; voor historische GTFS blijft dat gericht vervolgwerk.

## 4. Vervolgwerk, zonder blokkade van de overige vervoerders

| ID | Prioriteit | Open taak | Afsluitcriterium |
|---|---|---|---|
| **CT-01** | **Blokkerend** | **B5-4121 462-2025: max. 28 in artikel 1 p. 10 vs 18 in paragraaf 1 p. 20.** Vraag formele correctie/interpretatie bij AMB na; niet één waarde verzinnen. | Officiële rectificatie of voldoende juridisch bewijs welke capaciteit bindend is |
| **CT-02** | Hoog | **108-2023 afgerond op 3-11-2026:** OCR-artifact 13178511921, 8/8 pagina's; B4 p6 en B7 p7 visueel geverifieerd. | Nieuwe extraction `report.json` en p. 1–laatste pagina in artifact |
| **CT-03** | Hoog | **025-2011**: onjuiste PDF-link in manifest vervangen door echte originele PDF of item markeren als ontbrekende bron; huidige download is duplicaat van 331-2010. | Correcte officiële 025-2011 of expliciet `missing_original` |
| **CT-04** | Hoog | Feitelijke dienstregeling in 2026 en *hora pico / hora valle*-kloktijden voor alle 8 routes vinden. | Onafhankelijke week-/feestdagkalender en rit/intervalbewijs |
| **CT-05** | Hoog | Routegeometrie uit 462-2025 p. 5–20 sequentieel naar OSM, haltes en rijrichting vertalen. | Controleerbare `shapes`, `stop_sequence` en halteplaatsen |
| **CT-06** | Middel | Inwerkingtreding/looptijd 388-2018 (voorwaardelijk SITP) en 309-2014 (gefaseerde Transmetro) reconstrueren. | Officiële implementatie- en overgangsdatums |
| **CT-07** | Middel | Oudere OCR-route-/vloottabellen 243-2010 B7, 211/149 routebenaming, juridische bezwaren, tegen scans controleren. | Gevalideerde historische tabelwaarden met pagina |
| **CT-08** | Middel | 284-2024 gecorrigeerd B-itinerary vergelijken met B4-2025 en 108-2023; oude routevarianten niet als actuele B4-patronen behouden. | Straatsegment-diff met juridische tijdlijn |
| **CT-09** | Middel | Controleren of AMB na 27-11-2025 nog gemeenschappelijke of bedrijfsspecifieke besluiten heeft genomen. | Vastgelegde controle-datum en juridische status |

**Per 2 november 2026** toont de officiële COOTRANTICO-bedrijfspagina resolutie 462-2025 als recentste bedrijfsspecifieke PDF. Dit sluit algemene besluiten of niet-gepubliceerde opvolgingsdocumenten niet uit.

## 5. Opslag en GTFS-beoordeling

- `sources/amb/cootrantico_latest_route_parameters_2026-11-02.csv`: **acht routes**, inclusief zowel B5 `fleet_max_table=28` als `fleet_max_summary=18`, dossierstatus en PDF-pagina.
- `sources/amb/cootrantico_resolution_legal_index_2026-11-02.csv`: **20 manifest-/brondocument-regels**, juridische aard, oorspronkelijke document-hash voor duplicaatcontrole, tekstkwaliteit en vervolgwerk.
- `sources/amb/pdf_manifest.csv`: officiële ontbrekende **108-2023** toegevoegd.
- **`GTFS_READY=no` voor alle acht routes.** De vergunde frequenties zijn onderzoekbare bronwaarden, geen bewezen operationele ritten; geen productiewijzigingen in `frequencies.txt`, `trips.txt`, `calendar.txt`, `stop_times.txt` of `shapes.txt`.

### Officiële bronnen
- [AMB bedrijfsarchief COOTRANTICO](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrantico/)
- [462-2025 — 8 routes, p. 5–21](https://www.ambq.gov.co/wp-content/uploads/2025/12/RESOLUCION-METROPOLITANA-No-462-2025-COOTRANTICO.pdf)
- [108-2023 — B4 en B7, 26 april 2023](https://www.ambq.gov.co/wp-content/uploads/2023/06/RESOLUCION-M.-108-2023-L.pdf)
- [259-2024 — B4 itinerarios A/B](https://www.ambq.gov.co/wp-content/uploads/2024/10/RESOLUCION-METROPOLITANA-N%C2%B0-259-2024-COOTRANTICO.pdf)
- [284-2024 — B4 tekstcorrectie](https://www.ambq.gov.co/wp-content/uploads/2024/10/RESOLUCION-METROPOLITANA-N%C2%B0-284-2024.pdf)


## Archiefreconciliatie — 5 november 2026

Archiefhercontrole: B4 108-2023 7/9 is historisch en stemt numeriek overeen met 462-2025 7/9, maar 259-2024 A/B 15/17 betreft afzonderlijke itineraria en 7/9 daar de gedeelde sectie. B7 108-2023 7/9 is vervangen door 462-2025 6/8. De visueel gecontroleerde 462-2025 tabellen blijven leidend. Geen nieuwe OCR nodig.

Zie [route-voor-route classificatie](../sources/amb/amb_archive_route_reconciliation_2026-11-05.csv) en [inhoudelijke vergelijking](amb_archive_2020_2026_existing_register_comparison_2026-11-05.md).
