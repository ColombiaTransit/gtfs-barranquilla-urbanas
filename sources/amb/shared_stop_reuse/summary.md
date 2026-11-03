# Eén fysiek SIU stop_id voor meerdere route- en trip-kandidaten

Fysieke SIU-stopcatalogus wordt éénmalig gebruikt. Alle verbindingen met de 60 routevariant-KMZ's gebruiken dezelfde oorspronkelijke stop_id. Er wordt GEEN aparte halte per route aangemaakt. OSM-punten zijn hier expres niet aangemaakt als fysieke haltes.

## Tellingen

- physical_SIU_stop_catalog: **3117**
- SIU_source_stop_occurrences: **6407**
- physical_SIU_stops_with_nearby_missing_KMZ_route: **2867**
- SIU_stop_ID_route_candidate_references: **16515**
- SOBUSA_stop_ID_route_candidate_references: **3394**
- unique_physical_SIU_stop_ids_near_SOBUSA: **1123**
- source_OSM_proximity_entries_skipped_no_new_physical_ID: **108**
- new_physical_stops_created: **0**
- automatic_new_route_stop_service_approved: **0**

**Belangrijk:** dit koppelt bestaande locaties geografisch aan kandidaat-routes. SIU heeft niet vastgelegd dat de kandidaat-route hier stopt. Controleer de juiste straatkant, haltebediening, rijrichting en geordende haltepassages vóór opname in definitieve GTFS stop_times.txt.

Bestanden: shared_physical_SIU_stop_index.csv, missing_route_to_existing_stop_id_candidates.csv, sobusa_route_to_existing_stop_id_candidates.csv.
