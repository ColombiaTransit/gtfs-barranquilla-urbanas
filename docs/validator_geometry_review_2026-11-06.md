# MobilityData geometry review — 2026-11-06

Source: [GTFS v2 run 42166319999](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42166319999), validator 8.0.1, `gtfs-v2/validator-report/report.json`. This is a triage register, **not** a confirmation that the warnings are resolved.

The report contains 64 `stop_too_far_from_shape` notices and 4 `stops_match_shape_out_of_order` notices across 9 routes. The full report contains all 68 samples.

| GTFS route_short_name | Distance notices | Order notices | Initial finding | Status |
|---|---:|---:|---|---|
| B11-B-4192 | 44 | 0 | Stops 235–1996 m from KMZ; investigate wrong direction/variant or shape mapping before moving stops | needs_source_review |
| C4-4135 | 17 | 0 | Stops 112–417 m from KMZ; inspect SIU stop sequence versus official KMZ | needs_source_review |
| D7-4151 | 1 | 0 | Villa de Andalucia 146 m from shape | needs_source_review |
| B9-4125 | 1 | 0 | Calle 56 con Carrera 32 138 m from shape | needs_source_review |
| A16-4161 B | 1 | 0 | Carrera 22 con Calle 35 144 m from shape | needs_source_review |
| A7-4112 | 0 | 1 | Conjunto Tortola / CC Jardin del Rio order conflict | needs_source_review |
| B14-4174 | 0 | 1 | Carrera 30 con Calle 143B / Calle 143D con Carrera 29B order conflict | needs_source_review |
| B13-4128 | 0 | 1 | Calle 143D con Carrera 29B and adjacent stop order conflict | needs_source_review |
| C21-4182 B | 0 | 1 | Carrera 44 con Calle 84 order conflict | needs_source_review |

## Handling rules

1. Preserve official KMZ-first shapes; do not rebuild them with GraphHopper merely to silence validator warnings.
2. Compare each SIU itinerary UUID, stop sequence, route variant, official KMZ manifest entry and directional geometry; first check whether a wrong variant or SIU crosswalk was selected.
3. Distinguish wrong KMZ association, legitimate stop outside shape, wrong SIU stop coordinates and stop order errors; only change a mapping when supported by source evidence.
4. For order warnings, compare the complete original SIU stop occurrence sequence with monotonic progress along the matched KMZ, allowing loops/repeated geometry.
5. Record route_id, trip_id, stop_id, source evidence, proposed correction, review status and validation outcome in a canonical audit, rather than introducing a competing route register.
6. Re-run the GTFS generator and MobilityData validator; close a route only when warnings are resolved or documented as source-supported exceptions.

**Priority:** B11-B-4192 (44), C4-4135 (17), then the 3 single-distance routes, then 4 order warnings. No geometry or stop data were changed by this review document.
