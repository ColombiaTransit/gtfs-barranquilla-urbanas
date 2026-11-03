# SOBUSA: AMB-KMZ A/B-verschillen en halte-kandidaten

**Onderzoek, géén gevalideerde SOBUSA-stops.** SIU is voor SOBUSA niet opgenomen in de publieke 33-itinerarylijst. De geprojecteerde punten zijn afkomstig van SIU-haltes van andere lijnen of onbevestigde OSM-punten.

## Per routelabel

| AMB KMZ | Lengte KMZ (km) | Nabij SIU (35 m) | Nabij OSM (35 m) |
|---|---:|---:|---:|
| B18-4175 A | 75.6 | 451 | 4 |
| B18-4175 B | 73.6 | 423 | 3 |
| C11-4168 | 62.7 | 313 | 4 |
| C12-4169 A | 47.8 | 321 | 4 |
| C12-4169 B | 48.5 | 325 | 4 |
| C13-4143 | 48.1 | 240 | 3 |
| C14-4170 | 56.2 | 319 | 4 |
| C16-4167 A | 63.2 | 424 | 4 |
| C16-4167 B | 63.9 | 425 | 5 |

## A/B-routeverschillen (afstand tot de andere geometrie)

| Route | A-lengte (km) | B-lengte (km) | A-punten >25m van B | B-punten >25m van A |
|---|---:|---:|---:|---:|
| B18-4175 | 75.6 | 73.6 | 266 | 270 |
| C12-4169 | 47.8 | 48.5 | 58 | 86 |
| C16-4167 | 63.2 | 63.9 | 68 | 92 |

## Verificatie

- Projectie langs route geeft een **geometrische volgorde**, niet een valide haltevolgorde of geautoriseerde halte.
- Bij lussen, terugritten en tegenliggers is LineString-projectie ambigu; herhaalde haltepassages kunnen ontbreken.
- Nabij SIU-punt: bewezen locatie voor **een andere SIU-lijn**, niet voor SOBUSA.
- Nabij OSM-punt: **geen bevestigde TPC-instapplaats**; expliciete Transmetro-haltes zijn gefilterd.
- Bestaande officiële A/B-frequenties blijven leidend, maar zonder bevestigde haltes worden geen GTFS-ritpatronen gepubliceerd.
- Eerst terminalstraten en A/B-afwijkingszones controleren tegen resolutie 466-2025 en 082-2026.
