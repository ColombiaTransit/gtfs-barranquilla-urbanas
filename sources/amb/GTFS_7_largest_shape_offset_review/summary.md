# Zeven grootste SIU-/GH-shape-afwijkingen: bron- en validatoronderzoek

De zeven haltes liggen binnen 15 meter van officiële AMB KMZ 2026.
Er is geen bewijs voor een onjuiste SIU-stoplocatie; afwijking ligt
tussen bronroute en GraphHopper bus-wegroute. Nieuwe GH-alternatieven
worden alleen aanvaard na echte MobilityData-validatorcontrole
zonder verhoging van het aantal volgorde-/afstandsfouten.

## Resultaten

- original_high_priority_stop_offsets_over_250m: **7**
- source_route_patterns_with_high_priority_offsets: **5**
- GH_road_sections_implicated: **6**
- GH_bus_routing_alternative_profiles: **2**
- GH_bus_route_queries: **48**
- full_MobilityData_validation_trials: **11**
- GH_alternative_route_sections_accepted_under_full_validator: **1**
- MobilityData_baseline_off_shape_warnings: **64**
- MobilityData_final_off_shape_warnings: **64**
- MobilityData_baseline_out_of_order_warnings: **4**
- MobilityData_final_out_of_order_warnings: **4**
- seven_original_stops_resolved_from_GTFS_test_warnings: **2**
- seven_stops_remaining_unresolved: **5**

## Individuele bevindingen

| Route | SIU-halte | GH-afwijking vóór | KMZ-afstand | Validator na |
|---|---|---:|---:|---|
| COOTRANTICO B5-4121 | IPUC CARIBE VERDE - IGLESIA PENTECOSTAL (CALLE 130 - SN) | 355.1m | 7.2m | GH_bus_vs_source_KMZ_discrepancy_remains_unverified |
| COOTRANTICO B5-4121 | IPUC CARIBE VERDE - IGLESIA PENTECOSTAL (CALLE 130 - NS) | 353.4m | 1.5m | GH_bus_vs_source_KMZ_discrepancy_remains_unverified |
| COOTRASOL D3-4147 | INDETEC (CALLE 54 - NS) | 314.1m | 0.3m | GH_bus_vs_source_KMZ_discrepancy_remains_unverified |
| SOBUSA C16-4167 A | CARRERA 11 CON CALLE 37 (OE) | 258.5m | 0.6m | GH_bus_vs_source_KMZ_discrepancy_remains_unverified |
| SODETRANS B15-4129 A | CARRERA 30 CON CALLE 143B (OE) | 260.9m | 3.3m | distance_warning_resolved_in_test_only |
| SODETRANS B15-4129 A | CARRERA 30 CON CALLE 143C (EO) | 264.8m | 0.8m | distance_warning_resolved_in_test_only |
| TRANSMECAR D11-4153 | CARRERA 23 CON CALLE 28 (EO) | 255.7m | 2.8m | GH_bus_vs_source_KMZ_discrepancy_remains_unverified |

## Grenzen

Als een waypoint-kandidaat een nieuw stops_match_shape_out_of_order-signaal
oplevert, wordt de kandidaat-shape **niet** overgenomen, zelfs als
alle fysieke halteafstanden verbeteren.
Geen herordening, geen SIU GPS-verplaatsing, geen nieuwe vaste
dienstregeling, geen automatische productie-GTFS-publicatie.
