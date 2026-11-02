# COOTRASOL — vergunde frequenties, routewijzigingen en juridisch dossier

**Peildatum:** 2 november 2026. **Primaire bronnen:** de 13 geregistreerde PDF-extracties van GitHub Actions-run `41480204032` (artifact `amb-pdf-COOTRASOL`, ID `13160139422`) en de officiële [AMB-COOTRASOL-resolutie-index](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrasol/). Alle 13 manifestitems zijn technisch succesvol geëxtraheerd. **12 unieke originele PDF's:** `386-2018-v2` heeft dezelfde volledige SHA-256 als `386-2018`. **Belangrijk:** een bedrijfspagina die 467-2025 als recentste noemt bewijst geen actuele dienstregeling of volledige juridische status, alleen de laatst gevonden bedrijfsspecifieke gepubliceerde vergunning.

## 1. Laatste gevonden routevergunning: 467-2025 (1 december 2025)

Besluit: wijziging van exploitatievergunning voor **D3-4147**, **D4-4148** en **D5-4149** (artikel 1, p. 4–9) op basis van technisch rapport **012-2025 van 18 november 2025** (p. 2). De originele **PDF-tabellen p. 5, 7 en 9 zijn visueel geïnspecteerd**, om fouten in Spaanse OCR en gedraaide pagina's uit te sluiten.

| Route | Naam / voornaamste corridor | Spits | Dal | Voertuigen min–max | Lengte | Bewijs |
|---|---|---:|---:|---:|---:|---|
| **D3-4147** | **San Fernando – American Bar – Las Nieves – Paseo Bolívar – Prado – Circular** | **6,5 min** | **8 min** | **22–27** | **45,1 km** | art. 1 **p. 4–5**, scan p. 5 |
| **D4-4148** | **Ciudad Bonita – Las Moras – Calle 30 – Paseo Bolívar – Prado – Circular** | **7 min** | **9 min** | **18–22** | **36,4 km** | art. 1 **p. 6–7**, scan p. 7; p. 6 is *90° gedraaid*, OCR niet leidend |
| **D5-4149** | **El Edén – Calle 30 – Hipódromo – Paseo Bolívar – Prado – Circular** | **6,5 min** | **9 min** | **24–29** | **47,5 km** | art. 1 **p. 8–9**, scan p. 9 |
| **Som / COOTRASOL** | **Drie geautoriseerde routes** | | | **64–78** | | art. 1 par. 1 **p. 9**; technisch tabeloverzicht **p. 3** |

**Alle drie**: **Grupo C (Busetón–Buseta)**, openbaar passagiersvervoer. Het voorschrift **SIBUS RCC** staat in art. 1 par. 2 p. 9. Het aangegeven mogelijke venster `00:00–24:00` staat **onder voorwaarde van de vervoervraag** en is **geen bewijs** voor een dienst gedurende de hele nacht. De tabellen geven geen concrete tijdvakken van `hora pico` en `hora valle`.

### Standaardroute en dispatchlocatie, 2025
- **D3**: vertrek/einde in **sector San Fernando, Malambo**, ter hoogte van **Carrera 10A / Calle 28**, via Vía Caracolí/Diagonal 18, Soledad, Calle 17, Circunvalar, Las Nieves en centrum/corridores. Volledige opeenvolging: art. 1 **p. 4–5**.
- **D4**: vertrek/einde **sector Ciudad Bonita, Soledad**, in de omgeving van **Calle 77**, via Las Moras, Calle 45, Avenida Calle 30 en Paseo Bolívar / Prado; precieze volgorde: **p. 7** en kaart op p. 6.
- **D5**: vertrek/einde **sector El Edén, Malambo**, via Calle 16/14, Carrera 8, Vía Oriental, Soledad, Calle 30, Paseo Bolívar, Prado, retour; volledige volgorde: **p. 8–9**.

Er staan tevens bronpercentages voor overlapping met Transmetro in de routebladen: D3 **17% troncal/21% alimentador**, D4 **26%/63%**, D5 **16%/40%**. Deze zijn vergunnings-/modelparameters en geen GTFS routegeometrie.

## 2. Kernvergelijking: vloot 386-2018 → 467-2025

**386-2018 art. 1 p. 8** bevat expliciet de bedrijfsverdeling, in de huidige 2025-resolutie wordt de totale capaciteit volgens art. 1 par. 1 **niet verhoogd**:

| Route | Vloot 386-2018 | Vloot 467-2025 | Verandering |
|---|---|---|---|
| **D3** | 22–27 | **22–27** | gelijk |
| **D4** | 20–24 | **18–22** | **−2 min / −2 max** |
| **D5** | 22–27 | **24–29** | **+2 min / +2 max** |
| **Totaal** | **64–78** | **64–78** | **ongewijzigd** |

Het meest recent vastgelegde model verdeelt dus meer voertuigen naar D5 ten koste van D4. Er is **geen bewijs van extra netto bedrijfsvloot**.

### D5 frequentie: 2018 → 2025

| | 386-2018 (art. 1 p. 7–8) | 467-2025 (art. 1 p. 9) |
|---|---:|---:|
| Spitsinterval | **4 min** | **6,5 min** |
| Dalinterval | **6 min** | **9 min** |
| Min.–max. voertuigen | **22–27** | **24–29** |
| Vergunde lengte | **46,7 km** | **47,5 km** |
| Routebenaming | Villa Campo – Calle 30 – Boston – Circular | El Edén – Calle 30 – Hipódromo – Paseo Bolívar – Prado – Circular |

**D5** krijgt dus een **langer** gepland interval terwijl de vloottoewijzing wordt vergroot; dit is **niet** genoeg om dienstregeling of feitelijk aantal ritten af te leiden. Beide routeomschrijvingen en rijlijnen zijn verschillend; het is geen simpele administratieve frequentieaanpassing.

**Voor D3/D4** bevat **386-2018** de *vlootverdeling*, maar publiceert in de beschikkende artikelen **geen zelfstandige nieuwe D3- en D4-frequentietabellen**. Hun voorafgaande laatste intervals moeten uit eerdere besluiten worden opgebouwd, niet fictief aan 2018 worden toegeschreven.

## 3. Historische numerieke routegegevens en juridische ontwikkeling

| Besluit | Relevante route(s) | Historische waarden / rechtsgevolg |
|---|---|---|
| **197-2010**, art. 1 p. 6–8 | **D5** | **6/9 min**, **19–23** voertuigen, toen BUS; werking afhankelijk van kennisgeving bij Transmetro |
| **213-2010**, art. 1 p. 5–7 | **D4** | **3/5 min**, **26–32** voertuigen, toen MICROBUS; historische route Soledad–Centro–Circular |
| **214-2010**, art. 1 p. 6–8 | **D3** | **6/9 min**, **19–23** voertuigen, toen BUS; historische route Hipódromo–INEM |
| **365-2010**, art. 1–2 p. 4–5 | **D3** | **Correctie** van straattraject uit 214-2010; andere technische kenmerken niet onafhankelijk vernieuwd |
| **366-2010**, art. 1–2 p. 3–4 | **D5** | **Correctie** van route uit 197-2010, zonder zelfstandig nieuwe frequenties |
| **247-2011**, art. 1–3 p. 7–8 | **D5**, ondanks drukfout `B6` in openingszin art. 1 | Herstructureert D5; art. 2 verandert 366-2010 deels en art. 3 **behoudt technische kenmerken en capaciteit** |
| **381-2015**, art. 1 p. 9–10 | **D3 en D5** | De overheid **herstructureert zelf** deze routes en behandelt terminalverplaatsing. De door COOTRASOL aangevraagde *private* routewijziging was volgens dossier niet toelaatbaar wegens grotere lengteverandering; dit is **niet** hetzelfde als een afwijzing van de door AMB uitgevoerde herstructurering |
| **060-2016**, art. 1–3 p. 16–17 | **D3-4147 en D5-4149** | **Bezwaar deels toegewezen**: corrigeert vervangen art. 1 uit 381-2015 met nieuwe straattrajecten; bevestigt de andere artikelen en verduidelijkt afwijzing oorspronkelijke particuliere wijzigingsaanvraag |
| **386-2018**, art. 1 p. 6–8 | **D5-4149**, vlootaandeel D3+D4 | D5 **4/6 min**, **22–27**, **46,7 km**; 2018 totale vloot **64–78**. Behandelt *geen nieuwe A/B-varianten*. |
| **467-2025**, art. 1 p. 4–9 | **D3, D4, D5** | Nieuwe 2025 tabellen **6,5/8**, **7/9**, **6,5/9**; bedrijfsverdeling **64–78** |

### Twee historische intrekkingen
- **234-2010**, art. 1–2, p. 5–6: trekt oude lijn **Calle 30 – Murillo – La Paz** in, met werking gekoppeld aan Transmetrostart en AMB-kennisgeving.
- **235-2010**, art. 1–2, p. 5–6: trekt oude **Ruta No. 1 – Calle 30 – Aeropuerto** in, onder vergelijkbare invoeringsvoorwaarden.
Deze historische lijnen mogen niet automatisch opnieuw in de actuele GTFS worden opgenomen of gelijkgesteld aan D3/D4/D5.

### Belangrijke interne documentafwijking
**247-2011 art. 1 p. 7** noemt bij aanvang `ruta B6`, terwijl de route-identificatie in de tabel **`D5`** luidt en **art. 2 en 3 van hetzelfde besluit ondubbelzinnig D5** noemen. Dit is een **tekstuele tegenstrijdigheid in het besluit**, geen bewijs dat COOTRASOL een aparte B6 exploiteert. Bij juridische reconstructie moet de originele scan en eventuele rectificatie worden geraadpleegd.

## 4. Dubbele PDF in het extractie-artifact

`386-2018` en `386-2018-v2` hebben **identieke SHA-256**:
`5563fe84204154b850566a03961d890090115c1af16a29895e88030d176d9e48`.

Daarom: **13 manifestregels, 12 unieke PDF's, 12 verschillende juridische bronnen**. Het duplicaat in het manifest wordt gehandhaafd als bronregistratie maar mag geen extra resolutie of route creëren. In het juridische CSV staat een expliciete `exact_duplicate`-regel.

## 5. Werk voor de volgende controles (zonder andere bedrijven te blokkeren)

| ID | Prio | Te onderzoeken | Afsluitcriterium |
|---|---|---|---|
| **CSOL-01** | Hoog | Onafhankelijk vaststellen of D3/D4/D5 op 2-11-2026 daadwerkelijk rijden, en of een bedrijfsspecifiek later besluit bestaat | Officiële opvolgingsstatus of controleerbare operationele bron |
| **CSOL-02** | Hoog | Spits/dal-kloktijden, werk-/weekend-/feestdagroosters en concrete ritten achterhalen, eventueel SIBUS/RCC | `calendar`, `frequencies` en `stop_times` per periode met bron |
| **CSOL-03** | Hoog | Art. 1, p. 4–9 (2025) geordend omzetten naar straatsegmenten, haltes, richtingen en OSM-shapes; p. 6 gedraaid | Betrouwbare geometrie en stopvolgorde |
| **CSOL-04** | Middel | D3/D5 terminaladressen uit 381-2015/060-2016 vergelijken met 2025 (La Nevada vs San Fernando/El Edén); feitelijke terminallocaties vinden | Bronmatige geolocaties van echte begin-/eindhaltes |
| **CSOL-05** | Middel | 247-2011 art. 1 `B6` versus art. 2/3 `D5`: eventuele rectificatie en oude routecodering onderzoeken | Gedocumenteerde besluitfout en geldige historische routeidentificatie |
| **CSOL-06** | Middel | Manifestduplicaat 386-2018-v2 markeren `duplicate_of_386-2018` zonder bewijs te verwijderen | Deduplicatie in verwerkingspipeline |
| **CSOL-07** | Middel | Transmetro-afhankelijke intrekkingen 234/235-2010 en route-invoering 197/213/214-2010: daadwerkelijke ingangsdata | Gedateerde historische routeperioden |
| **CSOL-08** | Middel | Paginavisuele check oude 2010–2011 OCR-straatnamen en historische frequentietabellen bij GTFS-historie | Scans bevestigen specifieke oude routepatronen |
| **CSOL-09** | Middel | AMB brede resolutie **142-2026** (termijn naleven bedrijfscapaciteit) beoordelen of die COOTRASOL-implementatie beïnvloedt | Vastgelegde invloed op termijn, geen wijziging van route-intervallen zonder bewijs |

## 6. GTFS-uitkomst

- `sources/amb/cootrasol_route_parameters_2026-11-02.csv`: zeven historische/actuele vergunningrecords met **per-route** interval, vloot, voertuigklasse, besluit en exacte bronpagina.
- `sources/amb/cootrasol_resolution_legal_index_2026-11-02.csv`: **alle 13 documentregistraties** met SHA-256, artikellocatie, juridische aard, duplicaatmarkering en open punten.
- **`GTFS_READY=no`** voor D3, D4 en D5. Niet rechtstreeks `frequencies.txt`, `calendar.txt`, `trips.txt`, `stop_times.txt` of `shapes.txt` aanpassen: vergunde intervallen ≠ aangetoonde dagelijkse ritten.

**Officiële bronnen:**
- [AMB COOTRASOL-resoluties](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrasol/)
- [467-2025](https://www.ambq.gov.co/wp-content/uploads/2025/12/Resolucion-Metropolitana-No-467-2025-Permiso-de-operacion-cootrasol.pdf)
- [386-2018](https://www.ambq.gov.co/wp-content/uploads/2018/11/Resolucion-Metropolitana-386-18.pdf)
- [060-2016](https://www.ambq.gov.co/wp-content/uploads/2017/11/COOTRASOL-D3-D5-Resolucion-060-16.pdf)
- [381-2015](https://www.ambq.gov.co/wp-content/uploads/2017/11/COOTRASOL-D3-D5-Resolucion-381-15.pdf)
