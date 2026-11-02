# COOTRANSNORTE — analyse van de 12 resoluties en GTFS-bronparameters

**Peildatum:** 2 november 2026. **Bron:** GitHub Actions `Extract AMB PDFs by company`, run `41480204032`, artifact `amb-pdf-COOTRANSNORTE` (`13160525755`), 12 originele PDF's en per pagina de tekstextracties. Alle 12 zijn met `status=extracted_requires_review` geëxtraheerd. De scans van **156-2015 p. 6**, **208-2015 p. 7**, **183-2016 p. 7** en **022-2014 p. 9** zijn expliciet tegen de OCR/native text geverifieerd.

**Reikwijdte:** geregistreerde officiële beschikkingen vergelijken op routegeometrie, reistijd/frequentie, vloot en rechtsgevolgen. **Niet** verwarren met geobserveerde dienstregeling. Er is geen vergunning van na **183-2016** in dit dossier gevonden; dit betekent **niet** dat latere of actuele exploitatie is bewezen.

## 1. Kernconclusie: twee routes, verschillend laatst wijzigingsmoment

| Route | Laatste geanalyseerde routebesluit | Spits | Dal | Vloot min–max | Lengte | Voertuigklasse | PDF-verificatie |
|---|---|---:|---:|---:|---:|---|---|
| **A5-4110** | **156-2015** (route+frequentie) **en 208-2015** (latere vlootverdeling) | **6 min** | **8 min** | **22–27** | **51,3 km** | **Grupo C (busetón/buseta)** | 156 p. 6 + 208 p. 7 (beide scans gecontroleerd) |
| **A6-4111** | **183-2016** (traject+frequentie, na 208-2015) | **6 min** | **8 min** | **19–23** | **35,7 km** | **Grupo C (busetón/buseta)** | 183 p. 6–7, p. 7 scan gecontroleerd |

**Bedrijfsvloot:** **41–50** voertuigen (208-2015 p. 7; opnieuw aangehaald in het technisch onderzoek bij 183-2016 p. 6). Dit is de som van de **per-route geautoriseerde minima/maxima** (22+19 = 41; 27+23 = 50). Geen afzonderlijke derde route binnen dit manifest.

**Voorwaardelijk servicevenster:** de routebladen vermelden `00:00 a las 24:00 ... dependiendo de las necesidades de demanda`. Dit betekent **niet** dat de bussen werkelijk 24 uur rijden. Spits/dal zijn intervallen, geen gedocumenteerde tijdvakken.

## 2. Exacte wijzigingsketen A5 — de afwijking die makkelijk gemist wordt

| Besluit | Spits/dal | Vloot | Route/inhoud |
|---|---|---|---|
| **119-2010**, p. 6–7 | 5 / 8 min | 18–22 | Oude PRADO LUJO / La Playa – Paraíso – Circular |
| **211-2010**, art. 1–3 p. 8–9 | 5 / 8 min | oude basis 18–22, maar OCR van p. 9 toont onzeker `13` | Bezwaar deels gehonoreerd: wijzigingen traject en voertuigtypologie; exacte oude minima per scan controleren |
| **577-2010**, p. 10–11 | technisch **6 min spits** | 18–22 | Wijzigt traject zodat Centro / Mercado Público bereikbaar blijven; art. 3 houdt bestaande capaciteit in stand |
| **090-2012**, art. 1 p. 2–3 | geen nieuw interval | geen nieuwe vloot | Wijzigt A5 en A6 wegens verkeerslichten Calle 100 / Carrera 51B |
| **432-2013**, art. 1–2 p. 7–8 | **5 / 8 min** | **18–22, Grupo B** | A5 – La Playa – Corredor Universitario – Miramar – Calle 84 – Villa Carolina – Circular |
| **022-2014**, art. 1–2 p. 8–9 | **5 / 8 min** | **18–22, Grupo B** | Gedeeltelijke herroeping/aanpassing van **het traject** uit 432-2013 na bezwaar. Scan p. 9 bevestigd |
| **122-2015**, art. 1 p. 6 | **4,5 / 7 min** | **27–33, Grupo C** | Nieuw traject **La Playa – Miramar – Silencio – CUC – Simón Bolívar – Circular**, **40 km** |
| **156-2015**, art. 1 p. 5–6, art. 2 p. 7 | **6 / 8 min** | **27–33 op dat moment** | Nieuw traject **La Playa – Miramar – Silencio – Cordialidad – Circular**, **51,3 km**. Art. 2 behoudt vloot volgens 122-2015 |
| **208-2015**, art. 1 par. 1 p. 7 | **6 / 8 min ongewijzigd** | **22–27** | **Herverdeelt de bedrijfsvloot:** A5 krijgt 22–27, A6 19–23, totaal 41–50 |
| **183-2016**, technisch rapport p. 6 | A5 niet opnieuw gewijzigd | **22–27** | Bevestigt de verdeling, maar art. 1 herstructureert **alleen A6** |

**Waarom dit essentieel is:** de meest recente A5-routebeschrijving (**156-2015**) noemt **27–33** voertuigen, maar de later gepubliceerde en gescande vlootmatrix in **208-2015** geeft **22–27**. Een automatisch extractiescript dat alleen A5-besluiten selecteert, zou dus de verkeerde capaciteit overnemen.

**Routewijziging A5 uit 156-2015:** het traject gaat via Miramar/Silencio naar **Avenida Cordialidad (Calle 47)**, met een keermogelijkheid bij het knooppunt **Cordialidad/Circunvalar**, waarna de route terugloopt via onder andere Calle 53D. Het vorige 122-2015-traject omvatte CUC en Simón Bolívar. De gegeven **51,3 km** is een vergunningslengte, niet geverifieerd uit OSM.

## 3. Wijzigingsketen A6: 2015 → 2016

| Besluit | Spits/dal | Vloot | Lengte | Betekenis |
|---|---|---|---|---|
| **118-2010** (oude PRADO BOSTON), p. 6–7 | 5 / 8 min | 23–28 | — | Historische vergunning; uitvoering afhankelijk van AMB-mededeling Transmetro |
| **209-2010**, art. 1–3 p. 8–9 | geen nieuw interval in beschikkend artikel | eerder geautoriseerde capaciteit | — | Beroep deels toegewezen, route gecorrigeerd |
| **090-2012**, p. 2–3 | niet gewijzigd aangetoond | geen nieuwe vloot | — | Wijzigt A5+A6 bij Calle 100 / Carrera 51B |
| **122-2015**, p. 7 | **6 / 8 min** | **14–17** | **28 km** | La Playa – Buenavista – Villa Carolina – Vía 40 – Circular |
| **208-2015**, p. 5–7 | **6 / 8 min** | **19–23** | **42,7 km** | Verlengt A6 via **Vía 40, Prado, Centro**; vernieuwde vlootverdeling 41–50. Artikel 1 par. 2 vermeldt dat het vooral het A6-traject en de vlootdistributie van 122-2015 aanpast |
| **183-2016**, p. 6–7 | **6 / 8 min** | **19–23** | **35,7 km** | **Verkort A6 met 7,0 km** tegenover 208-2015, door directer over Vía 40 naar Prado/Centro te rijden en Villa Carolina niet langer in dit traject op te nemen |

In **183-2016** staat als routeomschrijving **`Urb. La Playa – Vía 40 – Prado – Centro – Circular`**. Het traject loopt van de terminal in La Playa naar Carrera 10, Vía 40, Calle 58/59, Carrera 44, Calle 30, Carrera 43, Calle 55 en via Carrera 54/58 en Vía 40 terug richting La Playa. De **exacte, volledige volgorde** staat in de beschikkende tekst op p. 6–7. Op p. 7 zijn **6/8 minuten**, **35,7 km**, **19/23 voertuigen** en **Grupo C** visueel bevestigd.

### Gerelateerde bron voor routevermelding in 2025

De AMB-publicaties over tijdelijke omleidingen noemen beide routes ook later: **A5-4110** in circular 028-2025 en **A6-4111** in circular 009-2025 en 034-2025. Dat is additionele aanwijzing dat de autoriteit de codes in 2025 nog gebruikte, maar de omleidingscirculaires zijn **geen** actuele dienstregeling of bewijs voor dagelijks gereden ritten.

- A5, circular 028-2025: https://www.ambq.gov.co/wp-content/uploads/2025/03/Circular-No.-028-2025-Cierre-Total-DESFILE-GRAN-PARADA-CARLOS-FRANCO.pdf
- A6, circular 009-2025: https://www.ambq.gov.co/wp-content/uploads/2025/02/Circular-No.-009-2025-Cierre-Total-GUACHERNA.pdf
- A6, circular 034-2025: https://www.ambq.gov.co/wp-content/uploads/2025/03/Circular-No.-034-2025-Cierre-Total-DESFILE-JOSELITO-SE-VA-CON-LAS-CENIZAS.pdf
- AMB-routeoverzicht met beide codes: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/

## 4. Volledig register van alle twaalf documenten

De per-resolutie classificatie, exacte bronnen en uitzonderingen staan in
`sources/amb/cootransnorte_resolution_legal_index_2026-11-02.csv`.

1. **118-2010:** primaire A6-voorganger (PRADO BOSTON), route en 5/8 min, 23–28.
2. **119-2010:** primaire A5-voorganger (PRADO LUJO), route en 5/8 min, 18–22.
3. **209-2010:** bezwaar tegen 118 deels toegewezen; oud A6-traject gewijzigd.
4. **211-2010:** bezwaar tegen 119 deels toegewezen; A5-traject en voertuigtype aangepast; historisch OCR-verschil in minimumvloot.
5. **577-2010:** A5-variant richting Centro/Mercado Público; technisch ontwerp 6-minuten-spits; geen bewijs dat alle 2010-besluitvoorwaarden meteen ingingen.
6. **090-2012:** geometriewijziging A5+A6 wegens verkeerslichten Calle 100/Carrera 51B.
7. **432-2013:** A5 herstructureerd, 5/8 min, 18–22 Grupo B.
8. **022-2014:** beslissing op bezwaren, gedeeltelijke herroeping **van de routewijziging uit 432**; blijft 5/8 en 18–22.
9. **122-2015:** beide routes opnieuw herstructureerd: A5 4,5/7 min, 27–33; A6 6/8 min, 14–17.
10. **156-2015:** A5 gewijzigd via Cordialidad, 6/8 min en 51,3 km; toen nog 27–33.
11. **208-2015:** A6 naar Prado/Centro, 6/8 en 42,7 km; herverdeelt hele vloot naar **A5 22–27 + A6 19–23**.
12. **183-2016:** A6 direct via Vía 40 naar Prado/Centro, **6/8, 35,7 km, 19–23**; bedrijfsvloot blijft **41–50**.

Er zijn **geen mislukte PDF-extracties binnen deze twaalf**. De zeven oudere documenten met beeld-OCR (vijf uit 2010, één uit 2012 en één uit 2013) kunnen wel onnauwkeurigheden in straatnamen bevatten. Het juridische onderscheid tussen wijziging, gedeeltelijke herroeping en technisch rapport is in het register expliciet bewaard.

## 5. Resterend werk — apart voor vervolgacties

| ID | Prioriteit | Onderzoek | Afsluitcriterium |
|---|---|---|---|
| **CNORTE-01** | Hoog | Werkelijke exploitatie **A5 en A6** in 2026 en eventuele vergunningen van na 183-2016 controleren | Recente officiële status/ritgegevens, geen aannames |
| **CNORTE-02** | Hoog | **Exacte straattrajecten** A5 (156 p. 6) en A6 (183 p. 7) aan geolocaties en haltes koppelen | Gecontroleerde routegeometry en stopvolgorde |
| **CNORTE-03** | Hoog | **Spits/dal tijdvakken**, week-/feestdagoperatie en werkelijke vertrekregeling verkrijgen | Verifieerbare basis voor `calendar`, `trips`, `frequencies`, `stop_times` |
| **CNORTE-04** | Middel | **Terminaladres**: 2015-teksten noemen Carrera 10/Calle 5 **520**, terwijl 183-2016 **No. 250** vermeldt | Adres met vergunning/geolocatie bevestigd vóór GTFS stoplocatie |
| **CNORTE-05** | Middel | Historische 211-2010 p. 9: OCR leest `13` als minimum terwijl 119-2010 en 432-2013 **18** hanteren | Scancontrole voor historische 2010-fleet |
| **CNORTE-06** | Middel | Effectieve ingangsdatum van Transmetro-afhankelijke 118/119/209/211-2010 en latere kennisgevingen | Onderbouwde historische `start_date` en `end_date` |
| **CNORTE-07** | Middel | Oude Grupo B → Grupo C overgang juridisch dateren en onderscheiden van ritfrequentie | Correcte voertuighistorie |
| **CNORTE-08** | Middel | Eventuele AMB 2025/2026 omleidingen uitsluitend als tijdelijke uitzonderingen verwerken | Geen permanente shape- of dienstregelingvervuiling |

## 6. GTFS-status en opgeslagen bestanden

- `sources/amb/cootransnorte_latest_route_parameters_2026-11-02.csv`: **twee routegebonden records** met laatste routebesluit, aparte vlootbesluitbron, intervallen, lengte, voertuiggroep en GTFS-waarschuwing.
- `sources/amb/cootransnorte_resolution_legal_index_2026-11-02.csv`: **12 juridische bronrecords**, inclusief afhankelijkheden en OCR-vragen.
- **`GTFS_READY=no`**; geen productie-`frequencies.txt`, `trips.txt`, `calendar.txt`, `stop_times.txt` of `shapes.txt` bijgeschreven.

**Belangrijkste primaire PDF's:**
- [156-2015 A5](https://www.ambq.gov.co/wp-content/uploads/2019/01/COOTRANSNORTE-A5-Resolucion-156-15.pdf)
- [208-2015 vlootverdeling / A6](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSNORTE/Resolucion-208-15.pdf)
- [183-2016 A6](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSNORTE/Resolucion-183-de-2016-Cootrasnorte.pdf)
- [122-2015 beide routes](https://www.ambq.gov.co/wp-content/uploads/2019/02/resolucion-122-15.pdf)
- [022-2014 bezwaar tegen 432-2013](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSNORTE/RESOLUCION-022-14-COOTRANSNORTE.pdf)
