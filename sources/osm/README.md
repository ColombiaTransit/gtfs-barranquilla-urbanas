# Overpass Barranquilla — archief en classificatie

**Bronbestand:** [Overpass-export van 3 november 2026](overpass_barranquilla_bus_stops_2026-11-03.json), door de gebruiker aangeleverd, OSM-snapshot **2026-11-03T06:51:24Z**, generator Overpass API 0.7.62.4. De zoekbox was globaal **10.78,-75.05,11.14,-74.62**. De export bevat alleen objecten met bushaltegerelateerde OSM-tags die binnen deze query vielen; volledigheid van traditionele TPC-haltes is **niet gegarandeerd**.

**Auteursrecht en licentie:** © OpenStreetMap contributors, [Open Database License (ODbL)](https://www.openstreetmap.org/copyright). Brondata is afkomstig van OpenStreetMap, niet van AMB. Bij gebruik en verdere publicatie blijven de ODbL-voorwaarden en attributie gelden.

## Controle met AMB-routelijnen

De herhaalbare [Audit OSM bus stops against AMB routes](../../.github/workflows/audit-osm-stops.yml) leest de originele Overpass-JSON en de [historische ArcGIS-routelaag](https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6) met 93 polyline-geometrieën. Met een UTM-18N-projectie berekent de Action afstanden tussen OSM-punten en de dichtstbijzijnde routelijn. Voor OSM-`way`-objecten gebruikt de analyse alleen het door Overpass geleverde middelpunt: dit is **niet** de volledige polygongeometrie.

| Klasse | Aantal |
|---|---:|
| OSM-objecten totaal | **599** |
| Node | 593 |
| Way (perrons met `center`) | 6 |
| Expliciet `Transmetro` of `Alimentador` | **487** |
| Regionale Baranoa–Barranquilla / Cootransguajaro | **33** |
| Netwerk niet te bepalen | **79** |
| Daarvan uitsluitend `stop_position` | **45** |
| Overige mogelijke boarding-/platformobjecten | **34** |
| Mogelijke instapplaatsen binnen **50 m** GIS-lijn | **16** |
| Mogelijke instapplaatsen binnen **100 m** | **18** |
| Mogelijke instapplaatsen met een naam | **3** |
| **Bevestigde TPC-haltepunten uit dit bestand** | **0** |

**Belangrijk:** `unclassified_candidate` betekent uitsluitend dat het OSM-object géén expliciet herkenbare netwerk-/operator-tag heeft. Het betekent **niet** dat het als TPC-halte is geïdentificeerd. Deze lijst kan ook nog Transmetro-punten bevatten, zeker in het stadscentrum waar vele lijnen overlappen. De afstanden tot de oude GIS-lijnen zijn alleen een geografische zoekhulp; geen enkele haltevolgorde per route wordt daaruit bewezen.

## Uitvoer in repository

- [Alle 599 punten met classificatie en dichtstbijzijnde route](analysis/all_osm_stops_audit.csv)
- [Alle 79 niet-geclassificeerde punten](analysis/unclassified_osm_stops.csv)
- [34 mogelijke boarding-/platformobjecten](analysis/possible_boarding_platforms.csv)
- [**16 prioriteitspunten bij GIS-lijnen**](analysis/priority_platforms_near_amb_routes_50m.csv)
- [GeoJSON voor de 34 mogelijke instapplaatsen](analysis/possible_boarding_platforms.geojson)
- [Korte samenvatting](analysis/summary.md)
- [Reproduceerbare Python-analyse](../../scripts/audit_osm_stops.py)

**Bepaal geen GTFS `stops.txt` op grond van deze dataset alleen.** Voor TPC hebben we nog ontbrekende instaphaltes, de stopvolgorde en de actuele A/B-routevariantgeometrie nodig. SIU/SIBUS kan daarvoor later een aanvullende bron zijn.

## Filterregels

1. Operator/netwerk `Transmetro` of netwerk `Alimentador`: expliciet Transmetro.
2. Netwerk bevat `Baranoa` of operator bevat `Cootransguajaro`: regionaal, niet automatisch AMB-TPC.
3. Overige: `unclassified_candidate`.
4. Onder (3): `public_transport=platform` of `highway=bus_stop` → mogelijk boarding-kandidaat. Alle `stop_position` zonder instapplaats-tag blijven afzonderlijk bewaard.
5. Binnen 50 m van de GIS-lijn betekent alleen **prioriteit voor validatie**. Geen operator, route, richting of haltevolgorde afleiden.

De herhaalde geografische audit moet dezelfde aantallen opleveren zolang de Overpass-input en de ArcGIS-laag niet gewijzigd zijn. Bij nieuwe OSM-export kan dezelfde pipeline met bijgewerkte `--osm` worden uitgevoerd.
