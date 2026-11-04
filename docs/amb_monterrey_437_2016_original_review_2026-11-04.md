# MONTERREY 437-2016 — controle originele PDF (4 november 2026)

## Herkomst en omvang
- Officiële bron: https://www.ambq.gov.co/wp-content/uploads/2017/01/REOLUCION-437-16-MONTERREY..pdf
- GitHub Actions-run: https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41856636491
- Artifact ID: 13337687749; origineel `amb-monterrey-437-2016/monterrey_437-2016/source.pdf`.
- SHA-256: `b47b2c45ea24fd490a8ad0984b9ec78366ac93d23ba9fe103db8a6a1e9213822`.
- 15 originele pagina's, alle 15 tekstlaag, 0 extra OCR-pagina's, 15 controlebeelden.
- PDF-identiteit Resolución Metropolitana **437-16**, vervoerder Transportes Monterrey, datum **21 december 2016** (originele p.11) bevestigd.

## Beschikkende artikelen (originele pagina's 7–11)
- **Artikel 1** herstructureert de toegestane trajecten voor **B8-4124, B11-4166 en B12-4127** en bevat routekaarten, straatlijsten, lengte en technische tabellen.
- **Artikel 2** bepaalt persoonlijke kennisgeving aan de wettelijke vertegenwoordiger, anders kennisgeving per aankondiging; dit is geen bewijs van de werkelijke kennisgevingsdatum.
- **Artikel 3** voorziet in een bezwaar-/heroverwegingsmogelijkheid (`recurso de reposición`).
- Er is op de gecontroleerde beschikkende pagina's **geen zelfstandige, bewezen feitelijke startdatum** van de dienst of bewijs van onherroepelijkheid vastgesteld.

## Bevestigde vergunde historische parameters
| Route | Officiële benaming | Lengte | Spits | Dal | Bronpagina's |
|---|---|---:|---:|---:|---|
| B8-4124 | Manuela Beltrán – Circunvalar – El Bosque – Campo Alegre – Viejo Prado – Circular | 56,5 km | 7 min | 9 min | 7–8 |
| B11-4166 | Manuela Beltrán – Villa Estadio – Sourdis – Ciudad Jardín – Villa Carolina – Circular | 57,4 km | 6 min | 8 min | 9–10 |
| B12-4127 | Las Flores – Vía 40 – Calle 30 – Carrera 27 – El Bosque – La Paz – Circular | 41,5 km | 6 min | **8 min** | 10–11 |

B12 dalinterval 8 minuten is op **originele p.11** visueel gecontroleerd; de tekstextractie liet daar het getal weg. De eerdere dataset `sources/amb/details/resolucion_437-2016_monterrey.csv` komt overeen met deze tabellen.

## Bronafwijkingen zonder GTFS-frequentieblokkade
- In de toelichtende tabel op **p.7** staat minimumvloot **78**, terwijl de definitieve verdeling in het **artikel-1-paragraaf op p.11** **28+28+23=79** bedraagt; maximum **33+33+27=93**. Gebruik 79 als waarde van de beschikkende tabel; bewaar de afwijking 78 als bronnotitie.
- De technische studie op p.12–15 betreft vooral het aanpassen van het **B8-traject** aan feitelijk bereden wegen en bevat historisch vergelijkingsmateriaal met 403-2013. Dat is geen zelfstandig nieuw besluit.
- De formulering `00:00 a las 24:00 ... dependiendo de las necesidades de demanda` is **voorwaardelijk**; zij bewijst geen 24-uursdienst en is geen grond voor automatische GTFS-dienstvensters.
- De officiële 437-2016 heeft drie routes; **B11-B-4192** is hier niet als extra vergunde route aangetoond. Deze variant vereist voor een eigen juridische basis een afzonderlijke latere bron.
- De tijdelijke B11-herstructurering **390-2018** moet als latere bron afzonderlijk worden toegepast; 437-2016 niet zonder meer als actuele situatie gebruiken.

## Afrondingsbesluit
**437-2016 origineel, artikel 1, drie route-identiteiten, historische lengtes en spits-/dalintervallen: AFGEROND — BEVESTIGD.**
**Latere wijzigingen, daadwerkelijke exploitatie en dienstkalender: afzonderlijk van deze broncontrole; geen hernieuwde OCR of bronidentiteitsblokkade.**

Geen productie-GTFS-bestanden aangepast.
