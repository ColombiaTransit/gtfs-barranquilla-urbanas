# COOLITORAL PT4/PT5 — operationele SIU-koppeling op basis van resolutie en haltevolgorde

## Bronnen
- Resolución 256-2026, p. 4 en 6; geverifieerde straatvolgorden: `sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv`.
- SIU-volgorde: `sources/siu/public_extract/siu_route_stop_sequences.csv`; eerdere controle `sources/siu/coolitoral_256_street_audit/summary.md`.
- KMZ-analyse: `docs/coolitoral_pt4_pt5_geometric_comparison.md`; run 41992183773.

## Operationeel besluit op basisrouteniveau
| SIU-itinerary | Haltes | Eerste SIU-halte | Resolutie: beginstraat | Operationele baseroute | Confidence |
|---|---:|---|---|---|---|
| CIRCUNVALAR VIA 40 | 132 | CALLE 17 CON CARRERA 28 (NS) | PT4: Calle 17 con Carrera 30 | **PT4-4104** | probable |
| VIA 40 CIRCUNVALAR | 124 | VIA 40 CON CARRERA 53B (SN) | PT5: Vía 40 No. 51-310 | **PT5-4105** | probable |

De 2019 AMB-KMZ's PT4 en PT5 zijn dezelfde gesloten lijn in omgekeerde volgorde (467 vertices); de SIU-haltevolgorde is voor beide richtingen geografisch sterk: 99,24% en 100% binnen 50 m, beide nul volgordefouten na cyclische wrap. Dit ondersteunt een operationele richtingstoewijzing, maar de KMZ zelf bevat geen A/B-detail.

**Beperking:** de vorige SIU-straatnamen-audit gebruikte de volledige haltevolgorde als cyclische reeks, maar bevestigde geen volledige GPS-op-wegvolgorde voor de afzonderlijke zijstraten uit 256-2026. Eerste halte is niet bewezen exact dispatchterminal; routenaam suggereert historisch omgekeerde codering. Daarom **probable operational base mapping**, geen juridische identificatie en geen A/B-toewijzing. Niet automatisch bestaande GTFS-mappings overschrijven.

## Nog open (alleen geometrisch)
- PT4-A vs PT4-B: PT4-B rijdt via Carrera 44 > Calle 10 > Carrera 41B > Calle 8.
- PT5-A vs PT5-B: PT5-B rijdt via Calle 8 > Carrera 41B > Calle 10 > Carrera 43.
- Voor A/B: toets doorlopende SIU-GPS-haltevolgorde aan deze specifieke straten, niet alleen straatnamen of kruispuntnabijheid. Gebruik waar beschikbaar OSM-wegen en de geverifieerde resoluties.

Geen nieuwe juridische bevestiging vereist voor operationele basisroute; afgesloten juridische onderzoeksfase niet heropenen.
