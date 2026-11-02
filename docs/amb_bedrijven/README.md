# AMB Barranquilla urbanas — 23 vervoerders, bronnen en frequenties

**Peildatum 2 november 2026.** Dit indexdossier maakt duidelijk welke bedrijven inhoudelijk zijn behandeld en waar juridische of operationele controles nog open staan.

De hybridemethode: **GitHub Actions** voor bron-PDF's en OCR, **inhoudelijke analyse** van routebesluiten, routevarianten, frequenties en geldigheidsperioden, vervolgens expliciete vervolgacties zonder fictieve waarden.

## Afbakening GTFS — voertuigcapaciteit uitgesloten (besluit 2 november 2026)

**Voertuigcapaciteit / vlootomvang (minimaal/maximaal aantal bussen, bustypen, padrónverdeling) valt buiten de scope van deze GTFS-opbouw.** Verschillen zoals *50–60 versus 56–68 voertuigen* zijn daarom **geen GTFS-blokkade** en hoeven niet apart te worden opgelost. Ook voertuigklasse is niet nodig voor de gekozen GTFS-datalevering. De bestaande cijfers blijven in de oorspronkelijke dossiers en CSV's staan **uitsluitend als bronarchief**, maar worden niet meegenomen bij prioritering, validatie, routefrequentieberekening of het genereren van GTFS.

**Wat wél telt voor GTFS:** routecode/bedrijf, juridisch geldige route en routevarianten/richting, geometrie en haltevolgorde, spits-/dalinterval **per itinerary**, dienstvensters en kalender (werkdagen/weekend/feestdagen), daadwerkelijke operationele status en herleidbare PDF-bronnen. Voor ritgeneratie is een vergund interval zonder begin-/eindtijd niet voldoende. Route-/codefouten en ontbrekende PDF's blijven relevant; een verschil **alleen in vlootaantal** niet.

Bestaande rapporten die voertuigconflicten als 'blokkerend' markeren moeten voor **GTFS** worden gelezen met **dit scopebesluit als override**. Er worden geen bestaande brongetallen verwijderd.


## Bronaudit 2 november 2026 — nog ontbrekende resoluties

- [**Geverifieerd resolutie-gatenregister**](../../sources/amb/resolution_gap_audit_2026-11-02.csv): **7** oorspronkelijke PDF-lacunes (FLOTA ÁNGULO **5**, COOLITORAL **256-2026** en COOTRANTICO **025-2011** met foutieve link), **2** te herextracteren reeds teruggevonden bronnen (SOBUSA **307-2014** en COOTRANTICO **108-2023**), plus **1** algemene pilotresolutie (**448-2025**) waarvan route-impact nog moet worden vastgesteld.
- [**GTFS-routedekkingsgaten**](../../sources/amb/route_coverage_gaps_2026-11-02.csv): extra routes/itinerarios in de AMB-visor, waarvoor nog geen apart gevalideerd frequentie- en routepatroon bestaat. Dit betekent **niet automatisch** dat er een ontbrekende resolutie is.
- De oorspronkelijke SOBUSA 307-2014-PDF (**20 pagina's**) is teruggevonden: https://www.ambq.gov.co/wp-content/uploads/2018/09/RESOLUCION_307-14-SOBUSA.pdf en de onjuiste URL is in het manifest vervangen. De nieuwe extractie is nog niet bevestigd.
- Voertuigcapaciteit is **buiten GTFS-scope** en wordt niet opgevoerd als bronblokkade.

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

**Dekking van deze batch:** 13 bedrijven, **159 manifestregistraties**, **44 route- en variantregels**, plus afzonderlijke vastlegging van openstaande juridische en operationele controles. **SOBUSA 307-2014** heeft een mislukte PDF-download; de overige bronbestanden zijn technisch geëxtraheerd, wat niet hetzelfde is als juridische controle.

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

- [**GTFS-gerichte kandidaatfrequenties zonder voertuigcapaciteit — 44 regels**](../../sources/amb/gtfs_route_frequency_candidates_no_fleet_2026-11-02.csv). Nog niet operationeel geverifieerd.\n- [Oorspronkelijke bronextractie inclusief historische vlootcijfers (alleen archief)](../../sources/amb/remaining_13_route_parameters_2026-11-02.csv).
- [PDF-/besluiteninventaris, 159 registraties](../../sources/amb/remaining_13_resolution_inventory_2026-11-02.csv).
- [41 vervolgitems uit de 13 bedrijfsdossiers](../../sources/amb/remaining_13_open_issues_2026-11-02.csv).
- [23-bedrijven-voortgangsregister](../../sources/amb/company_completion_backlog_2026-11-02.csv).

## Wat aantoonbaar klaar is en wat niet

**Klaar:** De officiële PDF's van alle 13 overgebleven bedrijven zijn systematisch doorzocht en de laatst gevonden beschikbare routefrequenties, routecodes en bronpaginanummers zijn opgenomen, met scancontrole van bepalende tabellen waar OCR fouten had. Bij COOCHOFAL zijn alle acht 2025-tabellen tegen de originele pagina's gecontroleerd.

**Nog niet klaar:** volledige rechtsgeldigheidscontrole van **iedere** historische resolutie, onvindbare PDF's (bijvoorbeeld FLOTA ÁNGULO 2025/2019 en SOBUSA 307-2014), interne tegenstrijdigheden binnen besluiten, 2026-actuele dienstregelingen, haltevolgordes en GPS-geometrie. Geen bedrijf krijgt een onvoorwaardelijke `GTFS_READY=yes` op basis van alleen deze vergunningen.

**Let op:** Een interval op een overlappend traject (bijv. B18-SOBUSA, A10-TRANSDIAZ) is niet gelijk aan de vertrekken van een individuele itinerary. Een voorwaardelijk dienstvenster `00:00–24:00 afhankelijk van vraag` is geen bewijs voor 24-uursbediening.

Er wordt geen productie-GTFS aangepast zolang deze controles ontbreken.
