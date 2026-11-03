## Update 3 november 2026 — stopvolgorde voor 60 nog ontbrekende SIU-routes; geen tijden

De [geslaagde GIS/KMZ-halte-naar-trip Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41624783681) heeft alle **60 AMB-KMZ-route-/variantvermeldingen zonder eigen SIU-itinerary-haltevolgorde** tegen de bestaande fysieke SIU-haltecatalogus gematcht. Bij ontbrekende of foutieve KMZ-geometrie is de historische 2019–2023 ArcGIS-routelaag duidelijk als fallback gemarkeerd. Er zijn geen route-specifieke nieuwe stop-ID's aangemaakt.

De definitieve herverwerkingsstand is [60/60 routevarianten](../sources/amb/missing_siu_trip_stop_patterns/route_readiness_summary.md), **9.000 voorlopig geordende haltepassages** met **2.368 bestaande fysieke SIU stop-ID's**. De [geografische haltevolgorde per onderzoekstrip](../sources/amb/missing_siu_trip_stop_patterns/candidate_stop_order_per_trip_NO_TIMES.csv) heeft stop_sequence, stop_id, KMZ-shapeafstand, afstand tot de lijn en richtingsindicatie; **geen arrival/departure**. De [GraphHopper waypoint-staging](../sources/amb/missing_siu_trip_stop_patterns/graphhopper_waypoint_staging_NO_TIMES.csv) bevat per haltevisit dezelfde fysieke ID, de originele SIU-coördinaten en lege tijdvelden. De oude SIU-route-stop-patronen zijn behouden en blijven een betrouwbaardere bron voor hun eigen lijnen.

**Kwaliteit vóór trips:** 57 routes hebben één lijncomponent, maar drie hebben meerdere geometriecomponenten (COOLITORAL A4, COOLITORAL PT2 met historische ArcGIS-fallback en LOLAYA D8 met historische ArcGIS-fallback). De componenten zijn geen automatisch bewezen afzonderlijke operationele ritten: de [route-QA met 60 varianten](../sources/amb/missing_siu_trip_stop_patterns/route_variant_mapping_readiness_60.csv) markeert onzekere segmentatie. **39 van de 60** routevarianten hebben minstens één ongebruikelijk gat van 2 km tussen geselecteerde haltes; dit kan een ontbrekende SIU-halte langs een corridor of een echte snelwegpassage zijn en moet niet blind worden ingevuld. SOBUSA B18 heeft daarnaast een mogelijk A/B-labelconflict met resolutie 082-2026.

**Modelgrenzen:** corridorafstand binnen 35 m zoeken, alleen kandidaten binnen 25 m selecteren, richtingcodes NS/SN/EO/OE vergelijken met de lokale routetangent en bij concurrerende haltes voorlopig 115 m minimale routeafstand. Dit bewijst geen werkelijk halteren, geen wettelijke trip-richting en geen volledig stop-patroon. Alle toewijzingen zijn onderzoeksdata. Geen productie-GTFS trips.txt, stop_times.txt of reistijden uit deze reconstructie gepubliceerd. GraphHopper-tijden worden apart onderzocht na controle van routepatroon en stops.


## Update 3 november 2026 — ontbrekende SIU-routehalte-koppelingen op bestaande haltes geprojecteerd

De [geslaagde GitHub Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41624525178) heeft nu **alle 60 KMZ-routevarianten zonder direct geordend SIU-route-haltepatroon** op bestaande fysieke SIU-haltes gematcht. Geen dienstregeling- of reistijdberekening: GraphHopper volgt pas in de latere tijdfase.

- **60/60 routevarianten** met een bestaande bronshape en minstens één bruikbaar voorlopig haltepatroon (minstens vijf haltes).
- **74 geografische kandidaatpatronen** (sommige bronshapes hebben meer dan één LineString), waarvan **70 met minimaal vijf kandidaat-haltes** en dus met een geordende stop_sequence in de staging.
- **9.000 kandidaat-haltebezoeken**, verwijzend naar **2.368 al bestaande fysieke SIU stop_id's**. Geen aparte haltes voor de buslijnen gemaakt; een bestaand SIU stop_id kan aan verschillende trip-patronen worden gekoppeld.
- Op 35m zijn **24.279 route-stop-projectiekandidaten** bekeken; selectie is restrictiever (maximaal 25m, richtingscontrole NS/SN/OE/EO en een model-spreidingsafstand van 115m). De niet-geselecteerde kandidaten blijven traceerbaar.
- [Trip-patronen zonder tijden](../sources/amb/missing_siu_trip_stop_patterns/trip_patterns_MISSING_SIU_NO_TIMES.csv) en [trip→stop_id, stop_sequence zonder tijden](../sources/amb/missing_siu_trip_stop_patterns/candidate_stop_order_per_trip_NO_TIMES.csv) vormen de nieuwe basis voor latere GraphHopper-reistijden.
- [Alle kandidaatselecties incl. afwijzingsreden](../sources/amb/missing_siu_trip_stop_patterns/all_projected_SIU_stop_candidates_WITH_DECISIONS.csv), [geometrie- en richting-QA](../sources/amb/missing_siu_trip_stop_patterns/route_shape_and_stop_mapping_QA.csv) en [samenvatting](../sources/amb/missing_siu_trip_stop_patterns/summary.md) zijn gearchiveerd.

**Shape-keuze:** officiële AMB-KMZ waar coherent en niet foutief gelabeld. **COOLITORAL PT2** verwijst op de AMB-website naar PT1 en gebruikt daarom voorlopig de expliciet gemarkeerde oudere ArcGIS-routevorm. **LOLAYA D8** heeft >100 grotendeels korte, ongeordende KML-fragmenten en is daarom overgezet naar ArcGIS 2019–2023 voor een veel kleinere, toetsbare verzameling routedeelpatronen. Ook COOCHOFAL C9 draagt de bestaande URL-conflictvlag. **Alle drie bronuitzonderingen blijven niet-publiceerbaar totdat de juiste lijn is gecontroleerd.**

**Beperkingen:** shapevolgorde is geen bewijs van werkelijk halteren, aparte routebediening of operationele tripgrenzen. De gekozen kandidaat-trip kan een hele heen/terug-lus zijn, en de afstandsfilter kan echte haltes missen. De 20 reeds gevonden SIU-haltevolgordes blijven **onveranderd**. De nieuwe voorgestelde basis-route_id voor A/B is gelijk per officiële lijn, maar de historische gtfs/routes.txt met meerdere A/B-rijen is in deze onderzoeksstap **nog niet genormaliseerd**. Pas na beoordeling van haltebediening, rijrichting, tripsegmentatie en latere tijdcalibratie komen de concepten in definitieve GTFS.


## Update 3 november 2026 — trip-sjablonen, gedeelde haltes en model-stop_times

De [geslaagde GitHub Action voor stop_times-staging](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41622390506) zet de **20 bestaande voorlopig aan AMB gekoppelde SIU-itineraries** om in [20 GTFS-achtige trip-sjablonen](../sources/amb/gtfs_trip_timing_staging/trips_MODEL_ONLY_NOT_FOR_PUBLICATION.txt) en [3.981 gemodelleerde haltepassages](../sources/amb/gtfs_trip_timing_staging/stop_times_MODEL_ONLY_NOT_FOR_PUBLICATION.txt). **Dit zijn geen officiële passage-/vertrektijden of publiceerbare GTFS-bestanden.** De SIU-volgorde is behouden; alle stop_id-waarden verwijzen naar de al gededupliceerde fysieke haltecatalogus. **2.394** unieke SIU-stop-ID's komen in deze sjablonen voor.

De [instelbare tijdmodelaannames](../sources/amb/gtfs_timing_model_assumptions.csv) zijn 20 km/u, wegfactor 1,25, 10 seconden modelvertraging per halte en minimaal 15 seconden tussen haltebezoeken. **17** trip-sjablonen hebben een bestaande officiële frequentie + voorlopig 2020-vertrekvenster, en er zijn [68 periode-rijen](../sources/amb/gtfs_trip_timing_staging/frequencies_MODEL_ONLY_NOT_FOR_PUBLICATION.txt) opgebouwd. **Drie** blijven voor frequenties geblokkeerd: **TRASALFA D14, TRASALFA D15 en COOCHOFAL C18** (officieel interval en/of historisch dienstvenster ontbreekt of is ongeldig). De modelritduren voor **LA CAROLINA D6/D7** zijn meer dan vijf uur; splitsing of kalibratie is nodig.

**Cruciale ritsegmentcontrole:** de [20 SIU-itineraries zijn op mogelijke rondritten onderzocht](../sources/amb/gtfs_trip_timing_staging/itinerary_direction_split_review.csv). **13** eindigen op maximaal 300 meter van hun begin, na eerst ruim 1,5 km uitgeweken te zijn; **alle 20** bevatten haltebenamingen met straatrichtingsaanduidingen van beide kanten. Een SIU-lijst kan een volledige heen-en-terugrit of cirkeltraject beschrijven. Eén SIU-lijst is dus niet automatisch één fysiek trip-segment. **Geen automatische direction_id of split**: verifieer eerst terminal, wettelijke route en keerpunt. Een cirkelroute kan wel één GTFS-trip zijn.

Voor de **60 ontbrekende KMZ-varianten** is [één gedeelde SIU-haltelijst](../sources/amb/shared_stop_reuse/shared_physical_SIU_stop_index.csv) hergebruikt: **2.867** bestaande SIU-haltes liggen nabij minstens één variant en leveren [16.515 geografische route-bestaand-stop-ID-kandidaten](../sources/amb/shared_stop_reuse/missing_route_to_existing_stop_id_candidates.csv). **3.394** links hebben betrekking op SOBUSA met **1.123 verschillende bestaande SIU-haltes**. **Nul nieuwe fysieke haltes of bewezen nieuwe routebedieningen**; rijrichting, perron en daadwerkelijk halteren blijven te verifiëren.

De onderzoeksbestanden staan onder sources/amb/gtfs_trip_timing_staging/ en sources/amb/shared_stop_reuse/. Geen productiebestanden onder gtfs/ gewijzigd. Volgende vereisten: ritsegmentatie/richting, rijtijdkalibratie, juridische routecrosswalk, kalender en publicatierechten.


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
