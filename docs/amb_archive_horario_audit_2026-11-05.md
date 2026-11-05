# Gerichte horario-controle — AMB-archief 2020–2026 (5 november 2026)

**Bron:** GitHub Actions-run [42074903207](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42074903207), artifact 13439191495. De bestaande 111 succesvol geëxtraheerde PDF-teksten zijn zonder nieuwe OCR doorzocht. Twee PDF-downloads mislukten (013-2022 en 295-2025) en vallen buiten deze volledige tekstcontrole.

## Zoektermen en tellingen
- 111 succesvolle PDF's; 45 documenten met ten minste één van de gerichte termen.
- Letterlijke teksttreffers (niet het aantal documenten): `horario` 116, `hora de inicio` 3, `hora de terminación` 1, `lunes a viernes` 9, `sábado` 28, `domingo` 8, `primer despacho` **0**, `último despacho` **0**. Ook `hora pico` 9 en `hora valle` 13. Dit is een **zoektermtelling**, geen validatie van dienstregeling of volledige semantische extractie.
- De meeste routegebonden `Horario de Servicio 00:00 a las 24:00 horas`-regels bevatten `dependiendo de las necesidades de demanda`. **Vergund vraagafhankelijk tijdvenster, niet eerste/laatste vertrek, geen bewijs voor nachtdienst.**
- Veel overige `horario`-treffers gaan over ambtelijke werktijden, administratieve processen, contracten en werkdagen; niet gebruiken voor GTFS.

## Routegebonden vergunningstekst (afzonderlijk bewaren)
| Besluit | Relevantie | Tijdwaarde | Classificatie |
|---|---|---|---|
| 093-2021 | TRANSMECAR D9-C tijdelijke vergunning | 00:00–24:00 afhankelijk van vraag | permitted_demand_dependent_window |
| 094-2021 | LA CAROLINA A16-C tijdelijke vergunning | idem | permitted_demand_dependent_window |
| 108-2023 | COOTRANTICO B4/B7 | idem | permitted_demand_dependent_window |
| 270-2023 | COOCHOFAL C3/C4 | idem | permitted_demand_dependent_window |
| 188-2024 | D13 | idem (OCR fragmentarisch) | permitted_demand_dependent_window |
| 264-2024 | COOLITORAL A4 | idem | permitted_demand_dependent_window |
| 349-2024 | SOBUSA routebladen | idem | permitted_demand_dependent_window |
| 358-2024 | COOTRAB C5/C6 en gezamenlijke A1 | idem | permitted_demand_dependent_window |

## Besluit en open werk
**Geen nieuw concreet `primer despacho`/`último despacho` gevonden in de doorzoekbare tekst.** Geen vervanging van de [78 voorlopige dienstvensters](../sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv). De oorspronkelijke 2020-routeposters blijven voor die vensters de expliciet geaccepteerde modelbron; de actuele frequenties blijven uit de geldige, visueel geverifieerde resoluties komen. De vijf ongeldige poster-eindtijden blijven leeg.

Dit is een **tekstzoekcontrole**, geen volledige visuele controle van elke tabel in 111 PDF's. Onleesbare afbeeldingen kunnen niet worden uitgesloten. Alleen als een specifieke relevante pagina een aanwijzing voor echte vertrekuren heeft maar de tekst ontbreekt, is gerichte beeldanalyse gerechtvaardigd. Geen nieuwe generieke OCR.

**GTFS-mutatie:** geen; geen `frequencies.txt`, `calendar.txt`, `stop_times.txt` of bestaande modelvensters overschreven.
