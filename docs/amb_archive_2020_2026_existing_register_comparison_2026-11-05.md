# Vergelijking AMB-archief 2020–2026 met bestaande bronregisters (5 november 2026)

Bronrun: [42074903207](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42074903207). De run heeft 113 PDF-verwijzingen, waarvan 111 verwerkt; de mislukte links 013-2022 en 295-2025 zijn afzonderlijke downloadproblemen. De nieuwe archiefselectie staat in [kandidaten-CSV](../data/research/amb_archive_2020_2026_route_frequency_candidates.csv). **De archiefselectie is geen leidend frequentiebestand.** Bestaande visueel geverifieerde latere beschikkingen gaan vóór historische extracties.

| Route | Nieuwe archiefbron | Reeds vastgesteld in repository | Classificatie / actie |
|---|---|---|---|
| A16-C | 094-2021 10/15 | LA CAROLINA A16-4161: 404-2023 3,5/5; A16-C is niet zonder bewijs dezelfde variant | Historische tijdelijke variant; niet samenvoegen |
| D9-C | 093-2021 10/15 | Geen gelijkwaardige actuele D9-C-vergunning in geraadpleegd centraal parameterregister | Historische aanvulling; geen actuele claim |
| B4-4120 | 108-2023 7/9; 259-2024 A/B 15/17, gedeelde sectie 7/9 | **462-2025 p8 7/9** visueel geverifieerd | Historische bevestiging van 7/9; **2025 leidend**; 2024-variantinterval niet gebruiken |
| B7-4123 | 108-2023 7/9 | **462-2025 p16 6/8** visueel geverifieerd | **Werkelijke wijziging in 2025**, niet de archiefwaarde 7/9 publiceren |
| C3-4134 | 270-2023 6,5/9 kandidaat | **242-2025 p12 7/10** visueel geverifieerd | Historisch; 2025 gaat vóór; kandidaat niet opnieuw OCR'en |
| C4-4135 | 270-2023 6,5/9 kandidaat | **242-2025 p14 3/5** visueel geverifieerd | Historisch; 2025 gaat vóór; kandidaat niet opnieuw OCR'en |
| D13-4155 | 188-2024 dal 7, piek oningevuld in kandidaten | **188-2024 p6 5/7** scan gecontroleerd in 13-bedrijvenregister | Reeds bevestigd; kandidaat aanvullen, geen nieuwe OCR |
| C7-4138 | 258-2024 3/5; 348-2026 zonder bevestigde nieuwe intervallen | **098-2026 pilot A/B elk 5/7**, 6 maanden vanaf 2 maart 2026; verlenging onbekend | 258 historische/permanente basis; pilot mogelijk verlopen; **348-2026 op artikelen vergelijken**, geen huidige frequentie kiezen |
| A8-4113 | 260-2024 3/5 | **260-2024 p5 3/5**, visueel gecontroleerd | Volledige bevestiging; geen nieuw gegeven |
| A4-4109 | 264-2024 9/11 | Geen specifieke latere routeparameter in geraadpleegd 13-bedrijvenregister | Aanvulling, juridische keten/route-ID controleren |
| B18-4175 | 349-2024 zonder betrouwbare frequentie | **082-2026 p6 A/B elk 10/12**, drukste sectie 5/6 | Historische routevermelding; 2026 leidend; gedeelde 5/6 niet als variant gebruiken |
| C11-4168 | 349-2024 kandidaat 3/5 | **466-2025 p8 3,5/5** visueel gecontroleerd | Historische kandidaat; 2025 leidend; verschil piek expliciet |
| C12-4149 | 349-2024 OCR-code kandidaat | **C12-4169** in 466-2025; p9 4149 vermoedelijke bronverschrijving; A 6/9, B 3/6, gedeelde sectie 3/5 | **Codeconflict**; geen nieuwe route C12-4149 aanmaken |
| C5-4136 | 358-2024 8/10 | **358-2024 p5 8/10** visueel gecontroleerd; kaartviewer noemt C5-4135 | Bevestiging; bestaande codeconflict blijft apart |
| C6-4137 | 358-2024 8/10 | **358-2024 p7 8/10** visueel gecontroleerd | Bevestiging; geen nieuwe waarde |
| A1-4106 | 358-2024 8,5/11 kandidaat | **192-2025** gezamenlijke COOLITORAL/COOTRAB: A 8,5/14, B 8,5/11; gedeelde sectie 4,5/6 | **2025 leidend**, 2024 niet als één A1-frequentie gebruiken; gezamenlijke agency |
| C7-4138 (348-2026) | Wijzigingsverwijzing zonder vastgestelde frequentie | 098-2026 tijdelijke pilot; 258-2024 3/5 | Open: bepaal of 348-2026 een wijziging/verlenging is, zonder vervroegde rechtsclaim |

## Conclusie
- **Reeds bekende bevestigingen:** A8, D13, C5, C6 en grotendeels B4; geen nieuwe OCR.
- **Latere bron verdringt archiefkandidaat:** B7, C3, C4, B18, C11 en A1. Niet terugzetten naar oudere intervallen.
- **Nieuwe historische aanwijzingen:** A16-C, D9-C en A4; alleen na route-identiteit en rechtsgevolg vastleggen.
- **Bronconflicten behouden:** C12-4149 versus C12-4169, C5-4135 versus C5-4136, gedeelde versus variantintervallen.
- **Gerichte resterende juridische controle:** 348-2026 C7 en eventuele opvolging van de 098-2026 pilot; 264-2024 A4. Geen automatische publicatie van een actuele dienst.
- **Niet geraakt:** SODETRANS 500-2025 is reeds door de gebruiker als geldende bron bevestigd, inclusief B13-B-4189 8/10 op p8. Niet opnieuw openen.

## Vergeleken bestaande registers
- [COOTRANTICO-vergunningen](cootrantico_route_frequencies_2026-11-02.md) en [visueel geverifieerde 462/242-tabellen](../sources/amb/legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv)
- [13-bedrijvenparameters](../sources/amb/remaining_13_route_parameters_2026-11-02.csv)
- [COOTRANSCO](cootransco_route_frequencies_2026-11-02.md), [COOTRAB](cootrab_route_frequencies_2026-11-02.md), [FLOTA ROJA](amb_bedrijven/flota_roja_route_frequencies_2026-11-02.md)
- [Bronregister](bronregister.md)

De bestaande frequentie-/juridische bronregisters blijven ongewijzigd. **Geen GTFS-generator, calendar, frequencies, trips of stop_times aangepast.**
