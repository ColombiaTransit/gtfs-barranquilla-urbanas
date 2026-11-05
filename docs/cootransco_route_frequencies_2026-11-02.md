# COOTRANSCO — frequenties, routewijzigingen en besluitketen

**Peildatum:** 2 november 2026. **Bronmateriaal:** de vijf COOTRANSCO-resoluties (120-2010, 222-2010, 024-2017, 258-2024 en 098-2026) uit GitHub Actions-extractie `amb-pdf-COOTRANSCO` (run `41480204032`, artifact `13159733043`). Alle vijf bestanden konden worden gedownload en geëxtraheerd. De **originele PDF-scans** van 258-2024 p. 3 en 5 en 098-2026 p. 6 zijn afzonderlijk visueel gecontroleerd.

**Conclusie:** één geregistreerde route **C7-4138**, met historische permanent vergunde parameters en een **tijdelijke pilot in 2026**. Er zijn **twee blokkerende onzekerheden**: (a) tegenstrijdige vlootcapaciteit in 258-2024, (b) onbekende verlengingsstatus van de pilot per november 2026. Vergunningstabellen zijn geen bewijs van daadwerkelijk gereden ritten.

## 1. Geanalyseerde frequenties

| Besluit | Juridische aard | Route/patroon | Spits (min) | Dal (min) | Vloot min–max | Lengte | Bewijs |
|---|---|---|---:|---:|---:|---:|---|
| **120-2010** | Oorspronkelijke herstructurering | C7, El Ferry – Paraíso – Circular | **4** | **7** | **41–60** | niet vastgesteld | p. 6–7 |
| **222-2010** | Gedeeltelijk toegewezen bezwaar / wijziging van traject | C7, Ruta Uno | **4** | **7** | **41–60** | niet vastgesteld | p. 7, 8–10; technisch ontwerp 120 blijft ongewijzigd |
| **024-2017** | Herstructurering | C7-4138, El Ferry – Paraíso – Circular | **3** | **5** | **50–60** | **42,9 km** | art. 1 p. 7–8 |
| **258-2024** | Herstructurering permanente vergunning | C7-4138, Las Ferias – Paraíso – Circular | **3** | **5** | **56–68 in art. 1** | **40,3 km** | art. 1 p. 4–5 |
| **098-2026** | **Tijdelijke pilot** | C7-4138, **Itinerario A** | **5** | **7** | **56–68 totaal** | **37,4 km** | art. 1 p. 3, 5–6 |
| **098-2026** | **Tijdelijke pilot** | C7-4138, **Itinerario B** | **5** | **7** | **zelfde 56–68 totaal, niet apart optellen** | **38,5 km** | art. 1 p. 3, 5–6 |
| **098-2026** | Alleen het **gedeelde drukste traject** van A+B | Gecombineerd interval | **2,5** | **3,5** | **zelfde routevloot** | n.v.t. | art. 1 p. 6 |

**Let op:** de gecombineerde intervalwaarde van **2,5/3,5 minuten** is *geen* individuele ritfrequentie van itinerary A of B. Voor een GTFS-patroon per richting/variant moet **5/7** apart worden beschouwd; pas op een gemeenschappelijk segment komen twee varianten samen. Het 00:00–24:00-venster is in de vergunning **afhankelijk van vraag** en dus geen bewezen nachtdienst.

## 2. Tijdelijkheid van 098-2026: belangrijkste juridisch aandachtspunt

- **Datum van besluit:** 26 februari 2026.
- **Artikel 1 p. 3–6:** keurt de uitvoering van een *plan piloto* voor C7-4138 goed en tekent twee alternatieve itinerarios A en B in plaats van het enkelvoudige traject uit 258-2024.
- **Artikel 2 p. 6:** `6 meses contados a partir del dos (2) de marzo de 2026`; **in beginsel tot rond 2 september 2026**, tenzij verlengd.
- Hetzelfde artikel zegt expliciet **`Este tiempo podrá ser prorrogado`**: *kan* worden verlengd, niet *is* verlengd.
- **Per peildatum 2 november 2026 is geen daadwerkelijk verlengings- of opvolgingsbesluit vastgesteld** binnen de vijf beschikbare documenten. De openbare index en een aanvullende zoekactie leverden geen geverifieerd besluit. **Daarom kan de pilot niet als huidige exploitatie worden aangemerkt.** Evenmin staat zonder aanvullend bewijs vast of de exploitatie na het pilotvenster daadwerkelijk terugkeerde naar 258-2024.

### Wat verandert geografisch in de pilot?
- **258-2024 p. 4–5:** naam *Las Ferias – Paraíso – Circular*, vertrek/einde bij terminal **Carrera 7B nr. 7A-83**; 40,3 km, 3/5-minuten.
- **098-2026 p. 3,5–6:** naam *El Ferry – Primero de Mayo – Los Trupillos – Calle 72 – Villa Carolina – Centro – Circular*, terminal eveneens **Carrera 7B nr. 7A-83**, maar **twee afzonderlijke straattrajecten** van 37,4 en 38,5 km. Teksten staan integraal in p. 5.
- Afname opgegeven lengte t.o.v. 2024 van **2,9 km (A)** en **1,8 km (B)**; geen bewijs dat dit een permanente nieuwe route is.
- De naamsverschillen *Las Ferias* versus *El Ferry* moeten aan straatgeometrie en officiële routeviewer worden getoetst voordat er nieuwe `route_short_name` of `route_long_name`-waarden worden vastgesteld.

## 3. Gebleken tegenstrijdigheid: 258-2024 vervoerscapaciteit

**Dit is géén OCR-artefact:** origineel PDF is visueel geïnspecteerd.

- **258-2024 p. 3**, geciteerd technisch rapport 003-24 van 29 augustus 2024: tabel `C7-4138 / Grupo C / Mínima 50 / Máxima 60`, `TOTAL COOTRANSCO 50–60`. De overweging stelt dat de **capaciteit gelijk blijft**.
- **258-2024 p. 5**, **beschikkend artikel 1**, technische tabel: `Mínima 56 / Máxima 68`. De paragraaf eronder stelt opnieuw expliciet dat de capaciteit **gelijk blijft**.
- **024-2017 p. 8** bevat eveneens **50–60**, wat de tegenspraak versterkt.
- **098-2026 p. 6** noemt **56–68**, in overeenstemming met de *beschikkende tabel* uit 258-2024, maar 098 is een **tijdelijke pilot** en lost niet vanzelf de interne juridische tegenstelling uit 258 op.

**Interpretatie:** noteer **56–68 als letterlijk in het beschikkende artikel opgenomen** en **50–60 als strijdige technische/voorhistorische tabel**. Zonder rectificatie, begeleidend capaciteitsbesluit of rechtsgeldige uitleg **geen definitief bedrijfsvlootmaximum voor productie-GTFS of voertuigcalculatie aannemen**.

## 4. Juridische chronologie: alle vijf besluiten

| Resolutie | Juridische strekking | Relevantie |
|---|---|---|
| **120-2010**, p. 6–7 | Artikel 1 herstructureert de toenmalige route **Soledad 2000/C7**; het effectief worden is afhankelijk van de invoering van Transmetro en een AMB-kennisgeving. | Historisch 4/7 min, 41–60 voertuigen. Geen bewijs voor huidige routefrequentie. |
| **222-2010**, p. 8–10 | Behandelt het bezwaar tegen 120: **artikel 1 gedeeltelijke bevestiging**, **artikel 2 routecorrectie**, **artikel 3 expliciete gedeeltelijke wijziging van 120**. Op p. 7 staat dat het operationele ontwerp uit 120 gelijk blijft. | Historische routecorrectie; geen nieuwe frequentie. |
| **024-2017**, p. 7–8 | Artikel 1 herstructureert C7-4138, El Ferry – Paraíso – Circular. | 3/5 min, 50–60 voertuigen, 42,9 km. |
| **258-2024**, p. 3–5 | Artikel 1 herstructureert C7-4138 en het straatverloop richting o.a. Vía 40 / Villa Carolina. | 3/5 min, 40,3 km; **50–60 versus 56–68-capaciteitsconflict**. |
| **098-2026**, p. 3–6 | Artikel 1 verleent tijdelijke pilot voor C7-4138 met twee itinerarios, art. 2 bepaalt zes maanden vanaf 2 maart 2026. | A/B elk 5/7; gedeeld traject 2,5/3,5; vloot 56–68. **Pilotstatus na september 2026 onbekend**. |

**Overige bronafwijking:** **222-2010 art. 4 p. 10** noemt voor de kennisgeving **COOTRANSNORTE** terwijl het besluit over **COOTRANSCO** gaat. Dit is zichtbaar in de OCR en moet, wanneer de formele rechtsgeldigheid relevant wordt, tegen de scan/correcties worden getoetst. Geen route aan COOTRANSNORTE overhevelen op basis van dit artikel.

## 5. Open werk, expliciet gereserveerd voor vervolgactie

| ID | Prioriteit | Werk | Afsluitcriterium |
|---|---|---|---|
| **COOTRANSCO-01** | **Blokkerend** | Technisch rapport 003-24 en art. 1 van 258-2024 vergelijken: **50–60 versus 56–68**; zoeken naar AMB-rectificatie / later besluit / gedocumenteerde vlootherverdeling. | Onderbouwde juridisch geldige vlootcapaciteit met bronbesluit. |
| **COOTRANSCO-02** | **Blokkerend** | Verlenging of afloop van de **098-2026 pilot** (na 2 september 2026) controleren. | Officieel opvolgingsbesluit of aantoonbare status per peildatum. |
| **COOTRANSCO-03** | Hoog | Werkelijke exploitatie en spits-/daltijdvakken onafhankelijk vaststellen, incl. werkelijke pilotimplementatie. | Bron voor `calendar`, `trips`, `stop_times` / `frequencies`, of expliciet afwezig. |
| **COOTRANSCO-04** | Hoog | Alle exacte straatsegmenten van 258-2024 p. 4–5 versus de twee itinerarios uit 098-2026 p. 5 georefereren; naam Las Ferias vs El Ferry onderzoeken. | Verifieerbare geometrie, richtingen en haltevolgorde. |
| **COOTRANSCO-05** | Normaal | Voor historische GTFS: transitie 120 → 222 in 2010, feitelijke kennisgeving/Transmetrostart en implementatiedatum bevestigen. | Aantoonbare historische geldigheidsperiode. |
| **COOTRANSCO-06** | Normaal | Kennisgevingsfout `COOTRANSNORTE` in 222-2010 art. 4 beoordelen. | Geverifieerde juridische duiding/rectificatie. |

## 6. Databestanden, kwaliteit en GTFS

- `sources/amb/cootransco_route_parameters_2026-11-02.csv`: routeparameterregels, **apart voor pilot A, B en gecombineerde sectie**, inclusief bronpagina, looptijd, status, vlootconflict en `gtfs_approved=no`.
- `sources/amb/cootransco_resolution_legal_index_2026-11-02.csv`: vijf resoluties, artikelverwijzingen, juridische functie, PDF SHA-256 en openstaande controles.
- **Geen productie-GTFS bijgewerkt**: eerst pilotverlenging en capaciteitsconflict oplossen; ritten en geometrie blijven onafhankelijk onderzoek.
- De tekstextractie is geslaagd voor **alle vijf** PDF's. De oude 2010-PDF's vereisten Spaanse OCR; de drie nieuwere PDF's zijn grotendeels native text. De kritieke numerieke verschillen zijn visueel tegen het origineel bevestigd.

### Officiële bronlinks
- [AMB COOTRANSCO-index](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootransco/)
- [098-2026 — tijdelijke pilot](https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-METROPOLITANA-No-PILOTO-098-26-COOTRANSCO.pdf)
- [258-2024 — permanente vergunning](https://www.ambq.gov.co/wp-content/uploads/2024/10/RESOLUCION-METROPOLITANA-N%C2%B0-258-2024-COOTRANSCO.pdf)
- [024-2017](https://www.ambq.gov.co/wp-content/uploads/2017/02/Resolucion-metropolitana-024-17.pdf)
- [120-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSCO/COOTRANSCO-C7-Resolucion-120-10.pdf)
- [222-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSCO/COOTRANSCO-C7-Resolucion-222-10.pdf)


## Archiefreconciliatie — 5 november 2026

Archiefhercontrole: 258-2024 3/5 blijft de gedocumenteerde permanente basis. 098-2026 A/B elk 5/7 is een tijdelijke pilot met onbekende verlenging. In het nieuwe archief is 348-2026 als potentiële opvolger aangemerkt, maar het beschikkende artikel en eventuele verlenging zijn nog **niet geverifieerd**. Daarom de pilot niet automatisch als actueel en 258 evenmin automatisch als hervat aanmerken. Alleen gerichte artikelcontrole 348-2026, zonder her-OCR van 258/098.

Zie [route-voor-route classificatie](../sources/amb/amb_archive_route_reconciliation_2026-11-05.csv) en [inhoudelijke vergelijking](amb_archive_2020_2026_existing_register_comparison_2026-11-05.md).
