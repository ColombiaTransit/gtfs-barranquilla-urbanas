# SIU → AMB-routekoppeling en voorlopige GTFS-haltes (3 november 2026)

## Update — gecontroleerde spellingsnormalisatie

Twee duidelijke bronfouten zijn via een [kleine, expliciete correctietabel](../sources/siu/stop_name_spelling_corrections_2026-11-03.csv) opgelost: `LOS MANATIALES` → `LOS MANANTIALES` en `COLEGIO LA ENSE?ANZA` → `COLEGIO LA ENSEÑANZA`. De bron-`stop_name` uit SIU wordt niet aangepast; per betrokken UUID bewaren we [de oorspronkelijke en de gestandaardiseerde naam](../sources/siu/gtfs_staging/stop_name_correction_audit.csv). De normalisatie wordt ook toegepast op de concept-`stops.txt` en de geordende haltevermeldingen.

Na de [geslaagde herbouw en vijf regressietests](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41600627039) zijn er **3.117 concept-haltes** en **53 resterende naamconflicten** (voorheen 3.118 en 54). De MANATIALES-variant is samengevoegd met de correct gespelde halte op exact dezelfde GPS; de oude `stop_id` blijft [als alias](../sources/siu/gtfs_staging/stop_id_alias_history.csv) naar de nieuwe kandidaat verwijzen. De schoolnaam is alleen gecorrigeerd: de richtingsaanduiding `-SN` blijft behouden, dus daar is niets samengevoegd.

Straatnummers, `EO/OE/NS/SN` en `REGRESO/RETORNO` worden bewust niet automatisch aangepast of samengevoegd. De officiële SIU-/GTFS-routekoppeling blijft voorlopig.

**Status:** onderzoek / staging, **geen publiceerbare GTFS-feed**. Script: [`scripts/build_siu_gtfs_stop_staging.py`](../scripts/build_siu_gtfs_stop_staging.py). Action: [Stage SIU route crosswalk and GTFS stop candidates](../.github/workflows/stage-siu-gtfs-stops.yml), geslaagde [run 41598939812](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41598939812).

## 1. Gegevens die nu bouwbaar zijn

| Onderdeel | Resultaat |
|---|---:|
| Openbare SIU-reguliere itineraries | **33** |
| Expliciet uitgesloten SIU-testitineraries | **3** |
| Geordende GPS-haltevermeldingen voor de 33 | **6.407** |
| Kandidaten voor fysieke `stop_id`, conservatief gededupliceerd | **3.117** |
| Regels samengebracht bij een al bekende kandidaat-halte | **3.290** |
| Naam- of richtingsverschillen op dezelfde berekende GPS-locatie, apart gehouden | **54** |
| **Sterke voorlopige SIU→GTFS-route-ID-koppelingen** | **12** |
| Itineraries zonder voldoende bewijs voor automatische routecodekoppeling | **21** |
| Geordende haltevermeldingen bij deze 12 voorlopig gekoppelde routes | **2.361** |
| Verschillende kandidaat-`stop_id` in die 12 routes | **1.802** |
| Definitief juridisch gecontroleerde SIU→AMB-route-ID-koppelingen | **0** |

Bronnen: [SIU-gegevens van 3 november 2026](../sources/siu/public_extract/siu_route_stop_sequences.csv), [36 SIU-itineraries](../sources/siu/public_extract/siu_itineraries.csv), [oude ArcGIS-routes en kandidaat-matching](../sources/siu/analysis/siu_to_amb_routecode_candidates.csv), bestaande [`gtfs/routes.txt`](../gtfs/routes.txt). Gebruik uitsluitend de **36** als correcte bronwaarde (33 regulier + 3 test).

### Sterke voorlopige routekoppelingen

De volgende 12 scores voldoen aan de **conservatieve automatische acceptatieregels**: zelfde vervoerder, exact één bestaand GTFS-route-ID met de GIS-code, ten minste 80% van de onderzochte SIU-haltepunten binnen 50 m van die lijn, en minimaal 15 procentpunt meer dekking dan de op één na beste GIS-lijn. **Dit is nog geen juridische verificatie van het route-ID.**

| SIU-weergavenaam | GTFS-routecode-kandidaat | GIS-dekking binnen 50 m |
|---|---|---:|
| ALAMEDA DEL RIO — FLOTA ÁNGULO | **A7-4112** | 98,3% |
| CALLE 30 — LA CAROLINA | **D6-4150** | 95,0% |
| CIRCUNVALAR CENTRO — TRANSURBAR | **D16-4173** | 100% |
| VILLA ESTADIO LAS FLORES — TRANSURBAR | **D19-4184** | 100% |
| EL BOSQUE CAMPO ALEGRE — MONTERREY | **B8-4124** | 90,0% |
| VILLA CAROLINA ZOOLOGICO — MONTERREY | **B11-B-4192** | 93,3% |
| LAS FLORES CORDIALIDAD — MONTERREY | **B12-4127** | 100% |
| PIMSA PLACA NEGRA — TRASALFA | **D15-4157** | 95,0% |
| LOS ROBLES CALLE 72 — COOCHOFAL | **C4-4135** | 98,3% |
| EL CAMPITO — COOCHOFAL | **C2-B-4187** | 96,7% |
| CENTRO PUEBLO SAN PABLO — COOLITORAL | **B3-4119** | 85,0% |
| CALLE 72 VIA 40 — COOLITORAL | **B2A-4177** | 100% |

De gebruiker heeft eerder beslist officiële AMB-vergunningsfrequenties en voorlopige 2020-route-dienstvensters als **GTFS-modelaannames** te gebruiken; dat is onafhankelijk van de juridische route-identiteit. De 2019–2023-GIS-routes zijn ouder dan verscheidene vergunningen uit 2025–2026. Het bestand `siu_amb_route_crosswalk_review.csv` bewaart daarom altijd `final_gtfs_route_mapping_confirmed=no` tot de huidige resolutie en richting zijn vergeleken.

### Waarom de overige 21 niet automatisch gekoppeld zijn

| Type openstaand probleem | Aantal | Wat controleren? |
|---|---:|---|
| Meerdere exploitanten bij één SIU-itinerary | **7** | Wie exploiteert welk legaal AMB-routepatroon? Soms gedeelde lijn, verschillende onderliggende GTFS-ID's |
| A/B-varianten nog niet te onderscheiden | **5** | Routebeschikking, doorrit/richting en de variantspecifieke stopvolgorde |
| GIS-dekking onder 80% | **4** | Mogelijke gewijzigde trajecten na 2023; namen en latere besluiten |
| Twee oude GIS-routes overlappen (verschil minder dan 15 procentpunt) | **4** | Meer routegeometrie uit latere vergunningen of tekstueel trajectbewijs |
| Beste GIS-match hoort bij een ander bedrijf | **1** | Niet blind de beste geometrische match gebruiken |

Concreet eerst uitzoeken: COOLITORAL **PT4/PT5** en de verschillende A/B-itineraries, LA CAROLINA **A16**, COOCHOFAL **C18 versus C9**, TRANSURBAR **A14 versus D16**, en COOTRAB **C5/C6** waarvan de oude GIS-lijn de huidige SIU-stops slechts gedeeltelijk dekt. Dit zijn geen ontbrekende GPS-haltes maar **onbesliste routecode- en variantenkoppelingen**.

## 2. Halte-deduplicatie en richtingen

Het programma neemt het volledige SIU-halte-UUID, de SIU-itinerary UUID en de expliciete `stop_sequence` uit de openbare SIU-gegevens. Het maakt uitsluitend stopclusters met:

1. **Exact dezelfde genormaliseerde volledige haltenaam** (hoofdletters, accenten en leestekens geneutraliseerd; richtingsafkortingen zoals `NS`, `SN`, `OE`, `EO` blijven in de naam).
2. **Onderlinge afstand maximaal 5 meter tussen alle punten in een cluster**, niet alleen via een keten van tussengelegen punten.
3. Identieke GPS-posities met verschillende namen of rijrichtingen blijven **afzonderlijk** en gaan naar de [53 conflictlocaties](../sources/siu/gtfs_staging/coincident_different_name_review.csv).

Het concept-`stop_id` is `SIU_<kleinste originele SIU-stop-UUID in het cluster>`, stabiel **binnen dezelfde bronopname**. Bij een volgende SIU-versie moeten de oude alias-/ID-koppelingen behouden blijven zodat publieke stop-ID's niet door een nieuwe invoer wijzigen. Het concept-geometrisch midden is de gemiddelde broncoördinaat, uitsluitend bij clusters binnen 5 m.

Een halte met dezelfde naam op 200 m afstand blijft een **andere** halte. Tegengestelde rijrichtingen worden niet samengevoegd, ook niet als hun coördinaten gelijk zijn.

## 3. GitHub-uitvoer

- [Volledige review-crosswalk van 33 routes](../sources/siu/gtfs_staging/siu_amb_route_crosswalk_review.csv) — bevat matchregels, percentuele GIS-dekking, operatorcontrole en status.
- [Catalogus van 3.117 fysieke stopkandidaten](../sources/siu/gtfs_staging/candidate_stops.csv) — bevat naam, GPS, bronschema en merge-herkomst.
- [Alle 6.407 SIU-stop-UUID's → voorlopige `stop_id` + volgnummer](../sources/siu/gtfs_staging/siu_stop_occurrence_crosswalk.csv) — volledig herleidbaar.
- [GTFS-achtige `stops.txt`-proefversie, **NIET PUBLICEREN**](../sources/siu/gtfs_staging/stops_draft_NOT_FOR_PUBLICATION.txt) — vijf standaard GTFS-stopvelden, exclusief interne researchmetadata.
- [Voorlopige route-stopvolgorde voor de 12 hoge-confidence routekoppelingen](../sources/siu/gtfs_staging/candidate_route_stop_orders_NO_TIMES.csv) — **2.361 regels**, met lege `trip_id`, `arrival_time` en `departure_time`.
- [53 conflicten op identieke berekende GPS-locatie](../sources/siu/gtfs_staging/coincident_different_name_review.csv)
- [Samenvatting van de stagingrun](../sources/siu/gtfs_staging/summary.json)

**Belangrijk voor GTFS:** `stops.txt` kent een fysieke instapplaats die door meerdere routes mag worden gebruikt; `stop_times.txt` vereist een gekoppeld `trip_id`, stopvolgorde en noodzakelijke tijdvelden. De preview van haltevolgordes is daarom **nog geen geldige `stop_times.txt`**.

## 4. Toepasbare bronvoorwaarden

AMB heeft een eigen [pagina over open data](https://www.ambq.gov.co/transparencia/datos-abiertos/) en maakt daar expliciet onderscheid tussen publieke toegang en herbruikbare datasets. De aparte [gebruiksvoorwaarden van de AMB-website](https://www.ambq.gov.co/condiciones-de-uso/) leggen beperkingen op voor commercieel/promotioneel hergebruik van webinhoud zonder toestemming. Het is **niet aangetoond** dat de GraphQL-route-/haltelijst in SIU onder de open-datalicentie valt of dat deze voorwaarden op de SIU-dienst van toepassing zijn. **Vóór publicatie van een herbruikbare GTFS buiten het onderzoeksarchief eerst de autorisatie/licentie laten bevestigen bij AMB of een officieel open-databestand vinden.** Geen toegangstokens of persoonsgegevens opgenomen; de gegevens zijn route- en haltegegevens van het openbare scherm.

## 5. Vervolg

Na inspectie van de 21 twijfelgevallen kunnen we de crosswalk route voor route uitbreiden en voor elk definitief gekoppeld itinerary de stopvolgorde hergebruiken. Daarvoor blijven de wettelijke A/B-status, controle op overlappende/nieuwe GIS-geometrie en een realistisch **ritduur-/reistijdmodel** nodig. De official AMB-`hora pico/hora valle`-intervallen zelf hoeven niet opnieuw met realtime data bewezen te worden.
