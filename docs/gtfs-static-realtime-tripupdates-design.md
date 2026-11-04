# Ontwerpbesluit: statische AMB-GTFS als basis voor SIU TripUpdates

Status: **ontwerp vastgesteld voor implementatie, niet productiegevalideerd** (4 november 2026).

## Onderzochte bestaande generatoren

- `scripts/build_amb_trip_timing_staging.py`: produceert 20 SIU-gebaseerde frequentie-triptemplates, 3.981 geordende stop_times in modelvorm, en `exact_times=0`. De `trip_id` is `AMB_MODEL_SIU_` + SIU itinerary UUID zonder streepjes. `service_id=AMB_MON_FRI_MODEL`, `direction_id` en `shape_id` leeg. Het starttijdstip 00:00:00 is een **relatieve referentie**, geen eerste vertrek. De rijtijden zijn aannames uit afstand, gemiddelde snelheid, omwegfactor en stopdwell. De uitvoer mag niet gepubliceerd worden.
- `scripts/build_amb_gtfs_geometry_validation_pilot.py`: aparte schema-/shape-QA ZIP met `QA_` trip IDs, fictieve 07:00 ritten en demonstratiekalender. Dit is **niet** de productie-generator en mag niet als ritbasis voor RT worden gebruikt.
- `gtfs/routes.txt` en `gtfs/agency.txt` bevatten juridische route-/vervoerderregistraties. `sources/siu/public_extract/siu_itineraries.csv` bevat SIU UUIDs, organisatie UUIDs, bedrijfsnamen en voorlopig te reviewen routekoppelingen.
- `docs/amb_peak_offpeak_model_2026-11-03.md`: officiële resoluties bepalen de frequenties; de dienstvensters uit 2020 en 07:00–09:00 / 17:00–20:00 zijn expliciete vervangbare projectaannames. Geen automatisch weekend/feestdagen en geen veronderstelde 24-uursdienst.

## Besluiten en redenen

### ADR-01 — Één canonieke patroonidentiteit en deterministische IDs

Een **trip pattern** is de combinatie van juridische routevariant, richting, geordende haltebezoeken en eventueel onderscheiden traject. Leg in een versieerbaar register vast:
`pattern_id, gtfs_route_id, direction_id, siu_itinerary_uuid, stop_sequence_signature, shape_id, review_status, provenance`.

De productie-`trip_id` is deterministisch afgeleid van een stabiele `pattern_id` plus diensttype (indien verschillende kalender-/tijdprofielen een eigen template vereisen). Geen random IDs, huidige datum of buildnummer in IDs. Een verandering van vormgeometrie alléén verandert niet automatisch de `trip_id`; een wezenlijke verandering in haltevolgorde/patroon vraagt review en zo nodig een nieuwe ID. **Waarom:** TripUpdates verwijzen naar de statische `trip_id`; willekeurige ID-wijzigingen breken die verwijzing.

Het huidige `AMB_MODEL_SIU_...` blijft uitsluitend staging-ID. De `QA_...` IDs blijven uitsluitend fixture-ID.

### ADR-02 — Behoud headway-gebaseerde frequenties

Gebruik `frequencies.txt` met `exact_times=0` wanneer de bron alleen een frequentie, niet de exacte vertrekken bevestigt. Gebruik geen kunstmatige vaste vertrektijden om RT matching te vereenvoudigen. De `stop_times.txt` van de template bevat relatieve, consistent berekende tijden; onzekerheid en timingmodelversie blijven in de provenance staan. **Waarom:** officiële AMB-resoluties bevestigen intervallen maar niet elke werkelijke rit.

Voor realtime is een **ritinstantie** iets anders dan een frequentie-triptemplate. De RT-tripdescriptor gebruikt de template-`trip_id` plus dienst-`start_date` en een stabiele `start_time` van de concrete rit. Een ETA is géén `start_time`. Als de ritstart niet betrouwbaar bepaald kan worden, blijft de rit unmatched en wordt geen misleidende TripUpdate gepubliceerd. Gebruik `UNSCHEDULED` niet als uitweg om ontbrekende identiteiten te verbergen.

### ADR-03 — Eén gedeeld stop-ID register

Hergebruik een fysiek `stop_id` voor dezelfde halte over meerdere routes. Bewaar `siu_stop_uuid -> gtfs_stop_id` met alias-historie en matchkwaliteit. Bewaar óók `pattern_id, stop_sequence, siu_stop_uuid, gtfs_stop_id`, want lussen kunnen dezelfde halte meerdere keren aandoen. **Waarom:** `StopTimeUpdate.stop_sequence` moet exact de corresponderende `stop_times.txt` sequence gebruiken; `stop_id` alleen is bij herhaalde haltes ambigu.

### ADR-04 — Geen verdubbeling bij gedeelde exploitatie

Wanneer meerdere vervoerders **exact dezelfde variant gezamenlijk exploiteren**, blijft dat één route/patroon/frequentie; de samengestelde virtuele GTFS-agency en afzonderlijke vervoerders/attributions blijven apart herkenbaar. Een gecombineerde corridorfrequentie mag niet zonder bewijs aan een afzonderlijke A/B-variant worden toegekend. **Waarom:** dubbele statische ritten veroorzaken dubbele realtime voorspellingen en foutieve headways.

### ADR-05 — Dienstkalender en tijdzone zijn onderdeel van identiteit

Gebruik `America/Bogota` voor dienstdata; onderscheid `service_id` voor werkelijk onderbouwde diensttypen. Voeg feestdagen en uitzonderingen via `calendar_dates.txt` toe wanneer bevestigd. `start_date` is de GTFS-servicedag (kan bij ritten na middernacht afwijken van de kalenderdag van de aankomst). **Waarom:** realtime trip matching vereist een ondubbelzinnige servicedag.

### ADR-06 — Bronprovenance en GTFS-versie

Publiceer pas een RT-feed bij een concrete statische GTFS-versie; leg `feed_info.feed_version` en een hash/versie van het matchingregister vast. De realtime feed-header `feed_version` moet met de gebruikte statische versie overeenkomen. Bewaar bron- en modelkwaliteit buiten de standaard GTFS-tabellen. **Waarom:** een RT-consument kan alleen IDs oplossen binnen de bijbehorende statische feed.

### ADR-07 — SIU-service en ETA's zijn eerst onderzoeksdata

Voor elke SIU-service volgen we in opeenvolgende snapshots alleen de minimaal noodzakelijke, privacybewuste sleutelvelden en tijdsemantiek. Leg een afzonderlijk register vast:
`siu_service_id, siu_itinerary_uuid, gtfs_pattern_id, gtfs_trip_id, start_date, start_time, match_confidence, match_evidence, first_seen_utc, last_seen_utc`.
Deze velden zijn een **doelschema**, geen bewering dat SIU ze allemaal levert. Een service-ID is niet automatisch een GTFS-trip-ID; `vin` is geen bevestigde positie. Valideer `eta`/`realETA` (eenheid, tijdzone, voorspeld vs feitelijk), statussen en versheid over meerdere snapshots. Pas dan kan een `StopTimeUpdate.arrival.time` worden gemaakt. Gebruik geen `delay` tegen fictieve modeltijden.

### ADR-08 — Harde publicatiepoorten

Geen RT-publicatie totdat:
1. De statische GTFS-feed geldig is en dezelfde stabiele route-, trip- en stop-IDs gebruikt.
2. Het patroon en de haltevolgorde ondubbelzinnig zijn gematcht.
3. De SIU-service aan **één concrete ritinstantie** gekoppeld is, inclusief vaste servicedag en starttijd.
4. De ETA semantisch is bevestigd, vers is en naar een geldige stop_sequence verwijst.
5. Publicatie-/hergebruikrechten voor de gebruikte SIU-data zijn vastgesteld.

Een lege realtime feed betekent **geen betrouwbare realtime informatie beschikbaar**, niet dat er geen dienst rijdt.

## Concrete generatorwijzigingen — implementatiewerklijst

1. Maak een canoniek `trip_pattern_registry.csv` en `siu_stop_crosswalk.csv` met reviewerstatus en historische aliases.
2. Refactor beide staging-builders om hetzelfde patroonregister te lezen; behoud `QA_` en `AMB_MODEL_` alleen als duidelijk gelabelde test-ID's, nooit als productie-ID.
3. Maak productie-`trips.txt` en `stop_times.txt` pas uit geverifieerde route/patroon/stop-koppelingen; voeg `direction_id` en `shape_id` toe waar bevestigd.
4. Valideer `frequencies.txt`: `exact_times=0`, correcte niet-overlappende vensters, `headway_secs>0`, exclusieve `end_time`; het laatste dispatchmoment uit AMB-bronnen mag niet onbedoeld wegvallen.
5. Voer een cross-build ID-diff uit: bij dezelfde bronnen moeten `route_id, trip_id, stop_id, service_id` gelijk blijven; wijzigingen vereisen changelog en migratieregister.
6. Produceer naast GTFS ZIP een machineleesbaar `gtfs_rt_static_contract.csv` met `pattern_id, trip_id, route_id, service_id, direction_id, shape_id, stop_sequence_signature, feed_version, match_status`. Dit is **geen** extra GTFS-bestand in de ZIP.
7. Koppel de SIU snapshot-analyse aan dat contract, maar genereer alleen een RT-protobuf na succesvolle semantische checks.

## Huidige blokkades

- Route/patroon-koppelingen deels voorlopig, richting niet bewezen.
- Rijtijden en eerste/laatste vertrekken zijn deels modelaannames; weekends/feestdagen onvolledig.
- SIU-service-ID en starttijd per rit nog niet gevalideerd; ETA-eenheid en statussemantiek niet bewezen.
- SIU-herpublicatierechten niet vastgesteld.

## Specificatie

- https://gtfs.org/documentation/schedule/reference/
- https://gtfs.org/documentation/realtime/reference/
