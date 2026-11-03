# MobilityData GTFS validator — proefbuild Barranquilla

**Dit rapport hoort bij een demonstratiefeed met fictieve trips, kalender en tijden. Niet publiceren.**

## Feedaantallen

- GTFS_agencies: **18**
- GTFS_routes: **59**
- GTFS_stops: **2362**
- GTFS_demo_trips: **67**
- GTFS_demo_stop_times: **8867**
- GTFS_shapes: **67**
- GTFS_shape_points: **45818**

## Validator 8.0.1

- ERROR notices: **0**
- WARNING notices: **6291**
- INFO notices: **1**

## Meest voorkomende codes

| Severity | Code | Aantal |
|---|---|---:|
| WARNING | stop_too_far_from_shape_using_user_distance | 3676 |
| WARNING | mixed_case_recommended_field | 2354 |
| WARNING | stop_too_far_from_shape | 249 |
| WARNING | equal_shape_distance_diff_coordinates_distance_below_threshold | 5 |
| WARNING | stops_match_shape_out_of_order | 4 |
| WARNING | missing_recommended_file | 1 |
| WARNING | stop_has_too_many_matches_for_shape | 1 |
| WARNING | trip_coverage_not_active_for_next7_days | 1 |
| INFO | future_calendar | 1 |

## Beperkingen

- De proef-ZIP, volledige report.html en report.json staan in het workflow-artifact.
- Een nulscore op validator-ERROR betekent **niet** dat deze routes worden bediend, dat brontrips correct gesplitst zijn of dat de dienstregeling klopt.
- Voor ingebruikname moeten officiële tripgrenzen, frequenties, haltebediening, de 21 geometrische afwijkingen en resterende haltevolgordesignalen worden opgelost.
- Geen productiefeed /gtfs gewijzigd.
