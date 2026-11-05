# GTFS v2 — actieve generator

Actief: `scripts/build_gtfs_v2.py` via [Build GTFS v2 with Flex and GTFS-RT contract](../../.github/workflows/build-gtfs-v2.yml). De oude synthetische generator is verplaatst naar `archive/research_2026/` en is **geen** publicatiepad. Oude onderzoeksworkflows zijn historisch en niet opnieuw gevalideerd na archivering.

## Invoer en contract
De workflow haalt de officiële KMZ-manifesten en GeoJSON opnieuw op. Alle aanvullende bestanden zijn expliciete review-inputs onder `sources/amb/gtfs_v2/`. Ontbrekende bestanden betekenen geen stilzwijgende defaults.

| Bestand | Verplichte kolommen voor relevante records | Doel |
|---|---|---|
| `shape_source_crosswalk.csv` | route_id,shape_id,company,route_label,direction,review_status,geometry_review | Exacte bronmapping; direction forward/reverse; multipart nog handmatige goedkeuring |
| `trip_pattern_registry.csv` | pattern_id,route_id,shape_id,direction_id,siu_itinerary_uuid,review_status | Stabiele identiteit |
| `siu_stop_crosswalk.csv` | siu_stop_uuid,gtfs_stop_id,review_status | Stop-ID crosswalk |
| `stops.csv` | stop_id,stop_name,stop_lat,stop_lon | Canonieke fysieke haltes |
| `pattern_stop_visits.csv` | pattern_id,stop_sequence,gtfs_stop_id,arrival_time,departure_time | Geordende stopbezoeken en relatieve template-tijden |
| `service_templates.csv` | pattern_id,trip_id,service_id,start_time,end_time,headway_secs,timing_provenance,review_status | Frequentietemplates; exact_times=0 |
| `calendar.txt` | GTFS calendar velden | Gevalideerde dienstkalender |
| `flex_scope.csv` | route_id,continuous_pickup,continuous_drop_off,review_status | Alleen expliciet goedgekeurde doorlopende opstapregeling |
| `booking_rules.txt`, `location_groups.txt`, `location_group_stops.txt`, `locations.geojson` | Officiële GTFS Flex velden | Optionele Flex-input; niet automatisch gegenereerd |
| `siu_realtime_crosswalk.csv` | siu_itinerary_uuid,pattern_id,review_status | Toekomstige RT-koppeling, geen realtime-feed |

## Uitvoer
`build/gtfs-v2/shapes_candidate.csv`, `held.csv`, `gtfs_rt_static_contract.csv`, `summary.json`. Alleen met `--publish` én volledige publicatiepoorten volgt `gtfs.zip`.

**Bekende beperkingen:** dit is de eerste functionele bron-gated kern, nog geen volledige productie-implementatie. De generator assembleert momenteel alleen enkelvoudige LineStrings; de meeste AMBQ-KMZ's hebben meerdere segmenten. Die moeten via expliciete segmentvolgorde worden gemapt, niet gegokt. De nieuwe registers zijn nog niet gevuld uit de geconsolideerde juridische/SIU-bronnen. De RT-contractoutput is een statische sleutelregistratie; geen realtime-protobuf. De workflow is nog niet succesvol uitgevoerd. Een publiceerbare Flex-feed vereist verdere semantische validatie van de optionele tabellen en een MobilityData-validatiepoort. De huidige `--publish`-poort is daarom niet voldoende voor een productie-release.

**Geen GTFS-RT-publicatie** voordat SIU service-identiteit, startdatum/starttijd, ETA-semantiek, dataversheid en herpublicatierechten zijn bevestigd.
