# Barranquilla SIU — vervolgonderzoek alle 21 open routekoppelingen

**Datum:** 3 november 2026. **Repository:** `ColombiaTransit/gtfs-barranquilla-urbanas`. **Status:** onderzoeksresultaten, nog geen definitieve juridische route-toewijzing en geen volledige GTFS.

De [GitHub Action Review all unresolved SIU to AMB route links](../.github/workflows/review-siu-open-route-links.yml) is voor alle **21** openstaande SIU-itineraries uitgevoerd, inclusief PT4/PT5. De [laatste geslaagde run](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41605472015) heeft het volledige [reviewregister](../sources/siu/open_route_review/open_21_route_crosswalk_review.csv) weggeschreven. De **12 eerdere sterke geografische routekoppelingen** blijven in hun afzonderlijke stagingbestand staan.

## Update — origineel pilotbesluit geverifieerd en alle voorstellen samengevoegd

De oorspronkelijke [AMB-resolutie **256-2026**](https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf) is nu **volledig teruggevonden en op de oorspronkelijke zeven PDF-pagina's gecontroleerd**. OCR was niet nodig. De [vier wettelijke straattrajecten](../sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv) bevestigen: **PT4-A/B vertrekken van Calle 17 con Carrera 30**; **PT5-A/B vertrekken van Vía 40 No. 51-310**. Het besluit noemt voor alle vier 9 minuten spits/14 minuten dal. De afzonderlijke B-varianten volgen een afwijkende zijstraatroute.

Deze primaire bron **lost het SIU-coderingprobleem niet automatisch op**: `CIRCUNVALAR VIA 40` begint in SIU bij Calle 17 (terminalstraat **PT4**), maar de routebenaming past bij de officiële titel van **PT5**. `VIA 40 CIRCUNVALAR` begint bij Vía 40 (terminalstraat **PT5**), maar de titel past bij **PT4**. Eerste SIU-halte is niet per se de officiële terminal. De twee oorspronkelijke juridische PT4/PT5-termini zijn in de pilot **niet gewijzigd**.

De [nieuwe gedetailleerde SIU-straatcontrole](../sources/siu/coolitoral_256_street_audit/pt4_pt5_street_sequence_review.csv) heeft **256 SIU-halteregels** vergeleken met de vier juridische A/B-routebeschrijvingen. Alleen één van de vier genoemde PT4-B-specifieke zijstraten komt in de ene SIU-lijst als haltenaam terug; voor de andere route nul van vier. **Dat is onvoldoende voor een betrouwbare A/B-toewijzing.** De vier definitieve juridische GTFS-route-ID's blijven dus open, hoewel het bron-PDF nu verwerkt is.

Na deze onderzoeksslag staan in [één gecombineerd, niet-publiceerbaar reviewbestand](../sources/siu/open_route_review/combined_20_route_stop_candidates_NO_TIMES.csv) **20 SIU-itineraries** (12 al sterke en 8 nieuwe voorlopige koppelingen), **3.981 geordende halteregels**, met **2.394 verschillende kandidaat-stop-ID's**. De nieuwe acht zijn uitdrukkelijk *extra basisroutevoorstellen*, niet acht definitief juridisch goedgekeurde koppelingen. Het [actuele reviewregister](../sources/siu/open_route_review/open_21_route_crosswalk_review.csv) omvat **alle 21** open oorspronkelijke dossiers; daarvan zijn **13 nog niet eens aan één enkel route-ID-kandidaat toe te wijzen** (8 gedeelde operatoren, 3 A/B-gevallen, 2 PT4/PT5-conflicten). **0 nieuwe juridische eindbevestigingen**.

## 1. Resultaat per categorie

| Categorie | SIU-itineraries | Uitkomst |
|---|---:|---|
| Eén vervoerder, één plausibele niet-A/B AMB-code | **8** | **Voorlopig basisroutevoorstel**, 1.620 geordende SIU-stops, juridisch nog te vergelijken |
| Eén gemeenschappelijke SIU-lijst voor meerdere vervoerders | **8** | Dezelfde lijst **niet** blind vermenigvuldigen tot GTFS-route-/ritpatronen per vervoerder |
| A/B-routevarianten zonder wettelijke variantcrosswalk | **3** | Eén SIU-lijst kan niet zonder bewijs naar één juridische A- of B-variant |
| PT4/PT5 met **tegenstrijdige titel- en vertrekpuntaanwijzingen** | **2** | Oorspronkelijke pilot-256-straattrajecten zijn gecontroleerd; beide SIU→basisroute- en A/B-toewijzingen blijven wegens tegenstrijdige SIU-namen en startstraten geblokkeerd |
| **Totaal** | **21** | Ieder geval beoordeeld; **0 nieuw juridisch definitief bevestigd** |

De scheiding is bewust strenger dan automatisch de dichtstbijzijnde 2019-GIS-lijn nemen.

## 2. COOLITORAL PT4/PT5 — prioriteit 1

| SIU-weergavenaam | Halteregels | Titelvolgorde suggereert | Terminal uit besluit 192-2025 suggereert | Status |
|---|---:|---|---|---|
| **VIA 40 CIRCUNVALAR** | 124 | PT4-4104 | **PT5-4105** | Tegenstrijdig |
| **CIRCUNVALAR VIA 40** | 132 | PT5-4105 | **PT4-4104** | Tegenstrijdig |

**Bewijs A (primaire vergunning 192-2025):** [originele AMB-PDF, pagina's 30–33](https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-METROPOLITANA-No.-192-2025.pdf), tabel per route en originele afbeeldingspagina's bekeken. Deze vergunning noemt de titel **PT4 `Vía 40 – Circunvalar – Circular`**, maar beschrijft een dispatchterminal **Calle 17 con Carrera 30**. **PT5** heet `Circunvalar – Vía 40 – Circular`, met dispatchterminal **Vía 40 No. 51-310**. Dit staat nu apart in [het herleidbare bronregister](../sources/amb/details/coolitoral_192_2025_pt4_pt5_terminals_verified_2026-11-03.csv).

**Bewijs B (SIU-2026):** SIU `CIRCUNVALAR VIA 40` begint in de aangeleverde complete lijst bij `CALLE 17 CON CARRERA 28 (NS)` en eindigt bij `CARRERA 30 CON CALLE 12 (EO)`. SIU `VIA 40 CIRCUNVALAR` begint bij `VIA 40 CON CARRERA 53B (SN)` en eindigt bij `PASTAS COMARICO (VIA 40 - SN)`. Het SIU-beginpunt lijkt dus bij de **andere** 2025-dispatchterminal te horen dan het legale routenaamvolgorde-label. De volledige dienst kan bovendien een circulair traject zijn: het eerste SIU-haltepunt is niet automatisch een formeel dispatchterminal. Dit is daarom **een conflict tussen aanwijzingen**, geen bewezen fout in één van de datasets.

**Bewijs C (resolutie 256-2026):** de [primaire officiële bron, zeven pagina's](https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf) is inmiddels volledig gecontroleerd en bevat **vier aparte itineraries** PT4-A/B en PT5-A/B, elk met **9 minuten spits/14 minuten dal**. De [juridische straatbeschrijvingen](../sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv) staan in een gestructureerde bron-CSV. De vertrekterminals blijven **Calle 17 con Carrera 30** (PT4) en **Vía 40 No. 51-310** (PT5), dus ook de primaire pilot bevestigt het verschil tussen de letterlijke SIU-routenamen en de eerste stopstraten. Artículo Segundo start de pilot op **22 juni 2026**, duur zes maanden, eventueel verlengbaar; de eventuele verlenging is niet bevestigd.

**Stopvolgordecontrole:** de twee SIU-lijsten delen bij vergelijking van exacte GPS-posities op zes decimalen **0 punten**, en slechts **1 identieke genormaliseerde haltenaam**. Dat ondersteunt dat SIU twee heel verschillende patronen toont. Het zegt **niet** welke van vier A/B-patronen daarbij horen.

**Praktisch besluit:** noch de twee basisroutecodes noch de vier A/B-ID's worden als bevestigd aangewezen. De [PT4/PT5-controlefile](../sources/siu/open_route_review/pt4_pt5_pilot_specific_review.csv) bewaart beide hypotheses, nu tegen de **gecontroleerde primaire 256-PDF**. Voor een besluit is aanvullend **ruimtelijk/ordelijk trajectbewijs vanuit SIU** of een verifieerbare expliciete koppeling tussen SIU en het juridische route-ID nodig.

## 3. Acht aanvullende voorlopige, enkelvoudige basisroutekoppelingen

Hiermee kunnen **1.620 SIU-haltevolgorderegels** alvast in *research-staging* naar een voorlopig, bestaand `route_id` verwijzen. Dit is **niet** gelijk aan definitieve bevestiging.

| SIU-naam | Plausibele AMB-route | Huidige basis voor koppeling | Onzekerheid |
|---|---|---|---|
| LAS PALMAS (COOTRAB) | **C5-4136** | Operator, GIS, titel 358-2024 noemt Las Palmas | C6 passeert eveneens Las Palmas; slechts 71,7% GIS-dekking |
| LAS NIEVES (COOTRAB) | **C6-4137** | Operator, GIS, titel 358-2024 noemt Las Nieves | C5 passeert eveneens Las Nieves; GIS-top maar 66,7%, marge 5 procentpunt |
| CENTRO CIRCUNVALAR (TRANSURBAR) | **A14-4116** | 100% GIS-koppeling, maar D16 heeft 86,7% | Tekstueel itinerariobewijs uit 051-2017 ontbreekt |
| VIA 4O PLACA ROJA (TRASALFA) | **D14-4156** | 90% GIS, D15 80% | Oorspronkelijke D14-routebeschrijving ontbreekt |
| CALLE 17 (LA CAROLINA) | **D7-4151** | 95% GIS, D6 83,3% | Sterk overlappend netwerk, bestemmingslabels in SIU geen AMB-codes |
| SANTUARIO PRADO (EMBUSA) | **B9-4125** | Operator, GIS 76,7%, vergunning 010-2026 bevestigt B9 | Naam `Santuario Prado` staat niet in de verkorte vergunningstitel; volledige straatvolgorde controleren |
| CIRCULAR (COOCHOFAL) | **C18-4141** | GIS 100%; C9 88,3% | C18 en C9 delen traject; beslissing op straatniveau nodig |
| PUEBLO SAN PABLO CENTRO (COOLITORAL) | **C19-4178** | GIS 73,3% én vergunningstitel `Villas de San Pablo – El Pueblo – Centro`; 199-2025 corrigeert routecode | De oude GIS-kaart wijkt duidelijk deels af; vol traject moet worden geverifieerd |

Onderliggende bronbewijzen: [C5/C6 officiële routeparameters](../sources/amb/cootrab_latest_route_parameters_2026-11-02.csv), [EMBUSA B9-010-2026](embusa_010_2026_validatie.md), [COOLITORAL 192-/199-2025](coolitoral_route_frequencies_2026-11-02.md), en [gestructureerde naam-bewijsaudit](../sources/siu/open_route_review/route_title_evidence_2026-11-03.csv).

**Werkelijk toegevoegd:** [voorlopige 8× routecode-crosswalk](../sources/siu/open_route_review/provisional_base_route_code_candidates.csv) en [1.620 geordende SIU-halteregels zonder tijden](../sources/siu/open_route_review/provisional_base_route_stop_sequences_NO_TIMES.csv). De oorspronkelijke 12 sterker onderbouwde matches zijn niet overschreven; we houden verschillende zekerheidsniveaus zichtbaar.

## 4. Drie A/B-gevallen (nog onbeslist)

| SIU-weergave | Geografisch vermoedelijke basisroute | Probleem |
|---|---|---|
| MIRAMAR ALAMEDA DEL RIO (LA CAROLINA) | A16-4161 | Kan A of B zijn, zonder expliciete match |
| LAS GAVIOTAS CALLE 76 (LA CAROLINA) | A16-4161 | Mogelijk een tweede A16-patroon |
| VIA 40 MURILLO (COOLITORAL) | PT3-4103 | PT2 ook 90% vergelijkbaar; PT3 heeft aparte A/B-vergunning in 210-2026 |

De twee A16-SIU-lijsten delen **116 GPS-punten** en hun gemeenschappelijke punten komen vrijwel geheel in dezelfde volgorde voor (**114 voorwaartse** tegenover **1 omgekeerde aangrenzende vergelijking**). Dit bewijst niet dat het de juridische A- en B-patronen zijn. [Vergelijkingsbestand](../sources/siu/open_route_review/selected_siu_sequence_pair_comparison.csv).

## 5. Acht gedeelde exploitatie- of operatorgevallen

| SIU-itinerary | Geografische basiscode | Wat moet worden uitgezocht? |
|---|---|---|
| MAKRO | B17-4163 | 192-2025 noemt Makro in B17; SIU noemt **drie** vervoerders, juridische route deelt COOLITORAL en SODETRANS |
| RIOMAR AMARILLA | B13-4128 | Exploitatie SODETRANS/TRANSDIAZ, patroon en frequentie per operator |
| ROJA RIOMAR | B13-B-4189 | Betekenis van B13/B13-B en verschillende GIS-trajecten |
| SOLEDAD 2000 CORREDOR UNIVERSITARIO | C21-4182 | A/B-variant en meerdere operators |
| JUAN MINA | PT1-4101 | PT1 is historisch gezamenlijk COOLITORAL/TRANSDIAZ, SIU noemt ook SODETRANS |
| SOLEDAD CALLE 84 VILLA CAROLINA | A10-4114 | A/B en gedeelde exploitatie; let op effectieve gezamenlijke frequentie |
| VILLA SAN PABLO | PT1-4101 | Tweede SIU-Itinerary met dezelfde PT1-basiscodekandidaat |
| SOLEDAD CALLE 84 | B17-4163 (geografisch) | Beste GIS-lijn hoort bij andere operator; **geen automatische koppeling** |

Hier mogen de route-stoplijsten **niet automatisch naar alle genoemde bedrijven worden gekopieerd**. De vergunning is leidend voor welke bedrijven daadwerkelijk dezelfde code exploiteren; SIU kan operationele weergavegroepen combineren. Per bedrijf kunnen `route_id` en `frequencies.txt` verschillen terwijl `stops.txt` dezelfde fysieke halte deelt. De kopie van één routepatroon naar meerdere maatschappijen zonder bewijs zou foutieve ritten opleveren.

## 6. Aanpak resterende verificatie

1. **256-2026 origineel — uitgevoerd:** volledige PDF gevonden en A/B-straten uitgewerkt; resterend is de expliciete SIU-codekoppeling of GPS-volgordecontrole van de B-zijstraten.
2. **210-2026 / 192-2025:** PT2/PT3 A/B-koppeling en terminal-/rijrichtingcontrole.
3. **COOTRAB 358-2024:** C5/C6 en alle straatsegmenten bij de 8 voorlopige routes tegen de actuele SIU-stopvolgorde leggen.
4. **LA CAROLINA / COOCHOFAL / TRANSURBAR:** overlappende routeparen of afsplitsingen verifiëren met de originele beschikking en GIS-kaart.
5. **SODETRANS / TRANSDIAZ:** per wettelijke vergunning toetsen welke partner het gezamenlijke traject exploiteert en of een eigen `route_id` en headway geldt.
6. **Daarna pas:** variantgebonden `trips.txt`, `stop_times.txt` en uiteindelijk de productie-GTFS. Tot dan blijven de voorlopige route- en haltebestanden buiten `gtfs/`.

**Er zijn 21 open dossiers doorlopen, maar niet 21 bevestigde mappings.** Het project blijft reproduceerbaar: [Review Action](../.github/workflows/review-siu-open-route-links.yml), [volledig auditbestand](../sources/siu/open_route_review/open_21_route_crosswalk_review.csv), [stand van zaken](../sources/siu/open_route_review/summary.json).
