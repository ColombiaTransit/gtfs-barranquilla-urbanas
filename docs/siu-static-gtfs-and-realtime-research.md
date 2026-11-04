# SIU GraphQL: static GTFS source and dynamic GTFS-RT feasibility

## Proven from the supplied production JavaScript (4 November 2026)

Source: `37.4ac577f1.chunk.js` (Webpack module 1455). Companion chunks 2, 7 and 32 contain supporting modules. The public route UI sends:

```graphql
query ServiceMngCompressedItineraryListing($organizationId:String) {
  ServiceMngCompressedItineraryListing(organizationId:$organizationId)
}
```

The response property `compressedModsBase64` is Base64 decoded, zlib inflated and JSON parsed; the UI spreads the decoded array into its React state setter. The existing exporter `scripts/extract_siu_public_itinerary_stops.py` expects an array whose first item is the itinerary array. This is a *verified application decode*, not a guaranteed published API contract.

The same chunk declares:

```graphql
subscription onServiceMngPisScheduleModified($id:ID!) {
  ServiceMngPisScheduleModified(id:$id) {
    id organizationId name description active
    metadata { createdBy createdAt updatedBy updatedAt }
  }
}
```

This is **schedule metadata change notification**, not a trip timetable or realtime arrival subscription. The page explicitly requests `fetchPolicy: "no-cache"`; this does not prove the backend always sends live updates.

## Static completeness

The route records observed by the existing exporter expose identifiers (`id`, `routeId`, `orgId`), names (`n`), company display names (`comps`), `active`, and ordered `stops`. Stop records expose `id`, `n`, `lat`, `lng` and `dis` (distance meaning not yet validated).

The new audit workflow captures the same public GraphQL response using anonymous Chromium, exports the latest itinerary and stop-sequence tables, and reports **field presence** and coordinates. It deliberately does not assert that every licensed AMB route is present: the earlier capture contained 36 itineraries while the legal register has a different scope. Only an explicit crosswalk can establish completeness. No calendar, frequencies, exact trip departure/arrival schedule, shapes or legal route authorizations can be inferred from these UI fields. Official AMB resolutions remain authoritative for documented frequencies; closed legal research stays closed.

Static integration checklist:
1. Match SIU itinerary UUID to reviewed AMB route/variant ID; flag unmatched and test records.
2. Validate stop UUID reuse, coordinate conflicts, order and direction.
3. Use KMZ geometry where present and routed fallback only when documented.
4. Preserve joint operators under the agreed composite agency model; avoid duplicate frequencies.
5. Generate `routes.txt`, `stops.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt` only after each required input is independently sourced. Never turn an ETA into a scheduled stop time.
6. Review SIU redistribution rights before publishing derived datasets.

## Dynamic fields and UI filtering

The route component loops over `item.servs` and their `service.stops`. Observed field names include `id`, `vin`, `vp`, `s`, `ts`, `td`, `itt`, `newETA`, and per-service-stop `id`, `eta`, `realETA`, `dts`.

The UI excludes services when `Date.now()-300000 >= service.stops[0].eta` **and** `!service.ts`. It computes `realETA - (service.newETA||{}).eta`, and a derived `newEta` from `arrivedTimeStamp` plus that difference. For a stop it chooses a minimum remaining `eta` after its own filtering. It applies status-dependent conditions including `READY_TO_START`, `STARTED`, `WAITING_TO_ARRIVE_TO_STARTING_POINT`, and `itt === "C"`. The code uses `Date.now() > newEta + 1800000` in a visibility condition. These are UI behaviors, **not evidence of authoritative ETA semantics**.

Important: `vin` and `vp` are *vehicle-related identifiers/fields in the code*, but exact semantics and stability are unverified. `ts` is used as a truthy flag, not established as a Unix timestamp. `td` and `dis` appear in a distance subtraction; units are not verified. `realETA`, `eta`, `newETA.eta` and `arrivedTimeStamp` require unit/timezone validation against real samples. Do not assume the UI's `eta` is a published GTFS-RT prediction.

## Realtime feasibility and probe design

Run **Actions → Audit SIU static source and probe GTFS-RT potential → Run workflow**. Default: three anonymous snapshots, 60 seconds apart. The workflow reloads the route page, captures only its own GraphQL response, decodes it, and writes:
- `static_itineraries.csv`: latest snapshot route metadata and presence of services.
- `static_route_stop_sequences.csv`: latest ordered stop IDs, names and coordinates.
- `sample_metrics.csv`: aggregate coverage and counts per snapshot.
- `audit.json`: observed field keys, field presence, service status histogram, and coverage.
- `report.md`: human-readable report.

No raw response, VIN, VP, cookies, JWT, individual vehicle trail or exact per-vehicle ETA is stored. This is intentional: first assess whether public response coverage justifies deeper work. If response is unavailable, the action fails rather than generating fake completeness statistics.

GTFS-RT gates:

| Feed type | Minimum remaining evidence |
|---|---|
| TripUpdates | Reliable static `trip_id` or defensible route+start_time+start_date mapping; verified per-stop ETA semantics; valid timestamp units; freshness and coverage |
| VehiclePositions | Actual vehicle lat/lon or supported position source; stable vehicle-to-trip mapping; observed position timestamps and license |
| Alerts | Explicit disruptions/alerts data and their affected entities; none established from this chunk |

Before publishing, measure daytime and nighttime coverage, changes across repeated samples, delay/ETA validity, whether services vanish/reappear, route/stop ID stability, and update latency. **This probe measures aggregate snapshots, not vehicle trajectories**. Realtime data availability can be zero outside operating hours; absence is not proof of an empty source.

## Boundaries

Public web access does not equal an open data license. Respect server rate limits, do not use authentication bypass or inferred private operations, and do not expose vehicle IDs in public artifacts. No GTFS-RT feed is generated until the evidence gates pass.
