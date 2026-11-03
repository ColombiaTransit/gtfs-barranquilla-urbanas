# GTFS Barranquilla Urbanas — voortgang eerste bouwketen (3 november 2026)

## Wat is nu reproduceerbaar

De bron-GTFS in `gtfs/` bevat op dit moment **23 operatoren** in `agency.txt` en **97 route-/variant-ID's** in `routes.txt`. Er is **geen geldige volledige GTFS-feed** zolang haltes, trips en stop_times ontbreken.

- **[Build AMB GTFS frequency staging](../.github/workflows/build-amb-gtfs-frequency-staging.yml):** verzamelt geldige/onderzochte resolutiefrequenties uit meerdere bedrijfsregisters, de als model aangenomen 2020-AMB-eerste/laatste vertrekken en de gekozen werkdagspits 07:00–09:00 / 17:00–20:00.
- **[De 97 GTFS-routekandidaten](../sources/amb/gtfs_staging/route_headway_candidates.csv):** per GTFS-route-ID de bronresolutie, piek- en dalfrequentie in seconden, aangenomen begin/eind, model-ID en eventuele reden voor uitzondering.
- **[245 kandidaat-perioden maandag–vrijdag](../sources/amb/gtfs_staging/weekday_period_staging.csv):** een voorbereide set **geen definitieve `frequencies.txt`**, omdat `trip_id` en benodigde `stop_times.txt` nog ontbreken.
- **[34 routes met open controles](../sources/amb/gtfs_staging/unresolved_route_issues.csv):** ontbreken van frequenties, oude vertrekvensters, A/B-variantpatronen, pilotstatus of tegenstrijdige bronextracties.
- **[Samenvatting](../sources/amb/gtfs_staging/summary.md):** de script-run van 3 november heeft **63 van de 97 routes** als klaar voor frequentie-staging aangemerkt, *niet* als een al operationeel gevalideerde feed.

De frequenties zijn gebaseerd op de **toepasselijke officiële AMB-resoluties**, niet op realtime-metingen. Voertuigcapaciteit is geheel buiten de GTFS-scope. De 2020-vensters en werkdagspits zijn expliciet **reversibele modelaannames**.

## Geometry bron voor de routes

De openbare **[ArcGIS-laag MO_RutasTransportePublico](https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6)** is opgehaald door [Harvest Barranquilla ArcGIS route shape candidates](../.github/workflows/harvest-amb-arcgis-shapes.yml). De laag bevat **93 bronpolyline-features**, met mapnamen onder `Rutas Transporte Publico 2019` en laatste bewerkingsdatum **27 december 2023**.

- Na normalisatie konden de routecodes van **96 van de 97 huidige GTFS-route-/variantregels** met een ArcGIS-feature worden gekoppeld; de ontbrekende 2019-namen `C18- 4141` zijn als schrijfvariant gematcht.
- De resterende COOTRAB-afwijking bleek dat het voorlopige GTFS-bestand `C5-4135` vermeldde, terwijl de **laatste vergunning 358-2024**, de AMB-2020-kaart en de GIS-bron **C5-4136** vermelden. Deze GTFS-`route_id` is in `routes.txt` naar **AMB_COOTRAB_C5_4136** gecorrigeerd. De Action wordt opnieuw gebouwd, waarna alle **97 op routecodeniveau** kunnen koppelen.
- **Belangrijk:** twee A/B-varianten kunnen naar dezelfde GIS-lijn verwijzen. Zo'n codekoppeling **betekent niet** dat de A- en B-richting/geometrie correct onderscheiden zijn. De bron is bovendien ouder dan meerdere huidige 2025/2026-routebesluiten.
- ArcGIS-`geojson` blijft **bron-/shape-kandidaat**, nog geen geverifieerde `shapes.txt`. Eerst het gewijzigde straatverloop met de nieuwste resolutie en haltevolgorde vergelijken.

De extractie-Action bewaart de volledige originele GeoJSON als artifact en publiceert [het compacte shape-matching-register](../sources/amb/arcgis_shape_staging/route_shape_matches.csv) en [GIS-dekkingsrapport](../sources/amb/arcgis_shape_staging/summary.json) in de repository.

## Nog nodig vóór een geldige GTFS ZIP

1. **Haltes:** een betrouwbare lijst met geocodes voor de traditionele TPC-bussen (niet zomaar de Transmetro-haltes) en een definitieve `stops.txt`.
2. **Haltevolgorde per richting/itinerary:** voor elke ritvorm de juiste stops, gekoppeld aan de te gebruiken vorm van de route.
3. **Reistijden:** per eerste en laatste en tussenliggende halte voldoende `stop_times.txt`-tijdwaarden of expliciet gemarkeerde interpolatie (`timepoint=0`) bouwen zonder verzonnen rijtijd uit alleen kilometers.
4. **`trips.txt`, `calendar.txt`, `calendar_dates.txt`:** met gekoppelde routevariant en een controleerbare week-/feestdagmodelkalender. Weekenddiensten zijn nu niet als officieel aangetoond.
5. **`frequencies.txt`:** pas samen met de trip-templates exporteren. Voor `exact_times=0` is de service frequentiegestuurd; de eindgrens is **exclusief** terwijl het AMB-`último despacho` een **inclusief laatste vertrek** is.
6. **Bijzonderheden:** gedeelde corridors (o.a. A1, B18, C12, A10), 2018-tijdelijke of 2026-pilotbesluiten, ontbrekende laatste dispatchwaarden voor vijf historische routes.

## Prioriteit volgende onderzoeksslag

In plaats van de officiële frequenties opnieuw te bewijzen, gericht de **haltebronnen en routevolgorde** onderzoeken. Voor nieuwe documenten of betere tijdinformatie kan de staging volledig opnieuw worden gebouwd zonder de bronhistorie te verliezen.

Geen fictieve stops of diensturen als AMB-officieel presenteren. Geen ongeldige 'GTFS.zip' publiceren.

**Technische referentie:** [GTFS Schedule Reference](https://gtfs.org/documentation/schedule/reference/).
