# SIU halteattributen en GraphQL-broncontrole — 5 november 2026

## Herkomst
- Publieke pagina: https://siu.ambq.gov.co/siu/schedule-mng/schedules
- GraphQL-pad: `/api/pis-gateway/graphql/http`
- In de publiek geserveerde JavaScript-code bevestigd: `query ServiceMngCompressedItineraryListing($organizationId:String) { ServiceMngCompressedItineraryListing(organizationId:$organizationId) }`.
- Respons: `compressedModsBase64` (Base64 + zlib); de browser decodeert een lijst met itineraries. Dit is geobserveerd applicatiegedrag, geen gegarandeerd API-contract.

## Bevestigde velden
- Itinerary: `id` (UUID), `routeId` (basisroute-UUID), `orgId`, `n` (naam), `comps` (vervoerders), `active`, `stops` (geordende lijst).
- Haltevermelding: `id` (SIU UUID), `n` (haltenaam), `lat`, `lng`, `dis` (betekenis/eenheid nog niet vastgesteld).
- De lijstpositie wordt als `siu_stop_sequence` (1-based) geëxporteerd; dat is een afgeleid attribuut en geen apart GraphQL-veld.
- De export bewaart `source_dis_uninterpreted`, `source_snapshot_utc`, `source_url`, `likely_test_itinerary`.

## Snapshot 2026-11-04T16:55:28Z
- 36 itineraries, waarvan 3 als test gemarkeerd; alle 36 met `active=true`.
- 6.873 haltepassages, 6.873 verschillende SIU stop-UUID's, 0 ongeldige GPS-coördinaten.
- Het aantal unieke UUID's is **niet** het aantal unieke fysieke haltes: identieke/nabije locaties met dezelfde volledige genormaliseerde naam kunnen worden samengevoegd.
- MHT-steekproef: 10/10 halte-UUID's aangetroffen op de verwachte posities 75–84.

## Bestaande GTFS-staging
`scripts/build_siu_gtfs_stop_staging.py` bouwt kandidaat-`stop_id` als `SIU_<uuid>`, behoudt richtingsmarkeringen in namen en clustert uitsluitend gelijke volledige genormaliseerde namen waarvan alle coördinaten onderling binnen 5 meter liggen. Er bestaat al een `stop_id_alias_history.csv` voor continuïteit. Een SIU UUID kan een passage-identificatie zijn; behandel hem niet zonder nader bewijs als een stabiele fysieke halte-identificatie.

## Openstaande GraphQL-vragen
1. Welke extra, niet geëxporteerde sleutels zijn aanwezig in individuele halte-objecten en in `stops`-gerelateerde UI-queries? Gebruik een **alleen-sleutels**-audit, zonder persoonsgegevens, autorisatiegegevens of volledige payloads te bewaren.
2. Wat betekent `dis`, in welke eenheid, en hoort dit bij de halte, de routepositie of een actuele service?
3. Zijn er aparte halte-detailoperaties die `stop_code`, `stop_desc`, `wheelchair_boarding`, `platform_code` of een persistent fysiek halte-ID leveren? **Niet aangetoond.**
4. Zijn stop-UUID's stabiel tussen onafhankelijke snapshots? De huidige 6.873/6.873 unieke UUID's bewijzen dat niet.
5. Zijn brondata en afgeleide gegevens herpubliceerbaar? **Rechten niet bevestigd.**

## Grenzen
De GraphQL-data levert geen bevestigde GTFS `arrival_time`/`departure_time`, rolstoeltoegankelijkheid of formele halteplatformcodes. `servs` en `service.stops` bevatten UI-/ETA-gerelateerde velden, maar zijn geen gevalideerde statische dienstregeling. De juridische onderzoeksfase blijft afgesloten; deze inventaris opent geen besluiten opnieuw.
