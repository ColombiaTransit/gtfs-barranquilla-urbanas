# Afwijkende AMB-routegeometrie opnieuw getoetst met dichter geplaatste KMZ-waypoints

Een busroute die wegens 950m-waypoints afwijkt van het brontraject is opnieuw via het busprofiel gerouteerd
met ongeveer 450m tussen de verplichte KMZ-punten. Dit voorkomt veel kortere omwegen over parallelwegen
maar bewijst geen concessiebediening of exacte haltes. De eerdere GH-geometrie is niet overschreven.

## Resultaat

- source_GH_full_route_sections: **352**
- previously_mismatching_sections: **42**
- sections_retried: **42**
- GH_route_queries: **42**
- new_road_candidates_consistent_with_KMZ_after_dense_waypoints: **21**
- alignment_improved_but_still_inconsistent: **7**
- still_inconsistent_or_unroutable: **14**
- additional_stop_visits_close_to_retried_GH_road_net: **127**
- road_candidates_mapped: **42**

## Bronnen / beperkingen

- Private GraphHopper via ColombiaTransit organisatievariabele GRAPHHOPPER_URL, profiel bus.
- Publieke GraphHopper API-documentatie: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md
- Officiële KMZ-routes; historische ArcGIS-geometrie blijft als fallback gemarkeerd.
- Geen stop_sequence, stop_id, routes.txt, trips.txt of stop_times.txt aangepast.

## Output

- GH_dense_anchor_road_segment_before_after_QA.csv: per wegdeel eerdere/nieuwe match en aantal haltes binnen 45m.
- GH_dense_KMZ_constrained_bus_road_candidates_RESEARCH_ONLY.geojson: dichter aan de bronroute gebonden kandidaat-weggeometrie.
