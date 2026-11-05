# Canonical registers and GTFS build contract (2026-11-05)

## Decision
One operational read model per data domain. Research sources remain immutable evidence, **not** alternative GTFS inputs. Never reopen closed legal findings without contradictory evidence.

| Domain | Canonical operational input | Provenance and historical evidence |
|---|---|---|
| Route identities / operators | `gtfs/routes.txt` and `gtfs/agency.txt` (stable route_id) | AMB resolutions, SIU mapping reviews |
| Frequency and dispatch window | **`build/registries/route_service.csv`** | `sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv`, `sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv`, legal closure notes |
| Shapes | Reviewed official KMZ manifest / crosswalk | `sources/amb/kmz/`, reviewed geometry decisions |
| Stops and ordered visits | SIU GTFS staging until fully promoted | SIU raw exports, stop aliases, name corrections |
| Flex and realtime contract | Reviewed GTFS v2 registry | `sources/amb/gtfs_v2/` |

## Frequency and dispatch contract
`scripts/build_gtfs_frequency_staging.py` translates source evidence and explicitly provisional dispatch assumptions into staging candidates. `scripts/consolidate_gtfs_frequencies.py` is the **only** writer of the operational route-service read model. It preserves source_file, official_resolution, first_dispatch_model, last_dispatch_model, headways, blockers, and consolidation_status; it adds `operational_status` (ready/held).

`scripts/build_gtfs_first_version.py` must read **only** `build/registries/route_service.csv` for frequency and dispatch. Both SIU and continuous-boarding/Flex branches reject held entries. Do not read the older `build/gtfs-v2/consolidated_route_headways.csv` as an alternative. That file remains a compatibility/audit output only.

A successful consolidation of 97 records is **not** proof that 97 routes are ready: readiness requires valid positive frequency values, an ordered departure window, and no unresolved source conflict. Missing route geometry or stops are separate blockers.

The 21:00 provisional model is explicitly distinct from verified official route-specific service hours. The historical 18:00 source remains available for provenance. Official frequency and legal-precedence decisions must not be silently overridden by a general model.

## Build pipeline
1. Harvest existing official KMZ geometry; reuse accepted geometry, no blanket GraphHopper shape refinement.
2. Stage historical and approved dispatch/frequency evidence.
3. Build research GTFS v2 and realtime contract.
4. Produce canonical route-service register and audit.
5. Generate first-version GTFS from canonical register.
6. Run MobilityData GTFS Validator; upload reports, canonical register and QA artifacts.

## Remaining migration
The current build still contains separate research and first-version GTFS builders. Route, stop, shape and Flex registries have **not yet** been merged into one generator. Their consolidation requires explicit crosswalk/geometry and publication-status checks; do not discard existing evidence. The canonical frequency read-model migration is the first enforced domain. CI and validator success do not imply publication approval.

## Governance
Any new source updates evidence first, then a single canonical model. Every operational value must have a stable route ID, provenance, status and applicable date/period. Historical or superseded data must not silently become active. Add CI tests for uniqueness, coverage, precedence, held statuses and generated GTFS validation before publication.
