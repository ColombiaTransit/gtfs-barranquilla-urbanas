# AMB resoluties — geconsolideerde GTFS-besluitketens (4 november 2026)

## Reikwijdte
Gebaseerd op reeds visueel gecontroleerde originele besluiten, de negen-documentenrun 41794757196 en bestaande route-/juridische registers. Dit is een **consolidatie van aantoonbare besluiten**, niet een bewering dat alle vervolg-PDF's of huidige dienstuitvoering gecontroleerd zijn. Wagenpark en verdeling zijn buiten scope. `current_operation_verified=no` en `gtfs_release_approved=no` voor alle onderstaande ketens.

| Exploitant / route | Laatste aangetroffen relevante besluit(en) | GTFS-relevant vastgesteld | Resterende broncontrole |
|---|---|---|---|
| COOTRANTICO B20 | 025-2011; latere 462-2025 genoemd in dossier | 025-2011 B20-4180 BARRANQUILLITA–MANGA–LOS OLIVOS–CIRCULAR; eerdere vergunningen voor deze route ingetrokken; start afhankelijk AMB-mededeling/Transmetro | 462-2025 volledige artikelen en B20-B-4191 vergelijken; actuele variant, intervallen en straatvolgorde niet afgerond |
| COOLITORAL A1, PT2–PT5, C19 | 192-2025; C19-correctie 199-2025; PT2/PT3 210-2026; PT4/PT5 256-2026 | C19-4178 is correctie, geen extra lijn. PT4/PT5 256-2026 pilot vanaf 22 juni 2026 zes maanden, A/B-varianten 9/14 min per variant volgens register; 192-2025 PT4 4,5/7 is eerdere basis en niet zonder meer nieuw uitgangspunt | 210/256 volledige varianttrajecten, ingangs- en eindvoorwaarden, eventuele verlenging pilot; overige 192-routebladen |
| COOTRAB C5/C6 en gezamenlijke A1 | 358-2024; voor A1 ook COOLITORAL 192-2025 | C5/C6 8/10 min; A1 A/B 8,5/11 per variant, gezamenlijke sectie 4,5/6; gedeelde exploitatie met COOLITORAL, geen dubbel getelde GTFS-frequentie | Latere A1-bepalingen en geometrie A/B; bewijs welke operatorcombinatie exact dezelfde variant rijdt |
| LA CAROLINA A16-4161 | 173-2010 → 067-2011 → 204-2012 → 199-2019 | 199-2019 herstructureert A16, 3,5 min piek / 5 min dal, 00–24 vraagafhankelijk; 204-2012 bevestigt circulaire en beveelt technisch onderzoek, geen zelfstandige nieuwe intervaltabel | 067/199 kaart en volledige straatvolgorde; mogelijke besluiten na 2019 |
| TRASALIANCO D17/D18, B19/D12 | D17 268-2010 → 411-2010; D18 267-2010 → 408-2013 | D17 411 corrigeert traject, 268 deels bevestigd, historische 5/7. D18 408 historische 7/10; B19 266 historische 4/6; D12 265 historische 4/6 | D18 408 versus 267 kaart/straatvolgorde; D17 volledige 411-shape; latere wijzigingen en activatie |
| SOBUSA B18, C12, C16 | 466-2025 → B18 082-2026 | B18 082: A/B ieder 10/12, gedeeld drukste deel 5/6. C12 466: A 6/9, B 3/6. C16 466: A en B 7/9. Geen optelling van gedeelde corridorfrequentie tot afzonderlijke trips | A/B-geometrie, ritfasering, feitelijke spits/dal-vensters, eventuele latere besluiten |
| EMBUSA B9-4125 | 231-2025 → 010-2026 | 010-2026 wijzigt B9, 4/6 min, route via Río Alto, 00–24 vraagafhankelijk | 231-2025 specifieke vervangen bepalingen en eventuele latere besluiten; straatvolgorde |
| COOCHOFAL A15, C2, C2-B, C3, C4, C9, C18, D20 | 242-2025; oudere 387-2018 | Acht visueel gecontroleerde intervaltabellen: A15 2,5/4; C2 6/9; C2-B 4,5/7; C3 7/10; C4 3/5; C9 7/10; C18 7/10; D20 2,5/4. **Codeconflicten:** A15-4129 versus A15-4159, C2-B-4187 versus 4188 | Codeconflicten juridisch oplossen via artikelen en latere correcties; exacte varianten/straatvolgorde |
| TRANSMECAR C17 | 324-2010 | Historisch 4/6 min volgens visuele OCR-registratie | Latere besluiten en routegeometrie/haltes, huidige status onbekend |

## Overkoepelende GTFS-regels
- Resolutiefrequenties zijn historische/vergunde bronwaarden voor hun juridische periode, geen bewijs van actuele ritten.
- `00:00–24:00` met vraagvoorbehoud bewijst geen nachtservice.
- Individuele A/B-frequenties en gecombineerde corridorintervallen apart houden; geen dubbeltelling.
- Eén samengestelde/virtuele agency bij werkelijk identieke gezamenlijke variant; operators afzonderlijk herkenbaar via attributies.
- Zonder aantoonbare tijdvakken, eerste/laatste ritten en bedieningsdagen geen definitieve `frequencies.txt`, `calendar.txt` of `stop_times.txt`.
- Onopgeloste codeconflicten blokkeren alleen de betrokken routes; niet automatisch alle andere routes.

## Resterend werk dat niet als afgerond mag worden gerapporteerd
1. Laatste en ontbrekende officiële besluiten/kennisgevingen verzamelen, vooral COOTRANTICO 462-2025, COOLITORAL 210/256-2026 en eventuele besluiten na 2019 voor LA CAROLINA.
2. Alle voor GTFS relevante artikelbladen en kaart-/straattabellen per route visueel vergelijken met opvolgers.
3. A/B-geometrie en haltevolgorde aan KMZ/OSM koppelen, conflicten oplossen.
4. Per route een versieerbare tabel met `effective_from`, `effective_to`, `source_resolution`, `headway_peak`, `headway_offpeak`, `route_variant`, `legal_status` maken.
5. Dienstkalender, piek/dal-uren en eerste/laatste vertrekken met AMB/SIU operationele bronnen vaststellen; daarna GTFS valideren.

Dit register is een **afgeronde dossierconsolidatie** maar **geen voltooide juridische eindverificatie**.
