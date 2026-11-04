# AMB — afsluiting bron- en juridische onderzoeksfase (4 november 2026)

## Besluit en reikwijdte

**De systematische onderzoeksfase wordt administratief afgesloten per 4 november 2026.** Dit is een *projectbesluit*, geen juridische verklaring dat alle vergunningen definitief van kracht zijn of dat de bussen daadwerkelijk volgens de vergunde frequenties rijden. We starten geen nieuwe algemene speurtochten naar oudere besluiten, hypothetische opvolgers, notificatiedata of ontbrekende scans. Alleen concreet nieuw primair bewijs dat een **specifieke GTFS-route, variant of frequentie** verandert kan later aanleiding geven tot een gerichte correctie.

**Bronregel:** de recentste onderzochte routegebonden AMB-resolutie is de basis voor de vergunde frequenties; bekende uitzonderingen en voorwaardelijke bepalingen blijven als bronnotitie bewaard. Piek-/dalvensters, dienstkalender en vertrekvensters zijn waar nodig expliciete modelaannames, geen door AMB bewezen feitelijke dienstregeling. Voertuigcapaciteit en formele notificatie worden niet gebruikt als algemene GTFS-releaseblokkade.

## Afgeronde broncontroles

| Dossier | Afgerond bewijs / vastgelegde keuze | Overdracht naar GTFS |
|---|---|---|
| MONTERREY | 437-2016 origineel (15 pagina's) gecontroleerd; 390-2018 is **afgesproken nieuwste gepubliceerde resolutie**; onderzoek naar latere resoluties gesloten | Vier routes B8-4124 (7/9), B11-4166 (4/6), B11-B-4192 (7/9), B12-4127 (4/6); SITP-tijdelijkheid als bronvoorwaarde |
| TRASALIANCO | 265/266/268-2010 en 408-2013 origineel visueel gecontroleerd | D12 en B19 historisch 4/6; D17 5/7; D18 7/10; moderne ID-koppeling afzonderlijke GTFS-gegevenscontrole |
| TRANSMECAR | 324-2010 origineel gecontroleerd | C17 historisch 4/6; niet zonder aanvullend bewijs als actuele dienst claimen |
| LA CAROLINA | 067-2011 artikel 2/3 en kennisgeving gecontroleerd | Traject gewijzigd; technische waarden uit 173-2010 behouden; later 199-2019 als gedocumenteerde keten |
| COOCHOFAL | 242-2025 acht tabellen en canonieke codes beoordeeld | A15-4159 en C2-B-4188; A15-4129/C2-B-4187 alleen historische bronaliassen, geen extra routes |
| COOTRANTICO | 025-2011 oorspronkelijke artikelen 3/6 eerder gecontroleerd; 462-2025 laatste bekende acht-route-besluit en slotartikelen gecontroleerd | Oude foutieve 025-PDF-link niet als nieuw onopgelost document presenteren |
| COOLITORAL | 192-2025, 199-2025, 210-2026 en 256-2026 in bronketens; C19 is codecorrectie, geen nieuwe route | PT4/PT5-pilot 22 juni t/m 21 december 2026; geen verlenging bewezen; A/B en gedeelde corridors niet dubbeltellen |
| SOBUSA | 082-2026 B18-variantgegevens na 466-2025 gedocumenteerd | B18 A/B elk 10/12, gemeenschappelijke sectie 5/6; corridor niet als afzonderlijke variant publiceren |
| EMBUSA | 010-2026 B9-4125 4/6 gedocumenteerd | 00:00–24:00 vraagafhankelijk, geen automatisch nachtaanbod |
| COOTRAB / COOLITORAL | Gedeelde A1-exploitatie vastgesteld | Eén virtuele samengestelde agency voor identieke gedeelde variant; oorspronkelijke vervoerders herleidbaar houden |

De bovenstaande afsluiting geldt voor **de gedocumenteerde onderzoekswerkzaamheden**, niet als claim dat alle oudere beschikkende artikelen uit de volledige AMB-inventaris zijn geverifieerd.

## Vastgelegde beperkingen — niet als heropeningsopdracht

- COOTRAB **C5-4135 versus C5-4136**: tegenstrijdige officiële vermeldingen blijven zichtbaar; 378-2023 en historisch KMZ ondersteunen 4136, een latere omleidingscirculaire noemt 4135. Behandel als **gericht GTFS-code-/geometrieconflict**, niet als reden voor algemeen juridisch onderzoek.
- **448-2025**: toepasselijke routes niet vastgesteld. Geen automatische wijziging van routes, vergunningen of frequenties op basis van een niet-toegewezen besluit.
- **COOLITORAL 256-2026**: pilotduur begrensd; geen veronderstelde verlenging na 21 december 2026. Tijdgebonden GTFS-registratie moet de bronbeperking respecteren.
- **MONTERREY 390-2018**: tijdelijke regeling onder SITP-voorwaarde; de projectkeuze dat dit het nieuwste gepubliceerde besluit is, bewijst geen actuele uitvoering.
- Ontbrekende notificatie-/bezwaardata, mogelijke latere niet-gevonden wijzigingen en actuele ritwaarnemingen zijn **onbekend**, niet stilzwijgend bevestigd.
- De bestaande historische registers kunnen nog labels `open` of `blocker` bevatten die bij deze sluitingsbeslissing niet meer als **onderzoekstaak** gelden. Dit document is het besluitregister; automatische regeneratie moet de sluitingsstatus respecteren.

## Overdracht aan GTFS-bouwfase

**Wel uit te voeren:** stop-ID's en naamnormalisatie, haltvolgorde, routegeometrie (KMZ waar beschikbaar; anders routering), patroon-/richtingidentiteit, toewijzing van A/B- en gedeelde corridors, dienstvensters met expliciete aannames, week-/feestdagenkalender, `trips.txt`, `stop_times.txt`, `frequencies.txt`, MobilityData-validator en correctie van concrete feedfouten.

**Niet opnieuw uitvoeren zonder specifiek nieuw bewijs:** brede AMB-resolutiezoektochten, opnieuw OCR'en van gecontroleerde PDF's, speculatieve notificatieonderzoeken, dubbel opnemen van dezelfde gedeelde ritten, of routes als actueel verklaren op grond van uitsluitend historische vergunningen.

## Bewijsregisters

- `docs/amb_monterrey_437_2016_original_review_2026-11-04.md`
- `docs/amb_ocr_visual_verification_results_2026-11-04.md`
- `docs/amb_legal_status_audit_2026-11-04.md` (historische auditmomentopname, niet de actuele werklijst)
- `sources/amb/remaining_13_open_issues_2026-11-02.csv` (oude werkvoorraad, inmiddels deels gesloten)
- `sources/amb/company_completion_backlog_2026-11-02.csv`
- `sources/amb/legal_validity_ocr_review/priority_legal_decision_chains.csv` (historische auditketens, niet automatische GTFS-blokkades)

**Onderzoeksfase: administratief gesloten. GTFS-productiefase: nog niet gevalideerd of vrijgegeven.**

## Generatorcorrecties (4 november 2026)

De auditgenerator `scripts/audit_amb_legal_ocr_priority.py` is aangepast: MONTERREY 437-2016 staat als origineel geverifieerd, COOTRANTICO 025-2011 wordt niet meer als ontbrekend origineel aangemerkt, en de gegenereerde prioriteitsregels verwijzen voor de volgende fase naar dit afsluitregister en de GTFS-overdracht. Commits: `c569a98`, `80d1e1b`, `b73b7da`.

**Controlegrens:** de generatorwijzigingen zijn gecommit, maar een nieuwe GitHub Actions-run ter verificatie van de gegenereerde bestanden is nog niet uitgevoerd. De historische tekstkolommen blijven bronbevindingen; de werkstatus `research_closed_gtfs_handoff` is leidend. Een bestaande statische CSV wordt pas bij een volgende succesvolle auditrun opnieuw gegenereerd.
