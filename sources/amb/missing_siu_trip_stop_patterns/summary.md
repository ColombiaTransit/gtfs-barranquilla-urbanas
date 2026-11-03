# KMZ/ArcGIS → ritpatronen en bestaande SIU-haltevolgorde (nog zonder tijden)

**Onderzoeksstaging: geen GTFS stop_times.txt gepubliceerd.**
Het programma verwerkt uitsluitend AMB-routevarianten zonder directe SIU-route-halte-koppeling. Bestaande SIU-route-haltevolgordes blijven ongewijzigd.

## Resultaten

- source_KMZ_route_variants_missing_SIU: **60**
- route_variants_with_at_least_one_shape: **60**
- generated_provisional_trip_patterns: **176**
- trip_patterns_with_at_least_five_candidate_stops: **72**
- distinct_company_base_routes_in_patterns: **55**
- provisional_route_stop_visits: **8979**
- distinct_existing_physical_SIU_stop_ids_reused: **2364**
- total_route_stop_projection_candidates_within_35m: **24607**
- arcgis_fallback_pattern_components: **4**
- missing_route_variants_with_no_geometry: **0**
- new_physical_stop_ids_created: **0**
- arrival_departure_times_generated: **0**
- graphhopper_route_duration_future_dependency: **True**
- SIU_existing_route_stop_links_preserved: **True**
- service_of_route_at_stop_confirmed_by_geometry_alone: **False**
- publication_ready: **False**

## Methode

1. Officiële AMB-KMZ is voorkeursgeometrie; bij foutief KMZ-bestandslabel wordt de 2019–2023 ArcGIS-bron gemarkeerd als tijdelijke fallback.
2. Vind bestaande fysieke SIU-stop-ID's binnen 35 meter van een shape. Projecteer elke halte op alle lijnpassages zodat een rondrit dezelfde fysieke halte bij terugkeer opnieuw kan bezoeken.
3. Bij haltebenamingen met NS/SN/OE/EO vergelijkt het script de rijrichting van de lokale routetangent; tegenstrijdige richting wordt niet geselecteerd.
4. Alleen kandidaten binnen 25 meter mogen in de modelrit worden geselecteerd. Kies per 115 meter afgelegde routeafstand één beste kandidaat om overmatige dubbele instappunten te vermijden.
5. Leg de geselecteerde bestaande stop_ID's vast in oplopende shapeafstand met aaneengesloten stop_sequence. Arrival/departure blijven leeg voor latere GraphHopper-berekening.

## Belangrijke beperkingen

- Een fysieke halte mag door veel routes en trips worden gedeeld. Er worden **geen route-specifieke haltes verzonnen**.
- Geografische nabijheid en richting zijn een **modelaanname**, geen officiële bevestiging dat een bus stopt.
- 115 meter is een selectieregel om te veel haltes te voorkomen, niet een vastgesteld halte-interval.
- Soms beschrijft één KML-lijn een volledige rondrit (heen én terug). De gegenereerde pattern is dan een onderzoeksroute, niet noodzakelijk één operationele trip.
- Bij verkeersassen waar heen/terug dezelfde geometrie delen, kan de richtingsclassificatie onzeker blijven.
- De bron-AM B18-variantlabels kunnen omgewisseld zijn; PT2 kan een oudere ArcGIS-fallback gebruiken. Iedere bronafwijking staat in de QA.
- Geen tijden of frequenties gewijzigd en geen GTFS-bestanden onder gtfs/ overschreven.

## Vervolg
Beoordeel per lijn de stopselectie en echte tripgrenzen. Vervolgens kan GraphHopper over de gekozen trajecten een reistijdmodel aanleveren.
