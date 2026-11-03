# MobilityData GTFS geometriecontrole: vóór en na gerichte GraphHopper-herroutering

**Uitsluitend test-GTFS met synthetische dienstregeling; niet publiceren.**
Echte validator 8.0.1 tweemaal uitgevoerd op afzonderlijke GTFS-test-ZIP's.

## Uitkomsten

- baseline_validation_errors: **0**
- new_validation_errors: **0**
- baseline_warnings_total: **2615**
- new_warnings_total: **2436**
- before_stop_to_shape_over_100m_count: **249**
- after_stop_to_shape_over_100m_count: **67**
- resolved_stop_to_shape_over_100m_warnings: **182**
- before_stop_match_out_of_order_warnings: **4**
- after_stop_match_out_of_order_warnings: **4**
- road_sections_selected_as_improved_candidates: **79**
- validated_reduction_without_new_order_warnings: **True**
- stop_id_or_stop_sequence_modified: **False**
- full_final_real_operator_feed_created: **False**
- fully_publishable: **False**

## Warning-codes

| Code | Ernst | Eerst | Nu | Verschil |
|---|---|---:|---:|---:|
| equal_shape_distance_diff_coordinates_distance_below_threshold | WARNING | 5 | 8 | 3 |
| future_calendar | INFO | 1 | 1 | 0 |
| missing_recommended_file | WARNING | 1 | 1 | 0 |
| mixed_case_recommended_field | WARNING | 2354 | 2354 | 0 |
| stop_has_too_many_matches_for_shape | WARNING | 1 | 1 | 0 |
| stop_too_far_from_shape | WARNING | 249 | 67 | -182 |
| stops_match_shape_out_of_order | WARNING | 4 | 4 | 0 |
| trip_coverage_not_active_for_next7_days | WARNING | 1 | 1 | 0 |

## Onopgeloste routevragen

1. Stopafstanden boven de MobilityData grens van 100m vragen een route- of stopbroncontrole, geen kunstmatige lijn naar halte.
2. Stops match shape out of order kan veroorzaakt worden door hetzelfde wegdeel bij een rondrit; zonder bewijs niet omwisselen.
3. Geen daadwerkelijke haltebediening, keerpunten, echte ritten of dienstregeling vastgesteld.
4. Twee MobilityData HTML/JSON rapporten en beide demonstratie-ZIP's zijn als workflow-artifact beschikbaar.
