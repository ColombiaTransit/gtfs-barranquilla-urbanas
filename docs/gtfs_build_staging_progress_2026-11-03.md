## Aanvulling 3 november 2026 — GTFS-halte- en routecrosswalk-staging

**Latere normalisatie:** twee duidelijke SIU-naamfouten zijn hersteld; daardoor zijn er **3.117 fysieke concept-haltes** en **53 nog open verschillende-naam-op-dezelfde-GPS-conflicten**. Eén samengevoegde halte heeft een expliciete historische `stop_id`-alias. Zie [het correctieregister](../sources/siu/stop_name_spelling_corrections_2026-11-03.csv) en [het auditbestand](../sources/siu/gtfs_staging/stop_name_correction_audit.csv). Er zijn geen rijrichtingen, straatnummers of GPS-coördinaten gewijzigd.



De [nieuwe reproduceerbare Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41598939812) heeft **3.117 kandidaat-haltes** opgebouwd uit 6.407 reguliere SIU-haltevermeldingen; **53 plaatselijke naams-/richtingsconflicten** zijn niet samengevoegd. Er zijn **12 sterke, voorlopige SIU→GTFS-routecodekoppelingen**; deze leveren **2.361 geordende stops** op, verwijzend naar **1.802 kandidaat-stop-ID's**. Voor de overige 21 itineraries blijven bedrijf- en routevariantenchecks open.

[Volledige SIU-kruisvalidatie en concept-`stops.txt`](siu_gtfs_stop_crosswalk_staging_2026-11-03.md). De preview wordt niet onder `gtfs/` geplaatst en bevat **geen gefingeerde rit- of haltevertrektijden**. Publicatierechten voor de uit SIU afgeleide brondata worden voor de verspreiding van een GTFS nader onderzocht.

## Aanvulling 3 november 2026 — SIU-haltegegevens gevonden

**Deze nieuwe bron verandert de eerdere status hieronder:** via het publieke SIU GraphQL-pakket zijn [36 SIU-itineraries](../sources/siu/public_extract/siu_itineraries.csv) gevonden, waarvan **3 testitineraries**. Voor de **33 overige itineraries** zijn [**6.407 geordende GPS-haltevermeldingen**](../sources/siu/public_extract/siu_route_stop_sequences.csv) beschikbaar. De 6.407 regels bevatten **3.612 unieke exact opgeslagen coördinaten** en **2.961 verschillende haltenamen**, maar dit zijn geen bevestigde aantallen fysieke haltes. Het bronpakket bevat inclusief de tests **6.873 vermeldingen** met unieke SIU-UUID's.

- Route `ALAMEDA DEL RIO` / FLOTA ÁNGULO bevat **127** geordende haltes; alle **10** uit de door de gebruiker opgeslagen MHT-bestanden zijn op dezelfde posities 75–84 teruggevonden.
- De [geografische SIU→AMB-GIS-kandidatenlijst](../sources/siu/analysis/siu_to_amb_routecode_candidates.csv) koppelt de 33 reguliere itineraries aan 93 oude GIS-routes: **16 sterk**, **5 ruimtelijk ambigu door overlap**, **12 gedeeltelijk/gewijzigd**. **0 definitief geverifieerde juridische GTFS-route-ID-koppelingen**; die vergen een vergelijking met nieuwste AMB-resoluties.
- Nog ontbrekend voor een valide productiefed: SIU→97 AMB-routecode crosswalk, halte-deduplicatie/rijrichting, passende actuele shapes en een onderbouwd reistijdmodel. De **hergebruik-/publicatielicentie voor SIU-routegegevens** moet voor distributie worden gecontroleerd.

De oorspronkelijke bouwstatus en prioriteiten hieronder geven de stand **vóór de nieuwe SIU-extractie** weer. Behoud ze voor de historische audit, maar gebruik bovenstaande informatie als de huidige haltebronstatus.

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

- Na normalisatie en correctie van `gtfs/routes.txt` konden **alle 97 huidige GTFS-route-/variantregels op routecodeniveau** aan een ArcGIS-feature gekoppeld worden; de variant `C18- 4141` is als schrijfvariant herkend. **Dit zijn 97 codelinks naar 93 bronfeatures; niet 97 verschillende geometrieën.**
- De resterende COOTRAB-afwijking bleek dat het voorlopige GTFS-bestand `C5-4135` vermeldde, terwijl de **laatste vergunning 358-2024**, de AMB-2020-kaart en de GIS-bron **C5-4136** vermelden. Deze GTFS-`route_id` is in `routes.txt` naar **AMB_COOTRAB_C5_4136** gecorrigeerd. De nieuwe [GIS-Action-run 41591621905](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41591621905) is inmiddels **geslaagd** met **97/97 codekoppelingen**.
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
