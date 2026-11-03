# Inventaris haltes en GPS-stoppunten — Barranquilla Urbanas (3 november 2026)

## Stand

**In de huidige repository ontbreekt `gtfs/stops.txt`**, evenals `stop_times.txt`, een routestop-sequentiebestand en een gevalideerde TPC-halte-GPS-dataset. De 97 routes in `gtfs/routes.txt` hebben wel routecodekoppelingen naar 93 GIS-bronpolyline-features, maar die geometrielijnen leveren **geen officiële haltepunten of haltevolgorde**.

## Beschikbare of onderzochte bronnen

| Bron | Huidige inhoud | Beoordeling voor traditionele TPC |
|---|---|---|
| [Gemeentelijke ArcGIS-laag MO_RutasTransportePublico](https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer/6) | 93 polyline routefeatures, historisch GIS | Geschikt om haltepunten later te koppelen, **geen stoplocaties** |
| [ArcGIS Movilidad_Transito_WFL1](https://services3.arcgis.com/oGYAc07w6wsvgUYr/ArcGIS/rest/services/Movilidad_Transito_WFL1/FeatureServer) | Laag 2: MO_EstacionesTransporteMasivo; laag 6: MO_RutasTransportePublico; overige lagen kantoren en wegen | **Geen aparte TPC-paraderos-laag** gevonden |
| [Datos Abiertos Paraderos del Sistema — hxy3-94yh](https://www.datos.gov.co/Transporte/Paraderos-del-Sistema/hxy3-94yh) | **928 rijen, zes kolommen**, waaronder `nombre_ruta`, `nombre_parada`, `secuencia_parada`, `coordenada_y`, `coordenada_x` en geocode | Alleen **Transmetro**; kan wel overstaplocaties opleveren. **928 is aantal route-halteregels, niet unieke TPC-haltes**. Feitelijke data update 28-09-2020 |
| [AMB vergunningen](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/) | Routecodes, straatvolgorde, terminaladressen, soms kaart | Geeft routeverloop en eindpunten; geen compleet haltebestand per route |
| [AMB juli 2020 routekaarten](https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/) | 24 kaarten, 84 routevermeldingen en dienstvensters | Vertrekuren; geen GPS-haltevolgorde |
| [OpenStreetMap](https://www.openstreetmap.org/) | Potentieel `highway=bus_stop`, `public_transport=platform` en `stop_position` | **Nog niet voor deze repository geoogst**; kan zowel TPC-, Transmetro- als andere haltepunten bevatten; eerst classificeren en met de routes kruisen |
| [AMB SIU/SIBUS](https://siu.ambq.gov.co/siu/schedule-mng/schedules) | Online gebruikersportaal; publieke download van haltepunten nog niet vastgesteld | **Hoogste prioriteit voor onderzoek**, omdat AMB technisch routegebonden GPS-referentiehaltes kan vastleggen |

## Waarom SIBUS extra belangrijk is

Het [officiële AMB RCC-technisch bestek (2021), paragraaf 5.2.8 op PDF-pagina 28](https://www.ambq.gov.co/wp-content/uploads/2021/08/Anexo-1-Anexo-T%C3%A9cnico-del-Sistema-RCC.pdf) beschrijft **referentie-stoppunten per lijn en GPS-coördinaten voor geldige overstappunten**. Paragraaf 5.3.1 beschrijft informatie over lijnen, diensten, frequenties en tijden op een webportal. Dit maakt SIBUS een potentiële bron voor route/stop-relaties, maar het technische bestek garandeert niet dat een publieke API of GTFS-feed beschikbaar is.

## OSM inventarisactie (voorstel)

Overpass-query voor een ruime, **ruwe** bbox rond Barranquilla, Soledad, Malambo, Galapa en Puerto Colombia. Deze bbox is een zoekgebied, geen officiële AMB-grens:

```overpassql
[out:json][timeout:120];
(
  node["highway"="bus_stop"](10.78,-75.05,11.14,-74.62);
  node["public_transport"="platform"]["bus"="yes"](10.78,-75.05,11.14,-74.62);
  node["public_transport"="stop_position"]["bus"="yes"](10.78,-75.05,11.14,-74.62);
  way["public_transport"="platform"]["bus"="yes"](10.78,-75.05,11.14,-74.62);
);
out center tags;
```

Bewaar `osm_type`, `osm_id`, `name`, `ref`, `operator`, `network`, `lat`, `lon`, `source=OSM`, `source_date`, `is_TPC_confirmed=no` en een apart kwalificatiestatusveld. Niet automatisch OSM-haltepunten voor alle 97 routepatronen aanwijzen als ze langs dezelfde weg liggen.

## Prioriteit

1. **SIBUS/SIU:** onderzoek of routegebonden haltepunten, GPS en haltevolgorde via publieke gebruikersinterface of geautoriseerde export vindbaar zijn.
2. **OSM:** inventariseer alle busstops/platforms; filter Transmetro, TPC en onbekend, en controleer de afstand tot de 93 GIS-routelijnen.
3. **Transmetro:** haal de 928 route/halte-rijen desgewenst apart op voor fysiek gedeelde overstaplocaties, **niet** als primaire TPC-haltes.
4. **Routekoppeling:** wanneer haltes bekend zijn, pas per richting/itinerary volgorde en route-ligging beoordelen. Alleen dan een betrouwbare `stops.txt` + `stop_times.txt` opbouwen.

**Geen synthetische haltes als officieel AMB presenteren.** Routeverloop of een routecodekoppeling bepaalt geen fysieke plaats waar passagiers kunnen instappen.
