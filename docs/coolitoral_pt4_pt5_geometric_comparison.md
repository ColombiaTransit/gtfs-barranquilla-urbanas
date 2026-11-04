# COOLITORAL PT4/PT5 — geometrische broncontrole (2026-11-04)

## Vastgesteld
- AMB KMZ PT4-4104 en PT5-4105 hebben ieder een gesloten LineString met 467 coördinaten.
- De twee geometrieën zijn **niet identiek**: 464 van de 467 posities verschillen.
- Beide beginnen en eindigen op dezelfde coördinaat: lon -74.779234, lat 10.989761.
- In beide metadata ontbreekt een A/B-variantlabel. Een geometrie kan daarom niet zonder verdere toetsing aan A of B worden gekoppeld.
- SIU heeft twee bekende reguliere haltevolgorden: 132 haltes (CIRCUNVALAR VIA 40) en 124 (VIA 40 CIRCUNVALAR).
- De Overpass-export van 2026-11-04 bevat 777 OSM ways, met onder andere Carrera 43, Carrera 44, Carrera 41B, Calle 8 en Calle 10.

## Juridische zijstraatverschillen (Resolución 256-2026)
- PT4-A: Calle 30 > Carrera 38 > Corredor Portuario > Carrera 30.
- PT4-B: Calle 30 > Carrera 44 > Calle 10 > Carrera 41B > Calle 8 > Carrera 38 > Corredor Portuario > Carrera 30.
- PT5-A: Calle 4 > Carrera 38 > Calle 30 > Via 40.
- PT5-B: Calle 4 > Carrera 38 > Calle 8 > Carrera 41B > Calle 10 > Carrera 43 > Calle 30 > Via 40.

## Nog te meten
1. Voor beide KMZ-lussen de routeafstand langs de LineString bepalen.
2. Elke KMZ-vertex projecteren op de relevante OSM-wegsegmenten; rapporteer de dekking en afstand per straat.
3. Controleer de *opeenvolgende* trajecten over B-specifieke straten, niet alleen nabijheid tot een kruispunt.
4. Vergelijk de SIU-haltevolgorde als een cyclische reeks met beide KMZ-geometrieën, inclusief richting; beginpunt mag verschuiven, volgorde niet omkeren.
5. Gebruik de wettelijke routevolgorde en OSM-oneway-gegevens als aanvullende toets; behoud onzekerheid bij ontbrekende verbindingswegen.

## Beslisregel
Koppel een KMZ/SIU-geometrie niet automatisch aan A of B op grond van een routenaam, beginpunt of één straatmatch. Een A/B-classificatie vergt een consistent traject over de exclusieve zijstraten in de juridisch voorgeschreven volgorde. Tot die tijd blijft de GTFS-koppeling onder review.

## Bronnen
- `sources/amb/kmz/geojson/COOLITORAL/PT4-4104_351a345396.geojson`
- `sources/amb/kmz/geojson/COOLITORAL/PT5-4105_2fa953e451.geojson`
- `sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv`
- `sources/siu/public_extract/siu_route_stop_sequences.csv`
- Gebruikersupload `export (7).json` (Overpass API, 2026-11-04; nog niet in repository).

## Berekende KMZ-vergelijking (2026-11-04)

- PT4 en PT5 bevatten elk 467 GPS-vertices en zijn **exact elkaars omgekeerde** (alle 467 coördinaten matchen na omkeren).
- Beide vormen dezelfde gesloten lijn; de gemeten haversine-polyline-lengte is **35,529 km**.
- Deze KMZ-data toont dus één fysieke lus in twee rijrichtingen, niet afzonderlijke A/B-omwegen.
- De nominale lengtes in 256-2026 zijn PT4-A/B 34,5 km, PT5-A 35,5 km, PT5-B 35,3 km. Lengteverschillen alleen bewijzen geen variant.
- De SIU-halte **CALLE 30 CON CARRERA 44** ligt circa 5–8 m van de KMZ-lus; **AV. SIMON BOLIVAR CON CARRERA 44** circa 34 m; **ENTRADA CARRERA 43 (CIRCUNVALAR)** circa 5 m. Dit zijn *kruispunt-/halte-nabijheidsmetingen*, geen bewijs dat de KMZ de exclusieve B-zijstraten afrijdt.
- Er zijn in de bestaande landmarksteekproef geen herkenbare haltes met de naam Carrera 41B, Calle 8 of Calle 10. Afwezigheid van een straatnaam in haltebenamingen bewijst niet dat de bus die straat niet gebruikt.

**Conclusie:** de KMZ-geometrie bevestigt het tegengestelde luspatroon van PT4/PT5, maar de A/B-variant is nog **niet bewezen**. De beslissende toets is een geometrische overlay van de volledige KMZ-lijn op OSM-wegsegmenten voor Carrera 44 / Calle 10 / Carrera 41B / Calle 8 (PT4-B) en Calle 8 / Carrera 41B / Calle 10 / Carrera 43 (PT5-B), met aaneengesloten segmentlengtes en rijrichting. De door de gebruiker aangeleverde Overpass-export is hiervoor geschikt, maar is nog niet in deze repository opgenomen.
