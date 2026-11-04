## Start 4 november 2026 — juridische besluitketens en beeldanalyse/OCR

De officiële AMB-PDF's zijn gescheiden van de juridische conclusies: automatische OCR en chronologische nummering leveren geen bewijs van rechtsgeldigheid. Een reproduceerbare [GitHub Action](../.github/workflows/audit-amb-legal-and-ocr-review.yml) bouwt een prioriteitenregister voor **13 juridische besluitenketens** en de **6 afzonderlijke OCR-/beeldanalysedossiers**. Zie de gegenereerde resultaten onder `sources/amb/legal_validity_ocr_review/` na geslaagde uitvoering.

**Nieuwe primaire juridische vergelijking:** [EMBUSA 231-2025 en 010-2026](amb_embusa_231_2025_vs_010_2026_legal_chain.md). De oudere 231-2025-periode mag voor B9 niet zonder voorbehoud naast de latere 010-2026-intervallen worden gepubliceerd. **Pilot COOLITORAL 256-2026** heeft inmiddels een teruggevonden en gecontroleerde originele PDF; alleen de eventuele verlenging en actuele geldigheidsstatus blijven open.

**Geen productie-GTFS gewijzigd.** Vlootgegevens blijven buiten scope. De OCR-actielijst blijft onafhankelijk van de reguliere bronketen.

# AMB TPC — afhandeling per bedrijf en vervolgwerk

## Projectbesluit 3 november 2026 — aangenomen eerste/laatste vertrekken

De AMB-routekaarten gepubliceerd in **juli 2020** worden vanaf nu **als voorlopige bron voor de huidige GTFS-model-diensturen** gebruikt. De bron blijft gemarkeerd als `source_period=2020-07` en `model_assumption`, niet als officieel bevestigde 2026-tijd. Een nieuwere betrouwbare bron kan deze gegevens **per route vervangen**, zonder dat alle andere routes of hun vergunningsfrequenties opnieuw moeten worden berekend.

- [**83 routevensters (78 compleet)**](../sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv).
- [**Modelmatch voor 44 routes: 38 bruikbare vensters; 35 daarvan inclusief complete piek- en dalfrequenties**](../sources/amb/gtfs_route_service_windows_assumed_2026-11-03.csv).
- [**138 kandidaatperiodeblokken**](../sources/amb/gtfs_weekday_frequency_period_candidates_2026-11-03.csv), waarvan 15 bij gedeelde corridorfrequenties en dus nog niet klaar voor individuele itinerarios.
- **Uitzonderingen:** vijf onbetrouwbare laatste vertrektijden uit de bronkaarten blijven open (TRASALFA D14/D15, COOCHOFAL C3/C9/C18); ontbrekende bronmatch TRASALFA B2-B blijft open.
- Het eerder afgesproken werkdagmodel 07:00–09:00/17:00–20:00 piek en dal daarbuiten blijft gelden; weekend, feestdagen, haltes, shapes, pilots en routevarianten moeten apart worden uitgewerkt.
- **GTFS-techniek:** laatste vertrek is inclusief; `frequencies.txt.end_time` exclusief. Per periodemodel nog het laatste vertrekmoment / tripfase correct genereren.

## Projectbesluit 3 november 2026 — frequenties uit resoluties zijn gezaghebbend

Voor de statische GTFS accepteren we de spits- en dalintervallen van het **toepasselijke officiële AMB-routebesluit als waarheid voor de geplande dienst**. Er is voor dit type vervoerder geen bruikbare GTFS-RT-feed beschikbaar; het ontbreken van realtime-waarnemingen is **geen GTFS-blokkade**. Een veldstudie, SIBUS-meting of andere observatie is niet vereist om de vergunde `headway_secs` te gebruiken.

**Nog wel nodig:** de chronologische geldigheid van de resolutie (waaronder afloop van pilots), expliciete routevariant / gedeelde trajecten, de gekozen werkdagmodel-spits/dalgrenzen, werkdag-/weekendkalenders en routegebonden eerste/laatste vertrekuren, routegeometrie, haltes en voldoende gegevens voor trips en stop_times. Als het eerste/laatste vertrek niet bekend is, mag dat niet als AMB-feit worden verzonnen: houd het ontbrekend of documenteer een afzonderlijke servicevenster-aanname. De algemene spits-/daluren zijn nu als model vastgelegd. De voorwaardelijke formulering `00:00–24:00 afhankelijk van de vraag` is geen officieel bevestigd nachtrooster.

**Voertuigcapaciteit blijft uitgesloten.** Oude rapporten met 'real-world operation confirmation required before using headways' zijn door dit beleid achterhaald; hun officiële getallen blijven geldig als bronwaarden, zonder een extra waarnemingscontrole. `GTFS_READY=no` kan blijven zolang andere noodzakelijke GTFS-invoer ontbreekt.

## Vastgestelde modeltijdvakken voor werkdagspits/dal (3 november 2026)

- **Tijdzone:** `America/Bogota` (Barranquilla, UTC−5).
- **Maandag–vrijdag:** `07:00–09:00` `hora pico`; `09:00–17:00` `hora valle`; `17:00–20:00` `hora pico`.
- **Overige uren:** uitsluitend als de route dan rijdt, de `hora valle`-frequentie toepassen.
- **Weekend en feestdagen:** nog geen algemeen model vastgelegd; routespecifieke tijden of apart vast te leggen aannames nodig.
- **Uitzonderingen:** expliciete geldige AMB-tijdvakken krijgen voorrang op dit projectmodel.
- **Niet afleiden:** een gehele 24-uursdienst; modeltijdvakken worden altijd begrensd door afzonderlijk beschikbare of aangenomen eerste en laatste vertrekken.
- **Bron:** [modeldocument](amb_peak_offpeak_model_2026-11-03.md) en [machineleesbare tijdvakken](../sources/amb/gtfs_peak_offpeak_period_model_2026-11-03.csv).

Hiermee is de keuze van algemene **spits-/dalgrenzen afgerond**. Voor `frequencies.txt` zijn nog route-dienstvensters en waar nodig afzonderlijke itinerary-regels nodig.

## Werkwijze
Per bedrijf: (1) controleer alle PDF's uit het manifest, (2) lees de beschikkende artikelen en technische tabellen, (3) leg per route vast welke besluiten wijzigingen, intrekkingen, verlengingen of pilots betreffen, (4) vergelijk besluiten chronologisch, (5) documenteer routesegmenten, haltes, frequenties en diensttijden met pagina en bron, (6) maak pas daarna GTFS-voorstellen. OCR-extractie is **geen** juridische of operationele verificatie.


## GTFS-scope: voertuigcapaciteit niet gebruiken (2 november 2026)

Per gebruikersbesluit zijn **vloot-/voertuigcapaciteit**, het aantal minimaal/maximaal vergunde bussen en voertuigklassen **buiten scope** van het GTFS-onderzoek. De historische vlootgegevens blijven als oorspronkelijke bronvermelding behouden, maar:

- **Niet** gebruiken als GTFS-acceptatiecriterium of reden om verwerking te blokkeren.
- Geen afzonderlijke werkzaamheden meer uitvoeren om tegenstrijdige wagenparkaantallen of wagenparkklassen op te lossen.
- Niet meenemen bij het afleiden van ritfrequenties; gebruik expliciete intervallen per route-/itinerary en formeel beschreven of afzonderlijk aangenomen dienstvensters.
- Routecodeconflicten, juridische geldigheidsduur, ontbrekende bronbesluiten, routegeometrie, haltes, periodegrenzen en dienstkalender **blijven relevant**.

De prioriteit van eerdere capaciteits-only issues in de dossiers vervalt voor GTFS; de getallen worden **niet uit het bronarchief gewist**.

## Bijgewerkt na de GitHub Actions van 3 november 2026

- **AMB-001 afgerond:** SOBUSA 307-2014 officiële PDF (20 p.) hersteld, geanalyseerd en aan manifest gekoppeld.
- **AMB-003 afgerond:** alle vijf ontbrekende FLOTA ÁNGULO-PDF's via herstelde Ninja Tables-AJAX-extractie opgehaald; A7-4112 laatste besluit **232-2025 3/5 min en 31,4 km**.
- **COOTRANTICO 108-2023 afgerond:** 8/8 pagina's met Spaanse OCR, B4 en B7 7/9 op scans bevestigd.
- **Bijgewerkt 4-11-2026:** COOLITORAL 256-2026 PILOTO is inmiddels teruggevonden en inhoudelijk gecontroleerd; **eventuele verlenging/eindwerking** blijft open. COOTRANTICO 025-2011 heeft nog een verkeerde PDF-link (verwijst naar 331-2010). Pilot 448-2025 moet nog op specifieke route-impact worden gecontroleerd.
- Voertuigcapaciteit blijft buiten de GTFS-scope. **De vergunde intervallen gelden als GTFS-bronwaarheid; de algemene werkdagperiodegrenzen zijn nu als model gekozen; routegebonden eerste/laatste vertrekken en weekend/feestdagkalenders moeten nog worden bepaald**.

## Voortgang
- 23 bedrijven en 274 manifestdocumenten in `sources/amb/company_completion_backlog_2026-11-02.csv`.
- 273 extracties geslaagd, 1 fout (SOBUSA 307-2014); dit zijn technische resultaten, geen gevalideerde routevergunningen.
- **EMBUSA B9-4125 bijgewerkt 4-11-2026:** artikelen 231-2025 en 010-2026 zijn op originele paginabeelden vergeleken: 231-2025 had 3/5 min en 42,5 km, 010-2026 wijzigt de route naar 4/6 min en 53,9 km. Zie [juridische ketencontrole](amb_embusa_231_2025_vs_010_2026_legal_chain.md). Historisch besluit 113-2012, actuele inwerkingtreding en eventuele nog latere besluiten blijven open.
- TRASALFA, TRANSURBAR en FLOTA_ANGULO hebben voorlopige extractie-/OCR-analyses in `docs/`. Andere bedrijven hebben een voorlopige batchinventarisatie; geen volledig artikelregister.
- Geen enkele route mag alleen op basis van dit register als actueel geëxploiteerd worden beschouwd.

## Open acties (blijven open tot bewijs is opgeslagen)
| ID | Prioriteit | Bedrijf | Werk | Afsluitcriterium |
|---|---|---|---|---|
| AMB-001 | **afgerond 3-11-2026** | SOBUSA | 307-2014 originele PDF hersteld en 20 pagina's geëxtraheerd; zes routes geanalyseerd | [Bronanalyse](sobusa_307_2014_analysis_2026-11-03.md) |
| AMB-002 | **bronherstel afgerond 3-11-2026** | COOLITORAL | Originele PDF 256-2026 gevonden; vier pilottrajecten PT4/PT5 A/B en 9/14-minutenintervallen gecontroleerd. Open: feitelijke geldigheidsduur na zes maanden / eventuele verlenging. | [Pilot-controle](siu_remaining_21_route_links_review_2026-11-03.md) en AMB-005 voor verlenging |
| AMB-003 | **afgerond 3-11-2026** | FLOTA_ANGULO | Vijf PDF's gevonden, zes totaal geëxtraheerd via Ninja Tables-AJAX | [Volledige analyse](flota_angulo_route_frequencies_2026-11-02.md) |
| AMB-004 | **deels afgerond 4-11-2026** | EMBUSA | De artikelen 231-2025 versus 010-2026 zijn op originele scans vergeleken (3/5 → 4/6 min; 42,5 → 53,9 km); 113-2012 en effectieve actuele werking blijven open. | [B9-besluitvergelijking](amb_embusa_231_2025_vs_010_2026_legal_chain.md) |
| AMB-005 | hoog | COOLITORAL | 256-2026 (pilot), 210-2026, 192-2025, 199-2025 en 264-2024 vergelijken | Per route juridisch effect + eventuele einddatum pilot |
| AMB-006 | hoog | SOBUSA | 082-2026, 466-2025, 225-2025 en eerdere wijzigingen vergelijken | Per route actuele vergunningsstatus |
| AMB-007 | normaal | alle 23 | Volledige artikelen/tabelrijen met PDF-paginaverwijzing in dossier per bedrijf | Iedere manifestresolutie heeft controleerbare conclusie of expliciete blokkade |
| AMB-008 | normaal | alle 23 | Officiële spits-/dalinterval rechtstreeks gebruiken; nog ontbrekende start-/eindtijden en kalenderdagen vaststellen of expliciet als modelaanname vastleggen | `headway_secs` uit resolutie plus herleidbare periodegrenzen voor `frequencies` / `calendar` |
| AMB-009 | normaal | alle 23 | Straattrajecten georefereren en aan haltes koppelen | Gecontroleerde richting, stopvolgorde en `shapes` |
| AMB-010 | normaal | alle 23 | Verschillen tussen OCR en scans gericht opnieuw controleren | Gemarkeerde twijfelgevallen met geverifieerde tabellen |

## Statusdefinities
- **EXTRACTED**: PDF leesbaar gemaakt; géén inhoudelijke goedkeuring.
- **REVIEWED**: beschikkende artikelen en tabellen gelezen en met bron/pagina vastgelegd.
- **LEGAL_CHAIN_CHECKED**: oudere en nieuwere besluiten vergeleken, incl. intrekkingen/pilots.
- **FREQUENCY_AUTHORIZED**: frequentie rechtstreeks uit juridisch toepasselijke AMB-resolutie, geen onafhankelijk realtime-bewijs vereist.
- **SERVICE_PERIOD_DEFINED**: begin/einde spits/dal en toepasselijke kalender zijn officieel vastgesteld of transparant als modelaanname beschreven.
- **GTFS_READY**: benodigde GTFS-velden herleidbaar en intern consistent; **vloot/capaciteit telt niet mee**.

Bedrijven worden niet als voltooid gemarkeerd voordat de vereiste stappen aantoonbaar zijn uitgevoerd. Werk aan ontbrekende scans, URL's en routegegevens wordt afzonderlijk bijgehouden zodat het onderzoek aan de overige bedrijven kan doorgaan.
