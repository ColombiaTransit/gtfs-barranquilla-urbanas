# Inventaris haltes en GPS-stoppunten — Barranquilla Urbanas (3 november 2026)

## Nieuwe bevinding: Overpass-export verwerkt op 3 november 2026

De gebruiker heeft de bovenstaande Overpass-query uitgevoerd en het volledige exportbestand aangeleverd. Dit staat nu als [originele bron in GitHub](../sources/osm/overpass_barranquilla_bus_stops_2026-11-03.json). De [reproduceerbare GitHub Action](../.github/workflows/audit-osm-stops.yml) kruist die 599 objecten met de 93 historische ArcGIS-lijnen en publiceert het [OSM-register met ODbL-bronvermelding](../sources/osm/README.md).

**Uitsplitsing:** 487 expliciet Transmetro/Alimentador, 33 expliciet regionale verbinding Baranoa–Barranquilla, en **79 zonder te identificeren netwerk**. Van deze 79 zijn er **45** uitsluitend `stop_position` en **34** mogelijke instapplaatsen of platformen. Van de 34 mogelijke instapplaatsen liggen **16 binnen 50 meter** van een AMB-GIS-routelijn; **18 binnen 100 meter**; slechts **drie** hebben in OSM een naam. Geen enkele van deze punten is door de dataset expliciet als TPC-halte bevestigd.

Er zijn bovendien enkele nabijgelegen expliciet getagde Transmetro-haltes; nabijheid van Transmetro kan een extra aanwijzing zijn dat een ongetagd platform niet tot TPC behoort. Daarom blijft `tpc_confirmed=no` staan voor alle 599 objecten; dit is **geen uitspraak dat Transmetro-haltes niet bestaan**, maar betekent dat er geen bewijs voor gebruik als *traditionele TPC-halte* is.

**Bestanden:**
- [599 OSM-objecten met netwerkclassificatie en GIS-afstanden](../sources/osm/analysis/all_osm_stops_audit.csv)
- [79 ongeclassificeerde objecten](../sources/osm/analysis/unclassified_osm_stops.csv)
- [34 mogelijke instappunten](../sources/osm/analysis/possible_boarding_platforms.csv)
- [16 punten binnen 50 m van de historische AMB-routes](../sources/osm/analysis/priority_platforms_near_amb_routes_50m.csv)
- [GeoJSON met 34 geolocaties](../sources/osm/analysis/possible_boarding_platforms.geojson)

**Betekenis voor onze GTFS:** OSM helpt om bestaande mogelijk relevante fysieke locaties te vinden, maar kan nog geen betrouwbare volledige `stops.txt` en vooral geen `stop_times.txt` of volgorde leveren. Het onderzoek verschuift nu naar bevestiging van de instapplaatsen/stopvolgorde via SIU/SIBUS of routespecifieke bronbestanden. Zelfs een afstand van 0 meter tot een lijn is nog geen bewijs dat de route bij die halte stopt.

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
| [OpenStreetMap](https://www.openstreetmap.org/) | Potentieel `highway=bus_stop`, `public_transport=platform` en `stop_position` | **Op 3 november 2026 via gebruikers-Overpass-export geoogst en geanalyseerd**; kan zowel TPC-, Transmetro- als andere haltepunten bevatten; eerst classificeren en met de routes kruisen |
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
2. **OSM (uitgevoerd):** alle 599 aangeleverde objecten geclassificeerd en ruimtelijk gekoppeld aan 93 historische GIS-routes; 16 kandidaatplatforms binnen 50 m. Nu handmatig/tegen aanvullende bron bevestigen of daadwerkelijk TPC-instapplaatsen.
3. **Transmetro:** haal de 928 route/halte-rijen desgewenst apart op voor fysiek gedeelde overstaplocaties, **niet** als primaire TPC-haltes.
4. **Routekoppeling:** wanneer haltes bekend zijn, pas per richting/itinerary volgorde en route-ligging beoordelen. Alleen dan een betrouwbare `stops.txt` + `stop_times.txt` opbouwen.

**Geen synthetische haltes als officieel AMB presenteren.** Routeverloop of een routecodekoppeling bepaalt geen fysieke plaats waar passagiers kunnen instappen.
