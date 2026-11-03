# Concepthaltevolgordes uitgebreid met 65 bestaande SIU-haltes

Onderzoeksstaging; niet publiceren als GTFS. De nieuwe stop_sequence is per bestaand geometrisch trip-patroon hernummerd na het invoegen van 65 GraphHopper-toevoegkandidaten precies tussen hun bestaande SIU-ankers.
Alle oorspronkelijke haltebezoeken blijven in dezelfde volgorde.
Een halte mag op meerdere trips of meerdere passages van een rondrit voorkomen.

## Aantallen

- original_existing_stop_visits: **9000**
- GH_add_candidates_inserted_in_concept: **65**
- concept_stop_visits: **9065**
- existing_trip_pattern_components: **70**
- route_variants_in_concept: **60**
- trip_pattern_components_with_additions: **19**
- route_variants_with_additions: **19**
- unique_existing_physical_SIU_stop_ids_reused: **2372**
- original_gaps_over_2km: **73**
- remaining_concept_gaps_over_2km: **57**
- close_pairs_under_60m_around_new_candidates: **7**
- new_physical_stops_created: **0**
- travel_times_generated: **0**

## Onderzoek en beperkingen

- Alle nieuwe rijen zijn bestaande fysieke SIU-stop_ID's, niet haltes per route.
- De GH-status bewijst geen daadwerkelijke stopbediening of officiële rijrichting.
- De geordende rijen verwijzen naar KMZ/ArcGIS-componenten; één component is niet altijd één echte trip.
- Bij twee haltepunten binnen 60 meter langs het traject blijft de mogelijke doublure behouden maar gemarkeerd.
- Arrival en departure blijven leeg, voor GraphHopper-rijtijdverwerking op een later moment.
- Geen source-bestanden of productiebestanden onder gtfs/ aangepast.

## Bestanden

- concept_trip_stop_order_ALL_NO_TIMES.csv: alle 9.065 haltepassages inclusief metadata.
- concept_stop_times_RESEARCH_NO_TIMES.csv: GTFS-achtig concept, nadrukkelijk zonder tijden.
- GH_65_insertions_with_new_sequences.csv: exacte nieuwe positie en twee omliggende oorspronkelijke stop-ID's.
- route_variant_coverage.csv: resultaten per officiële routevariant.
- remaining_gaps_over_2km_CONCEPT.csv: resterende geografische gaten.
- close_stop_pairs_after_insertion_REVIEW.csv: korte onderlinge afstanden die aparte controle vragen.
