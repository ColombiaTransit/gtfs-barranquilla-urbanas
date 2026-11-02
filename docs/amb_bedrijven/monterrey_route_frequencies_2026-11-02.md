# MONTERREY — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-MONTERREY`. **Manifest:** 12 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

De vier routebladen B8, B11, B11-B en B12 staan in artikel 1, met 77–93 voertuigen samen. Artikel 3 bepaalt expliciet dat deze tijdelijke reorganisatie niet mag voortduren na invoering van het SITP.

**Belangrijkste onderzochte besluiten:** 390-2018 (tijdelijke vergunning).

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| B8-4124 | 7 | 9 | 27–33 | 56.5 | 9: scan bevestigd |
| B11-4166 | 4 | 6 | 20–24 | 59 | 10: scan bevestigd |
| B11-B-4192 | 7 | 9 | 10–12 | 53.8 | 11: scan bevestigd |
| B12-4127 | 4 | 6 | 20–24 | ? | 12: scan bevestigd, lengte niet betrouwbaar uit scan |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 390-2018 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2018/11/Resolucion-Metropolitana-390-18.pdf) | nieuwste / sleutelbesluit |
| 437-2016 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/RESOL-404-13-MONTERREY.pdf) | historisch; artikelen nader toetsen |
| 404-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/RESOL-404-13-MONTERREY.pdf) | historisch; artikelen nader toetsen |
| 403-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/RESOL-403-13-MONTERREY.pdf) | historisch; artikelen nader toetsen |
| 402-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/RESOL-402-13-MONTERREY.pdf) | historisch; artikelen nader toetsen |
| 294-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/RESOLUCION-294-13-MONTERREY.pdf) | historisch; artikelen nader toetsen |
| 301-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-1702-Resolucion-301-10.pdf) | historisch; artikelen nader toetsen |
| 300-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-1704-Resolucion-300-10.pdf) | historisch; artikelen nader toetsen |
| 299-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-1706-Resolucion-299-10.pdf) | historisch; artikelen nader toetsen |
| 298-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-B8-Resolucion-298-10.pdf) | historisch; artikelen nader toetsen |
| 296-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-B11-Resolucion-296-10.pdf) | historisch; artikelen nader toetsen |
| 297-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/MONTERREY/MONTERREY-B12-Resolucion-297-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- MON-01 Latere/actuele rechtsgeldigheid tijdelijke 2018-vergunning
- MON-02 437-2016 B11-4146 versus B11-4166
- MON-03 werkelijke ritten/haltes en kaartgeometrie.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
