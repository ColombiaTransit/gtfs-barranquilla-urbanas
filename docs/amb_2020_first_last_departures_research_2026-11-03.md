# AMB TPC — eerste/laatste vertrekken op officiële routekaarten (juli 2020)

**Onderzoeksdatum:** 3 november 2026. **Primaire bron:** [AMB: Continúan las rutas y frecuencias del Transporte Público Colectivo](https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/).

AMB publiceerde **24 afbeeldingskaarten** (WordPress uploads `2020/07`) met voor elke opgenomen route: **RUTA**, **NOMBRE CAMPO**, **PRIMER DESPACHO (AM)**, **ÚLTIMO DESPACHO (PM)**, **HORA PICO (MINUTOS)** en **HORA VALLE (MINUTOS)**. Een kaart kan meerdere routes bevatten.

**Ze zijn historisch (2020), niet de actuele 2026-exploitatie.** De beelden kunnen COVID-gerelateerde of anderszins tijdsgebonden tijden bevatten. Geen route of vertrektijd als 'momenteel bevestigd' presenteren zonder specifiek recenter bewijs.

## Automatische bronoogst en OCR

[GitHub Action: Extract historic AMB first/last departures (2020 posters)](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/workflows/harvest-amb-2020-route-posters.yml), eerste run [41586978991](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41586978991).

Script: `scripts/harvest_amb_2020_route_posters.py`. Haalt alle 24 poster-links uit de officiële pagina met vaste reproductie-fallback, probeert het origineel in plaats van de 350×350 thumbnail te downloaden, bewaart poster en uitsnede van onderste routetabel en maakt Spaanse OCR-tekst (PSM 6 en 11). Genereert `poster_index.csv`, `report.json` en per kaart afbeeldingen en OCR-bestanden.

**Belangrijk:** OCR is pas een kandidaatresultaat; eerste/laatste vertrektijden moeten aan de originele kaarttabel worden gecontroleerd. Een poster met onleesbare thumbnail krijgt expliciet onvoldoende bronevidence. Een jaartalmap van 2020 mag niet als huidige 2026-tijd worden geciteerd.

## Handmatig bevestigde voorbeelden

| Route | Bedrijf (bronkaart) | Eerste dispatch (2020) | Laatste dispatch (2020) | Spits/dal (2020) | Bewijs |
|---|---|---:|---:|---|---|
| **B19-4176** | Trasalianco | **04:30** | **18:00** | 5/10 min | [AMB originele kaart](https://www.ambq.gov.co/wp-content/uploads/2020/07/WhatsApp-Image-2020-07-17-at-11.31.15-AM.jpeg) |
| **D12-4154** | Trasalianco | **04:30** | **18:00** | 5/10 min | dezelfde bronkaart |
| **D17-4158** | Trasalianco | **04:30** | **18:00** | 5/10 min | dezelfde bronkaart |
| **D18-4179** | Trasalianco | **04:30** | **18:00** | 5/10 min | dezelfde bronkaart |
| **A13-4162** | Transportes Atlántico | **05:30** | **18:30** | 10/20 min | [AMB originele kaart](https://www.ambq.gov.co/wp-content/uploads/2020/07/WhatsApp-Image-2020-07-17-at-11.31.16-AM-2.jpeg) |
| **B9-4125** | Embusa | **05:14** | **18:30** | 6/10 min | [AMB originele kaart](https://www.ambq.gov.co/wp-content/uploads/2020/07/WhatsApp-Image-2020-07-17-at-11.31.18-AM-1.jpeg) |
| **B4-4120** | Cootrántico | **05:00** | **18:00** | *6 y 8* / *10 y 15* (bron bereik/varianten) | [AMB originele kaart](https://www.ambq.gov.co/wp-content/uploads/2020/07/WhatsApp-Image-2020-07-17-at-11.31.18-AM-3.jpeg) |

Op de COOTRANTICO-kaart hebben ook B5, B5-B, B6, B7, B20 en B20-B **05:00–18:00**; de 2020-frequentie staat als *6 y 8* / *10 y 15*, **geen eenduidig gezamenlijk per-route interval**. Voor deze routes gebruiken we hun **2025-resoluties** voor de vergunde spits/dalfrequenties.

## Toepassing op de GTFS

1. De **nieuwste juridisch toepasselijke AMB-routevergunning** blijft de leidende bron voor frequenties; eerdere 2020-kaarten overschrijven die niet.
2. Gebruik de op kaarten vermelde eerste/laatste vertrekken als **historische referentie** of als expliciet gemarkeerde **provisorische diensturen-aanname**, niet als bewezen dienstvenster voor 2026.
3. Ons vastgestelde werkdagmodel `07:00–09:00` en `17:00–20:00` peak blijft overeind. Voor elke route moet dit worden **afgesneden op het dienstvenster**; bij laatste vertrek `18:00` zou een *als aanname overgenomen* 2020-venster de avondspits dus om 18:00 laten eindigen, niet om 20:00.
4. Een **laatste vertrek** is het laatste dispatchmoment, niet noodzakelijk het moment waarop de laatste bus aankomt. Een GTFS-`frequencies.txt`-`end_time` is een **exclusieve bovengrens**; het exacte laatste dispatchmoment kan afzonderlijke logica of een expliciete laatste rit vergen.
5. De afbeeldingen vermelden niet expliciet een aparte zaterdag-/zondag- of feestdagkalender. Deze voor 2026 niet verzinnen. `America/Bogota` is de juiste lokale tijdzone.
6. Gedeelde corridors, routes met A/B itinerarios en beëindigde routevergunningen vereisen matching met de nieuwste vergunningsroutecode.
7. **Geen voertuigcapaciteit in GTFS.**

**Volgende fase:** tabelgegevens uit 24 oorspronkelijke kaarten in een machineleesbare route-CSV verifiëren, dan per route naar de recentere vergunningen linken. Per regel `source_period=2020-07`, `source_is_historical=true`, `review_status` en `current_2026_service_window_confirmed=false` gebruiken.
