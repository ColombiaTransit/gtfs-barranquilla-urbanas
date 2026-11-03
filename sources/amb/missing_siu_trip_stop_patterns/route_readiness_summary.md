# Routevarianten versus lijnstukken: QA vóór echte GTFS-trips

Een losse KML/ArcGIS LineString is niet automatisch één operationele busrit. De bestaande geprojecteerde haltevolgorde is een **kandidaat**; fysieke halte-ID's blijven over routes heen gedeeld.

- route_variants_with_geometry: **60**
- single_component_route_variants: **57**
- multiple_component_route_variants: **3**
- extremely_fragmented_route_variants_10plus_parts: **0**
- route_variants_with_5plus_stop_candidates_in_a_component: **60**
- route_variants_with_gaps_over_2km: **39**
- ordered_stop_visits_prepared_for_future_GraphHopper: **9000**
- source_SIU_physical_stop_ids_reused: **2368**
- new_physical_stop_ids_created: **0**

De waypoint-staging bevat lege tijden voor latere GraphHopper-berekening. Zonder gevalideerde haltebediening en richting is dit geen publiceerbare stop_times-indeling.

### Bestanden

- route_variant_mapping_readiness_60.csv: alle routes, bronnen, afwijkingen, selectie- en geometriecontroles
- graphhopper_waypoint_staging_NO_TIMES.csv: geordende bestaande SIU-stops inclusief coördinaten en lege tijden
