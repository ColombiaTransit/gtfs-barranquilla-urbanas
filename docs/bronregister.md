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
