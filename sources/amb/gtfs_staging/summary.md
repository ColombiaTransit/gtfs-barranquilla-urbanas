# AMB GTFS headway staging — preliminary, NOT a GTFS ZIP

- routes_in_routes_txt: **97**
- routes_ready_to_stage: **45**
- routes_held_for_review: **52**
- staged_weekday_periods: **175**
- source_records_considered: **127**

## Reasons routes were held

- conflicting_official_extractions: 2
- historic_last_dispatch_invalid: 5
- historic_window_not_found: 8
- legal_effective_period_and_operational_activation_unverified: 12
- missing_headway_source: 7
- official_interval_missing: 3
- permanent_backup_pending_pilot_expiry_check: 1
- pilot_A_B_not_in_routes_txt: 1
- route_variant_scope_and_legal_effect_unverified: 16
- variant_headway_not_documented: 6

No stops.txt, trips.txt, stop_times.txt or route geometry was invented.
The 2020 first/last departures are a reversible model assumption and
the official applicable AMB resolutions determine the headways.
frequencies.txt.end_time is exclusive while last despacho on the posters is inclusive;
the staging boundaries must be translated carefully after stop_times templates exist.
