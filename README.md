# GTFS Barranquilla Urbanas

Onderzoeksrepository voor een **statische GTFS-feed van het traditionele collectieve busvervoer (TPC)** in het Área Metropolitana de Barranquilla. **Niet** de Transmetro-GTFS.

> **Registerbeleid (5 november 2026):** [Canonical register architecture](docs/canonical_register_architecture.md) is leidend. De GTFS-generator leest frequenties en vertrekvensters uitsluitend uit `build/registries/route_service.csv`, dat tijdens de workflow wordt geconsolideerd. Oudere staging- en bronbestanden zijn bewijs/QA, geen alternatieve operationele invoer. De volledige migratie van haltes, shapes en Flex naar één generator is nog openstaand.

## Huidige status — 3 november 2026

**GTFS-onderzoeksmodel, nog geen volledige publiceerbare feed.**

| Onderdeel | Status |
|---|---|
| `gtfs/agency.txt` | 23 vervoerbedrijven |
| `gtfs/routes.txt` | 97 route-/variant-ID's, waaronder correctie COOTRAB C5-4136 |
| Vergunningsfrequenties + voorlopig dienstvenster | 63/97 routepatronen voorbereid |
| Weekdagperiodeblokken | 245 kandidaten voor een latere `frequencies.txt` |
| Nog te onderzoeken | 34 route-/variantregistraties |
| GIS-geometry | 93 bronfeatures, 97/97 **routecodekoppelingen** (geen gevalideerde shapes) |
| Haltes en haltevolgorde | **3.117 conservatief samengevoegde concept-haltes** uit 6.407 SIU-stopvermeldingen; 12 sterke plus 8 extra voorlopige SIU→AMB-basisroutekoppelingen en 3.981 concept-route-stopvolgorderegels |

De officiële AMB-resoluties gelden als onze leidende bron voor de **spits-/dalfrequenties**. De [eerste/laatste vertrekuren uit AMB-kaarten van juli 2020](sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv) en de indeling 07:00–09:00 / 17:00–20:00 spits maandag–vrijdag vormen **expliciete, vervangbare modelaannames**, niet officieel bevestigde 2026-rijtijden. **Voertuigcapaciteit telt niet mee.**

Twee evidente SIU-spelfouten zijn via een [controleerbare correctietabel](sources/siu/stop_name_spelling_corrections_2026-11-03.csv) genormaliseerd, zonder oorspronkelijke namen of richtingsinformatie te verliezen. Eén eerder afzonderlijke stop-ID is [als alias](sources/siu/gtfs_staging/stop_id_alias_history.csv) bewaard.

## Reproduceerbare GitHub Actions

- [Build AMB GTFS frequency staging](.github/workflows/build-amb-gtfs-frequency-staging.yml): leest de onderzochte resoluties, matcht de huidige route-ID's en schrijft 245 voorlopige perioden, 34 open issues en samenvatting.
- [Harvest Barranquilla ArcGIS route shape candidates](.github/workflows/harvest-amb-arcgis-shapes.yml): downloadt de historische gemeentelijke geometrielijnen en matcht routecodes; publiceert een bron-/matchingrapport en bewaart de GeoJSON als artifact.
- [Extract AMB PDFs](.github/workflows/extract-amb-pdfs.yml), [PDF batch-extractie](.github/workflows/extract-amb-pdfs-batch.yml) en [validatie](.github/workflows/validate-amb-resolutions.yml): originele vergunningen, OCR en artikelcontrole.
- [Extract historic AMB first/last departures](.github/workflows/harvest-amb-2020-route-posters.yml): verwerkt 24 officiële historische routekaarten.
- [Stage SIU route crosswalk and GTFS stop candidates](.github/workflows/stage-siu-gtfs-stops.yml): maakt conservatieve fysieke stop-ID's, 12 voorlopige routekoppelingen, 53 stopnaamconflicten en een complete reviewqueue.
- [Review all unresolved SIU to AMB route links](.github/workflows/review-siu-open-route-links.yml): controleert 21 open SIU-itineraries, levert 8 extra basisroutevoorstellen en 3.981 stopvolgorderegels voor 20 voorgestelde routecodes.
- [Recover AMB Coolitoral 256-2026 original pilot PDF](.github/workflows/recover-amb-coolitoral-256.yml) en [SIU/PT4/PT5-straatcontrole](.github/workflows/audit-siu-coolitoral-256-streets.yml): geverifieerd origineel besluit en vier A/B-straattrajecten, maar nog geen bevestigde SIU→A/B-koppeling.

## Belangrijke bestanden

- [Onderzoeksrapport GTFS-bouwketen](docs/gtfs_build_staging_progress_2026-11-03.md)
- [Inventaris haltebronnen en nog ontbrekende TPC-stopdata](docs/stop_data_inventory_2026-11-03.md)
- [**SIU-route- en halteonderzoek:** 36 itineraries, 6.873 route-halteregels, inclusief 33 reguliere itineraries](docs/siu_sibus_mht_route_stop_analysis_2026-11-03.md)
- [SIU-routehaltelijst met naam, GPS en volgorde](sources/siu/public_extract/siu_route_stop_sequences.csv)
- [**SIU-review: 12 sterke + 8 nieuwe voorlopige routekoppelingen; 13 nog ambigu**](docs/siu_remaining_21_route_links_review_2026-11-03.md)
- [**3.117 concept-haltes en 53 naamconflicten**](docs/siu_gtfs_stop_crosswalk_staging_2026-11-03.md)
- [Concept `stops.txt` — niet publiceren](sources/siu/gtfs_staging/stops_draft_NOT_FOR_PUBLICATION.txt)
- [OSM/Overpass-resultaten: 599 bushalteobjecten, 34 mogelijke instapplaatsen en 16 GIS-prioriteitslocaties](sources/osm/README.md)
- [Frequentiebron per GTFS-route](sources/amb/gtfs_staging/route_headway_candidates.csv)
- [Voorgestelde weekdagperiodeblokken](sources/amb/gtfs_staging/weekday_period_staging.csv)
- [34 routes met open punten](sources/amb/gtfs_staging/unresolved_route_issues.csv)
- [ArcGIS-shape-koppelingen](sources/amb/arcgis_shape_staging/route_shape_matches.csv)
- [23-bedrijven- en resolutieregister](docs/amb_bedrijven/README.md)
- [Tijdvakkenmodel](docs/amb_peak_offpeak_model_2026-11-03.md)

## Vervolg: haltegegevens en ritpatronen

De SIU-bron heeft nu **33 reguliere geordende itineraries met 6.407 GPS-stopvermeldingen** (plus drie testitineraries). Voor een echte GTFS moeten we nog haltes correct dedupliceren, de SIU-itineraries aan de AMB-routecodes koppelen en `stops.txt`, `trips.txt`, `stop_times.txt`, een kalender en geverifieerde `shapes.txt` genereren. **We maken geen fictieve halteposities of rijtijden.** De ArcGIS-lijnen stammen hoofdzakelijk uit een 2019-collectie, laatste GIS-bewerking december 2023. Recentere resolutiegeometrie uit 2025/2026 kan daarvan afwijken; A/B-varianten die één lijn delen zijn nog geen afzonderlijk gecontroleerde ritgeometrieën.

Vaste officiële bron: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/
