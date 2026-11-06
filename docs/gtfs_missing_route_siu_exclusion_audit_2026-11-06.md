# GTFS v2 missing-route SIU exclusion audit — November 6, 2026

## Scope and source

This audit compares **only** the 12 routes missing from [workflow run 42175792211](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42175792211), artifact `gtfs-v2-flex-rt-contract`, file `gtfs-v2/first_version_missing_routes.csv`, against the existing SIU mapping decisions and crosswalk. It does **not** reopen shape refinement or propose speculative A/B mapping.

Sources: `sources/siu/open_route_review/siu_amb_crosswalk_visual_decisions_2026-11-05.csv`, `sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv`, and generated `gtfs-v2/siu_amb_operational_crosswalk_research.csv` and `first_version_held.csv` from the same workflow artifact.

## Route-by-route findings

| Missing GTFS route | Build reason | Existing SIU evidence | Exclusion review |
|---|---|---|---|
| `AMB_COOTRAB_C5_4136` | `flex_missing_or_ambiguous_official_kmz` | LAS PALMAS (159 stop occurrences) was provisionally mapped to C5-4135, whereas the legal/code review retains a C5-4136 conflict | **Keep excluded** pending an explicit route-code reconciliation; do not silently reinterpret C5-4135 as C5-4136 |
| `AMB_COOCHOFAL_C2_B_4188` | `flex_missing_or_ambiguous_official_kmz` | No accepted unique SIU itinerary for this variant | **Keep excluded** |
| `AMB_COOLITORAL_A4_4109` | `flex_invalid_or_multipart_kmz` | No accepted unique SIU mapping in reviewed operational crosswalk | **Keep excluded** pending source-supported geometry or SIU match |
| `AMB_COOLITORAL_PT2_4102_A` | `flex_missing_or_ambiguous_official_kmz` | No accepted SIU mapping to variant A | **Keep excluded** |
| `AMB_COOLITORAL_PT2_4102_B` | `flex_missing_or_ambiguous_official_kmz` | No accepted SIU mapping to variant B | **Keep excluded** |
| `AMB_COOLITORAL_PT3_4103_A` | `flex_missing_or_ambiguous_official_kmz` | VIA 40 MURILLO, 211 stop occurrences, supports PT3 base route but not A/B assignment | **Keep excluded** until A/B evidence is available |
| `AMB_COOLITORAL_PT3_4103_B` | `flex_missing_or_ambiguous_official_kmz` | Same SIU base itinerary; do not duplicate it across both variants | **Keep excluded** |
| `AMB_COOLITORAL_PT4_4104_A` | `flex_missing_or_ambiguous_official_kmz` | CIRCUNVALAR VIA 40 (132 stops) and VIA 40 CIRCUNVALAR (124 stops) have conflicting PT4/PT5 base-route evidence; A/B unresolved | **Keep excluded** |
| `AMB_COOLITORAL_PT4_4104_B` | `flex_missing_or_ambiguous_official_kmz` | Same unresolved base and variant crosswalk | **Keep excluded** |
| `AMB_COOLITORAL_PT5_4105_A` | `flex_missing_or_ambiguous_official_kmz` | Same unresolved base and variant crosswalk | **Keep excluded** |
| `AMB_COOLITORAL_PT5_4105_B` | `flex_missing_or_ambiguous_official_kmz` | Same unresolved base and variant crosswalk | **Keep excluded** |
| `AMB_LOLAYA_D8_4165` | `flex_invalid_or_multipart_kmz` | No accepted unique SIU mapping in reviewed operational crosswalk | **Keep excluded** pending source-supported geometry or SIU match |

## Conclusion

**All 12 exclusions are consistent with the currently approved SIU crosswalk.** This is a review of current evidence, not proof that these services do not operate. In particular, PT3/PT4/PT5 have real SIU stop sequences, but assigning those sequences to specific licensed A/B route IDs is unresolved.

The existing generator policy is correct: a **uniquely matched** SIU itinerary may be generated without `shape_id`; KMZ absence alone is not a blocker. That policy does not authorize guessing variant identities or duplicating an SIU trip into multiple A/B routes.

The build's `first_version_held.csv` also includes nine SIU mapping/review entries in addition to the 12 missing route entries. These are not 21 additional missing GTFS routes; the scopes differ.

**Action:** no generator, shape, or SIU mapping change is justified by this audit. Revisit only the specific crosswalks when positive source evidence appears.
