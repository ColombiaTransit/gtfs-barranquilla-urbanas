# AMB GTFS headway staging — preliminary, NOT a GTFS ZIP

- routes_in_routes_txt: **97**
- routes_ready_to_stage: **74**
- routes_held_for_review: **23**
- staged_weekday_periods: **328**
- source_records_considered: **138**

## Reasons routes were held

- conflicting_official_extractions: 2
- historic_last_dispatch_invalid: 5
- historic_window_not_found: 8
- missing_headway_source: 3
- permanent_backup_pending_pilot_expiry_check: 1
- pilot_A_B_not_in_routes_txt: 1
- pilot_SIU_to_legal_AB_mapping_unresolved: 4

No stops.txt, trips.txt, stop_times.txt or route geometry was invented.
The 2020 first/last departures are a reversible model assumption and
the official applicable AMB resolutions determine the headways.
frequencies.txt.end_time is exclusive while last despacho on the posters is inclusive;
the staging boundaries must be translated carefully after stop_times templates exist.
