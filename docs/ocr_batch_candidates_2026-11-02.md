# OCR-batch: aanvullende kandidaatdocumenten (2026-11-02)

Dit is een **kandidatenlijst** naast `docs/ocr_wachtrij.md`. Eerst programmatisch toetsen of PDF-tekst al uitleesbaar is; alleen scans naar OCR sturen.

| Bedrijf | Document | Bron | Actie |
|---|---|---|---|
| COOTRANSNORTE | Resolución 183-2016 | https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/COOTRANSNORTE/Resolucion-183-de-2016-Cootrasnorte.pdf | Download, pdftotext per pagina, zo nodig OCR; routecodes en besluitsoort verifiëren |
| TRASALFA | Resolución 111-2012 B2B | https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-B2B-Resolucion-111-12.pdf | Tekst al online beschikbaar: eerst rechtstreeks extraheren; OCR alleen voor onleesbare kaarten/tabellen |
| MONTERREY | Nog te identificeren besluiten | https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-monterrey/ | Eerst PDF-links achterhalen; nog geen OCR-job zonder PDF |
| TRANSURBAR | Nog te identificeren besluiten | https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-transurbar/ | Archief tijdelijk onbereikbaar; bronlinks verzamelen vóór OCR |
| TRASALFA | 139-2013, 282/283/284/285/286/287-2010 | https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-trasalfa/ | Individuele PDF's identificeren, tekstlaag meten, alleen scans naar OCR |

## Voorstel GitHub Actions
- Manual `workflow_dispatch` met optioneel `agency` en `resolution`.
- Manifest met URL, SHA-256, resolutienummer, bedrijf en routecode; geen binaire PDF's committen.
- Download met timeouts en retries; controleer PDF-signatuur en paginatelling.
- Probeer eerst `pdftotext -layout` per pagina; OCR alleen op pagina's met onvoldoende tekst.
- OCR Spaans (`tesseract` taalpakket `spa`) op gerenderde pagina's, behoud paginanummers en extractiemethode.
- Upload originele PDF's, ruwe tekst en OCR-rapport als GitHub Actions-artifacts.
- Markeer tabellen, routecodes en frequenties als `requires_manual_verification`; **niet automatisch `gtfs/routes.txt` wijzigen**.
