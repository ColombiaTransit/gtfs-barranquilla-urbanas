# AMB PDF processing — full batch (November 2, 2026)

The central worklist is [pdf_manifest.csv](../sources/amb/pdf_manifest.csv): 273 PDF references for 22 operators. Six documents were already included in the original manifest and extracted in run 41476363247; the remaining 267 were added from the public resolution index maintained by IngBenichi/Urban-Route_AI.

## Running the batch

Open [Extract AMB PDFs by company (batch)](../.github/workflows/extract-amb-pdfs-batch.yml) in GitHub Actions, select **Run workflow**, and leave `agency` blank to process all 22 operators. To process one operator, enter its exact `agency` column value, such as `TRANSURBAR`. Up to four operators run in parallel. Each operator produces an `amb-pdf-OPERATOR` artifact containing source PDFs, page-by-page text, and `report.json`. The existing `extract-amb-pdfs.yml` workflow remains available for individual resolutions.

## Quality assurance

- `pending` means listed for processing, **not** verified as successfully downloaded or extracted.
- The index is an external inventory; URLs, resolution numbers, and operator names may contain errors.
- Suffixes such as `-v2` in manifest resolution keys disambiguate duplicate numbers and are **not official resolution numbers**.
- `177-undated` has no reliable year in the index.
- Each batch limits downloads to 35 MB per PDF and 150 pages; failures are recorded in `report.json`.
- OCR text, tables, and route sequences remain `extracted_requires_review`; only substantively validated data may enter GTFS.
- The batch does not modify `gtfs/`.

## Review order

Review TRANSURBAR (12 resolutions) and TRASALFA (8) first, then process the remaining operators individually. Compare original resolutions with subsequent amendments; report route codes, both directions, street sequences, peak/off-peak headways, vehicle capacity, service hours, and contradictions. Maintain a separate reprocessing list for `failed` records and unreadable pages.
