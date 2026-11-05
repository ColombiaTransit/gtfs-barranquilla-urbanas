# Open verificatiepunt: COOTRAB C5-routecode

Status: **open — niet corrigeren zonder bronverificatie**

## Geconstateerd verschil
- AMB-webcatalogus: `C5-4135` (volgens eerder onderzoek; opnieuw controleren).
- Resolución Metropolitana 378-2023: `C5-4136` (volgens extractie in `sources/amb/details/resolucion_378-2023_cootrab.csv`; controleer tegen origineel).

## Uit te voeren werk
1. Vergelijk de originele AMB-webcatalogus met Resolución 378-2023, inclusief de gedrukte routecode en eventuele bijlagen.
2. Zoek naar latere besluiten, rectificaties of hernummeringen van COOTRAB C5.
3. Controleer de relatie met C4-4135 en mogelijke verschrijving/verwisseling.
4. Leg de gekozen officiële code, bron-URL, besluitdatum en motivatie vast in het bronregister.
5. Controleer pas daarna `gtfs/routes.txt`, eventuele ArcGIS-shapes en latere GTFS-koppelingen; houd `route_id` en administratieve code conceptueel gescheiden.

Tot verificatie: **geen automatische wijziging aan routes.txt of shapes**.


## Archiefreconciliatie — 5 november 2026

Archiefhercontrole: 358-2024 bevestigt 8/10 voor C5-4136 en C6-4137, maar lost het al bekende conflict C5-4135 in AMB-kaartviewer versus C5-4136 in beschikkingen niet op. Geen automatische routecodecorrectie en geen nieuwe OCR van reeds gecontroleerde tabel.

Zie [route-voor-route classificatie](../sources/amb/amb_archive_route_reconciliation_2026-11-05.csv) en [inhoudelijke vergelijking](amb_archive_2020_2026_existing_register_comparison_2026-11-05.md).
