# EMBUSA — besluitketen B9-4125 (broncontrole uit GitHub Actions-artifact)

**Bronmateriaal:** `amb-pdf-EMBUSA`, extractierun 41480204032. Alle vijf manifestitems bekeken: 293-2010, 293-2010-v2, 113-2012, 231-2025, 010-2026. Paginaverwijzingen hieronder verwijzen naar de PDF-pagina's.

## Vastgestelde chronologie
| Besluit | Artikel/locatie | Feitelijke bevinding | Betekenis |
|---|---|---|---|
| 293-2010 | art. 1, p. 6–9 | Reorganisatie van historische route CENTRO; gedetailleerde tabel op p. 8 | Historische basis; niet zonder meer huidige B9-4125 |
| 293-2010-v2 | alle pagina's | PDF SHA-256 identiek aan 293-2010: `f69abe7a1dbbc8d482dc10f74d3bcc4e06d84c4c11f0f791aaf0674a4360aefb` | Exact duplicaat; één juridische bron, twee manifestitems |
| 113-2012 | p. 5–7, art. 1–2 | Herstructureert B9-4125; 4 min spits, 6 min dal, 37–45 voertuigen; bestaande capaciteit blijft volgens art. 2 gelijk | Historische routewijziging |
| 231-2025 | p. 5–6, art. 1 | Wijzigt B9-4125, *El Boliche–Las Nieves–Carrera 8–Calle 53D–Lucero–El Recreo–Carrera 58–Calle 77–Bellavista–Montecristo–Calle 54–La Sierra–Carrera 8–Calle 17–Carrera 38*; 42,5 km; 3 min spits, 5 min dal; 47–56 voertuigen | Nieuwere vergunningsparameters, maar inmiddels door 010-2026 gewijzigd |
| 010-2026 | p. 3–5, art. 1 | Wijzigt B9-4125, *Zona Franca–Las Nieves–Carrera 8–Lucero–El Recreo–Carrera 58–Calle 77–Vía 40–Río Alto–Las Flores–Circular*; 53,9 km; 4 min spits, 6 min dal; 47–56 voertuigen | Laatste aangetroffen expliciete routeparameters |

## Relevante wijzigingen 231-2025 → 010-2026
- **Lengte:** 42,5 → 53,9 km (+11,4 km).
- **Spitsinterval:** 3 → 4 min (+1 min).
- **Dalinterval:** 5 → 6 min (+1 min).
- **Capaciteit:** 47–56 voertuigen in beide besluiten; 010-2026 art. 1, par. 1 bevestigt ongewijzigde capaciteit.
- **Route:** nieuwe dekking Río Alto en Las Flores.
- **Overlapping:** 231-2025 p. 5 noemt troncal 16% en alimentación 59%; 010-2026 p. 5 noemt 10,7% en 51%.
- **Voorwaardelijk venster:** beide besluiten vermelden 00:00–24:00 *afhankelijk van de vraag*. Dit is **geen** bewijs van daadwerkelijke 24-uursdienst.

## Kwaliteit en vervolg
- **Bronzekerheid:** hoog voor de numerieke waarden uit 010-2026 (native text), middel voor 231-2025 (OCR is vervormd, numerieke tabel leesbaar). 
- **Juridische beperking:** besluiten en artikels zijn geanalyseerd, maar inwerkingtreding, beroep en latere besluiten buiten het manifest zijn niet onafhankelijk vastgesteld.
- **Open EMB-01:** 231-2025 p. 4–8 handmatig verifiëren op kaart/straattraject, OCR is sterk vervormd.
- **Open EMB-02:** 293-2010 p. 7–8 tabel en routecodes exact transcriberen.
- **Open EMB-03:** precieze rijrichtingen, haltes, spits-/dalvensters en feitelijke diensttijden uit actuele bron verifiëren.
- **Open EMB-04:** duplicaat 293-2010-v2 markeren in manifest zonder bron te verwijderen.

**GTFS:** geen `frequencies.txt`, `stop_times.txt` of `shapes.txt` genereren op grond van vergunningsparameters alleen. Huidige exploitatie is onbevestigd.
