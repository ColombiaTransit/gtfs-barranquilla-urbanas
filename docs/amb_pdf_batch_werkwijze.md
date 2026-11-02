# AMB PDF-verwerking — volledige batch (2 november 2026)

De centrale werklijst staat in [pdf_manifest.csv](../sources/amb/pdf_manifest.csv): 273 PDF-verwijzingen voor 22 bedrijven. Zes documenten stonden al in het oorspronkelijke manifest en zijn in run 41476363247 eerder geëxtraheerd; de overige 267 zijn toegevoegd op basis van het publieke resolutieoverzicht van `IngBenichi/Urban-Route_AI` (`scraper/data/ambq/resoluciones_index.json`).

## Uitvoeren

Open [Extract AMB PDFs by company (batch)](../.github/workflows/extract-amb-pdfs-batch.yml) in GitHub Actions, kies **Run workflow** en laat het veld `agency` leeg om alle 22 bedrijven te verwerken. Een bedrijf afzonderlijk verwerken kan met de exacte waarde uit de kolom `agency`, bijvoorbeeld `TRANSURBAR`. Maximaal vier bedrijven lopen parallel. Ieder bedrijf krijgt een apart artifact `amb-pdf-BEDRIJF` met bron-PDF's, paginagewijze tekst en `report.json`. De bestaande workflow `extract-amb-pdfs.yml` blijft beschikbaar voor een specifieke resolutie.

## Kwaliteitscontrole

- `pending` betekent: in de werklijst, **niet** geverifieerd als succesvol gedownload of uitgelezen.
- De index is een externe inventaris; URL, resolutienummer en bedrijf kunnen fouten bevatten.
- Suffixen `-v2` etc. in de manifest-resolutie zijn technische sleutels voor dubbele nummers en **geen officiële resolutienummers**.
- `177-undated` heeft geen betrouwbaar jaartal uit de index.
- Elke batch heeft een downloadlimiet van 35 MB per PDF en een maximum van 150 pagina's; fouten verschijnen in `report.json`.
- OCR-tekst, tabellen en routevolgordes blijven `extracted_requires_review`; pas na inhoudelijke validatie mogen gegevens in GTFS worden verwerkt.
- De batch maakt geen aanpassingen aan `gtfs/`.

## Analysevolgorde

Eerst TRANSURBAR (12 resoluties) en TRASALFA (8), vervolgens de andere bedrijven per bedrijf. Vergelijk basisbesluiten en latere wijzigingen, rapporteer routecodes, beide rijrichtingen, straatvolgorde, spits-/dalinterval, voertuigcapaciteit, diensturen en eventuele tegenstrijdigheden. Maak een aparte herverwerkingslijst van `failed` records en onleesbare pagina's.
