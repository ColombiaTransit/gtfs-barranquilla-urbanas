# Nieuwe conceptversie van haltevolgordes (zonder tijden) — GraphHopper 65 toevoegkandidaten

**DIT IS ONDERZOEKSSTAGING; er zijn geen GTFS-bestanden aangepast.**
De 9.000 bestaande route-haltebezoeken blijven behouden, in exact dezelfde relatieve volgorde.
Alle 65 bestaande fysieke SIU-haltes zijn als voorlopige haltepassage tussen de twee oorspronkelijk gekoppelde haltes van hun bron-gat gezet. Een reeds elders in de route genoemde stop_id mag terugkomen bij een andere passage van een rondrit.
Alle 125 GraphHopper-kandidaten blijven apart in de classificatie; alleen de 65 toevoegkandidaten komen in deze nieuwe *conceptversie* voor.

## Resultaten

- existing_route_stop_visits_preserved: **9000**
- new_GH_addition_candidate_visits: **65**
- concept_route_stop_visits_total: **9065**
- unique_existing_SIU_physical_stop_ids_newly_referenced: **50**
- affected_trip_patterns: **19**
- affected_route_variants: **19**
- trip_patterns_with_existing_sequence: **70**
- new_candidates_that_already_occur_elsewhere_in_same_trip: **26**
- adjacent_pairs_with_new_candidate_under_115m_to_review: **13**
- all_original_stop_visit_orders_preserved: **True**
- all_original_physical_stop_ids_preserved: **True**
- new_physical_stop_ids_created: **0**
- trip_timing_calculation_performed: **False**
- source_KMZ_GH_route_stop_service_verified: **False**
- production_GTFS_stops_trips_or_stop_times_changed: **False**
- source_observed_counts_expected: **True**

## Stapsgewijze verificatie

1. Controleer twijfelachtige korte halteafstanden (onder 115 m), dubbele stop_id-passages en bron-A/B-varianten.
2. Verifieer dat de 65 kandidaat-haltes daadwerkelijk door deze buslijn worden bediend; GraphHopper bewijst alleen berijdbaarheid.
3. Bevestig de werkelijke tripgrenzen en keerpunten op basis van originele AMB- en SIU-routegegevens.
4. Zodra de geordende trips zijn gevalideerd, laat GraphHopper afstand en rijtijd per opeenvolgende halte berekenen.
5. Publiceer alleen na brontoetsing in GTFS trips.txt en stop_times.txt; er zijn nu geen arrival/departure tijden.

## Bestanden

- candidate_trip_stop_sequences_v2_NO_TIMES_NOT_GTFS.csv — complete conceptvolgorde per routepatroon.
- new_GH_addition_candidates_65_with_concept_position.csv — precies de nieuw ingevoegde 65 haltepassages.
- trip_pattern_new_stop_counts_QA.csv — voortgang en checks per patroon.
- close_adjacent_stop_visits_REVIEW_ONLY.csv — potentiële nabijheid/dubbele passages voor menselijke beoordeling.
