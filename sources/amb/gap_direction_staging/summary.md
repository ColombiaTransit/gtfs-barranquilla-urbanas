# Onderzoek bestaande SIU- en OSM-data voor latere GraphHopper-richtingstoets

**Geen nieuwe Overpass-queries. Geen GTFS-wijzigingen.**

We hergebruiken de reeds ontvangen OSM-export en alle in de GIS/KMZ-analyse afgewezen SIU-haltes. Dezelfde fysieke SIU-stop-ID's worden hergebruikt; een OSM-punt dicht bij een SIU-halte krijgt hooguit een voorlopige verwijzing naar die bestaande ID, geen nieuwe halte.

De rijrichting uit een haltebenaming of een KMZ-lijntangent is geen controle van eenrichtingswegen. Juist de eerder als tegenovergesteld gemarkeerde stops worden voor GraphHopper bewaard.

## Resultaten

- overpass_queries_made: **0**
- input_OSM_boarding_candidate_count: **34**
- long_shape_stop_gaps_considered: **73**
- gaps_without_original_SIU_candidates: **38**
- all_original_SIU_direction_alternatives_preserved: **111**
- original_OSM_source_to_route_gap_candidate_links: **14**
- OSM_links_without_nearby_existing_physical_SIU_stop_id: **14**
- gaps_with_at_least_one_candidate: **44**
- total_future_GraphHopper_direction_review_candidates: **125**
- original_SIU_candidates_with_earlier_opposite_direction_assessment: **80**
- new_GTFS_stop_ids_created: **0**

## Vervolg

1. Laat GraphHopper later voor de geplande route in beide richtingen de feitelijke toegestane rijbaan en bochten bepalen.
2. Vergelijk elke haltekandidaat met motorvoertuig-routing langs de shape en de toegankelijke straatkant.
3. Voeg pas na die toets en aanvullende route-/haltebedieningsvalidatie wijzigingen aan de trip-haltevolgorde toe.
4. Houd OSM-ODbL-attributie en SIU-bronvermelding gescheiden.
