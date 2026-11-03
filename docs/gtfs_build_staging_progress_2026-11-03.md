## Update 3 november 2026 — KMZ/SIU-routes zonder haltevolgorde, SOBUSA eerst

De [werkende GitHub Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41620034866) heeft de **60 van de 93 officiële KMZ-route-/variantvermeldingen zonder SIU-basisroutekandidaat** omgezet in een [prioritaire werkvoorraad](../sources/amb/kmz_stop_research/workqueue/siu_missing_60_kmz_route_variant_workqueue.csv). Dit betreft 55 verschillende combinaties van vervoerder plus basisroutecode, **geen 60 aparte GTFS-route_id's**. De 12 sterkere en 8 voorlopige reeds bestaande SIU-route-/haltevolgordes blijven behouden.

**SOBUSA-proef:** negen KMZ-records (zes basisroutes, drie A/B-paren) zijn verwerkt. [Bron- en haltekandidaatanalyse](../sources/amb/kmz_stop_research/sobusa/summary.md), [geprojecteerde SIU-/OSM-haltekandidaten](../sources/amb/kmz_stop_research/sobusa/sobusa_all_nearby_candidates_NOT_CONFIRMED.csv) en [A/B-verschillen](../sources/amb/kmz_stop_research/sobusa/sobusa_AB_shape_differences.csv). **3.276 route-kandidaat-combinaties binnen 35 meter** (3.241 vanuit SIU op *andere* lijnen en 35 vanuit niet-bevestigde OSM-objecten) zijn louter geografische kandidaten; **0 formeel bevestigde SOBUSA-haltes**. Geen verzonnen stopvolgorde, GTFS-trip of stop_times toegevoegd.

**Nieuwe bronconflicten:** [vergelijking officiële lengte versus KMZ](../sources/amb/kmz_stop_research/sobusa/legal_length_QA.md) laat zien dat SOBUSA **B18 A/B wat lengtes betreft precies omgewisseld lijkt**: resolutie 082-2026 p6 A 73,6 km en B 75,6 km, terwijl KMZ A 75,56 km en B 73,61 km meet. **C16** wijkt ook af van 466-2025 p18. Geen automatische A/B-omwisseling of export voordat de wettelijke straattrajecten tegen KMZ zijn gecontroleerd.

**SIU crosswalk-review:** alle 33 reguliere SIU-itineraries tegen de nieuwe officiële KMZ vergeleken (296 ruimtelijke vergelijkingen); [13 nog onbesliste SIU-koppelingen](../sources/amb/kmz_stop_research/siu_crosswalk/thirteen_unresolved_siu_itineraries_kmz_ranking.csv) kregen gerangschikte opties. Dit zijn *alleen geografische aanwijzingen*: gedeelde operators, overlappende corridors en vier dubbele KMZ-URL's kunnen een nummer-1 match misleidend maken. [Volledige review](../sources/amb/kmz_stop_research/siu_crosswalk/summary.md). **0 routecodes of varianten juridisch definitief bevestigd door enkel geografie**.

**Vervolg:** valideren van haltebediening per route tegen aanvullende primaire/derdepartijbronnen, eerst SOBUSA, daarna de overige werkvoorraad. De bronbestanden en kilometer-/A/B-conflicten zijn nu reproduceerbaar gearchiveerd, zonder brongegevens te overschrijven of een onvolledige GTFS te publiceren.


## Aanvulling — review van alle 21 open SIU→AMB routecodes

De [volledige 21-dossiersreview](siu_remaining_21_route_links_review_2026-11-03.md) heeft **acht nieuwe, strikt voorlopige één-op-één basisroutevoorstellen** en **1.620 extra haltevermeldingen** in staging gezet. Inclusief de eerdere 12 sterke geografie-kandidaten is nu een [gecombineerd 20-routebestand met **3.981** haltevolgorderegels en **2.394** afzonderlijke stop-ID's](../sources/siu/open_route_review/combined_20_route_stop_candidates_NO_TIMES.csv) beschikbaar. Voor de overige 13 itineraries blijven 8 gedeelde exploitatiegevallen, 3 A/B-gevallen en 2 PT4/PT5-conflicten open.

De [oorspronkelijke AMB-resolutie 256-2026](https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf) is geverifieerd; de A/B-straattracés zijn geëxtraheerd en tegen 256 geordende SIU-haltevermeldingen afgezet. Ondanks de oorspronkelijke PDF blijven SIU→PT4/PT5-basiscodes en A/B-varianten **onbeslist** door tegenstrijdige naam/terminal-aanwijzingen. **Geen productietrip of stop_times.txt is verzonnen of aangemaakt.**

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
