# Barranquilla SIU — vervolgonderzoek alle 21 open routekoppelingen

**Datum:** 3 november 2026. **Repository:** `ColombiaTransit/gtfs-barranquilla-urbanas`. **Status:** onderzoeksresultaten, nog geen definitieve juridische route-toewijzing en geen volledige GTFS.

De [GitHub Action Review all unresolved SIU to AMB route links](../.github/workflows/review-siu-open-route-links.yml) is voor alle **21** openstaande SIU-itineraries uitgevoerd, inclusief PT4/PT5. De [laatste geslaagde run](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41603387801) heeft het volledige [reviewregister](../sources/siu/open_route_review/open_21_route_crosswalk_review.csv) weggeschreven. De **12 eerdere sterke geografische routekoppelingen** blijven in hun afzonderlijke stagingbestand staan.

## 1. Resultaat per categorie

| Categorie | SIU-itineraries | Uitkomst |
|---|---:|---|
| Eén vervoerder, één plausibele niet-A/B AMB-code | **8** | **Voorlopig basisroutevoorstel**, 1.620 geordende SIU-stops, juridisch nog te vergelijken |
| Eén gemeenschappelijke SIU-lijst voor meerdere vervoerders | **8** | Dezelfde lijst **niet** blind vermenigvuldigen tot GTFS-route-/ritpatronen per vervoerder |
| A/B-routevarianten zonder wettelijke variantcrosswalk | **3** | Eén SIU-lijst kan niet zonder bewijs naar één juridische A- of B-variant |
| PT4/PT5 met **tegenstrijdige titel- en vertrekpuntaanwijzingen** | **2** | Beide basisroute- en A/B-koppelingen expliciet geblokkeerd tot de juiste 2026-pilotstraattrajecten zijn gecontroleerd |
| **Totaal** | **21** | Ieder geval beoordeeld; **0 nieuw juridisch definitief bevestigd** |

De scheiding is bewust strenger dan automatisch de dichtstbijzijnde 2019-GIS-lijn nemen.

## 2. COOLITORAL PT4/PT5 — prioriteit 1

| SIU-weergavenaam | Halteregels | Titelvolgorde suggereert | Terminal uit besluit 192-2025 suggereert | Status |
|---|---:|---|---|---|
| **VIA 40 CIRCUNVALAR** | 124 | PT4-4104 | **PT5-4105** | Tegenstrijdig |
| **CIRCUNVALAR VIA 40** | 132 | PT5-4105 | **PT4-4104** | Tegenstrijdig |

**Bewijs A (primaire vergunning 192-2025):** [originele AMB-PDF, pagina's 30–33](https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-METROPOLITANA-No.-192-2025.pdf), tabel per route en originele afbeeldingspagina's bekeken. Deze vergunning noemt de titel **PT4 `Vía 40 – Circunvalar – Circular`**, maar beschrijft een dispatchterminal **Calle 17 con Carrera 30**. **PT5** heet `Circunvalar – Vía 40 – Circular`, met dispatchterminal **Vía 40 No. 51-310**. Dit staat nu apart in [het herleidbare bronregister](../sources/amb/details/coolitoral_192_2025_pt4_pt5_terminals_verified_2026-11-03.csv).

**Bewijs B (SIU-2026):** SIU `CIRCUNVALAR VIA 40` begint in de aangeleverde complete lijst bij `CALLE 17 CON CARRERA 28 (NS)` en eindigt bij `CARRERA 30 CON CALLE 12 (EO)`. SIU `VIA 40 CIRCUNVALAR` begint bij `VIA 40 CON CARRERA 53B (SN)` en eindigt bij `PASTAS COMARICO (VIA 40 - SN)`. Het SIU-beginpunt lijkt dus bij de **andere** 2025-dispatchterminal te horen dan het legale routenaamvolgorde-label. De volledige dienst kan bovendien een circulair traject zijn: het eerste SIU-haltepunt is niet automatisch een formeel dispatchterminal. Dit is daarom **een conflict tussen aanwijzingen**, geen bewezen fout in één van de datasets.

**Bewijs C (resolutie 256-2026):** de [gecurateerde vergunningsregels](../sources/amb/details/resolucion_256-2026.csv) onderscheiden **vier legale itineraries**, namelijk PT4-A, PT4-B, PT5-A en PT5-B, elk met **9 minuten spits en 14 minuten dal**. Volgens het [AMB-resolutieoverzicht](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/) bestaat het officiële document **256-2026 PILOTO**. Het volledige originele PDF-bestand is in onze onderzoekskopie **nog niet verifieerbaar**, zodat de **straatbeschrijvingen en eventuele nieuwe terminals van de 2026-pilot** ontbreken. De pilot is eerder vastgelegd met start **22 juni 2026** en duur **6 maanden**, met mogelijkheid tot verlenging; die geldigheid moet later opnieuw worden getoetst.

**Stopvolgordecontrole:** de twee SIU-lijsten delen bij vergelijking van exacte GPS-posities op zes decimalen **0 punten**, en slechts **1 identieke genormaliseerde haltenaam**. Dat ondersteunt dat SIU twee heel verschillende patronen toont. Het zegt **niet** welke van vier A/B-patronen daarbij horen.

**Praktisch besluit:** noch de twee basisroutecodes noch de vier A/B-ID's worden nu als bevestigd aangewezen. De [PT4/PT5-controlefile](../sources/siu/open_route_review/pt4_pt5_pilot_specific_review.csv) bewaart beide hypotheses. Voor de volgende juridische stap moet het *originele* 256-2026-besluit worden opgehaald en de route- en A/B-straatverlopen één voor één vergeleken met SIU.

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

1. **256-2026 origineel:** PT4/PT5 juridisch actuele tracés en A/B, oude terminal-tegenspraak oplossen.
2. **210-2026 / 192-2025:** PT2/PT3 A/B-koppeling en terminal-/rijrichtingcontrole.
3. **COOTRAB 358-2024:** C5/C6 en alle straatsegmenten bij de 8 voorlopige routes tegen de actuele SIU-stopvolgorde leggen.
4. **LA CAROLINA / COOCHOFAL / TRANSURBAR:** overlappende routeparen of afsplitsingen verifiëren met de originele beschikking en GIS-kaart.
5. **SODETRANS / TRANSDIAZ:** per wettelijke vergunning toetsen welke partner het gezamenlijke traject exploiteert en of een eigen `route_id` en headway geldt.
6. **Daarna pas:** variantgebonden `trips.txt`, `stop_times.txt` en uiteindelijk de productie-GTFS. Tot dan blijven de voorlopige route- en haltebestanden buiten `gtfs/`.

**Er zijn 21 open dossiers doorlopen, maar niet 21 bevestigde mappings.** Het project blijft reproduceerbaar: [Review Action](../.github/workflows/review-siu-open-route-links.yml), [volledig auditbestand](../sources/siu/open_route_review/open_21_route_crosswalk_review.csv), [stand van zaken](../sources/siu/open_route_review/summary.json).
