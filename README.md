# GTFS Barranquilla Urbanas

Onderzoeksrepository voor een GTFS-feed van het traditionele openbaar busvervoer (TPC, *urbanas*) in Barranquilla en omliggende gemeenten. **Niet** de Transmetro-feed.

## Status
**Onderzoek / concept — niet publiceren als operationele GTFS.**

- 23 voorlopige vervoerders en 97 vergunningvermeldingen.
- ArcGIS-routelijnen en voorlopige shape-kandidaten.
- Vergunningen geven toegestane routes en frequenties weer; geen bewijs van actuele exploitatie.
- Haltes, dienstkalenders, ritten en rijrichtingen ontbreken of zijn nog niet gevalideerd.
- Shapes worden later waar mogelijk met GraphHopper gevalideerd.

## Structuur
- `gtfs/`: conceptbestanden `agency.txt` en `routes.txt`
- `sources/amb/`: vergunningencatalogus en bronregister
- `sources/arcgis/`: brongeometrie, segmenten en topologie-audit
- `docs/`: verificatieregister en openstaande kwesties

## Bron
AMB: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/

ArcGIS: https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6

## Vervolg
Importeer de bestanden uit het reeds voorbereide `gtfs-barranquilla-urbanas-starter.zip` in deze repository. Voeg vervolgens automatische validatie en een build-workflow toe.
