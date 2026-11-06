# Central OCR and image-verification work queue

## November 4, 2026 update — original scans are technically available

The [successful OCR and source retrieval workflow](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41786660704) retrieved **6/6 source PDFs**, performed Spanish OCR on **61/61 PDF pages**, and collected **48 original page images** for verification. **All six documents retain outstanding manual/visual reviews of operative articles and maps**; only retrieval and OCR are technically complete.

The [initial manual review](amb_ocr_first_visual_verification_2026-11-04.md) examined original pages from TRANSMECAR 324-2010, TRASALIANCO 408-2013, LA CAROLINA 067-2011, and TRASALIANCO 266-2010. A legally significant finding for LA CAROLINA 067-2011 is confirmed: **067 modifies the A16 itinerary but retains the technical route parameters from 173-2010**. Therefore, no new headway can be inferred from 067 alone.

The historical queue is retained below; three outdated notices that an original PDF was still missing have been corrected.

Status as originally recorded on November 2, 2026. Only register documents lacking a reliable machine-readable text layer here. This queue is separate from general AMB source research.

| Operator | Resolution | Route | Reason | Required review |
|---|---|---|---|---|
| TRANSMECAR | 324-2010 | C17-4160 | Scan without reliable text extraction | Read tables and itinerary page by page; independently verify |
| TRASALIANCO | 408-2013 | D18-4179 | Scanned document; historical figures provisionally registered separately | Verify map and street sequence |
| LA CAROLINA | 067-2011 | A16-4161 | Scanned document | Verify itinerary and references to 173-2010/204-2012 |
| TRASALIANCO | 266-2010 | B19-4176 | **Original PDF retrieved; Spanish OCR for all 10 pages; cover visually checked** | Verify B19 association, operative articles, and map pages |
| TRASALIANCO | 265-2010 | D12-4154 | **Original PDF retrieved; Spanish OCR for all 10 pages** | Verify document identity, route map, and tables against original images |
| TRASALIANCO | 268-2010 | D17-4158 | **Original PDF retrieved; Spanish OCR for all 10 pages** | Verify original images, relationship to 411-2010, and route map |

EMBUSA 113-2012 has already been partially extracted through visual inspection. Its complete street sequence requires separate verification, but it must not be marked as wholly unprocessed again.

For newly discovered scanned sources, add a row here. Do not import GTFS parameters from OCR without visual validation.
