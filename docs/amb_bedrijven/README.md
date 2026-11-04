# AMB Barranquilla urbanas — 23 vervoerders, bronnen en frequenties

**Peildatum 2 november 2026.** Dit indexdossier maakt duidelijk welke bedrijven inhoudelijk zijn behandeld en waar juridische of operationele controles nog open staan.

De hybridemethode: **GitHub Actions** voor bron-PDF's en OCR, **inhoudelijke analyse** van routebesluiten, routevarianten, frequenties en geldigheidsperioden, vervolgens expliciete vervolgacties zonder fictieve waarden.

## Besluit 3 november 2026 — AMB-2020 vertrektijden zijn een aanvaard voorlopig GTFS-model

De gebruiker heeft besloten de eerste en laatste dispatch-tijden van de AMB-routekaarten uit **juli 2020** voor de huidige model-GTFS **voorlopig te gebruiken**. De aanname is omkeerbaar: zodra een betere officiële routebron wordt gevonden, vervangen we per route het vertrekvenster en bewaren we bronjaar en oorspronkelijke waarden. De vertrekuren worden **niet voorgesteld als officieel bevestigd voor 2026**.

- [**83 historische routevensters → voorlopig model (78 compleet)**](../../sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv).
- [**44 routekandidaten → 38 bruikbare voorlopige vensters, 35 met volledige vergunningsfrequenties**](../../sources/amb/gtfs_route_service_windows_assumed_2026-11-03.csv).
- [**138 werkdag-spits/dalperiode-kandidaten**](../../sources/amb/gtfs_weekday_frequency_period_candidates_2026-11-03.csv). Hiervan zijn **15 periodevoorstellen gedeelde corridorwaarden**, dus nog niet zonder itinerary-splitsing als patroonfrequentie bruikbaar.
- [Volledig tijdvakkenbeleid, inclusief vervangingsregels](../amb_peak_offpeak_model_2026-11-03.md).

Voorlopig **maandag–vrijdag**: 07:00–09:00 en 17:00–20:00 piek; elders binnen de aangenomen diensturen dal. **Vijf bronregels hebben geen bruikbare laatste vertrektijd; die blijven leeg**. Weekenden, feestdagen, haltes, shapes en afzonderlijke A/B-routes blijven buiten deze aanname. Frequencies end_time is exclusief; de laatste dispatch uit de poster moet bij ritgeneratie apart correct worden verwerkt. Voertuigcapaciteit negeren we.

## Historische AMB-tijden voor eerste/laatste vertrek (2020)

Een afzonderlijke officiële [AMB-publicatie van **17 juli 2020**](https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/) bevat **24 routekaarten** met vertrekvensters en veelal frequenties. Deze bron is volledig uitgelezen via de [geslaagde Action-run 41588049698](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41588049698), met **24/24 unieke originele beelden**.

- [Volledig AMB-vertrektijdenregister, 84 regels en 83 unieke bedrijf-routes](../../sources/amb/amb_2020_first_last_dispatch_times_verified.csv).
- [Koppeling aan nieuwste onderzoeksfrequenties: 42 exact, 1 codealias, 1 zonder match](../../sources/amb/amb_2020_vs_resolution_route_dispatch_matching.csv).
- [Historische publicatieanalyse en data-afwijkingen](../amb_2020_first_last_departures_research_2026-11-03.md).

**Beleid:** het jaar **2020 is verplicht als bronperiode**. De oude eerste/laatste vertrekken zijn niet bewezen geldig in 2026; ze mogen als afzonderlijk gemarkeerde *dienstvenster-modelaanname* worden voorgesteld maar niet zonder besluit worden ingevoerd als officiële huidige tijden. Het huidige resolutie-interval blijft leidend. **Vijf oude kaarten bevatten in de laatste-vertrekkolom een ongeldig AM-achtervoegsel; deze waarden staan niet in de bruikbare eindtijdkolom.**

## Vastgesteld model voor werkdagspits en -dal (3 november 2026)

We hanteren voortaan voor **maandag t/m vrijdag, lokale tijd Barranquilla**: **07:00–09:00 spits**, **09:00–17:00 dal**, **17:00–20:00 spits**; voor overige uren geldt **dal uitsluitend binnen de diensturen van de route**. Dit is een **expliciete ColombiaTransit-modelaanname**, geen AMB-bepaling. Weekend/feestdagroosters, eerste en laatste vertrek blijven apart te bepalen. Een resolutie met specifieke afwijkende tijdvakken gaat voor.

- [Modelafspraken met voorbeeld en voorwaarden](../amb_peak_offpeak_model_2026-11-03.md)
- [Machineleesbare periodegrenzen](../../sources/amb/gtfs_peak_offpeak_period_model_2026-11-03.csv)
- De [44 GTFS-routekandidaten](../../sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv) verwijzen nu naar model `AMB_WEEKDAY_0709_1720_V1` en blijven **niet** automatisch goedgekeurd als volledige feed zonder halte- en dienstvensterdata.

## Frequentiebeleid voor GTFS — officiële AMB-intervallen zijn leidend (3 november 2026)

**Projectbesluit:** neem de spits- en dalfrequenties die in de **toepasselijke AMB-resolutie** staan als de te gebruiken GTFS-bronwaarden. Een onafhankelijke controle met GPS, SIBUS, voertuigmetingen of GTFS-Realtime is **niet vereist en geen blokkade**. We claimen daarmee niet dat iedere bus in de praktijk precies op tijd rijdt; we publiceren de **officieel vergunde/geplande dienst**.

- **Controleer wel welk besluit geldt** per route (latere wijziging, ingetrokken vergunning, tijdelijke pilot met einddatum, gedeelde exploitatie). Gebruik niet automatisch het hoogste resolutienummer of de meest recente PDF als de rechtsgeldigheid onduidelijk is.
- **Gebruik exact het interval uit de oorspronkelijke tabel**, na controle van OCR/scan als de tekstlezing twijfelachtig is. Geen handmatige correctie om het aan waargenomen realiteit aan te passen.
- **Houd aparte itinerarios en gedeelde corridors uit elkaar.** Een effectief 5-minuteninterval op een overlap is niet noodzakelijk de 5-minutenfrequentie van elk individueel patroon.
- **Frequentie ≠ diensturen:** `frequencies.txt` vereist nog `start_time`, `end_time` en `headway_secs`. Als een besluit geen spits-/dal-kloktijden noemt, gebruiken we de aangenomen **werkdagmodelgrenzen 07:00–09:00 en 17:00–20:00**, met dal daartussen en daarbuiten alleen binnen feitelijke/afzonderlijk vastgelegde servicediensturen. Dit is geen officieel AMB-feit; het model is apart gedocumenteerd.
- Routegeometrie, haltevolgorde, feestdagen/werkdagpatroon, juridisch relevante pilotstatus en ontbrekende geldige besluitinformatie blijven aparte werkzaamheden. **Voertuigcapaciteit blijft buiten scope.**
- `GTFS_READY=no` in bestaande bronregisters betekent daarom **niet dat de vermelde frequentie onbetrouwbaar is**: het betekent dat andere GTFS-velden of de toepasselijke vergunningsstatus nog ontbreken.

**Geen GTFS-RT nodig** om de officiële statische frequentie te gebruiken. Real-time afwijkingen zijn een ander product.

**Voortgang bronkandidaten:** in de gecombineerde GTFS-frequentietabel staan **44 regels**, waarvan **38** complete officiële spits-/dalintervalparen hebben. De overige **6** missen ten minste één interval; deze zijn nog geen bruikbare frequentie-invoer. **4** van de 38 complete intervalparen betreffen een effectief interval op een gedeeld traject: hiervoor ontbreken nog afzonderlijke patroonspecifieke vertrektijden. `headway_secs` is voor de 38 volledige waarden exact uit minuten × 60 vastgelegd. Dit is **bronacceptatie**, nog geen volledig genereerbare `frequencies.txt` omdat de **eerste/laatste diensttijden per route** ontbreken (de algemene spits-/dalmodelgrenzen zijn nu wel gekozen).

## Afbakening GTFS — voertuigcapaciteit uitgesloten (besluit 2 november 2026)

**Voertuigcapaciteit / vlootomvang (minimaal/maximaal aantal bussen, bustypen, padrónverdeling) valt buiten de scope van deze GTFS-opbouw.** Verschillen zoals *50–60 versus 56–68 voertuigen* zijn daarom **geen GTFS-blokkade** en hoeven niet apart te worden opgelost. Ook voertuigklasse is niet nodig voor de gekozen GTFS-datalevering. De bestaande cijfers blijven in de oorspronkelijke dossiers en CSV's staan **uitsluitend als bronarchief**, maar worden niet meegenomen bij prioritering, validatie, routefrequentieberekening of het genereren van GTFS.

**Wat wél telt voor GTFS:** routecode/bedrijf, juridisch geldige route en routevarianten/richting, geometrie en haltevolgorde, spits-/dalinterval **per itinerary**, dienstvensters en kalender (werkdagen/weekend/feestdagen), de vergunde/formeel toepasselijke routeperiode en herleidbare PDF-bronnen. Voor ritgeneratie is een vergund interval zonder begin-/eindtijd niet voldoende. Route-/codefouten en ontbrekende PDF's blijven relevant; een verschil **alleen in vlootaantal** niet.

Bestaande rapporten die voertuigconflicten als 'blokkerend' markeren moeten voor **GTFS** worden gelezen met **dit scopebesluit als override**. Er worden geen bestaande brongetallen verwijderd.


## Bronaudit bijgewerkt op 3 november 2026

- [**Gatenregister met actuele status**](../../sources/amb/resolution_gap_audit_2026-11-02.csv): van de **zeven oorspronkelijk ontbrekende documenten zijn de vijf van FLOTA ÁNGULO volledig teruggevonden**. **Update 4 november 2026:** COOLITORAL 256-2026 PILOTO is na deze historische inventaris alsnog als originele PDF teruggevonden en gecontroleerd; alleen de originele PDF-link bij COOTRANTICO 025-2011 is nog aantoonbaar onjuist. De bronperiode en juridische verlengingsvraag van 256 blijven afzonderlijk open.
- **SOBUSA 307-2014**: [volledige 20-pagina-analyse](../sobusa_307_2014_analysis_2026-11-03.md), zes historische route-intervallen; Action-run **41523701666** geslaagd.
- **COOTRANTICO 108-2023**: Action-run **41523797737** geslaagd, acht OCR-pagina's en twee routebladen geverifieerd. De routewijzigingen blijven historisch en zijn later door 2024/2025-besluiten opgevolgd.
- **FLOTA ÁNGULO 6/6**: na ontdekking van de WordPress Ninja Tables-AJAX-bron zijn alle zes originele PDF's uitgepakt in [run 41582220020](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41582220020). De nieuwste **232-2025** geeft voor **A7-4112** **3 minuten spits, 5 minuten dal, 31,4 km**, met een route via Miramar en Alameda del Río. Zie [bijgewerkt bedrijfsrapport](../flota_angulo_route_frequencies_2026-11-02.md).
- [**GTFS-routedekkingsgaten**](../../sources/amb/route_coverage_gaps_2026-11-02.csv): routes en itinerarios in de AMB-routeviewer waarvoor nog geen afzonderlijk geverifieerd interval en geometrie bestaan. Geen automatische ontbrekende PDF-claim.
- Algemene pilot **448-2025**: betekenis voor specifieke routes nog uitzoeken. **Voertuigcapaciteit is buiten GTFS-scope**.

## De 13 laatst behandelde bedrijven

| Bedrijf | Aantal PDF-registraties in eerste extractiebatch | Dossier |
|---|---:|---|
| COOCHOFAL | 25 | [Analyse en open acties](coochofal_route_frequencies_2026-11-02.md) |
| FLOTA_ROJA | 6 | [Analyse en open acties](flota_roja_route_frequencies_2026-11-02.md) |
| LA_CAROLINA | 10 | [Analyse en open acties](la_carolina_route_frequencies_2026-11-02.md) |
| LOLAYA | 10 | [Analyse en open acties](lolaya_route_frequencies_2026-11-02.md) |
| MONTERREY | 12 | [Analyse en open acties](monterrey_route_frequencies_2026-11-02.md) |
| SOBUSA | 21 | [Analyse en open acties](sobusa_route_frequencies_2026-11-02.md) |
| SODETRANS | 14 | [Analyse en open acties](sodetrans_route_frequencies_2026-11-02.md) |
| TRANSDIAZ | 17 | [Analyse en open acties](transdiaz_route_frequencies_2026-11-02.md) |
| TRANSMECAR | 8 | [Analyse en open acties](transmecar_route_frequencies_2026-11-02.md) |
| TRANSOLEDAD | 5 | [Analyse en open acties](transoledad_route_frequencies_2026-11-02.md) |
| TRANSURBAR | 12 | [Analyse en open acties](transurbar_route_frequencies_2026-11-02.md) |
| TRASALFA | 8 | [Analyse en open acties](trasalfa_route_frequencies_2026-11-02.md) |
| TRASALIANCO | 11 | [Analyse en open acties](trasalianco_route_frequencies_2026-11-02.md) |

**Historische batchstand (2 november):** 13 bedrijven, **159 oorspronkelijke manifestregistraties**, **44 route- en variantregels**. De SOBUSA-307-2014-downloadfout is op **3 november** hersteld; zie de bronaudit hierboven. De tijdelijke batchinventarisatie is geen volledige juridische verificatie.

## Eerder behandelde bedrijven

| Bedrijf | Dossier |
|---|---|
| COOASOATLAN | [Onderzoeksrapport](../../docs/cooasoatlan_route_frequencies_2026-11-02.md) |
| COOLITORAL | [Onderzoeksrapport](../../docs/coolitoral_route_frequencies_2026-11-02.md) |
| COOTRAB | [Onderzoeksrapport](../../docs/cootrab_route_frequencies_2026-11-02.md) |
| COOTRANSCO | [Onderzoeksrapport](../../docs/cootransco_route_frequencies_2026-11-02.md) |
| COOTRANSNORTE | [Onderzoeksrapport](../../docs/cootransnorte_route_frequencies_2026-11-02.md) |
| COOTRANSPORCAR | [Onderzoeksrapport](../../docs/cootransporcar_route_frequencies_2026-11-02.md) |
| COOTRANTICO | [Onderzoeksrapport](../../docs/cootrantico_route_frequencies_2026-11-02.md) |
| COOTRASOL | [Onderzoeksrapport](../../docs/cootrasol_route_frequencies_2026-11-02.md) |
| EMBUSA | [Onderzoeksrapport](../../docs/embusa_b9_4125_besluitketen_2026-11-02.md) |
| FLOTA_ANGULO | [Onderzoeksrapport](../../docs/flota_angulo_route_frequencies_2026-11-02.md) |

## Centrale onderzoeksbestanden

- [**GTFS-gerichte kandidaatfrequenties zonder voertuigcapaciteit — 44 regels**](../../sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv). Officiële resolutie-intervallen zijn geaccepteerd als GTFS-bron; ontbrekende periodegrenzen/haltes blijven open.
- [Oorspronkelijke bronextractie inclusief historische vlootcijfers (alleen archief)](../../sources/amb/remaining_13_route_parameters_2026-11-02.csv).
- [PDF-/besluiteninventaris, 159 registraties](../../sources/amb/remaining_13_resolution_inventory_2026-11-02.csv).
- [41 vervolgitems uit de 13 bedrijfsdossiers](../../sources/amb/remaining_13_open_issues_2026-11-02.csv).
- [23-bedrijven-voortgangsregister](../../sources/amb/company_completion_backlog_2026-11-02.csv).

## Wat aantoonbaar klaar is en wat niet

**Klaar:** De officiële PDF's van alle 13 overgebleven bedrijven zijn systematisch doorzocht en de laatst gevonden beschikbare routefrequenties, routecodes en bronpaginanummers zijn opgenomen, met scancontrole van bepalende tabellen waar OCR fouten had. Bij COOCHOFAL zijn alle acht 2025-tabellen tegen de originele pagina's gecontroleerd.

**Nog niet klaar:** volledige rechtsgeldigheidscontrole van **iedere** historische resolutie, nog ontbrekende correcte originele PDF voor COOTRANTICO 025-2011 en de nog onvolledig gecontroleerde technische/juridische details van overige besluiten (COOLITORAL 256-2026-PDF is inmiddels hersteld), interne tegenstrijdigheden binnen besluiten, dienstvensters, kalenderdagen, haltevolgordes en GPS-geometrie. De vergunde frequenties zijn als normbron voldoende; `GTFS_READY` vereist daarnaast dienstvensters, kalender, routepatroon en haltes.

**Let op:** Een interval op een overlappend traject (bijv. B18-SOBUSA, A10-TRANSDIAZ) is niet gelijk aan de vertrekken van een individuele itinerary. Een voorwaardelijk dienstvenster `00:00–24:00 afhankelijk van vraag` is geen bewijs voor 24-uursbediening.

Er wordt geen productie-GTFS aangepast zolang deze controles ontbreken.
