# Review of 21 unresolved public SIU→AMB itinerary crosswalks

> **Update 2026-11-05:** De bovenstaande tellingen en onderstaande oorspronkelijke kandidaten zijn een historisch gegenereerd review-snapshot van 3 november, niet de actuele beslissingen. De 11 handmatig beoordeelde routes zijn geconsolideerd in [`siu_amb_crosswalk_visual_decisions_2026-11-05.csv`](siu_amb_crosswalk_visual_decisions_2026-11-05.csv). Alle 11 kaarten beoordeeld; A/B, operator-toewijzing en geometriegaten blijven waar vermeld open. Bij conflicten (zoals ROJA RIOMAR en SOLEDAD CALLE 84) heeft de nieuwere handmatige review voorrang. Dit bestand wijzigt geen GTFS-output of generatorlogica.

**All 21 cases processed. No assignment to an A/B route pattern has been verified.**

## Results

- siu_open_records_reviewed: 21
- PT4_PT5_base_route_title_matches: 2
- PT4_PT5_terminal_conflicts_to_reconcile: 2
- PT4_PT5_AB_assignments_verified: 0
- single_operator_single_route_base_proposals: 8
- stop_occurrences_in_new_single_route_proposals: 1620
- combined_strong_and_provisional_itineraries: 20
- combined_research_only_stop_occurrences: 3981
- combined_candidate_stops_distinct: 2394
- shared_operator_or_AB_or_uncertain_remaining: 13
- legally_confirmed_new_route_matches: 0
- prior_high_confidence_geographic_candidates_untouched: 12
- pairwise_stop_sequence_comparisons: 5
- source_legal_table: sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv
- original_256_PDF_verified: True
- warning: No legal A/B assignments, no TPC GTFS route_id modifications or stop_times; proposals only.

## PT4/PT5 (source 256-2026)

- SIU **CIRCUNVALAR VIA 40** (132 stops): **title suggests PT5-4105** while **2026 legal terminal street suggests PT4-4104**. This contradiction blocks any base or A/B confirmation.
- SIU **VIA 40 CIRCUNVALAR** (124 stops): **title suggests PT4-4104** while **2026 legal terminal street suggests PT5-4105**. This contradiction blocks any base or A/B confirmation.

For PT4 and PT5, each of A and B has **9 min peak / 14 min offpeak** according to the curated resolution table. A/B refers to a licensed pattern, not automatically the SIU route's outbound/return half. A 2019 GIS line that matches at 100% to both routes does not disambiguate direction.
**Both original 192-2025 and 256-2026 PDFs have been checked:** PT4 A/B starts at Calle 17/Carrera 30 and PT5 A/B at Vía 40 No. 51-310. In 256 the B variants use distinct side-street branches; exact SIU A/B crosswalk still cannot be proven from available names.

## Other unresolved links

- LAS PALMAS (COOTRAB): C5-4136 — provisional_base_candidate_legal_review_required
- LAS NIEVES (COOTRAB): C6-4137 — provisional_base_candidate_legal_review_required
- MAKRO (SODETRANS;COOLITORAL;TRANSDIAZ): B17-4163 — shared_operator_route_pattern_not_allocatable
- CENTRO CIRCUNVALAR (TRANSURBAR): A14-4116 — provisional_base_candidate_legal_review_required
- VIA 4O PLACA ROJA (TRASALFA): D14-4156 — provisional_base_candidate_legal_review_required
- CALLE 17 (LA CAROLINA): D7-4151 — provisional_base_candidate_legal_review_required
- SANTUARIO PRADO (EMBUSA): B9-4125 — provisional_base_candidate_legal_review_required
- CIRCULAR (COOCHOFAL): C18-4141 — provisional_base_candidate_legal_review_required
- MIRAMAR ALAMEDA DEL RIO (LA CAROLINA): A16-4161 — base_code_plausible_but_AB_pattern_unresolved
- VIA 40 MURILLO (COOLITORAL): PT3-4103 — base_code_plausible_but_AB_pattern_unresolved
- RIOMAR AMARILLA (TRANSDIAZ;SODETRANS): B13-4128 — shared_operator_route_pattern_not_allocatable
- ROJA RIOMAR (SODETRANS;TRANSDIAZ): B13B-4189 — shared_operator_route_pattern_not_allocatable
- SOLEDAD 2000 CORREDOR UNIVERSITARIO (SODETRANS;TRANSDIAZ): C21-4182 — shared_operator_route_pattern_not_allocatable
- JUAN MINA (COOLITORAL;TRANSDIAZ;SODETRANS): PT1-4101 — shared_operator_route_pattern_not_allocatable
- SOLEDAD CALLE 84 VILLA CAROLINA (SODETRANS;TRANSDIAZ): A10-4114 — shared_operator_route_pattern_not_allocatable
- PUEBLO SAN PABLO CENTRO (COOLITORAL): C19-4178 — provisional_base_candidate_legal_review_required
- VILLA SAN PABLO (COOLITORAL;TRANSDIAZ;SODETRANS): PT1-4101 — shared_operator_route_pattern_not_allocatable
- LAS GAVIOTAS CALLE 76 (LA CAROLINA): A16-4161 — base_code_plausible_but_AB_pattern_unresolved
- SOLEDAD CALLE 84 (SODETRANS;TRANSDIAZ): B17-4163 — shared_operator_route_pattern_not_allocatable

The combined 20-route research table has candidate stop IDs with two confidence tiers; not legal confirmations.
No timetable, stop_times, approved direction or final mapping added to GTFS.
Original 256-2026 verified and compared; pilot starts 22 June 2026 for six months with possible extension. Continued legal applicability and SIU-to-licensed A/B ID assignment remain separate checks.
