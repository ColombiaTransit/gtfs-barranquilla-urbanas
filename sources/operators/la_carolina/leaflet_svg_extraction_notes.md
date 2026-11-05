# Leaflet MHT geometry extraction

Three uploaded MHT snapshots contain SVG `path.leaflet-interactive` geometries rendered by Leaflet. The visible SVG paths can be converted from screen coordinates to WGS84 using the OSM XYZ tile zoom and tile origin recorded in each MHT. This is **rendered, viewport-clipped, pixel-quantized geometry**, not necessarily the full original route. Do not treat as verified GTFS `shapes.txt` without comparison to AMB KMZ.

- Miramar: zoom 14, 50 SVG vertices.
- Ruta Express: zoom 14, 79 SVG vertices.
- Ruta 17: zoom 12, 163 SVG vertices.

Original MHT snapshots supplied by user; the generated GeoJSON is provided in the conversation. No bus stops or horarios were extracted.
