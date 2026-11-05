# GTFS-generator v2 — vastgestelde bouwafspraken (2026-11-05)

## Doel
Eén reproduceerbare generator met expliciete bronregistraties, validatie en scheiding tussen onderzoeksdata en publiceerbare GTFS. De bestaande research-pilots zijn geen productie-input.

## Bronhiërarchie en invarianten
1. Gebruik de actuele officiële AMBQ-KMZ-harvest met de vier routecode-overrides in `scripts/harvest_amb_kmz_routes.py`. Alle 93 KMZ's werden op 5 november geïmporteerd zonder URL-conflicten. Oude PT2/D8 fallback-labels zijn geen bewijs van ontbrekende KMZ.
2. Koppel routes via expliciete, controleerbare crosswalk op bedrijfsnaam, routecode en A/B-variant. Een ontbrekende exacte stringmatch is een mapping-issue, niet automatisch een ontbrekende shape. Nooit automatisch een andere routecode kiezen.
3. Bewaar KMZ-geometrie als officiële bron. Geen nieuwe GraphHopper-verfijning, ArcGIS-override of route-inventarisatie. Eventuele bestaande goedgekeurde geometriecorrecties alleen met expliciete provenance en zonder stopvolgordeverandering.
4. A4-4109 en D8-4165 blijven `DEFERRED_GEOMETRY_REVIEW`: geen definitieve shape-approval op basis van voorlopige geometrie.
5. Gebruik bestaande fysieke SIU-stop-ID's en bronvolgorde; geen verzonnen haltes, stop_sequences, richtingen of tripgrenzen. Projecteer stopvolgorde op kandidaat-shape en registreer afwijkingen.
6. Gezamenlijk geëxploiteerde exact dezelfde variant: één samengestelde/virtuele agency, één dienstregeling/frequentie, behoud afzonderlijke vervoerders in provenance/attributions. Geen automatische samenvoeging op alleen routenummer.
7. Leg bronbesluiten en frequenties uit AMBQ-resoluties en eerder geconsolideerde staging vast. Eerder afgesproken modelaannames blijven als aannames gelabeld; geen nieuwe tijden of piek/dalvensters verzinnen.
8. Schrijf geen fictieve stop_times of calendar in een publiceerbare feed. Geen synthetic research-demo export onder `gtfs/`.

## Pipeline
- **01 source snapshot**: AMBQ manifest/GeoJSON + checksum; SIU-stopbronnen; routes/agency; resolutie- en headway-registers.
- **02 identity crosswalk**: route-ID, routecode, variant, exploitanten, source KMZ en legal status; expliciete `held` redenen.
- **03 shapes**: per geaccepteerde routevariant brongetrouwe LineString(s) assembleren met controle op aansluitingen, richting en stopvolgorde. `shape_id` deterministisch en traceerbaar.
- **04 service**: trip templates alleen als bronritpatroon en richting aantoonbaar zijn; dienstkalender en frequenties alleen met vastgelegde bron/modelstatus.
- **05 validation**: referentiële integriteit van shape_id/trip_id/route_id/stop_id; unieke stopvolgorde; shape nabijheid; MobilityData validator; geen regressie.
- **06 outputs**: `build/gtfs-v2/research/` voor onvolledige kandidaatfeeds; `build/gtfs-v2/publish/` uitsluitend na volledige gate. `coverage.csv`, `held_routes.csv`, `source_provenance.csv`, `validation_summary.json`.

## Publicatie-gates
Een KMZ met `geometry_imported` is **niet** automatisch een goedgekeurde GTFS-shape. Een route met onvolledige geometrie, stopvolgorde, dienstkalender of frequentie wordt apart gerapporteerd. De generator mag bij ontbrekende informatie niet stilzwijgend op ArcGIS, GraphHopper of fictieve tijden terugvallen.

## Bekende historische cijfers (geen actuele dekkingsclaim)
- 93/93 KMZ geïmporteerd; 334 LineStrings; nul URL-conflicten in run 42038312511.
- De eerdere 70-patroon/67-demo-trip build gebruikte nog PT2- en D8-fallbacks en is daarom niet de basis voor publicatie.
- `gtfs/routes.txt` bevat 97 route-registraties; de eerdere exacte bronkoppeling vond 87 matches en 10 mapping-reviews. PT2 is wel als KMZ geïmporteerd maar staat niet als eigen route in deze lijst.
- A4 en D8 blijven bewust geparkeerd.

## Migratie
Bestaande bron- en QA-scripts blijven behouden als historische bewijsstukken. Nieuwe generator leest de actuele manifesten en expliciete crosswalks; hij mag geen oude `GH_bus_fallback_no_usable_2026_KMZ` status zonder hercontrole overnemen. Vóór productie eerst de tien mapping-reviews en publicatie-gates toetsen.
