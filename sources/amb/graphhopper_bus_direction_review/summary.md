# Busprofiel GraphHopper: wegrichting en bereikbaarheid voor SIU-haltegaten

**Gebruikt uitsluitend ColombiaTransit organisatievariabele GRAPHHOPPER_URL.** Er is geen privé-adres, token of querystring naar documentatie, GitHub of console geschreven.

De test is uitsluitend onderzoek naar bus-toegankelijke wegtrajecten, rijrichtingsasymmetrie en de omweg bij rijden via een bestaande SIU-/OSM-haltekandidaat. Een route kan een juridisch andere corridor volgen dan de kortste GraphHopper-busroute. Curbside werkt alleen bij edge-based turn-cost routing en een ondersteund busprofiel.

## Resultaat

- GraphHopper_connection: **responded_to_info**
- required_profile: **bus**
- bus_profile_present: **True**
- version_reported: **11.1**
- OSM_import_date_reported: **2026-10-25T13:53:41Z**
- input_gap_count: **73**
- input_candidate_links: **125**
- gap_bus_routes_tested: **10**
- bus_baseline_success: **10**
- bus_reverse_success: **10**
- gaps_with_observed_bus_directional_asymmetry: **2**
- candidates_in_tested_gaps: **22**
- bus_via_queries_attempted: **22**
- curbside_queries_attempted: **5**
- successful_right_curbside_tests: **0**
- total_route_queries: **79**
- total_info_queries: **1**
- GTFS_stops_created: **0**
- GTFS_trip_sequences_modified: **False**
- new_OSM_queries: **0**
- route_operator_boarding_proven: **False**

## Bestanden

- bus_route_gap_direction_checks.csv — A→B versus B→A routeafstanden en vergelijking met officiële KMZ-corridor
- bus_candidate_access_and_oneway_review.csv — bus via stop-kandidaat en eventueel curbside-check; route-stop-service blijft onbevestigd
- GraphHopper_bus_paths_for_KMZ_comparison.geojson — gegenereerde busweg-geometrie voor vergelijking met officiële bronlijnen

## Bronnen en vervolg

- Publieke API-referentie: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md
- De private runtime-URL staat alleen in de ColombiaTransit GitHub Actions-organisatievariabele.
- Niet automatisch toevoegen of verwijderen: busroute en curbside kunnen afwijken van exacte AMB-shape; aanvullende operator-/haltevalidatie nodig.
- In een vervolgactie kan dezelfde workflow voor 73 gaten en 125 kandidaten volledig worden uitgevoerd.
