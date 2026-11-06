# GTFS Barranquilla Urbanas

Research repository for a **static GTFS feed for traditional collective bus transport (TPC)** in the Barranquilla metropolitan area, Colombia. **This is not the Transmetro GTFS feed.**

> **Canonical register policy (November 5, 2026):** [Canonical register architecture](docs/canonical_register_architecture.md) governs the build. The generator reads service frequencies and dispatch windows exclusively from `build/registries/route_service.csv`, produced during the workflow. Historical staging and source files provide evidence and quality assurance, not alternative operational inputs.

## Current research status

**Research-grade GTFS model — not yet verified for public release.** Figures below are from the most recent confirmed successful build, [run 42166319999](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42166319999), before subsequent changes were revalidated.

| Item | Last confirmed result |
|---|---|
| Registered routes / variants | 97 |
| Generated routes | 73 (23 SIU stop-sequence routes; 50 KMZ-based continuous-boarding routes) |
| Missing routes | 24 (13 dispatch-window/service holds, 9 geometry mappings, 2 invalid or multipart geometries) |
| Generated stops | 2,781 |
| Generated trips | 146, including holiday templates |
| MobilityData GTFS Validator | 0 errors; warnings remain under review |

Recent unverified changes include provisional 05:00–21:00 dispatch windows for 13 selected routes, display-name normalization for stops, and moving B11-B-4192 and C4-4135 to KMZ-based continuous boarding. **Do not treat these changes as validated until the next workflow report is reviewed.**

## Modelling and source policies

- Official AMB resolutions are the primary evidence for authorized peak and off-peak headways. Operational service is not independently verified.
- Missing or invalid dispatch windows for 13 explicitly selected routes may use a **provisional** 05:00–21:00 model; original source values are preserved.
- No reliable weekday-versus-weekend headway breakdown is currently available. The daily and holiday schedule assumptions are provisional.
- Official KMZ geometry is preferred. Do not automatically assign a base-route KMZ to unresolved A/B variants.
- **SIU routes with verified stop order and coordinates can be generated without a shape.** Leave `shape_id` empty and do not enable continuous pickup/drop-off.
- **KMZ-only routes** may use continuous boarding along a valid, correctly matched shape, with explicitly documented modelled travel times.
- Routes lacking both usable SIU stop sequences and valid variant geometry remain excluded pending source review.
- Preserve raw source evidence and provenance. Do not invent stop coordinates, official schedules, or variant directions.

## Build and validation

Run [Build GTFS v2 with Flex and GTFS-RT contract](.github/workflows/build-gtfs-v2.yml) from GitHub Actions. The workflow refreshes the KMZ manifest, consolidates route service inputs, builds the research GTFS feed, runs the MobilityData validator, and uploads QA artifacts.

The generated feed is **not automatically approved for publication**. Review `build/gtfs-v2/first_version_route_coverage.csv`, `first_version_missing_routes.csv`, `first_version_summary.json`, and the validator report from the workflow artifact.

## Documentation and source registers

- [Canonical register architecture](docs/canonical_register_architecture.md)
- [GTFS v2 generator design](docs/gtfs-generator-v2-design-2026-11-05.md)
- [Geometry validator review and deferred shape work](docs/validator_geometry_review_2026-11-06.md)
- [Closure of legal/source research phase](docs/amb_research_phase_closure_2026-11-04.md)
- [Source register](docs/bronregister.md)
- [SIU route and stop research](docs/siu_sibus_mht_route_stop_analysis_2026-11-03.md)
- [Stop data inventory](docs/stop_data_inventory_2026-11-03.md)
- [Operator and resolution research](docs/amb_bedrijven/README.md)

Official AMB transport source: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/

## Documentation language

**English is the required language for public-facing documentation, including the README, research notes, QA summaries, and workflow descriptions.** Preserve Spanish names of operators, routes, legal acts, and original quoted source material. Technical GTFS fields, file paths, identifiers, and source records must not be translated. Historical documentation is being migrated; some archived research notes may still contain Dutch text.
