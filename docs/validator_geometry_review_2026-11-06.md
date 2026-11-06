# MobilityData geometry review — 2026-11-06

Source: [GTFS v2 run 42166319999](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42166319999), validator 8.0.1, `gtfs-v2/validator-report/report.json`. This is a triage register, **not** a confirmation that the warnings are resolved.

The report contains 64 `stop_too_far_from_shape` notices and 4 `stops_match_shape_out_of_order` notices across 9 routes. The full report contains all 68 samples.

| GTFS route_short_name | Distance notices | Order notices | Initial finding | Status |
|---|---:|---:|---|---|
| B11-B-4192 | 44 | 0 | Stops 235–1996 m from KMZ; investigate wrong direction/variant or shape mapping before moving stops | needs_source_review |
| C4-4135 | 17 | 0 | Stops 112–417 m from KMZ; inspect SIU stop sequence versus official KMZ | needs_source_review |
| D7-4151 | 1 | 0 | Villa de Andalucia 146 m from shape | deferred_minor_distance |
| B9-4125 | 1 | 0 | Calle 56 con Carrera 32 138 m from shape | deferred_minor_distance |
| A16-4161 B | 1 | 0 | Carrera 22 con Calle 35 144 m from shape | deferred_minor_distance |
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

**Current decision (2026-11-06):** B11-B-4192 and C4-4135 have been excluded from SIU-to-KMZ matching in generator commit `2e7664cfb34bf825f277bb7ed147af61c5d7a9d0` and will be built as KMZ Flex routes; rerun validation pending. The three remaining single-stop distance warnings (138–146 m) are deliberately **deferred** to a later review, not corrected or closed. Keep their stop coordinates and KMZ geometry unchanged. **Next active priority:** the four stop-order warnings. This document is the worklist; no competing register is introduced.

## Detailed stop-order investigation (2026-11-06)

Evidence: MobilityData 8.0.1 `stops_match_shape_out_of_order` samples and `gtfs-first-version.zip` from run 42166319999. Sequence numbers below are the actual SIU trip `stop_sequence` (not the validator's CSV row numbers).

| Route | SIU trip_id | First stop in GTFS order | Next stop in GTFS order | Evidence / disposition |
|---|---|---|---|---|
| A7-4112 | `SIU_3ef82d0c83c4627e` | #55 CC JARDIN DEL RIO (CALLE 114) | #56 CONJUNTO TORTOLA (CALLE 114) | Validator finds #56 earlier on the KMZ shape than #55. Review the local Calle 114 direction and loops; **no automatic swap**. |
| B14-4174 | `SIU_945609c6696a63a7` | #3 CALLE 143D CON CARRERA 29B (SN) | #4 CARRERA 30 CON CALLE 143B (OE) | Validator finds #4 earlier than #3. Review shared Carrera 28–30 / Calle 143D circuit with B13; **no automatic swap**. |
| B13-4128 | `SIU_8e5e5a0b4aa613af` | #2 CARRERA 28 CON CALLE 143D (EO) | #3 CALLE 143D CON CARRERA 29B (SN) | Validator finds #3 earlier than #2. Same SIU stop IDs and nearby sequence as B14; check common loop and direction once for both routes. |
| C21-4182 B | `SIU_b45398378e9e743b` | #135 EDIFICIO VERONA (CARRERA 44 - OE) | #136 CARRERA 44 CON CALLE 84 (OE) | Very close neighboring stops; validator finds #136 earlier on the KMZ. Check road side and projection ambiguity; **no automatic swap**. |

### Review result and next decision

- **Confirmed:** four warnings are reproducible in generated trip sequences; two belong to a shared geographic cluster (B13/B14). No evidence yet that the original SIU ordering is wrong.
- **Not confirmed:** whether KMZ travel direction, loop/repeated segment, nearest-shape projection or SIU stop order causes each warning. Do not call these resolved.
- **Next source review:** compare the relevant KMZ LineString around each flagged stop pair with SIU stop occurrences and direction, including adjacent stops; record whether the shape revisits a segment. Only change source mapping or stop order with positive source evidence.
- **Scope:** no KMZ shapes, SIU source records or generator output modified in this investigation. The three small distance warnings remain deferred.

## User visual review of OSM/KMZ overlay (2026-11-06)

The user inspected the four flagged pairs in the interactive OSM/KMZ/SIU viewer and reported:

- **A7-4112, B13-4128, B14-4174:** the **KMZ geometry/direction appears wrong**, not the SIU stop sequence. Classification: `suspected_kmz_geometry_or_direction`. Preserve SIU stop order and existing KMZ until checked against original official KMZ and surrounding road direction. Do not swap stops or silently reverse a whole shape.
- **C21-4182 B:** the **KMZ appears correct**, while the SIU #135 → #136 order is suspect. Classification: `suspected_siu_stop_order`. Verify KMZ vertex direction and adjacent #134/#137 before changing stop occurrences, including any shared stop IDs/trips.

This is a user visual assessment, not yet a validated source correction. Re-run MobilityData after evidence-based changes.

## Closure decision: defer all four stop-order warnings (2026-11-06)

User decision: **park the four `stops_match_shape_out_of_order` warnings** for A7-4112, B14-4174, B13-4128 and C21-4182 B. No better official KMZ route shapes are available. These are MobilityData **warnings, not errors**, and do not block continued GTFS generation.

Status for all four: `deferred_source_limit`. Preserve existing KMZ-first geometry and SIU stop sequence; do not reroute with GraphHopper, swap stop order or reverse geometry solely to eliminate warnings. The user's visual hypotheses from the preceding section remain recorded as unverified. Reopen only if a better authoritative geometry, SIU source correction or other concrete contradictory evidence becomes available.

The three minor stop-distance warnings remain `deferred_minor_distance`. Continue with GTFS route coverage and remaining source blockers rather than further geometry refinement.
