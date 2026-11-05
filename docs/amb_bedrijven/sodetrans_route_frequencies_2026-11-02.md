# SODETRANS — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-SODETRANS`. **Manifest:** 14 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

719-2018 herstructureert B13, B14 en C21; B15/B17 worden in de bedrijfsvlootmatrix genoemd maar krijgen in dit besluit geen zelfstandige nieuwe frequentietabel. B17-4163 deelt exploitatie met COOLITORAL.

**Belangrijkste onderzochte besluiten:** 719-2018; B17 gedeeld later in COOLITORAL 192-2025.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| B13-4128 | 5 | 7 | 34–41 | 73.2 | 719-2018 p8: beschikkend routeblad |
| B14-4174 | 5 | 7 | 34–41 | 67.4 | 719-2018 p9: beschikkend routeblad |
| C21-4182 | 4 | 6 | 51–62 | 72.7 | 719-2018 p10: beschikkend routeblad |
| B15-4129 | **onbevestigd** | **onbevestigd** | 20–24 | ? | 719-2018 p7: alleen bedrijfsvlootmatrix, frequentie afzonderlijk bepalen |
| B17-4163 | **onbevestigd** | **onbevestigd** | 31–37 | ? | 719-2018 p7: 2018 bedrijfsvlootmatrix; Coolitoral 192-2025 noemt 35–42 per partij; cross-operator reconciliatie nodig |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 719-2018 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2018/11/Resolucion-Metropolitana-719-18.pdf) | nieuwste / sleutelbesluit |
| 270-2014 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2017/11/SODETRANS-B17-Resolucion-270-14.pdf) | historisch; artikelen nader toetsen |
| 031-2015 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2017/11/SODETRANS-B17-Resolucion-031-15.pdf) | historisch; artikelen nader toetsen |
| 325-2016 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2017/01/Resolucion-N%C2%B0-325-16-.pdf) | historisch; artikelen nader toetsen |
| 181-2016 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads//2016/RESOLUCIONES-DE-RUTAS/SODETRANS/Resolucion-181-16-sodetrans.pdf) | historisch; artikelen nader toetsen |
| 216-2016 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/resolucion-216-16-ilovepdf-compressed.pdf) | historisch; artikelen nader toetsen |
| 311-2014 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2017/04/Resolucion-311-14.pdf) | historisch; artikelen nader toetsen |
| 459-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-B13-Resolucion-459-10.pdf) | historisch; artikelen nader toetsen |
| 457-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-B14-Resolucion-457-10.pdf) | historisch; artikelen nader toetsen |
| 458-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-B15-Resolucion-458-10.pdf) | historisch; artikelen nader toetsen |
| 190-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-B17-Resolucion-190-10.pdf) | historisch; artikelen nader toetsen |
| 111-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-C21-resolucion-111-11.pdf) | historisch; artikelen nader toetsen |
| 121-2012 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-C21-resolucion-121-12.pdf) | historisch; artikelen nader toetsen |
| 461-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SODETRANS/SODETRANS-C21-resolucion-461-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- SODE-01 B17-aandeel 2018 versus 2025 formeel reconciliëren
- SODE-02 B15-frequentie uit eerdere besluiten
- SODE-03 huidige dienst en voertuigklasse D-padrón
- SODE-04 geometrie en haltevolgorde.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).


## Actualisatie 5 november 2026 — Resolución Metropolitana 500-2025

**Leidende officiële bron:** https://www.ambq.gov.co/wp-content/uploads/2026/02/Resolucion-Metropolitana-No.-500-2025-SODETRANS.pdf. De gebruiker heeft bevestigd dat geen nieuwer besluit de frequenties wijzigt. Dit besluit gaat voor op de hierboven weergegeven historische 719-2018-waarden waar het dezelfde routes wijzigt; de oudere tabellen zijn uitsluitend historisch en mogen niet automatisch in de huidige GTFS worden gebruikt.

| Route | Piek (min) | Dal (min) | Bron / status |
|---|---:|---:|---|
| B13-4128 | 7 | 9 | 500-2025, eerdere gespreksextractie; controleren bij machineleesbare import |
| B13-B-4189 | **8** | **10** | 500-2025 p8, **visueel en juridisch door gebruiker gevalideerd** |
| B14-4174 | 7 | 9 | 500-2025, eerdere gespreksextractie; controleren bij machineleesbare import |
| B15-4129 | — | — | 500-2025 bevat A/B-itinerarios; exacte eigen intervallen per variant nog uitlezen, niet afleiden uit sectiefrequentie |
| B17-4163 | — | — | gezamenlijke exploitatie met COOLITORAL behouden; 500-2025-waarden en samenloop verifiëren |
| C21-4182 | — | — | 500-2025 bevat meerdere itinerarios; genoemde 4-minuten-drukste-sectie niet zonder meer per variant overnemen |

**Besluit:** B13-B-4189 is niet langer `missing_headway`. Alle zes routes zijn juridisch aan 500-2025 gekoppeld; voor B15/B17/C21 is de afzonderlijke machineleesbare numerieke extractie nog niet bewezen. Het bestaan van een besluit is niet hetzelfde als een succesvolle GTFS-build. Voorkom heropening van afgeronde OCR-taken; voer een expliciete frequentiedekkingscontrole uit op alle routevarianten in de generator.
