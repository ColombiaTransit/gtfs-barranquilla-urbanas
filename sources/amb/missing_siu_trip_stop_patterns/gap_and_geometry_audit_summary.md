# AMB: grote haltegaten en gefragmenteerde lijngeometrie

Bron: 60 ontbrekende SIU-routevarianten, officiële KMZ en expliciete historische ArcGIS-fallback.
**Een lange halteafstand bewijst géén ontbrekende halte.** Er kan een snelwegtraject zijn.
Een nabije SIU-halte op een andere route bewijst bovendien niet dat de nieuwe lijn daar stopt.

## Samenvatting

- source_route_variants: **60**
- route_variants_with_geometric_stop_gaps_over_2km: **39**
- individual_stop_sequence_gaps_over_2km: **73**
- possible_nearby_SIU_candidates_for_review: **111**
- routes_with_geometry_edges_longer_than_800m: **25**
- geometry_edges_longer_than_800m: **59**
- route_variants_with_multiple_shape_components: **3**
- component_near_endpoint_pairs_within_80m: **9**
- new_boarding_stops_or_stop_times_generated: **0**
- existing_trip_stop_orders_modified: **False**
- autoroute_component_stitching_performed: **False**

## Classificatie van gaten

- no_source_SIU_stop_on_this_corridor: 38
- nearby_existing_SIU_stops_outside_25m_limit: 18
- only_opposite_direction_source_stops_nearby: 17

## Gefragmenteerde routes

- COOLITORAL A4-4109: 6 componenten, 3 kandidaat-eindpuntverbindingen binnen 80 m; NIET automatisch samengevoegd
- COOLITORAL PT2-4102: 4 componenten, 1 kandidaat-eindpuntverbindingen binnen 80 m; NIET automatisch samengevoegd
- LOLAYA D8-4165: 7 componenten, 5 kandidaat-eindpuntverbindingen binnen 80 m; NIET automatisch samengevoegd

## Volgende controles

1. Loop P1-routes na met KMZ/ArcGIS en officiële straattracés; controleer of lange lijnen echte doorgaande wegdelen zijn.
2. Beoordeel bestaande SIU-haltes binnen grote gaten inclusief rijrichting; voeg deze niet zonder aanvullend bewijs automatisch toe.
3. Bij gefragmenteerde shapes: inspecteer eventuele eindpuntverbindingen en de volgorde; verbind alleen met bronbewijs.
4. Pas nadat route-trips en instapplaatsen gevalideerd zijn, GraphHopper voor reistijden gebruiken. Geen tijden berekend.
