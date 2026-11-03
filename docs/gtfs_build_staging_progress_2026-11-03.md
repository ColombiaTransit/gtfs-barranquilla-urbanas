## Update 3 november 2026 — KMZ-bronroutes waar nodig met GraphHopper-buswegbochten verfijnd

De [geslaagde routeverfijning en volledige MobilityData-validatie](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41702838829) heeft de **144 KMZ-deeltrajecten** met ongedetailleerde bron-vertices onderzocht. Daarin zitten **457 individuele bronverbindingen groter dan 400 meter**. Alle 457 zijn tegen het private GraphHopper-profiel bus gerouteerd, zonder de oorspronkelijke AMB-KMZ-sleutelpunten te veranderen. **414** kandidaat-wegverbindingen voldeden lokaal aan de corridortoets, de eindpuntaansluiting, een begrensde rijomweg en geen verslechtering van SIU-halteafstand; 43 zijn al op deze lokale toets afgevallen.

De ruwe bundel met 414 kandidaat-wegverbindingen bleek niet veilig genoeg: MobilityData-waarschuwingen gingen van 2.381 naar **2.474**. Daarom is conservatief **per volledig bron-ritpatroon** teruggevallen waar nieuwe validator-waarschuwingen ontstonden. Van 136 kandidaat-aangepaste KMZ-deeltrajecten zijn **22 daadwerkelijk behouden** op **13 ritpatronen**, met samen **40** individueel verfijnde langere verbindingen. **114 deeltrajecten** zijn teruggezet naar de officiële KMZ-bron. Die 114 kunnen later met fijnmaziger, individueel gevalideerde segmentkeuzes worden heronderzocht; ze mogen niet onvoorwaardelijk als gewijzigde routes worden overgenomen.

De **uiteindelijke veilige proefbuild** is opnieuw door de echte MobilityData 8.0.1-validator gegaan, met exact dezelfde 59 routes, 67 synthetische trips, 8.867 haltebezoeken, agency/calendar/stops/trips/stop_times als de KMZ-first-referentie: alleen shapes.txt wijzigt.

| Melding | KMZ-first referentie | KMZ met validator-veilige GH-bochten |
|---|---:|---:|
| GTFS ERROR | 0 | 0 |
| Alle WARNING | 2.381 | **2.378** |
| stop_too_far_from_shape | 1 | **1** |
| stops_match_shape_out_of_order | 0 | **0** |

Er zijn **geen nieuwe offroute-halte-ID's of volgordewaarschuwingen**. De enige resterende stopafstandsmelding is onveranderd **LOLAYA D8-4165, Homecenter Calle 30 (SN), ca. 105,24 m**, op een GH-fallbackroute zonder bruikbare AMB-KMZ. De **7 oorspronkelijke GH-fallback-onderzoekscomponenten** (3 COOLITORAL PT2, 4 LOLAYA D8, samen 12 secties) zijn bij deze ronde ongemoeid gelaten.

**Nieuwe reproduceerbare scripts:** [lokale GH-buswegbochten](../scripts/refine_amb_sparse_kmz_edges_on_gh_bus_roads.py), [selectie met validator-blokkade en terugval](../scripts/select_amb_kmz_sparse_road_candidates_by_mobilitydata.py), [feitelijke bron-/eindvergelijking](../scripts/compare_amb_kmz_refined_with_mobilitydata.py), [GitHub Action](../.github/workflows/refine-amb-kmz-sparse-road-geometry.yml). Onderzoeksresultaten: [summary.md](../sources/amb/KMZ_GH_road_refinement_QA/summary.md), [besluit per lange KMZ-verbinding](../sources/amb/KMZ_GH_road_refinement_QA/KMZ_sparse_edges_GH_bus_decisions.csv), [validatorrollback per sectie](../sources/amb/KMZ_GH_road_refinement_QA/KMZ_sparse_road_refinement_validator_guard.csv), [overblijvende waarschuwing](../sources/amb/KMZ_GH_road_refinement_QA/remaining_stop_vs_refined_shape_QA.csv) en [samengevoegde onderzoeksshapes](../sources/amb/KMZ_GH_road_refinement_QA/GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson). Complete demo-GTFS-ZIP's en echte MobilityData-reports staan in het GitHub Action-artifact.

**Nog steeds onderzoek, niet publiceerbaar:** Een GraphHopper-lijn langs KMZ-keypoints is niet hetzelfde als bewezen actuele concessiebediening; de volledige GTFS-proefkalender en de tijden zijn fictief, tripgrenzen en rijrichtingen nog niet juridisch bevestigd. Geen productiebestanden onder gtfs/ en geen oorspronkelijke SIU-haltegegevens gewijzigd.


## Update 3 november 2026 — officiële KMZ-first-shapes met GraphHopper-fallback door MobilityData

[Geslaagde tweeledige MobilityData 8.0.1-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41699328357). De vergelijking wijzigde **uitsluitend shapes.txt**: agency, routes, stops, trips, stop_times en calendar waren byte-identiek in beide proef-ZIP's met **59 routes, 67 synthetische ritten en 8.867 haltebezoeken**.

| MobilityData-code | Veilige GraphHopper-busshapes | AMB-KMZ 2026-first, GH fallback |
|---|---:|---:|
| ERROR | 0 | 0 |
| stop_too_far_from_shape | 64 | **1** |
| stops_match_shape_out_of_order | 4 | **0** |
| alle WARNING | 2.433 | **2.381** |

De onderzoeksbron omvat **63 patronen met officiële KMZ 2026 (340 deeltrajecten)** en **7 zonder bruikbare KMZ (12 deeltrajecten)** waarvoor de bestaande GH-buswegroute is hergebruikt. De 7 zijn **COOLITORAL PT2-4102** (3 onderzoekscomponenten zonder corresponderende route-ID, niet in test-GTFS opgenomen) en **LOLAYA D8-4165** (4 componenten gebouwd vanaf oudere ArcGIS-/GH-onderzoeksgegevens, wél in de test-GTFS). Dus de **67 daadwerkelijk gevalideerde demo-trips** gebruiken **63 KMZ-shapes en 4 GH-fallback-shapes**. De fallback is geen bewezen actuele concessieroute.

**Enige resterende stop-afstandsmelding:** LOLAYA D8-4165, HOMECENTER CALLE 30 (SN), stop-ID SIU_2ace23a6-7511-43ce-b421-36400dc6728f, afstand tot bestaande GH-fallback-shape circa **105,24 meter**. Alle zeven eerder onderzochte P1-afwijkingen boven 250 meter veroorzaken nu geen MobilityData-afstandsmelding meer.

**Geometriekwaliteit apart controleren:** in **144 van de 340 KMZ-routedelen** is er ten minste één afstand tussen opeenvolgende bron-shapepunten van meer dan **400 meter**. Dat kan een rechte verbinding voorstellen waar de weg in werkelijkheid buigt. De betere MobilityData-meldingen bewijzen dus halte-shape-nabijheid, niet dat KMZ op kaartniveau de hele echte weg volgt. Eventueel bronconform verfijnen langs het wegennet zonder bronroute of haltevolgorde te veranderen.

[Bronkeuze per patroon](../sources/amb/KMZ_first_GH_fallback_validation/source_shape_source_by_pattern.csv), [validatorverschillen](../sources/amb/KMZ_first_GH_fallback_validation/MobilityData_notice_comparison_by_code.csv), [review per route](../sources/amb/KMZ_first_GH_fallback_validation/MobilityData_geometry_validation_per_pattern.csv), [de zeven oorspronkelijke P1-haltes](../sources/amb/KMZ_first_GH_fallback_validation/seven_P1_stop_warnings_KMZ_vs_GH.csv) en [KMZ met grote sprongen](../sources/amb/KMZ_first_GH_fallback_validation/source_shape_sparse_vertex_or_connector_QA.csv) zijn gecommit. Beide proef-ZIP's en volledige MobilityData-validatorreports staan in het Action-artifact. Geen productie-GTFS aangepast en nog steeds geen echte tripgrenzen of tijden.


## Update 3 november 2026 — MobilityData GTFS-afstands- en volgordeproblemen gericht gecorrigeerd

De [geslaagde GraphHopper/MobilityData-correctie-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41648106866) heeft **alle 122 GraphHopper-routeonderdelen die de 249 oorspronkelijke stop-to-shape-waarschuwingen veroorzaken** opnieuw via het ColombiaTransit-profiel `bus` gerouteerd, met circa 240 meter tussen KMZ-tussenpunten (GH /route). De eerste GIS-afstandsselectie nam 110 verbeterde trajecten over: de MobilityData-validator zag daarna slechts 13 afstandswaarschuwingen, maar wel **32 in plaats van 4** volgordewaarschuwingen. Deze onveilige tussenuitkomst is **niet als eindresultaat overgenomen**.

Daarom is de nieuwe [volgorde-guard](../scripts/guard_amb_gh_shape_fixes_against_validator_order.py) uitgevoerd: 28 patronen met nieuwe volgordewaarschuwingen zijn conservatief teruggezet naar hun oude wegengeometrie en vervolgens zijn 56 afzonderlijke sectievarianten een voor een opnieuw door de **echte MobilityData GTFS-validator 8.0.1** gehaald. Er zijn **79 GraphHopper-shapeverbeteringen behouden en 31 teruggedraaid**, zonder fysieke SIU-stop_id of stop_sequence aan te passen. De **definitieve onafhankelijke onderzoekstest** geeft **0 ERROR, 2.436 WARNING, 1 INFO**: **249 → 67** stop_too_far_from_shape-waarschuwingen (**182 opgelost**) en **4 → 4** stops_match_shape_out_of_order-waarschuwingen (geen extra afwijkingen). De [vergelijking met alle codes](../sources/amb/GTFS_shape_validator_recheck/MobilityData_notice_counts_before_after.csv), [eindsamenvatting](../sources/amb/GTFS_shape_validator_recheck/summary.md) en [besluiten per opnieuw getoetst wegdeel](../sources/amb/GTFS_shape_validator_recheck/GH_reintroduced_road_candidates_under_order_guard.csv) staan in de repository. Het GitHub Actions-artifact bevat alle 3 niet-publiceerbare proef-ZIP's met volledige validatorrapporten (baseline, onveilige tussenversie en volgordeveilige eindversie).

De [aanvullende geografische review-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41649425569) heeft de **67 resterende afstandswaarschuwingen** gemapt: ze liggen in **39 bronroutedeelpatronen**, alle 67 SIU-haltepunten liggen nog binnen **35 m van de oorspronkelijke KMZ/ArcGIS-shape** maar zijn meer dan 100 m van de huidige GraphHopper-wegshape verwijderd, en 7 gevallen hebben een afwijking van meer dan 250 m. Dat wijst primair op een **verschil tussen de bronroute en het berekende huidige buswegennet**, niet op bewijs dat de fysieke SIU-halte GPS-positie verkeerd is. [Alle 67 haltepunten als GeoJSON](../sources/amb/GTFS_shape_validator_recheck/67_remaining_stop_vs_GH_shape.geojson), [bronmetingen per halte](../sources/amb/GTFS_shape_validator_recheck/67_remaining_stop_vs_shape_source_evidence.csv) en [routeprioriteiten](../sources/amb/GTFS_shape_validator_recheck/remaining_67_source_review_by_route.csv) zijn beschikbaar. De meeste restgevallen zijn COOTRANSPORCAR C8 (8), MONTERREY B11 (6) en SODETRANS B15 A (4).

Voor de **vier resterende volgordewaarschuwingen** bij COOCHOFAL C2, COOTRANTICO B4 en B7 en TRANSMECAR D10 laat de [analyse van oorspronkelijke KMZ-kilometrering en SIU-IDs](../sources/amb/GTFS_shape_validator_recheck/4_remaining_stop_order_source_evidence.csv) zien dat de bronvolgorde van de specifieke halteparen **in alle vier gevallen oplopend** is. Bij COOTRANTICO B4 heeft een fysieke SIU-stop bovendien meerdere passages binnen hetzelfde onderzoeksritpatroon. Dit past bij meervoudige routepassages / door MobilityData gekozen dichtstbijzijnde geometriepunten, maar sluit een echte bronfout nog niet uit. Daarom is geen enkele routehalte omgewisseld of verwijderd. [Kaart van de vier betrokken halteparen](../sources/amb/GTFS_shape_validator_recheck/4_remaining_order_warning_pairs_NOT_ROUTES.geojson) is alleen een visuele QA-koppeling, **geen werkelijk busrouteverloop**.

Dit blijft een **test-GTFS met fictieve ritten, werktijden en dienstregeling**. Er zijn nog geen werkelijke tripgrenzen, haltebediening of reistijden bewezen; 21 historisch vastgestelde bron-wegafwijkingen blijven voor brononderzoek open. In `gtfs/` zijn **geen productie-outputbestanden** gewijzigd. De private GraphHopper-server-URL blijft uitsluitend in de GitHub organisatievariabele GRAPHHOPPER_URL.


## Update 3 november 2026 — gegenereerde GTFS-proefbuild en MobilityData 8.0.1

De [geslaagde GTFS-geometry GitHub Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41645007629) maakt een volledige maar **niet-publiceerbare GTFS-test-ZIP** van de al onderzochte GraphHopper-busweggeometrie. De [generator](../scripts/build_amb_gtfs_geometry_validation_pilot.py), [rapport-parser](../scripts/summarize_amb_gtfs_mobilitydata_validation.py) en [workflow](../.github/workflows/validate-amb-gtfs-geometry-pilot.yml) zijn reproduceerbaar en gebruiken de officiële MobilityData GTFS Schedule-validator 8.0.1 met SHA256-gecontroleerde JAR.

De proef-ZIP bevat agency.txt, routes.txt, stops.txt, trips.txt, stop_times.txt, shapes.txt en calendar.txt: **18 agencies, 59 bestaande routes, 2.362 fysieke SIU-haltes, 67 synthetische voorbeeldritten, 8.867 haltebezoeken en 67 GH-shapes met 45.818 shapepunten**. Van de 70 onderzoeksroutepatronen zijn er 67 opgenomen; 10 A/B-routevarianten zijn expliciet aan hun correcte bestaande route-ID gekoppeld. **3 COOLITORAL PT2-componenten met 153 haltebezoeken** ontbreken omdat er geen bestaande route-ID voor PT2 in routes.txt staat; er zijn geen routes verzonnen. De proefbuild betreft dus niet alle 97 bronroutes en nog niet alle direct gekoppelde SIU-itineraries.

**MobilityData: 0 ERROR, 2.615 WARNING, 1 INFO.** In het [echte validatoroverzicht](../sources/amb/GTFS_geometry_validator_pilot/validation_summary.md) staan 2.354 hoofdletterwaarschuwingen uit bestaande bronnamen, **249 te grote stop-to-shape-afstanden**, **4 mogelijke foute haltevolgordes**, 5 heel kleine distance/coordinate-afwijkingen, en drie enkelvoudige warnings over feed_info, een stop met veel shape-matches en de actieve week. De info betreft de toekomstige testkalender. [Codes en aantallen](../sources/amb/GTFS_geometry_validator_pilot/notice_counts.csv), [route-ID-crosswalk](../sources/amb/GTFS_geometry_validator_pilot/pattern_to_real_gtfs_route_crosswalk.csv) en [bouwtelling](../sources/amb/GTFS_geometry_validator_pilot/build_summary.json) zijn gecommit. Het GitHub Action-artifact bevat de proef-ZIP plus report.html en report.json.

In de eerste proefronde waren er 6.291 waarschuwingen, waaronder 3.676 veroorzaakt door voorlopig KMZ-afgeleid stop_times.shape_dist_traveled. Omdat deze per-halte-afstanden nog niet exact op de GH-weg waren gematcht, is dit optionele veld uit de proef-stop_times weggelaten. De werkelijke weg-shapepunt-afstanden in shapes.txt blijven behouden; de proef GTFS-structuur heeft geen specificatiefouten.

**Geen publiceerbare feed:** het model gebruikt een volledig fictieve werkdagkalender, één 07:00-voorbeeldrit per KMZ-component en synthetische 18 km/h plus 20 seconden stop-pauze. Geen bewijs voor operationele ritgrenzen, echte haltebediening of werkelijke aankomst- en vertrektijden. Productie-gtfs/ blijft ongewijzigd. Volgende stap: **249 halte-shape-afstanden**, **4 out-of-order-waarschuwingen**, ontbrekende PT2-crosswalk en 21 eerdere afwijkende wegdelen gericht onderzoeken.


## Update 3 november 2026 — complete routegeometrie en haltevolgorde gecontroleerd met GraphHopper bus

De [volledige 70-patronen GH-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41641356150) heeft alle 9.020 SIU-fysieke haltebezoeken van de opgeschoonde concept-v3 op **352 opeenvolgende KMZ-/ArcGIS-routedelen** gecontroleerd. Via de private ColombiaTransit-variabele GRAPHHOPPER_URL en GraphHopper profiel bus zijn **alle 352 wegroutes geslaagd**, waarvan 310 aanvankelijk binnen onze tweezijdige bron-geometriecriteria vielen. Per routeafsnede werden KMZ-tussenpunten opgegeven om ongewenste GH-kortere routes te beperken.

De [gerichte routegeometrie-hercontrole](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41642539811) heeft de 42 afwijkende delen met KMZ-ankers ongeveer elke 450 meter opnieuw gerouteerd: **21 opnieuw passend**, 7 duidelijk verbeterd maar nog onbevestigd en 14 blijvend afwijkend. De [geslaagde consolidatie-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41643007499) heeft uitsluitend de **21 nu passende** GraphHopper-buswegkandidaten in een nieuwe onderzoeks-versie samengevoegd. Daarmee zijn **331 van de 352 bronroutedelen voorwaardelijk weg-netwerkconform**, **21 blijven onbevestigd**. [De gecombineerde GraphHopper-buswegen als GeoJSON](../sources/amb/GH_combined_bus_road_geometry/GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson) staan naast de [bronvergelijking en herkomst per segment](../sources/amb/GH_combined_bus_road_geometry/GH_road_candidate_selection_provenance.csv).

Na een nieuwe [volgordeanalyse met mogelijke herhaalde passages op dezelfde straat](../sources/amb/GH_combined_stop_order_QA/summary.md) blijken **7.842 van de 9.020 haltebezoeken voorlopig geometrisch en qua volgorde passend** (4.570 via een meerduidige GH-wegpassage en 3.272 met een eenduidige wegpassage). Er zijn **1.178 controlepunten**: 554 haltes zonder passende GH-buswegpassage binnen 75 m, 177 haltes op 45–75 m afstand, 398 op routegedeelten die onvoldoende aansluiten op KMZ en 49 met onopgeloste volgordesprongen. Van de eerste 852 haltes op meer dan 45 m van de GH-busweg blijven na de geconsolideerde geometrie **739** over (113 minder). Van de eerste 144 mogelijke achteruitlopende projecties zijn 117 na de eerste meervoudige-passagecontrole opgelost of afgezwakt; op de nieuwe geconsolideerde geometrie blijven **49 signalen** over. Dit betekent niet dat die 49 gegarandeerd verkeerd zijn: kruisingen en rondritten vergen broncontrole.

**Nieuwe kaartbestanden voor gericht vervolgonerzoek:** [alle 1.178 stopproblemen](../sources/amb/GH_combined_stop_order_QA/GH_unresolved_stop_location_issues_REVIEW.geojson), [de 49 volgordeproblemen](../sources/amb/GH_combined_stop_order_QA/GH_unresolved_stop_order_49_points.geojson), [de 21 blijvend afwijkende wegroutedelen](../sources/amb/GH_combined_stop_order_QA/GH_road_segments_differing_from_KMZ_REVIEW.geojson) en de [prioriteitenlijst per patroon](../sources/amb/GH_combined_stop_order_QA/GH_route_review_priority_by_pattern.csv). Er zijn **43 patronen met P1-controleprioriteit** op basis van volgorde-, weg- of bronafwijkingen. De andere patronen zijn nog niet automatisch publicatieklaar.

Dit werk bevestigt busprofiel-wegberijdbaarheid volgens het GraphHopper-wegennet van 25 oktober 2026, **niet de wettelijke AMB-tracering of echte haltebediening**. Alle originele 9.000 SIU/KMZ-bezoeken en de 20 overgebleven GH-kandidaten blijven staan, alle SIU-stop_ID's zijn behouden en geen stop_sequence is automatisch gewijzigd. Geen nieuwe OSM-query's, geen dienstregeling, geen tripgrenzen, geen productie-GTFS-mutaties. Het private endpoint is niet vastgelegd; in documentatie wordt uitsluitend verwezen naar de [publieke GraphHopper-API](https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md).


## Update 3 november 2026 — ruisreductie in concept-v3

De [geslaagde clean-v3 Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41639746032) heeft alle op verzoek gemarkeerde nieuwe GraphHopper-haltepassages uit een **afzonderlijke concept-v3** uitgesloten. De eerdere 39 QA-signalen waren **26 herhaalde fysieke SIU-stop-ID's** plus **13 te korte paren van twee GH-toevoegingen** (26 bezoeken); zeven bezoeken vielen in beide groepen. Daarom zijn er **45 verschillende nieuwe GH-haltebezoeken** uitgesloten en blijven **20 van de oorspronkelijke 65 GH-kandidaten** over.

De [gehele concept-v3 met nieuw aaneengesloten stopvolgnummer](../sources/amb/provisional_trip_stop_order_v3_clean/candidate_trip_stop_sequences_v3_CLEAN_NO_TIMES_NOT_GTFS.csv) telt **9.020 bezoeken**. Alle 9.000 oorspronkelijke SIU/KMZ-haltebezoeken zijn behouden, inclusief hun relatieve volgorde. De [lijst met alle 45 uitgesloten GH-kandidaten en de concrete reden](../sources/amb/provisional_trip_stop_order_v3_clean/excluded_GH_candidates_45_WITH_REASONS.csv), [de twintig resterende kandidaten](../sources/amb/provisional_trip_stop_order_v3_clean/remaining_GH_candidates_20_with_v3_sequence.csv) en [QA per onderzoekstrip](../sources/amb/provisional_trip_stop_order_v3_clean/route_pattern_cleaning_QA.csv) blijven reproduceerbaar.

Dit is ruisreductie in onderzoeksstaging, **geen bewijs dat de uitgesloten locaties niet als halte worden bediend**. Een terugkerend fysiek stop-ID kan bij een rondrit een legitieme tweede passage zijn. Fysieke SIU-haltes, originele bronstaging, concept-v2 en productie-GTFS zijn niet gewijzigd; geen reistijden berekend.


**Aanvullende onafhankelijke controle (3 november 2026):** [GraphHopper-uitgebreide conceptcontrole](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41638603524) reproduceert exact **9.000 + 65 = 9.065** haltebezoeken over **70** patronen en **60** routevarianten. Bij de voorlopige invoeging verminderen de gaten van meer dan 2 km langs de KMZ van **73 naar 57**; dit is een geometrische indicatie, geen bewijs van nieuwe haltebediening. De [extra QA](../sources/amb/gh_expanded_stop_concept/summary.md) signaleert **7** opeenvolgende haltebezoeken met een nieuw kandidaatpunt binnen **60 m**; de oorspronkelijke v2-QA hanteert 115 m en signaleert **13** paren. De [provisional_trip_stop_order_v2](../sources/amb/provisional_trip_stop_order_v2/summary.md) blijft de primaire conceptversie; de GH-expanded-output is een aanvullende controle. Er zijn geen GTFS-publicatiebestanden gewijzigd.

## Update 3 november 2026 — concept-v2 trip-haltevolgordes met 65 GraphHopper-toevoegkandidaten

De [geslaagde GitHub Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/workflows/build-amb-GH-stop-order-v2.yml) voegt de **65 bestaande SIU-fysieke haltebezoeken** die bij de vorige GraphHopper-busbeoordeling als toevoegkandidaat werden gemarkeerd samen met de **9.000 bestaande** KMZ-/ArcGIS-onderzoeks-stopbezoeken. De **concept-v2-lijst bevat 9.065 voorlopig geordende stopvisits** verspreid over 70 onderzoeksritpatronen; 19 daarvan hebben nieuwe kandidaten. Er zijn **50 verschillende bestaande SIU stop-ID's onder de 65 toevoegingen**; 26 van de 65 nieuwe passages gebruiken een stop-ID die elders in dezelfde rit al voorkomt (mogelijk legitieme rondrit/terugpassage, controleren). Er zijn **13 paren met aangrenzende bezoeken binnen 115 meter** voor controle op overbodige stops.

De [complete concept-stopvolgorde met nieuwe stop_sequence](../sources/amb/provisional_trip_stop_order_v2/candidate_trip_stop_sequences_v2_NO_TIMES_NOT_GTFS.csv) bewaart alle oorspronkelijke haltebezoeken in hun relatieve volgorde en voegt de nieuwe kandidaten tussen de door de originele gap-analyse aangewezen ankerhaltes in. [Alle 65 invoegingen en hun nieuwe positie](../sources/amb/provisional_trip_stop_order_v2/new_GH_addition_candidates_65_with_concept_position.csv), [QA per ritpatroon](../sources/amb/provisional_trip_stop_order_v2/trip_pattern_new_stop_counts_QA.csv) en [korte opeenvolgende halteafstanden](../sources/amb/provisional_trip_stop_order_v2/close_adjacent_stop_visits_REVIEW_ONLY.csv) staan afzonderlijk in de repository.

**Deze concept-v2 is geen bewijs van werkelijke haltebediening door de exploitant en geen publiceerbare GTFS.** Hergebruik van een fysiek stop_id bij meerdere routes is normaal; een herhaald stop_id binnen één rondrit kan een tweede passage betekenen. Er zijn geen nieuwe stop-ID's aangemaakt, geen officiële trips.txt of stop_times.txt aangepast, en geen reistijden berekend. Volgende stap: controles op korte afstanden, herhaalde passages, juiste A/B-variant en operationele ritgrenzen; daarna GraphHopper voor rijtijden.


## Update 3 november 2026 — alle 125 GraphHopper-busroute-haltealternatieven geclassificeerd

De [geslaagde classificatie-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41636303001) heeft de bestaande 125 halte-kandidaten uit de 73 GraphHopper-busroutegaten in **65 toevoegkandidaten**, **24 mogelijke rijrichtings-/toegangsconflicten** en **36 onzekere kandidaten** ingedeeld. **47 van de 80 kandidaten die door de SIU-naamsrichting niet pasten, zijn weer toevoegkandidaat** omdat GraphHopper een route langs de officiële KMZ-corridor met geringe omweg vindt. Zonder curbside- of juridische stopbedieningscontrole zijn dit geen definitieve haltes.

De berekening gebruikt de opgeslagen **KMZ-waypoint-begrensde GraphHopper-busroutes**, niet alleen de kortste A-B-route, want die kan de officiële corridor overslaan. Voor toevoegkandidaten gebruiken we maximaal 300 meter extra, omwegfactor maximaal 1,12, minstens 70% van de berekende route op maximaal 50 meter van de KMZ, een road snap van maximaal 15 meter en een bestaande SIU-fysieke stop-ID. Onbetrouwbare brongeometrie (historische ArcGIS-fallback en officiële A/B-labelconflicten) blijft apart gemarkeerd. Grote omwegen geven alleen **een mogelijk richtingsconflict**, niet het bewijs van eenrichtingsverkeer.

Bestanden: [volledige GH-kandidaatbeoordeling](../sources/amb/graphhopper_stop_classification/GH_bus_stop_candidate_decisions_125.csv), [voorlopige plaats binnen de bestaande trip-haltevolgorde](../sources/amb/graphhopper_stop_classification/proposed_insertion_order_NO_TIMES_REVIEW_ONLY.csv), [resultaten per routevariant](../sources/amb/graphhopper_stop_classification/GH_bus_stop_classification_by_route.csv) en [methodologie en tellingen](../sources/amb/graphhopper_stop_classification/summary.md).

De resultaten bestrijken **29 routevarianten met haltekandidaten**; ze verklaren dus niet automatisch alle routehiaten. Er zijn **geen nieuwe GraphHopper- of Overpass-aanvragen** uitgevoerd. Er zijn **nul nieuwe fysieke haltes, nul automatische stop_sequence-wijzigingen en nul publiceerbare GTFS-ritpatronen** gemaakt.


## Update 3 november 2026 — geen nieuwe OSM-query; bestaande haltes bewaren voor GraphHopper-richtingstoets

De [geslaagde staging Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41627896318) gebruikt uitsluitend de reeds ontvangen OSM-export en bestaande SIU-haltepunten. **0 nieuwe Overpass-query's.** De 73 eerder ontdekte route-haltegaten bevatten 38 segmenten zonder SIU-alternatief. Uit de bestaande 34 niet-geclassificeerde OSM-instapkandidaten komen **14 route-gap-kandidaatverwijzingen** naar voren, verdeeld over **9 van die 38 SIU-lege gaten**. De overige **29 gaten** hebben in beide reeds aanwezige bronnen geen kandidaat.

Er is nu een [gezamenlijke kandidaatpool](../sources/amb/gap_direction_staging/existing_SIU_OSM_direction_candidates_for_GraphHopper.csv) met **125 route-gap-kandidaatverwijzingen**: 111 bestaande SIU-kandidaten, en 14 verwijzingen naar al bekende OSM-objecten. **80 SIU-kandidaten** waren eerder door de KMZ-naamsrichtingsheuristiek als tegengesteld beoordeeld; ze blijven voor de latere **GraphHopper-eenrichtingsweg-, rijbaan- en instapzijdecontrole** beschikbaar in plaats van definitief afgewezen. Voor sommige OSM-objecten ontbreekt een SIU-fysieke stop_id; die behouden hun OSM-ID en zijn niet als nieuwe GTFS-halte aangemaakt.

De [controle per gat](../sources/amb/gap_direction_staging/gap_review_with_existing_OSM_snapshot.csv) bevat de eerste en laatste reeds toegewezen SIU-stop_ID's plus de kandidaten daartussen. [Kaartpunten als GeoJSON](../sources/amb/gap_direction_staging/existing_source_direction_candidates.geojson) geven positie en herkomst. Geen trip stop_sequence, GTFS-halte, aankomsttijd of vertrektijd gewijzigd. GraphHopper is nog niet aangeroepen.


## Update 3 november 2026 — grote route-haltegaten en gefragmenteerde shapes beoordeeld

De [geslaagde QA Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41625987637) heeft de 60 routevarianten zonder eigen SIU-haltevolgorde verder beoordeeld. De 39 routes met een grootste tussenhalteafstand boven 2 km hebben samen **73 concrete gaten**: **38** zonder bestaande SIU-halte binnen de onderzoekscorridor, **18** met SIU-locaties op 25–35 m van de shape en **17** waar alleen haltes met tegengestelde richtingsaanduiding in de buurt liggen. Deze aantallen zeggen niets definitiefs over de daadwerkelijke haltebediening: een lang niet-stoppend wegdeel kan correct zijn.

[De exacte 73 gap-corridors staan als GeoJSON](../sources/amb/missing_siu_trip_stop_patterns/gap_corridors_for_review.geojson), samen met [111 alternatieve, bestaande SIU-haltepunten](../sources/amb/missing_siu_trip_stop_patterns/SIU_stop_alternatives_inside_gaps_REVIEW_ONLY.geojson) en [alle 73 bron-/reviewregels](../sources/amb/missing_siu_trip_stop_patterns/stop_gaps_over_2km_review.csv). De [prioritaire controlelijst](../sources/amb/missing_siu_trip_stop_patterns/route_gap_priority_queue_60.csv) begint met COOTRANTICO B4 (max. 22,36 km zonder geselecteerde halte), LOLAYA B10 (11,25 km), TRASALIANCO D18 (8,43 km) en SOBUSA B18-B (8,22 km). Deze hiaten moeten tegen OSM-wegen en bronstraten worden getoetst; geen automatische stopfabricatie.

De drie [routegeometrieën met afzonderlijke onderdelen](../sources/amb/missing_siu_trip_stop_patterns/fragmented_shape_route_summary.csv) zijn COOLITORAL A4 (6), COOLITORAL PT2 met gemarkeerde oude ArcGIS-fallback (4) en LOLAYA D8 met oude ArcGIS-fallback (7). De [eindpuntafstanden](../sources/amb/missing_siu_trip_stop_patterns/shape_fragment_join_candidates_REVIEW_ONLY.csv) tonen **9 mogelijke verbindingen binnen 80 m**, maar geen geverifieerde rijrichting of segmentvolgorde. Er zijn **25 routes met 59 onderliggende rechte polyline-randen langer dan 800 m**; zulke ruwe geometrie kan legitiem zijn of extra broncontrole vergen.

**Geen enkele bestaande stop_sequence, stop_id, trip, shape of timetable is automatisch aangepast.** Reistijden blijven voor later, met GraphHopper. Alle nieuwe resultaten zijn onderzoeksdata, niet de publiceerbare GTFS.


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
