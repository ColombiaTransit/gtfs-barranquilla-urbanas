# AMB KMZ → SIU-haltedekking en geografische onderzoekskandidaten

Bronnen: openbare AMB KMZ-routeviewer (93 vermelde bestanden), SIU-itineraries (33 reguliere), OSM Overpass (34 niet-geclassificeerde instapplaatskandidaten).

## Status

- siu_staged_strong_candidate: **12** KMZ-vermeldingen
- no_siu_route_stop_candidate: **60** KMZ-vermeldingen
- siu_link_ambiguous: **13** KMZ-vermeldingen
- siu_staged_provisional_candidate: **8** KMZ-vermeldingen

**Geografische nabijheid geeft GEEN bewezen haltebediening of stop_sequence.**
SIU-basisroutekoppelingen zijn nog niet juridisch definitief geverifieerd.
De SIU-bron is niet het complete AMB-netwerk; licentie/actuele vergunningstatus apart toetsen.
De KMZ-site kent 4 dubbele verwijzingen voor verschillende routelabels.

## Welke KMZ-routevermeldingen missen SIU?

| Bedrijf | Geen SIU-routekandidaat | SIU-koppeling onbeslist |
|---|---|---|
| FLOTA-ANGULO | — | — |
| TRANSMECAR | C17-4160, D10-4172, D11-4153, D9-4152 | — |
| FLOTA-ROJA | A8-4113 | — |
| TRANSDIAZ | A11-4115, B16-4130 | A10-4114 A, A10-4114 B |
| COOTRAB | — | — |
| EMBUSA | — | — |
| MONTERREY | B11-4166 | — |
| LA-CAROLINA | — | A16-4161 A, A16-4161 B |
| COOTRANSPORCAR | C8-4139 | — |
| COOCHOFAL | A15-4159, C2-4133, C3-4134, C9-4140, D20-4185 | — |
| TRASALFA | B2-B-4118 | — |
| COOLITORAL | A1-4106 A, A1-4106 B, A2-4107, A3-4108, A4-4109, B1-4117, PT2-4102 | B17-4163, PT1-4101, PT3-4103, PT4-4104, PT5-4105 |
| COOTRANTICO | A18-4183, B4-4120, B5-4121, B5-B-4190, B6-4122, B7-4123, B20-4180, B20-B-4191 | — |
| LOLAYA | B10-4126, B10-B-4193, D8-4165 | — |
| COOTRANSCO | C7-4138 | — |
| COOTRASOL | D3-4147, D4-4148, D5-4149 | — |
| SOBUSA | B18-4175 A, B18-4175 B, C11-4168, C12-4169 A, C12-4169 B, C13-4143, C14-4170, C16-4167 A, C16-4167 B | — |
| TRANSOLEDAD | D13-4155 | — |
| TRANSURBAR | — | — |
| SODETRANS | B14-4174, B15-4129 A, B15-4129 B | B13-4128, B13-B-4189, C21-4182 A, C21-4182 B |
| COOTRANSNORTE | A6-4111, A5-4110 | — |
| TRASALIANCO | B19-4176, D18-4179, D12-4154, D17-4158 | — |
| COOASOATLAN | C1-4132, C1-B-4186, C20-4181, C20-B-4187 | — |

## Reconstructie-onderzoek

- 60 routevarianten zonder SIU-kandidaat op maximaal 50m van bestaande SIU-halteplaatsen en OSM-punten getest.
- 60 van die varianten hebben minstens één SIU-punt binnen 30m (geen route-toewijzing).
- 38 varianten hebben minstens één OSM-kandidaat binnen 30m (geen bewezen TPC-halte).
- Posities langs een KML LineString zijn alleen geometrisch gesorteerd; volledige wettelijke rijrichting en haltevolgorde onbekend.
- Prioriteit: SOBUSA B18/C12/C16; overige bedrijven zonder SIU; varianten met KMZ-linkconflicten apart.
- Outputs: kmz_siu_route_stop_coverage.csv, uncovered_route_stop_search_summary.csv, nearby_stop_candidates_NOT_CONFIRMED.csv.
- Geen wijzigingen aan gtfs/trips.txt, gtfs/stop_times.txt of gtfs/shapes.txt.
