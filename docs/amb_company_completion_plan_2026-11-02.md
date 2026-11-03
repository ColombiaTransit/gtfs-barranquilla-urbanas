# AMB TPC — afhandeling per bedrijf en vervolgwerk

## Werkwijze
Per bedrijf: (1) controleer alle PDF's uit het manifest, (2) lees de beschikkende artikelen en technische tabellen, (3) leg per route vast welke besluiten wijzigingen, intrekkingen, verlengingen of pilots betreffen, (4) vergelijk besluiten chronologisch, (5) documenteer routesegmenten, haltes, frequenties en diensttijden met pagina en bron, (6) maak pas daarna GTFS-voorstellen. OCR-extractie is **geen** juridische of operationele verificatie.


## GTFS-scope: voertuigcapaciteit niet gebruiken (2 november 2026)

Per gebruikersbesluit zijn **vloot-/voertuigcapaciteit**, het aantal minimaal/maximaal vergunde bussen en voertuigklassen **buiten scope** van het GTFS-onderzoek. De historische vlootgegevens blijven als oorspronkelijke bronvermelding behouden, maar:

- **Niet** gebruiken als GTFS-acceptatiecriterium of reden om verwerking te blokkeren.
- Geen afzonderlijke werkzaamheden meer uitvoeren om tegenstrijdige wagenparkaantallen of wagenparkklassen op te lossen.
- Niet meenemen bij het afleiden van ritfrequenties; gebruik expliciete intervallen per route-/itinerary en werkelijke dienstvensters.
- Routecodeconflicten, juridische geldigheidsduur, ontbrekende bronbesluiten, routegeometrie, haltes en werkelijke dienstregeling **blijven relevant**.

De prioriteit van eerdere capaciteits-only issues in de dossiers vervalt voor GTFS; de getallen worden **niet uit het bronarchief gewist**.

## Bijgewerkt na de GitHub Actions van 3 november 2026

- **AMB-001 afgerond:** SOBUSA 307-2014 officiële PDF (20 p.) hersteld, geanalyseerd en aan manifest gekoppeld.
- **AMB-003 afgerond:** alle vijf ontbrekende FLOTA ÁNGULO-PDF's via herstelde Ninja Tables-AJAX-extractie opgehaald; A7-4112 laatste besluit **232-2025 3/5 min en 31,4 km**.
- **COOTRANTICO 108-2023 afgerond:** 8/8 pagina's met Spaanse OCR, B4 en B7 7/9 op scans bevestigd.
- **Openstaande bronlacunes:** COOLITORAL 256-2026 PILOTO en de onjuiste bron voor COOTRANTICO 025-2011. Pilot 448-2025 moet nog op specifieke route-impact worden gecontroleerd.
- Voertuigcapaciteit blijft buiten de GTFS-scope. **Alle vergunde intervallen blijven onder voorbehoud van feitelijke diensttijden**.

## Voortgang
- 23 bedrijven en 274 manifestdocumenten in `sources/amb/company_completion_backlog_2026-11-02.csv`.
- 273 extracties geslaagd, 1 fout (SOBUSA 307-2014); dit zijn technische resultaten, geen gevalideerde routevergunningen.
- EMBUSA 010-2026 heeft een afzonderlijk inhoudelijk rapport in `docs/embusa_010_2026_validatie.md`; vergelijk nog met EMBUSA 231-2025 en eerdere besluiten.
- TRASALFA, TRANSURBAR en FLOTA_ANGULO hebben voorlopige extractie-/OCR-analyses in `docs/`. Andere bedrijven hebben een voorlopige batchinventarisatie; geen volledig artikelregister.
- Geen enkele route mag alleen op basis van dit register als actueel geëxploiteerd worden beschouwd.

## Open acties (blijven open tot bewijs is opgeslagen)
| ID | Prioriteit | Bedrijf | Werk | Afsluitcriterium |
|---|---|---|---|---|
| AMB-001 | **afgerond 3-11-2026** | SOBUSA | 307-2014 originele PDF hersteld en 20 pagina's geëxtraheerd; zes routes geanalyseerd | [Bronanalyse](sobusa_307_2014_analysis_2026-11-03.md) |
| AMB-002 | hoog | COOLITORAL | Resolutie 256-2026 PILOTO op officiële bedrijfsarchiefpagina: directe PDF-URL achterhalen, manifest aanvullen, extraheren en juridische status pilot bepalen | PDF + bron-URL + artikelanalyse |
| AMB-003 | **afgerond 3-11-2026** | FLOTA_ANGULO | Vijf PDF's gevonden, zes totaal geëxtraheerd via Ninja Tables-AJAX | [Volledige analyse](flota_angulo_route_frequencies_2026-11-02.md) |
| AMB-004 | hoog | EMBUSA | 010-2026 tegenover 231-2025 en 113-2012 vergelijken | Artikel-voor-artikel chronologie voor B9-4125 |
| AMB-005 | hoog | COOLITORAL | 256-2026 (pilot), 210-2026, 192-2025, 199-2025 en 264-2024 vergelijken | Per route juridisch effect + eventuele einddatum pilot |
| AMB-006 | hoog | SOBUSA | 082-2026, 466-2025, 225-2025 en eerdere wijzigingen vergelijken | Per route actuele vergunningsstatus |
| AMB-007 | normaal | alle 23 | Volledige artikelen/tabelrijen met PDF-paginaverwijzing in dossier per bedrijf | Iedere manifestresolutie heeft controleerbare conclusie of expliciete blokkade |
| AMB-008 | normaal | alle 23 | Dienstregeling/actualiteit los van vergunningsfrequentie verifiëren | Onderbouwde `calendar`, `stop_times`, `frequencies` of expliciet onbekend |
| AMB-009 | normaal | alle 23 | Straattrajecten georefereren en aan haltes koppelen | Gecontroleerde richting, stopvolgorde en `shapes` |
| AMB-010 | normaal | alle 23 | Verschillen tussen OCR en scans gericht opnieuw controleren | Gemarkeerde twijfelgevallen met geverifieerde tabellen |

## Statusdefinities
- **EXTRACTED**: PDF leesbaar gemaakt; géén inhoudelijke goedkeuring.
- **REVIEWED**: beschikkende artikelen en tabellen gelezen en met bron/pagina vastgelegd.
- **LEGAL_CHAIN_CHECKED**: oudere en nieuwere besluiten vergeleken, incl. intrekkingen/pilots.
- **OPERATION_CONFIRMED**: onafhankelijk bewijs voor huidige exploitatie en tijden.
- **GTFS_READY**: benodigde GTFS-velden herleidbaar en intern consistent; **vloot/capaciteit telt niet mee**.

Bedrijven worden niet als voltooid gemarkeerd voordat de vereiste stappen aantoonbaar zijn uitgevoerd. Werk aan ontbrekende scans, URL's en routegegevens wordt afzonderlijk bijgehouden zodat het onderzoek aan de overige bedrijven kan doorgaan.
