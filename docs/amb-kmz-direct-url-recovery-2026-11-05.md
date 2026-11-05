# AMB KMZ direct-URL recovery — 2026-11-05

Four AMB webpage source-link collisions were resolved by directly downloading a KMZ whose URL uses its own route code. The files were provided by the user; local ZIP/KML inspection verified their contents. These are **new source files**, not yet incorporated into the automated KMZ manifest or SIU matching pipeline.

| Code | Direct source URL | Size bytes | SHA-256 | KML Placemark | LineString points | Previous incorrect link |
|---|---|---:|---|---|---:|---|
| PT2-4102 | https://www.ambq.gov.co/ruta-de-buses/COOLITORAL/PT2-4102.kmz | 23270 | 912e3afbd7b55dae5010831ac8de4b45f9bd1281fa54bac02114da8849d3b39a | PT2-4102 | 964 | PT1-4101.kmz |
| A16-4161 B | https://www.ambq.gov.co/ruta-de-buses/LA-CAROLINA/A16-4161%20B.kmz | 7677 | 29f020fc00205ed15149cc2fd61623125f0c2e1d9078abafa48818d8e73944a9 | A16-4161 B | 159 | A16-4161 A.kmz |
| B13-B-4189 | https://www.ambq.gov.co/ruta-de-buses/SODETRANS/B13-B-4189.kmz | 20569 | cb245dd833ba3bc2a86dba6407fd2139409b3ee64ecbb5a47cfce1c34507c64f | B13-B-4189 | 528 | B13-4128.kmz |
| C18-4141 | https://www.ambq.gov.co/ruta-de-buses/COOCHOFAL/C18-4141.kmz | 17970 | 465c4e2a72efa4ab193931e166bde40a45679461c7f1ab346ce94b729ec370d4 | C18- 4141 | 728 | C9-4140.kmz |

## Required follow-up

1. Patch KMZ importer to prefer route-code direct URL for these four records, preserve original webpage URL as provenance, and validate expected KML Placemark and SHA.
2. Regenerate manifest and GeoJSON; do not assume previous A/B stop coverage scores are valid for these corrected geometries.
3. Re-run SIU sequence and stop-distance matching for JUAN MINA, VILLA SAN PABLO, MIRAMAR ALAMEDA DEL RIO, LAS GAVIOTAS CALLE 76, RIOMAR AMARILLA, ROJA RIOMAR and COOCHOFAL route candidates.
4. Keep legal route codes and SIU itinerary identities distinct; do not merge routes or approve GTFS shapes before recomputation.

The earlier PT4/PT5 entries have **different** file SHA-256 values and are not part of these collisions.

## Reproduceerbaarheid en bewaarbeleid (besluit 2026-11-05)

**GitHub Actions-artifacts zijn voor dit project voldoende als opslag van de herbouwde AMB-KMZ-brondata.** Er is geen eis om elke KMZ-snapshot automatisch terug te committen naar de repository, en er komt hiervoor geen afzonderlijke persistente bronarchiefworkflow.

De workflow [Rebuild corrected AMB KMZ and SIU matches](../../.github/workflows/rebuild-corrected-amb-kmz-siu-matches.yml) is handmatig te starten via `workflow_dispatch`. Hij haalt de AMB-pagina op, downloadt de KMZ's met de vier gecontroleerde directe URL-overrides uit `scripts/harvest_amb_kmz_routes.py`, converteert naar GeoJSON, controleert de vier herstelde bronverschillen en berekent de SIU-matches en reviewkaarten opnieuw. Het artifact `corrected-amb-kmz-siu-matches` bevat de ruwe KMZ's, GeoJSON, manifest/metadata en match- en reviewresultaten.

**Grenzen:** artifacts hebben een door GitHub ingestelde bewaartermijn en zijn geen onbeperkt archief. Een nieuwe run is reproduceerbaar zolang de publieke AMB-bronnen beschikbaar blijven en dezelfde inhoud aanbieden; `manifest.csv` met bron-URL's en SHA-256 maakt verschillen tussen runs controleerbaar. De workflow is toegevoegd maar de succesvolle uitvoering en artifact-inhoud zijn nog niet bevestigd. De workflow commit geen bronbestanden en wijzigt geen goedgekeurde GTFS-routes of -shapes.
