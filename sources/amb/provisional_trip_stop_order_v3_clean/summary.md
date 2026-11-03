# Opgeschoonde trip-haltevolgorde v3 — 39 signalen gecontroleerd

39 was het **aantal signalen**, niet het aantal unieke halte-ID's.
26 meldingen betroffen een herhaald fysiek SIU-stop-ID elders in een ritpatroon; 13 andere meldingen betroffen twee GH-toevoegingen binnen 115 meter van elkaar.
Bij 7 van die 26 + 26 verwijzingen was er overlap. We hebben **alle bij deze 39 meldingen betrokken GH-toevoegingen** uit een nieuwe conceptversie geweerd: 45 unieke haltebezoeken.

## Tellingen

- baseline_existing_original_stop_visits_preserved: **9000**
- v2_added_GH_visits: **65**
- review_alerts_total: **39**
- review_alerts_repeated_stop_id: **26**
- review_alerts_short_adjacent_candidate_pairs: **13**
- GH_visits_in_close_pairs: **26**
- GH_visits_flagged_both_repeat_and_close: **7**
- distinct_GH_candidate_visits_excluded_from_v3: **45**
- v3_GH_candidate_visits_remaining: **20**
- v3_all_concept_stop_visits: **9020**
- v3_route_patterns: **70**
- affected_route_variants: **14**
- number_of_physical_stop_records_deleted: **0**

## Bewuste bescherming

- De 9.000 oorspronkelijke KMZ-/SIU-haltebezoeken en hun onderlinge volgorde zijn integraal behouden.
- De centrale fysieke SIU-haltecatalogus blijft ongewijzigd; hergebruik van stop_ID's op meerdere routes is nog steeds normaal.
- Bij een echte rondrit kan dezelfde halte opnieuw worden bediend: uitsluiting hier is een **ruisreductie op verzoek** en geen bewijs dat zo'n tweede haltepassage onmogelijk is.
- Ook de twee GH-kandidaten van een te kort paar zijn weggelaten om geen willekeurige winnaar te kiezen.
- De oorspronkelijke v2 en de GH-classificatie blijven voor herstel beschikbaar.
- Geen tijden, GraphHopper-aanvragen of publiceerbare GTFS-wijzigingen.

## Bestanden

- candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv — nieuwe complete conceptvolgorde van 9.020 passages.
- excluded_GH_candidates_45_WITH_REASONS.csv — exact welke 45 GH-haltebezoeken niet in v3 zijn overgenomen.
- remaining_GH_candidates_20_with_v3_sequence.csv — alle 20 resterende GH-toevoegingen.
- route_pattern_cleaning_QA.csv — controles en aantallen per trip-patroon.
