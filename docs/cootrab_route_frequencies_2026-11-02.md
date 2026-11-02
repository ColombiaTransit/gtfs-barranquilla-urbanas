# COOTRAB — routefrequenties, routewijzigingen en juridische besluitketen

**Peildatum:** 2 november 2026. **Bron:** de tien originele PDF's en per-pagina-extracties in GitHub Actions-artifact `amb-pdf-COOTRAB` (run `41480204032`, artifact `13159127716`). Voor de gezamenlijk geëxploiteerde route A1 is bovendien het opvolgende COOLITORAL-besluit 192-2025 vergeleken (artifact `amb-pdf-COOLITORAL`). De AMB-overzichtspagina is afzonderlijk gecontroleerd.

**Status:** alle tien geregistreerde COOTRAB-resoluties inhoudelijk geclassificeerd; de recentste beschikkende tabellen voor C5 en C6 **visueel gecontroleerd**. Dit is een overzicht van **laatst geanalyseerde vergunningsparameters**, niet van onafhankelijke actuele ritten.

## 1. Laatst geanalyseerde routeparameters

| Route | Geldend in onderzochte keten | Spitsinterval | Dalinterval | Aandeel COOTRAB | Lengte | PDF |
|---|---|---:|---:|---:|---|---|
| **C5-4136** | **358-2024** art. 1 | **8 min** | **10 min** | **17–19** | **38,6 km** | p. 3–5, technische tabel **p. 5** visueel gecontroleerd |
| **C6-4137** | **358-2024** art. 1 | **8 min** | **10 min** | **16–18** | **38,1 km** | p. 5–7, technische tabel **p. 7** visueel gecontroleerd |
| **A1-4106** (*joint operation with COOLITORAL*) | **192-2025** van COOLITORAL, later dan 358-2024 | **4,5 min op drukste gemeenschappelijke traject** | **6 min op drukste gemeenschappelijke traject** | **23–28** | Itin. A **55,3**, B **58,3 km** | 192-2025 **p. 7–8**, gedeelde vlootmatrix **p. 8** |

**Correcte frequentie A1 per itinerary:** de twee itinerarios A en B rijden volgens 192-2025 elk **8,5 minuten in de spits**, **14 minuten (A)** respectievelijk **11 minuten (B)** in het dal. De waarden **4,5/6** gelden alleen voor het overlappende drukste traject. De gezamenlijk geautoriseerde vloot A1 is **46–56**, waarvan **23–28 COOLITORAL en 23–28 COOTRAB** (192-2025 p. 8). A1 is **geen exclusieve COOTRAB-lijn**.

De nieuwste zichtbare routecodes komen uit officiële beschikkingen. De AMB **Visor de Rutas** op de overzichtspagina vermeldt echter **`C5-4135`**, in tegenstelling tot **`C5-4136`** in 378-2023 en 358-2024. Dit is een **bronconflict** en moet tegen de kaartdatabron van de visor worden opgehelderd.

## 2. Vergelijking: 378-2023 → 358-2024

| Onderdeel | 378-2023, 28 nov. 2023 | 358-2024, 12 dec. 2024 | Delta |
|---|---|---|---|
| C5 spits / dal | 5 / 7 min | **8 / 10 min** | beide +3 min |
| C5 voertuigen | 25–30 | **17–19** | −8 min / −11 max |
| C5 lengte | 35,4 km | **38,6 km** | **+3,2 km** |
| C6 spits / dal | 4,5 / 6 min | **8 / 10 min** | +3,5 / +4 min |
| C6 voertuigen | 30–35 | **16–18** | −14 min / −17 max |
| C6 lengte | 38,1 km | **38,1 km** | ongewijzigde opgegeven lengte |
| Cootrab-aandeel A1 | Niet in 378-2023 toegewezen | **22–28** via artikel 2 | Shared operation toegevoegd in 358 |
| Totale COOTRAB-toewijzing | **55–65** voor C5+C6 | **55–65** voor C5+C6+A1 | Som ongewijzigd |

**Rekencontrole:** 2023 `(25+30)–(30+35) = 55–65`; 2024 `(17+16+22)–(19+18+28) = 55–65`. Daarmee is de tekst **“la capacidad transportadora ... no se modifica”** in 358-2024 consistent met de per-route-tabellen, mits de gezamenlijke A1-toewijzing wordt meegeteld.

**Nieuwe complicatie 2025:** 192-2025 noemt **COOTRAB 23–28 op A1**, één extra ondergrens ten opzichte van 358-2024 (22–28). Dit leidt rekenkundig tot **56–65** als C5 en C6 uit 2024 ongewijzigd blijven. Dit is **geen onafhankelijk bevestigd nieuw bedrijfstotaal**. Het is expliciet vervolgwerk om te controleren of 192-2025 alleen de minimumverdeling herziet of elders een begeleidende compensatie bepaalt.

## 3. Routewijzigingen

**378-2023, art. 1 (p. 5–8):**
- C5: **Manuela Beltrán – Los Puertos – La Arboleda – Galán – Universidades – Calle 72 – Calle 30 – Circular**.
- C6: **Manuela Beltrán – Los Puertos – La Arboleda – Las Nieves – Universidades – Vía 40 – Las Nieves – Simón Bolívar – Circular**.
- Beide vertrekken volgens de artikelen vanaf terminal **Calle 48 con Carrera 5C**. Dit is een dispatchterminal, niet automatisch een GTFS-halte.

**358-2024, art. 1 (p. 3–7):**
- C5: **Manuela Beltrán – Las Palmas – Universidades – Vía 40 – Las Nieves – Simón Bolívar**. Lijn loopt via andere verbindingen door o.a. Calle 77 / Vía 40; exacte straatvolgorde staat in p. 4–5.
- C6: **Manuela Beltrán – Los Puertos – La Arboleda – Las Nieves – Universidades – Vía 40 – Las Palmas**. Exacte straatvolgorde in p. 6–7.
- Beide veranderen de lengte/frequentie en verdeling van voertuigen.
- **Art. 2 (p. 7–10):** autoriseert COOLITORAL-route **A1-4106** met twee itinerarios A/B en gezamenlijke exploitatie COOLITORAL / COOTRAB, **22–28 per bedrijf** in 2024. A1 krijgt later nieuwe tabellen in 192-2025.

**Oude routes mogen niet automatisch als huidige varianten worden gebruikt.** In 200-2019 vertrekken de routes nog van **Calle 42 No. 26-02, La Arboleda (Soledad)**; in 378-2023 staat de andere terminal en een nieuw traject.

## 4. Historische besluitketen — alle tien manifestitems

| Resolutie | PDF's pagina's | Operationele/juridische functie | Resultaat en relevantie |
|---|---:|---|---|
| **156-2010** | 18 | Herstructureert 1A/1B en machtigt samenwerking met **COOASOATLAN** | Historische samenwerkingsconstructie; geen huidige C5/C6-parameter |
| **497-2010** | 15 | Beslissing op *solicitud de revocatoria directa* tegen 156-2010 | **Artikel 1 wijst verzoek tot intrekking af**; dus géén intrekking van 156-2010 uit dit besluit afleiden |
| **174-2011** | 22 | Wijzigt 1A/1B / C5/C6 en het samenwerkingskader | Historisch **4/6 min**, C5 **22–27**, C6 **23–28**, juridische identificatie van oude codes controleren |
| **282-2011** | 7 | Lokale herstructurering C5 wegens verkeerslichten **Calle 36B / Carrera 8** | Historisch **3/5 min** en **30–36** voertuigen; niet voor huidige route gebruiken |
| **303-2014** | 16 | Art. 2 herstructureert C5/C6 | C5 **4,5/6**, **22–27**; C6 **4,5/6**, **23–28**; art. 3 noemt gefaseerde invoering afhankelijk van Transmetro-vloot |
| **121-2015** | 8 | Art. 1 wijzigt C6, m.n. traject Las Nieves/Vía 40/CUC | **4,5/6 min**, art. 2 laat voertuigcapaciteit uit 303-2014 ongewijzigd; OCR maximum op p. 7 niet betrouwbaar |
| **319-2016** | 9 | Herstructureert C5/C6 | C5 **4,5/6**, **22–27**; C6 **4,5/6**, **23–28**; totaal **45–55** |
| **200-2019** | 10 | Art. 1 wijzigt beide routes | C5 **6/7**, **22–27**, **37,3 km**; C6 **5/6**, **23–28**, **36,8 km** |
| **378-2023** | 8 | Art. 1 herstructureert C5/C6 | C5 **5/7**, **25–30**, **35,4 km**; C6 **4,5/6**, **30–35**, **38,1 km** |
| **358-2024** | 10 | Art. 1 wijzigt C5/C6; art. 2 gezamenlijke route A1 met COOLITORAL | C5 **8/10**, **17–19**, **38,6 km**; C6 **8/10**, **16–18**, **38,1 km**; COOTRAB-A1 **22–28** |

**2010 legaliteitsnoot:** de oude gezamenlijke operatie met COOASOATLAN en de latere met COOLITORAL zijn **niet dezelfde samenwerking**. Routebesluiten mogen niet overgenomen worden zonder datum en operatorrelatie.

## 5. Afwijkingen / verplichte vervolgacties

- **COOTRAB-01 — identificatie:** AMB-kaartviewer toont **C5-4135**, terwijl officiële 2023/2024-PDF's **C5-4136** vermelden. Kaartbron/API en wijzigingshistorie controleren vóór `route_id`-vaststelling. Bron: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/.
- **COOTRAB-02 — vloot 2025:** verifieer eventuele nieuwe toedeling van bedrijfsbrede minimale capaciteit nadat 192-2025 het COOTRAB-A1-aandeel van 22 naar 23 verhoogt.
- **COOTRAB-03 — externe pilot:** controleer ontbrekende **COOLITORAL 256-2026 PILOTO** op impact voor gedeelde A1, vóór definitieve geldigheidsclaim.
- **COOTRAB-04 — OCR historische bron:** resolutie 121-2015 p. 7 (maximumcapaciteit 26/28) tegen scan en artikel 2 controleren; bron zegt expliciet dat oude capaciteit behouden blijft.
- **COOTRAB-05 — ontbrekende dienstregeling:** spits/dal-vensters, werkelijk aantal ritten, dagen van dienst, eindhaltes en recente operatie onafhankelijk bevestigen. Tekst **00:00–24:00 afhankelijk van vraag** is geen bewezen 24-uursbedrijf.
- **COOTRAB-06 — geometrie:** exact straattraject C5 (358 p. 3–5) en C6 (358 p. 5–7), plus A1 2025 itinerarios A/B, aan OSM/haltes koppelen; niet zomaar oude 2019-shapes hergebruiken.
- **COOTRAB-07 — historische juridische ingang:** bij reconstructie van historische dienstverlening controleer gecommuniceerde inwerkingtredingsdata van de gefaseerde 303-2014 en 2010/2011 samenwerkingsakkoorden.

## 6. GTFS-resultaat

- **Juridisch meest recent in de geanalyseerde documenten:** C5 en C6, resolutie 358-2024; gedeelde A1, resolutie 192-2025, **onder voorbehoud van latere, nog ontbrekende 256-2026**.
- Routegegevens machineleesbaar in `sources/amb/cootrab_latest_route_parameters_2026-11-02.csv`.
- Besluitclassificatie alle tien in `sources/amb/cootrab_resolution_legal_index_2026-11-02.csv`.
- **GTFS_READY=no**. Noch `stop_times.txt`, `calendar.txt`, `frequencies.txt` noch `shapes.txt` automatisch aanpassen op alleen de vergunningsparameters.

### Kernbronnen
- 358-2024: https://www.ambq.gov.co/wp-content/uploads/2024/12/RESOLUCION-METROPOLITANA-358-24.pdf
- 378-2023: https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-METROPOLITANA-No-7.pdf
- 192-2025 (Coolitoral): https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-METROPOLITANA-No.-192-2025.pdf
- 200-2019: https://www.ambq.gov.co/wp-content/uploads/2019/11/RESOLUCION-N-200-1920190820.pdf
- 303-2014: https://www.ambq.gov.co/wp-content/uploads/2017/11/COOTRAB-C5-C6-Resolucion-303-14.pdf
