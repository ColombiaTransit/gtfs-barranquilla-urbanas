# Barranquilla GTFS proefbuild — uitsluitend schema/shape-validatie

**WAARSCHUWING: FICTIONELE RITTEN EN TIJDEN, NIET PUBLICEREN.**
Elke opgenomen voorlopige KMZ/ArcGIS component heeft één kunstmatige
QA-rit van 07:00, een voorbeeldkalender op werkdagen 9 november–11 december
2026 en een theoretisch reistijdmodel (18 km/h + stop-pauze).
Dit is NIET de AMB-dienstregeling. Richting, begin/eindpunten en stopbediening
zijn NIET uit juridische exploitatiegegevens bevestigd.

## Aantallen

- existing_amb_routes_total: **97**
- source_route_patterns_with_stop_sequences: **70**
- demonstration_patterns_included: **67**
- patterns_excluded_without_real_route_id: **3**
- A_B_variant_route_ids_fixed_using_existing_routes_txt: **10**
- GTFS_agencies: **18**
- GTFS_routes: **59**
- GTFS_stops: **2362**
- GTFS_demo_trips: **67**
- GTFS_demo_stop_times: **8867**
- GTFS_shapes: **67**
- GTFS_shape_points: **45818**
- GH_road_segments_total_available: **352**
- GH_road_aligned_segments_total_available: **331**
- GH_unresolved_segment_count_total_available: **21**
- source_GTFS_visit_count: **9020**
- excluded_visitor_count_due_to_missing_route_id: **153**
- synthetic_cruise_speed_km_h: **18.0**
- synthetic_minimum_leg_seconds: **30**
- synthetic_dwell_seconds: **20**

## Technische methode

- shapes.txt: wegenvolgende GH-buswegsegementen in KMZ-volgorde; 21 bronafwijkingen blijven gemarkeerd.
- stop_times.shape_dist_traveled: bron-KMZ-afgelegde afstand lineair omgerekend binnen het overeenkomstige GH-routedeel; uitsluitend voor testconsistente referenties.
- Werkelijke route_id: exacte combinatie agency_id en route_short_name uit bestaande gtfs/routes.txt; geen nieuwe fictieve routes.
- COOLITORAL PT2 niet opgenomen omdat de bestaande gtfs/routes.txt geen overeenkomende officiële route_id heeft.
- Onbevestigde SIU-haltebediening en bron-A/B-routeprovenance blijven QA-risico.
- De GTFS ZIP is uitsluitend een GitHub Actions artifact, niet een publicatiefeed.

## Validator

MobilityData GTFS Schedule validator CLI 8.0.1 (https://github.com/MobilityData/gtfs-validator).
De HTML/JSON-validatorrapporten worden bij de proefbuild als artifacts opgeslagen.
