# GTFS Barranquilla — brondata consolideren, werkpakket 1 (4 november 2026)

## Doel en status

Dit document legt de **bestaande** bronbestanden, gezaghebbende volgorde en concrete aansluitpunten vast. Het is de eerste consolidatiestap, **geen** claim dat 97 routes al complete en bevestigde ritpatronen hebben. Juridisch onderzoek is administratief afgesloten volgens `docs/amb_research_phase_closure_2026-11-04.md`; brononzekerheden worden bij GTFS als datakwaliteitsvelden bijgehouden, niet opnieuw als algemene juridische onderzoeksopdrachten.

## Bronhiërarchie per GTFS-onderdeel

| GTFS-onderdeel | Primaire bron | Aanvullende bron | Verwerkingsregel |
|---|---|---|---|
| `agency.txt`, `routes.txt` | `gtfs/agency.txt`, `gtfs/routes.txt` | `sources/amb/research_closure_and_gtfs_handoff_2026-11-04.csv` | Bestaande IDs behouden; canonieke aliassen A15-4159, C2-B-4188; gezamenlijke identieke varianten slechts eenmaal modelleren |
| Frequenties | `sources/amb/gtfs_staging/route_headway_candidates.csv` | `sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv`; recentere gecontroleerde resolutieconclusies | Waarden zijn vergund/bronafgeleid, niet automatisch actuele dienstuitvoering; latere vastgelegde resolutie wint waar relevant |
| Haltepunten | `sources/siu/gtfs_staging/candidate_stops.csv` | `sources/siu/public_extract/siu_route_stop_sequences.csv` | SIU-UUID's per vermelding niet gelijkstellen aan unieke fysieke haltes; naam- en richtingconflicten apart houden |
| Haltevolgorde | `sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv` | `sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv` | Alleen voorlopige SIU→AMB matches; geen bevestigde routevariant zonder expliciete koppeling |
| Shapes | `sources/amb/KMZ_first_GH_fallback_validation/source_shape_source_by_pattern.csv` | `sources/amb/KMZ_GH_road_refinement_QA/`; `sources/amb/arcgis_shape_staging/` | Officiële AMB-KMZ eerst; GraphHopper-fallback uitsluitend voor ontbrekende KMZ; alleen validator-veilige verfijningen |
| Vertrekvensters | `sources/amb/gtfs_route_service_windows_assumed_2026-11-03.csv` | `sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv` | AMB 2020-vertrektijden zijn expliciete modelaanname voor 2026, niet actueel geverifieerd |
| Spits/dal | `sources/amb/gtfs_peak_offpeak_period_model_2026-11-03.csv` | `sources/amb/gtfs_staging/weekday_period_staging.csv` | Ma–vr 07–09 en 17–20 modelaanname, geen bewezen officiële spitsdefinitie |
| Ontbrekende data | `sources/amb/gtfs_staging/unresolved_route_issues.csv` | `sources/amb/route_coverage_gaps_2026-11-02.csv` | Herclassificeer als `missing_gtfs_input`, `ambiguous_mapping` of `source_date_limit`; niet automatisch juridische onderzoeksfase heropenen |

## Gecontroleerde broninventaris uit repository

- **23** bestaande agencies, **97** bestaande GTFS-route-/variantregistraties.
- **63/97** routes met voorbereide frequentie-/dienstvensterkandidaten, **34** met open punten volgens bestaande staging.
- **33** reguliere SIU-itineraries, **6.407** geordende haltevermeldingen; **3.117** conservatief samengevoegde halte-kandidaten; **53** naam-/positieconflicten.
- SIU-koppelingen: **12** sterk voorlopige plus **8** extra basisroutevoorstellen; **13** SIU-itineraries nog ambigu volgens het bestaande rapport. Geen van deze aantallen impliceert dat A/B-varianten definitief zijn gekoppeld.
- KMZ-first onderzoeksvalidatie: **59** routes, **67** synthetische trips, **8.867** haltebezoeken, **0** MobilityData-errors, **1** resterende halteafstandwaarschuwing; proeftrips en kalendertijden zijn **niet publiceerbaar**. Latere veilige GH-wegbochtverfijning: **2.378** waarschuwingen, zonder nieuwe haltevolgordefouten.

De hierboven genoemde aantallen zijn **momentopnames uit bestaande rapporten** (3 november); een herberekende volledige integriteitscontrole volgt bij het bouwen van de consolidatiescript-output.

## Concreet eerste aansluitwerk

1. **Sleutelbestand:** alle `gtfs/routes.txt`-regels met exacte `route_id`, `agency_id`, `route_short_name` als leidende lijst gebruiken.
2. **Frequentiejoin:** op `gtfs_route_id` koppelen aan `route_headway_candidates.csv`; ontbrekende of dubbele matches zichtbaar houden, nooit invullen met nul of verzonnen interval.
3. **SIU-crosswalk:** kandidaat `suggested_gtfs_route_id` alleen overnemen waar aanwezig; `final_gtfs_route_mapping_confirmed=no` blijft voorlopig, ook bij sterke GIS-overlap.
4. **Shape-crosswalk:** KMZ-rapport op `official_route_label` plus vervoerder aan basisroute koppelen; één basisroute kan meerdere `trip_pattern_id` hebben. Geen automatische één-op-één toewijzing bij ambigue varianten.
5. **Aannames apart:** historische vertrekvensters, spits/dal en modelkalender niet in bron- of juridische statuskolommen mengen.
6. **Output-QA:** maak één regel per GTFS-route met `headway_status`, `siu_mapping_status`, `shape_status`, `calendar_status`, `gtfs_build_ready`, `reason` en volledige bronpaden.
7. **Bijzondere gevallen:** COOCHOFAL-aliassen niet dupliceren; COOTRAB C5-codeverschil als gerichte route-ID QA; gezamenlijke A1 alleen onder virtuele agency wanneer exact dezelfde variant; COOLITORAL PT4/PT5 pilot einddatum 2026-12-21.

## Beslissingen voor deze fase

**Geen nieuwe algemene juridische OCR/validiteitswerkvoorraad.** We kunnen de beschikbare SIU-haltevolgorde en officiële KMZ-bronnen direct benutten, maar **nog niet** zonder kwaliteitsvlaggen een productie-`stop_times.txt` of echte dienstkalender genereren.

**Volgende technische stap:** reproduceerbare routebron-join met een machineleesbare QA-tabel en daarna de eerste zeven routepatronen selecteren op daadwerkelijk aanwezige haltevolgorde én shapes, niet alleen op beschikbare frequenties.
