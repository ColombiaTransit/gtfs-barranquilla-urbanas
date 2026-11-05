# Bronnen en status

## Officiële AMB-vergunningen
De onderzoeksbasis is de vergunningencatalogus van 97 vermeldingen (stand 2026-11-02). Een vergunning bevestigt niet dat de lijn momenteel rijdt.

Bronportaal: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/

Onderzochte resoluties:
- COOLITORAL: 192-2025, 210-2026, 256-2026
- COOCHOFAL: 242-2025
- COOTRANTICO: 462-2025
- COOTRASOL: 467-2025
- TRANSDIAZ: 501-2025
- COOTRANSPORCAR: 389-2025

## Officiële AMB KMZ-routeviewer — nieuw bronspoor (2026-11-03)
Op het bestaande AMB-bronportaal `https://www.ambq.gov.co/transporte/transporte-publico-colectivo/` staat óók **Visor de Rutas AMBQ**. De HTML bevat routeitems per bedrijf, waaronder expliciet **SOBUSA B18-4175 A/B, C12-4169 A/B en C16-4167 A/B**, evenals A/B van TRANSDIAZ A10, LA CAROLINA A16 en SODETRANS B15/C21. Een route-item is nog geen geverifieerd/downloadbaar KMZ-bestand: de **werkelijke `data-*`-download-URL's moeten nog uit ruwe HTML worden uitgelezen en getest**.

**Huidige repo-status:** nog geen originele KMZ-bestanden, KMZ-inventaris of op KMZ gebaseerde route-shapes ingeladen. Bestaande `sources/amb/arcgis_shape_staging` is de **andere**, oudere AMB ArcGIS FeatureServer/6 bron (93 geometrieën).

**Apart bevestigde webindexen, met mogelijk verschillende generaties kaarten:**
- `https://www.ambq.gov.co/rutas-de-buses/SOBUSA/`: index van **zes niet-A/B-opgesplitste** SOBUSA-KMZ's, met bestandsdatum **26 oktober 2018**. Geen bewijs dat deze aan de **2025/2026**-vergunningen voldoen.
- `https://www.ambq.gov.co/ruta-de-buses/COOLITORAL/`: index met onder meer **A1-4106 A.kmz / A1-4106 B.kmz**, bestandsdatum **20 mei 2026**; het lijkt een nieuwere KMZ-verzameling.
- `https://www.ambq.gov.co/ruta-de-buses/EMBUSA/`: **B9-4125.kmz**, bestandsdatum **20 mei 2026**.

**Aanbevolen technische volgende stap:** spider de ruwe HTML en lees de echte `data-*`-waarden uit; download alleen publiek bereikbare `.kmz`-bestanden met HTTP-status/inhoudstype/ZIP-validatie en SHA256-manifest; extraheer KML `LineString` + trackmetadata; bouw een **basisroute + A/B-variant-crosswalk** op basis van bestandsnamen én actuele vergunningen; controleer geometrie tegen SIU-haltevolgorde en bronjaar. Geef prioriteit aan SOBUSA C12/C16/B18. Niet direct automatisch naar `gtfs/shapes.txt` publiceren; controleer actualiteit/licenties.

## GIS
Bron: https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6

Laag: MO_RutasTransportePublico. Export: 93 geometrieën. Historische of onbevestigde trajecten; niet direct publiceren.

De voorlopige topologische reconstructie leverde 493 afzonderlijke ketens op. Validatie met wegennet/GraphHopper volgt later.

## Nog te importeren bronbestanden
- sources/amb/vergunningencatalogus.csv
- sources/amb/routes_bronregister.csv
- sources/arcgis/route_shape_kandidaten.csv
- sources/arcgis/shape_topologie_audit.csv
- sources/arcgis/shape_segmenten.csv
- sources/arcgis/shapes_voorlopig.txt
- docs/agency_verificatie.csv
- docs/shape_koppeling_review.csv

De genoemde bestanden staan in het lokale onderzoeksstartpakket; deze index is geen vervanging voor de bronbestanden.


## SODETRANS — actualisatie 2026-11-05

Officiële actuele frequentiebron: [Resolución Metropolitana 500-2025](https://www.ambq.gov.co/wp-content/uploads/2026/02/Resolucion-Metropolitana-No.-500-2025-SODETRANS.pdf). Betrokken routes: B13-4128, B13-B-4189, B14-4174, B15-4129, B17-4163 en C21-4182. Gebruiker bevestigt geen later besluit dat de frequenties wijzigt. **B13-B-4189, pagina 8: 8 min piek / 10 min dal; visueel gevalideerd, juridische bronvraag afgesloten.** Historische OCR-registratie met `missing_headway` is voor deze route achterhaald. Voor overige routevarianten zijn exacte machineleesbare frequentiegegevens en GTFS-dekking afzonderlijk te toetsen; claim geen volledige dekking zonder build-audit.


## Archiefreconciliatie — 5 november 2026

De archiefkandidaten 2020–2026 zijn vergeleken met de bestaande visueel geverifieerde frequentietabellen. De machineleesbare classificatie staat in `sources/amb/amb_archive_route_reconciliation_2026-11-05.csv`, de onderbouwing in `docs/amb_archive_2020_2026_existing_register_comparison_2026-11-05.md`. Oudere intervallen overschrijven geen latere beschikkingen. Alleen C7-4138 (348-2026), A4-4109 en de afzonderlijke tijdelijke A16-C/D9-C-varianten blijven voor nieuwe bronkoppeling open. Geen nieuwe OCR of GTFS-publicatie.

Zie [route-voor-route classificatie](../sources/amb/amb_archive_route_reconciliation_2026-11-05.csv) en [inhoudelijke vergelijking](amb_archive_2020_2026_existing_register_comparison_2026-11-05.md).
