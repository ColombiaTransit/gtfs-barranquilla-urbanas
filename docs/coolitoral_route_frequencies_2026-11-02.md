# COOLITORAL — routefrequenties, wijzigingen en juridische besluitketen

**Bron:** 37 PDF's in GitHub Actions-artifact `amb-pdf-COOLITORAL`, run `41480204032`, plus de officiële AMB-index. Versie 2 november 2026.

**Status:** nieuwste beschikbare besluiten inhoudelijk geanalyseerd; **actuele exploitatie niet bevestigd**. De AMB-index noemt bovendien een ontbrekende **256-2026 PILOTO**. Zolang die niet is gecontroleerd, zijn onderstaande gegevens *laatst geanalyseerde* vergunningsparameters en niet noodzakelijk de absoluut nieuwste.

## 1. Kernbesluiten en rechtsgevolg
| Besluit | Belangrijkste inhoud | Waar |
|---|---|---|
| **192-2025**, 23 mei 2025 | Artikel 1 wijzigt de vergunningen en frequenties van **14 routes**; paragraaf 1 verdeelt **340–408** voertuigen over het COOLITORAL-aandeel; paragraaf 2 verplicht SIBUS | p. 5–34 |
| **199-2025**, 29 mei 2025 | Formele correctie van foutcode **C19-4119** in 192-2025 naar **C19-4178**; geen materiële routewijziging | p. 1–3; scan p. 1 gecontroleerd |
| **210-2026**, 8 mei 2026 | Artikel 1 wijzigt **PT2-4102 en PT3-4103**: twee itinerarios A/B, nieuwe lengtes en frequenties; paragraaf 1 zegt vlootcapaciteit **ongewijzigd** | p. 3–8; tabellen p. 5 en 7 visueel gecontroleerd |
| **332-2023** | Artikel 1 verplaatst dispatchterminals; artikel 2 herstructureert tijdelijk negen routes (tot SITP-herstructurering) | p. 7–22 |
| **264-2024**, 7 oktober 2024 | Artikel 1 herstructureert A4-4109; destijds 9/11 min en 16–19 voertuigen | p. 3–5 |
| **321-2016 / 325-2016** | Eerdere aanpassingen vlootcapaciteit, onder meer C19/PT2/PT3 en B17 | betreffende artikelen |
| **189-2010 / 190-2010** | Historische toestemming voor gezamenlijke exploitatie met respectievelijk TRANSDIAZ en SODETRANS | artikel 1 |
| **236/237/238-2010** | **Intrekkingen** van oude routes; niet terug opnemen in GTFS | artikel 1 |
| **223-2010** | Bezwaar / recurso de reposición met betrekking tot 149-2010; uitkomst nog precies toetsen | relevante artikelen |
| **718-2018** | Toestemming voor vijf Grupo D-voertuigen; géén bewijs dat een besproken proeflijn werkelijk gereden heeft | artikel 1 |

Machineleesbare classificatie van **alle 37 PDF's**: `sources/amb/coolitoral_resolution_legal_index_2026-11-02.csv`. Dit is een classificatie van het beschikkende onderwerp, niet voor iedere historische PDF een volledige juridische toets.

## 2. Laatst geanalyseerde intervallen per route

Eenheid = minuten tussen vertrekken. 'Spits/dal' zijn **vergunningsparameters**. Voor routes met itinerarios A/B staat het interval van het gemeenschappelijke drukste traject naast de intervallen per itinerary.

| Route | Besluit | Spits | Dal | COOLITORAL-vloot min–max | Lengte / bijzonderheid | Bron |
|---|---|---:|---:|---:|---|---|
| A1-4106 | 192-2025 | **4,5 effectief** | **6 effectief** | 23–28 | A 55,3 km / B 58,3 km; elk itinerary spits 8,5; dal A 14 en B 11; samen met COOTRAB | p. 5–8 |
| A2-4107 | 192-2025 | 8,5 | 11 | 22–26 | 56,1 km | p. 8–10 |
| A3-4108 | 192-2025 | 6 | 9 | 21–25 | 37 km | p. 11–12 |
| A4-4109 | 192-2025 | 9 | 11 | 22–26 | 56,7 km; p. 14 visueel gecontroleerd | p. 12–14 |
| B1-4117 | 192-2025 | 8 | 11 | 13–16 | 26,9 km | p. 14–16 |
| B2-A-4177 | 192-2025 | 4,5 | 7 | 24–29 | 31,5 km | p. 17–18 |
| B3-4119 | 192-2025 | 6 | 8 | 18–22 | 32,1 km | p. 19–20 |
| B17-4163 | 192-2025 | **2,5** | 4 | **35–42** | 51,9 km; gezamenlijke vloot SODETRANS + COOLITORAL **70–84** | p. 21–22 |
| C19-4178 | 199-2025 corrigeert 192-2025 | 5,5 | 8 | 18–22 | 30,1 km | 192 p. 23–24; 199 p. 1–3 |
| PT1-4101 | 192-2025 | 10 | 14 | **17–20** | 55,4 km; gezamenlijke vloot TRANSDIAZ + COOLITORAL **34–40** | p. 25–26 |
| **PT2-4102** | **210-2026** | **5 effectief** | **6 effectief** | 36–44 | A 52,9 / B 57,2 km; itinerary A en B elk **10/12** | 210 p. 3–5,8 |
| **PT3-4103** | **210-2026** | **5,5 effectief** | **6,5 effectief** | 37–44 | A 55,2 / B 60 km; itinerary A en B elk **10,5/13** | 210 p. 3,6–8 |
| PT4-4104 | 192-2025 | 4,5 | 7 | 27–32 | 34,5 km | p. 30–32 |
| PT5-4105 | 192-2025 | 4,5 | 7 | 27–32 | 35,5 km | p. 32–34 |

**Controle B17:** in de OCR stond `25` voor de spits. De scan van resolutie 192-2025 **p. 22** toont ondubbelzinnig `2.5 minutos`. De gezamenlijke vloot is 70–84, maar COOLITORAL heeft een aandeel van 35–42; dit is overeenkomstig de vlootmatrix op p. 34.

**Controle C19:** in 199-2025 p. 1 toont de scan `C19-4119` als foutcode en **`C19-4178`** als juiste code. De OCR schreef abusievelijk `C19-4173`. Niet als zelfstandige GTFS-route registreren.

## 3. Welke routeparameters zijn na 2025 daadwerkelijk veranderd?

| Route | 192-2025 | 210-2026 | Juridische betekenis |
|---|---|---|---|
| PT2-4102 | 5 min spits / 7 min dal; 52,9 km | **A/B elk 10/12**, drukste gezamenlijke traject **5/6**; A 52,9 km / B 57,2 km | Routesplitsing in itinerarios en lager effectief dalinterval |
| PT3-4103 | 5 min spits / 7 min dal; 53,7 km | **A/B elk 10,5/13**, drukste gezamenlijke traject **5,5/6,5**; A 55,2 km / B 60 km | Nieuwe itinerarios, andere trajectlengte en interval |
| Beide | PT2 36–44, PT3 37–44 voertuigen | Paragraaf 1 zegt capaciteit ongewijzigd | Geen fleetverhoging op grond van 210-2026 |

**Afwijking voertuigklasse:** 192-2025 p. 34 noemt voor **PT3 Grupo D**; de tabel op 210-2026 p. 7 noemt **Grupo C (Busetón–Buseta)**, terwijl de capaciteit volgens paragraaf 1 gelijk blijft. Eerst juridische verificatie of dit bewust is gewijzigd vóór koppeling van `vehicle_type` aan GTFS of fleetgegevens.

## 4. Wijzigingen aan terminals en historische capaciteit
**332-2023 artikel 1, p. 7:** A1/A2 verplaatsen naar **Calle 48 con Carrera 5C, Manuela Beltrán**; A3/A4/B1/B3 naar **Carrera 10 con Calle 119, Urbanización El Pueblo**. Artikel 2 wijzigt tijdelijk A1, A2, A3, A4, B1, B3, C19, PT2 en PT3.

**332-2023 p. 6 → 192-2025 p. 34 (COOLITORAL-aandeel):**
- A1 **22–28 → 23–28**;
- A2 **22–28 → 22–26**;
- A3 **16–19 → 21–25**;
- A4 **16–19 → 22–26**;
- B1 **13–16 → 13–16**;
- B3 **17–20 → 18–22**;
- C19 **17–21 → 18–22**;
- PT2 **48–58 → 36–44**;
- PT3 **48–58 → 37–44**.

Dit toont waarom oude vergunningen **niet** automatisch de huidige vlootwaarden mogen leveren. Een terminal in een vergunning is evenmin een geverifieerde GTFS-halte.

## 5. Open werkzaamheden — apart vastgelegd
- **COOL-01 / blocking:** officiële PDF van **256-2026 PILOTO** vinden, in manifest opnemen en beoordelen of de pilot een van bovenstaande routes raakt. Index: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/
- **COOL-02 / blocking:** PT3 voertuigklasse Grupo D (192-2025) versus Grupo C (210-2026) juridisch duiden.
- **COOL-03 / routegeometry:** volledige itinerarios uit 192-2025 p. 5–34 en 210-2026 p. 4–7 als geordende straten/haltes vastleggen en georefereren.
- **COOL-04 / historical:** alle 37 besluiten op juridische samenhang toetsen, vooral **223-2010 vs 149-2010**, 181-2016 dat **SODETRANS** als vergunninghouder noemt, en hoofdstuk 306-2014.
- **COOL-05 / actual service:** daadwerkelijke vertrektijden, spits-/dalvensters, actuele ritten en uitzonderingen onafhankelijk verzamelen; voorwaardelijke 00:00–24:00-tekst bewijst **geen** 24-uursdienst.
- **COOL-06 / cross operator:** B17 met SODETRANS, PT1 met TRANSDIAZ en A1 met COOTRAB in wederzijdse dossiers reconciliëren.

## GTFS-advies
- Gebruik routecodes als **geautoriseerde historische/laatst geanalyseerde IDs**, niet als bewezen actuele exploitatie.
- Maak voor PT2/PT3 twee aparte direction/pattern-varianten A/B; **5/6 en 5,5/6,5 gelden voor samenvallend drukste traject, niet automatisch per individuele rit**.
- De CSV `sources/amb/coolitoral_latest_route_parameters_2026-11-02.csv` bevat 14 routegebonden parameterrecords met besluit en paginabewijs.
- Geen automatische `calendar.txt`, `stop_times.txt`, `frequencies.txt` of `shapes.txt` voordat echte exploitatie en ontbrekende 256-2026 PILOTO zijn gecontroleerd.

### Officiële bronnen
- 192-2025: https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-METROPOLITANA-No.-192-2025.pdf
- 199-2025: https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-M.-199-2025-ERROR-FORMAL.pdf
- 210-2026: https://www.ambq.gov.co/wp-content/uploads/2026/05/RESOLUCION-METROPOLITANA-No.-210-2026-COOLITORAL-PT2-y-PT3_.pdf
- 332-2023: https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-METROPOLITANA-332-2023.pdf
- 264-2024: https://www.ambq.gov.co/wp-content/uploads/2024/12/RESOLUCION-METROPOLITANA-264-24.pdf
