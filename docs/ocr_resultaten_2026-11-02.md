# OCR-resultaten en kwaliteitscontrole — 2026-11-02

Bron: [GitHub Actions-run 41476363247](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41476363247), artifact `amb-pdf-extractions` (ID 13158200676). Zes resoluties, 57 tekstpagina's. **Historische vergunningswaarden, niet bevestigd als actuele dienstregeling.**

| Bedrijf | Resolutie | Route | Spits (min) | Dal (min) | Voertuigen | Status |
|---|---|---|---:|---:|---|---|
| TRASALFA | 111-2012 | B2B-4118 | — | — | Ongewijzigd t.o.v. 287-2010 | OCR, handmatige controle |
| COOTRANSNORTE | 183-2016 | A6-4111 | 6 | 8 | 19–23 | Tekstextractie, handmatige controle |
| TRANSMECAR | 324-2010 | Soledad–Murillo–Vivero | 4 | 6 | 40–48 | OCR, routecode verifiëren |
| TRASALIANCO | 408-2013 | D18-4179 | 7 | 10 | 27–33 | OCR, traject controleren |
| LA CAROLINA | 067-2011 | A16-4161 | — | — | Zie 173-2010 | OCR, basisbesluit nodig |
| EMBUSA | 113-2012 | B9-4125 | 4 | 6 | 37–45 | OCR, traject controleren |

Deze waarden zijn onderzoeksnotities die aan de originele pagina's moeten worden getoetst. Niet direct in `frequencies.txt` zetten: spits/dal-uren, geldigheid en latere wijzigingen zijn onbekend. Geen 24-uursdienst afleiden uit een voorwaardelijk venster 00:00–24:00.

## Vervolgvolgorde
1. TRANSURBAR: 051-2017 (A14, D16, D19), 717-2018, daarna historische besluiten.
2. TRASALFA: 285-2010 (D15), 286-2010 (D14), 287-2010 (B2B), daarna 139-2013 en overige besluiten.
3. Alleen PDF's zonder tekstlaag naar OCR; wijzigingen van latere besluiten boven eerdere leggen.

Zie `sources/amb/transurbar_trasalfa_resolutions_index.csv` voor 20 geïdentificeerde bronverwijzingen. De index is geen inhoudelijke PDF-extractie.
