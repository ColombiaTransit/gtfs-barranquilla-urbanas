# Busprofiel GraphHopper: wegrichting en bereikbaarheid voor SIU-haltegaten

**Gebruikt uitsluitend ColombiaTransit organisatievariabele GRAPHHOPPER_URL.** Geen privé-adres, token of querystring wordt door het Python-script geprint of opgeslagen. GitHub organisatievariabelen zijn geen geheimen: gebruik een Organization Secret als het adres zelf vertrouwelijk moet blijven.

De test vergelijkt de kortste busroute met een via KMZ-tussenpunten begrensde busroute om te voorkomen dat een korte weg een officieel omwegtraject overslaat. De test is uitsluitend onderzoek naar bus-toegankelijke wegtrajecten, rijrichtingsasymmetrie en de omweg bij rijden via een bestaande SIU-/OSM-haltekandidaat. Een route kan een juridisch andere corridor volgen dan de kortste GraphHopper-busroute. Curbside werkt alleen bij edge-based turn-cost routing en een ondersteund busprofiel.

## Resultaat

- GraphHopper_connection: **responded_to_info**
- required_profile: **bus**
- bus_profile_present: **True**
- version_reported: **11.1**
- OSM_import_date_reported: **2026-10-25T13:53:41Z**
- input_gap_count: **73**
- input_candidate_links: **125**
- gap_bus_routes_tested: **73**
- bus_baseline_success: **71**
- bus_reverse_success: **71**
- KMZ_anchor_constrained_bus_success: **73**
- direct_bus_shortcuts_under_half_KMZ_distance: **14**
- gaps_with_observed_bus_directional_asymmetry: **23**
- candidates_in_tested_gaps: **125**
- bus_via_queries_attempted: **125**
- curbside_queries_attempted: **0**
- KMZ_constrained_via_candidate_success: **125**
- successful_right_curbside_tests: **0**
- total_route_queries: **469**
- total_info_queries: **1**
- GTFS_stops_created: **0**
- GTFS_trip_sequences_modified: **False**
- new_OSM_queries: **0**
- route_operator_boarding_proven: **False**

## Bestanden

- bus_route_gap_direction_checks.csv — kortste A→B/B→A en KMZ-tussenpunt-begrensde busroute, met shortcut-status
- bus_candidate_access_and_oneway_review.csv — kortste en KMZ-begrensde routes via halte-kandidaat; haltebediening onbevestigd
- GraphHopper_bus_paths_for_KMZ_comparison.geojson — gegenereerde busweg-geometrie voor vergelijking met officiële bronlijnen

## Bronnen en vervolg

- Publieke API-referentie: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md
- De private runtime-URL staat alleen in de ColombiaTransit GitHub Actions-organisatievariabele.
- Niet automatisch toevoegen of verwijderen: busroute en curbside kunnen afwijken van exacte AMB-shape; aanvullende operator-/haltevalidatie nodig.
- In een vervolgactie kan dezelfde workflow voor 73 gaten en 125 kandidaten volledig worden uitgevoerd.
