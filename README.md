# GTFS Barranquilla Urbanas

Onderzoeksrepository voor een **statische GTFS-feed van het traditionele collectieve busvervoer (TPC)** in het Área Metropolitana de Barranquilla. **Niet** de Transmetro-GTFS.

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
| Stops, stopvolgorde, trips en rijtijden | 599 OSM-objecten geïnventariseerd; 0 bevestigde TPC-haltes; blokkeert complete GTFS |

De officiële AMB-resoluties gelden als onze leidende bron voor de **spits-/dalfrequenties**. De [eerste/laatste vertrekuren uit AMB-kaarten van juli 2020](sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv) en de indeling 07:00–09:00 / 17:00–20:00 spits maandag–vrijdag vormen **expliciete, vervangbare modelaannames**, niet officieel bevestigde 2026-rijtijden. **Voertuigcapaciteit telt niet mee.**

## Reproduceerbare GitHub Actions

- [Build AMB GTFS frequency staging](.github/workflows/build-amb-gtfs-frequency-staging.yml): leest de onderzochte resoluties, matcht de huidige route-ID's en schrijft 245 voorlopige perioden, 34 open issues en samenvatting.
- [Harvest Barranquilla ArcGIS route shape candidates](.github/workflows/harvest-amb-arcgis-shapes.yml): downloadt de historische gemeentelijke geometrielijnen en matcht routecodes; publiceert een bron-/matchingrapport en bewaart de GeoJSON als artifact.
- [Extract AMB PDFs](.github/workflows/extract-amb-pdfs.yml), [PDF batch-extractie](.github/workflows/extract-amb-pdfs-batch.yml) en [validatie](.github/workflows/validate-amb-resolutions.yml): originele vergunningen, OCR en artikelcontrole.
- [Extract historic AMB first/last departures](.github/workflows/harvest-amb-2020-route-posters.yml): verwerkt 24 officiële historische routekaarten.

## Belangrijke bestanden

- [Onderzoeksrapport GTFS-bouwketen](docs/gtfs_build_staging_progress_2026-11-03.md)
- [Inventaris haltebronnen en nog ontbrekende TPC-stopdata](docs/stop_data_inventory_2026-11-03.md)
- [OSM/Overpass-resultaten: 599 bushalteobjecten, 34 mogelijke instapplaatsen en 16 GIS-prioriteitslocaties](sources/osm/README.md)
- [Frequentiebron per GTFS-route](sources/amb/gtfs_staging/route_headway_candidates.csv)
- [Voorgestelde weekdagperiodeblokken](sources/amb/gtfs_staging/weekday_period_staging.csv)
- [34 routes met open punten](sources/amb/gtfs_staging/unresolved_route_issues.csv)
- [ArcGIS-shape-koppelingen](sources/amb/arcgis_shape_staging/route_shape_matches.csv)
- [23-bedrijven- en resolutieregister](docs/amb_bedrijven/README.md)
- [Tijdvakkenmodel](docs/amb_peak_offpeak_model_2026-11-03.md)

## Vervolg: haltegegevens en ritpatronen

Voor een echte GTFS moeten we nog `stops.txt`, `trips.txt`, `stop_times.txt`, een dagkalender en gecontroleerde `shapes.txt` maken. **We maken geen fictieve halteposities of rijtijden.** De ArcGIS-lijnen stammen hoofdzakelijk uit een 2019-collectie, laatste GIS-bewerking december 2023. Recentere resolutiegeometrie uit 2025/2026 kan daarvan afwijken; A/B-varianten die één lijn delen zijn nog geen afzonderlijk gecontroleerde ritgeometrieën.

Vaste officiële bron: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/
