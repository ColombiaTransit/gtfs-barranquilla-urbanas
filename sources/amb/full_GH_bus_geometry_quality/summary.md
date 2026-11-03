# AMB routegeometrie en haltevolgorde langs GraphHopper bus-wegennet

GraphHopper wordt uitsluitend via ColombiaTransit GRAPHHOPPER_URL benaderd; de privé-URL staat niet in deze uitvoer.
Officiële AMB-KMZ is de uitgangsroute; historisch ArcGIS blijft expliciet als onbevestigde fallback.
De route is opgedeeld in opeenvolgende delen met KMZ-tussenpunten, zodat GH niet eenvoudig de busroute inkort.
Elke route-passagescore vergelijkt **beide richtingen van de geometrieafstand** (bron→busweg en busweg→bron).
SIU stop_ID en bronvolgorde blijven identiek; iedere passage wordt alleen op het passende routedeel beoordeeld.

## Resultaten

- patterns_selected: **70**
- total_v3_patterns_available: **70**
- GH_segment_route_requests: **352**
- GH_sequential_sections: **352**
- GH_segments_succeeded: **352**
- GH_road_segments_with_source_alignment: **310**
- candidate_road_shapes_geojson_features: **352**
- v3_source_stop_visits_audited: **9020**
- GH_stops_over_45m_from_bus_road: **852**
- GH_stop_order_backwards_over_120m: **144**
- new_stop_ids_created: **0**
- times_generated: **0**
- OSM_Overpass_queries: **0**

## Belangrijk

- GraphHopper maakt een bus-berijdbare kandidaat-shape; niet automatisch het werkelijk gereden concessietraject.
- De segmenten blijven afzonderlijk opgeslagen. Bij terugkerende routes en rondritten wordt niet op een volledige zelf-overlappende lijn geprojecteerd.
- Voor zover GH-segment en KMZ niet overeenstemmen, blijven officiële brongeometrie en stopvolgorde de onbevestigde referentie; geen overschrijven.
- Bus haltebediening, triprichtingen en keerpunten zijn niet geverifieerd. Geen aankomst- of vertrektijden.

## Onderzoeksbestanden

- GH_full_route_bus_segment_alignment.csv — alle GH-bussegmenten versus KMZ, met afwijkingen.
- GH_stop_sequence_and_road_access_audit.csv — elke SIU-stoppassage gekoppeld aan eigen bron- en GH-routedeel, plus lokale volgordecontrole.
- GH_route_pattern_quality_register.csv — controleoverzicht per bronroutedeel / concept-patroon.
- GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson — wegenvolgende geometrie om tegen de AMB-KMZ te leggen.

Geen nieuwe fysieke stops, geen hernummering, geen publicatie-GTFS gewijzigd.
