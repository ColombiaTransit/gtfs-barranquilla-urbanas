# Continuous pickup/drop-off policy — Barranquilla urban routes

Status: operator practice confirmed by project user on 2026-11-05 for the urban routes under discussion. **Scope must not be generalized to Transmetro, intermunicipal routes, or other services without evidence.**

## GTFS encoding

- For applicable fixed-route services, use `continuous_pickup=0` and `continuous_drop_off=0` in `routes.txt` (or, if necessary, on specific `stop_times.txt` segments with the GTFS precedence rules).
- This is standard GTFS continuous boarding/alighting along a fixed route, **not** a license to create `locations.geojson` service areas or on-demand service.
- Do not set continuous pickup on unrelated routes until scope is explicitly established.
- Where a route has SIU stops, preserve their ordered stop sequences and apply continuous pickup/drop-off only where operationally allowed.
- Where no SIU stops are available, use the AMB KMZ shape as geometry source, but **do not invent anchor stops**. Reliable terminal or timing points and a viable stop_times/trip model are still required.
- Preserve existing AMB frequency source hierarchy and model assumptions separately from verified timetable data.
- Never duplicate trips for jointly operated identical patterns: keep the established virtual combined-agency policy and operator attribution.
- Exclude route sections where boarding/alighting is prohibited, if such restrictions are subsequently documented.

## Consolidation status

Classify per route/pattern:
- `FIXED_STOPS_CONTINUOUS_ALLOWED`: SIU stops available and boarding between stops permitted.
- `CONTINUOUS_ANCHORS_PENDING`: no SIU stops, official shape available, reliable start/end/timing anchors still missing.
- `CONTINUOUS_READY_FOR_MODEL`: official shape plus supported anchors and service model, pending validator check.
- `SERVICE_DATA_PENDING`: stop/anchor structure available but trip/calendar model missing.
- `SCOPE_NOT_CONFIRMED`: applicability of continuous boarding not established.

**Important:** the user confirmed practice for 'these routes', not an individual exhaustive route-code allowlist. Do not mass-enable all AMB routes without confirming the target set.
