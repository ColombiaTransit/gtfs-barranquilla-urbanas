# Betere controle van haltepassages bij terugkerende buswegtrajecten

Alle routegeometrieën en stop_ID's komen uit bestaande SIU/KMZ-data plus de al berekende GraphHopper-busroutes.
Een nearest-point projectie kan de verkeerde passage op een rondgaande weg kiezen. Daarom vergelijken
we alle dichtbijliggende wegpassages en verkiezen een globale volgorde met een sterke straf voor achteruitlopen.
Alle keuzes blijven voorlopige geografiebeoordelingen: geen hernummering, geen bewijs van haltebediening.

## Resultaten

- full_route_patterns_audited: **70**
- graphhopper_road_segments_reused_without_new_queries: **352**
- physical_SIU_stop_visits_preserved: **9020**
- old_nearest_projection_backtrack_signals: **139**
- refined_unresolved_backwards_signals: **49**
- old_backtrack_signals_resolved_or_softened: **113**
- stops_with_multiple_graphhopper_road_passages: **4927**
- road_order_compatible_tentative: **7842**
- route_patterns_needing_priority_1_review: **43**
- stop_review_point_features: **1178**
- unresolved_stop_order_point_features: **49**
- GH_bus_road_mismatch_sections_geojson: **21**
- graphhopper_new_queries: **0**
- SIU_stops_created_or_removed: **0**

## Classificaties

- multiple_road_passages_order_resolved_tentative: 4570
- no_GH_bus_road_pass_within_75m: 554
- road_order_backwards_unresolved: 49
- road_order_compatible_tentative: 3272
- road_route_deviates_from_KMZ_review: 398
- stop_45_to_75m_from_GH_road: 177

## Volgende geometrische controles

1. Beoordeel GH-buswegcorridors die afwijken van de originele AMB-KMZ; maak geen automatische concessieroutecorrecties.
2. Beoordeel onopgeloste achteruitlopende stopprojecties op echte keerpunten, eenrichtingswegen en kruisingen.
3. Beoordeel haltes boven 45 meter van de GH-busweg en bronroute (netwerk-/stopspecifiek), niet blind verwijderen.
4. Zodra routegeometrie en haltevolgorde betrouwbaar genoeg zijn, kunnen reisduur en tripgrenzen apart komen.

## Kaartbestanden voor broncontrole

- GH_unresolved_stop_location_issues_REVIEW.geojson: alle haltebezoeken met nog onopgeloste weg-/volgordeafwijking.
- GH_unresolved_stop_order_49_points.geojson: haltepunten waarbij de volgorde ook na mogelijke alternatieve wegpassages achteruitloopt.
- GH_road_segments_differing_from_KMZ_REVIEW.geojson: buswegsegmenten die nog onvoldoende met het brontraject overeenstemmen.

Bron: GraphHopper bus 11.1 via private organisatievariabele; publieke API: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md
Geen OSM-query's, nieuwe GraphHopper-query's of productie-GTFS-wijzigingen.
