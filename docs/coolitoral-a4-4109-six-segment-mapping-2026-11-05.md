# COOLITORAL A4-4109 — koppeling van zes KMZ-LineStrings aan officiële recorrido

Status: **geometrische bronanalyse voltooid; straatmatching en GTFS-reconstructie nog niet gevalideerd**. Geen ArcGIS-fallback.

Bron: `sources/amb/kmz/geojson/COOLITORAL/A4-4109_539ee1b2e3.geojson`; officiële geordende straatbeschrijving: `docs/coolitoral-a4-4109-official-recorrido-geometry-review-2026-11-05.md`.

## Feitelijke KMZ-segmentinventaris (volgorde in bronbestand, 1-based)

| Segment | Punten | Begin [lon,lat] | Einde [lon,lat] | Interpretatie |
|---|---:|---|---|---|
| 1 | 142 | -74.8385531, 11.0156775 | -74.8363449, 10.9764933 | West/zuidwestelijk lang traject met lus; begin = segment 2 begin, einde = segment 3 einde |
| 2 | 37 | -74.8385531, 11.0156775 | -74.8319782, 11.0119914 | Noordelijke verbinding; eind ≈ begin segment 3 |
| 3 | 288 | -74.8319783, 11.0119914 | -74.8363449, 10.9764933 | Westelijk/noordelijk lang traject, met grote omweg; deelt eindpunt met segment 1 |
| 4 | 50 | -74.8269594, 11.0046063 | -74.8269594, 11.0046063 | Gesloten oostelijk gelegen lus |
| 5 | 86 | -74.8291819, 10.9960139 | -74.8291819, 10.9960139 | Gesloten oostelijk gelegen lus |
| 6 | 54 | -74.8095361, 10.9925813 | -74.8095361, 10.9925813 | Gesloten meest oostelijke lus |

Alle 657 punten zijn aanwezig. De segmentnummers komen overeen met de volgorde van de GeoJSON-features en met de oorspronkelijke viewer.

## Zeker aantoonbare verbindingen
- 1.start == 2.start (exact).
- 2.end ≈ 3.start (verschil ~0,01 m).
- 1.end == 3.end (exact).
- Segmenten 4, 5, 6 zijn elk op zichzelf gesloten. Dat betekent **niet** dat ze als geheel aan de andere segmenten gekoppeld zijn.
- Een route kan via hetzelfde knooppunt terugkeren, maar een gedeeld eindpunt bewijst nog geen verkeerskundig toegestane afslag.

## Matching met de officiële recorrido (voorlopige geografische indeling)
| Officiële passage | KMZ-kandidaat | Bewijsstatus |
|---|---|---|
| El Pueblo, Carrera 10, Circunvalar, Carrera 9G | 1/3 (westelijk traject) | Kandidaat; exacte rijrichting en segmentknip vereist |
| Pinar del Río, Carrera 38, Calle 120, Carrera 37, Calle 123, Carrera 31, retorno Carrera 28 | 1/3 | Kandidaat; niet per straat geverifieerd |
| Carrera 52, Calle 106, Carrera 51B, Universidad del Atlántico | 2/3/4 | Kandidaat; knooppunten en brug/afslag afzonderlijk controleren |
| Calle 96, Carrera 46, Calle 90, Parque Venezuela | 4/5 | Kandidaat; geordende straatmatching vereist |
| Calle 90, Carrera 42B1, Calle 81, Carrera 42A, Calle 80B, Carrera 42, Calle 75B, Carrera 41D, Calle 74, Carrera 44, Calle 37, Carrera 43, Carrera 42F | 5/6 | Kandidaat; oostelijke lus nog niet met straatnamen geverifieerd |
| Calle 75B, Carrera 42, Calle 80B, Carrera 42B, Calle 81, Carrera 42B1, Calle 93, Carrera 51B, glorieta, Circunvalar, Carrera 9G, El Pueblo | 6/5/4/3/1 | Kandidaat; kan niet worden vastgesteld zonder interne knippunten en gerichte wegtopologie |

**Waarschuwing:** de kandidaatkolom is geen vastgestelde routevolgorde. De geografische indeling is een eerste hypothese op basis van segmentbereik en de aangeleverde routekaart; ze mag niet rechtstreeks worden gebruikt om GTFS-shapes te genereren.

## Reconstructievoorwaarden
1. Georeferentieer de officiële straten/kruispunten op OSM en leg voor ieder waypoint vast welk segment en welke vertex/edge het raakt.
2. Splits LineStrings op echte knooppunten, inclusief midden-op-lijn-aansluitingen.
3. Bouw een gerichte graaf; verifieer weghelft, eenrichtingsverkeer, toegestane afslag en retorno.
4. Volg de officiële waypointvolgorde, inclusief expliciete terugritten; laat geen automatisch kortste-pad-algoritme het voorgeschreven traject vervangen.
5. Exporteer alleen na controle van aaneengesloten en verkeerskundig geldige lijnstukken naar een GTFS-shape; behoud QA/provenance en geef onzekere koppelingen een blocker.
6. ArcGIS OBJECTID 16 blijft uitgesloten wegens `ARCGIS_ROUTE_GEOMETRY_CONFLICT`.

**Nog geen goedgekeurde GTFS-shape:** exacte straat-to-segmentkoppeling en gerichtheid zijn met de huidige geometrische inventaris niet bewezen.
