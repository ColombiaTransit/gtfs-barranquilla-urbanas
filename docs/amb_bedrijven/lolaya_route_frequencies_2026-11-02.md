# LOLAYA — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-LOLAYA`. **Manifest:** 10 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

De drie routes B10, B10-B en D8 zijn opnieuw geautoriseerd, met ongewijzigd bedrijfsvlootmaximum volgens het besluit. Alle drie tabellen p6/p8/p10 zijn op scans gecontroleerd; 389-2018 was een tijdelijke herstructurering.

**Belangrijkste onderzochte besluiten:** 068-2025.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| B10-4126 | 4.5 | 6 | 48–57 | 64.8 | 6: scan bevestigd |
| B10-B-4193 | 4 | 6 | 47–56 | 54.9 | 8: scan bevestigd |
| D8-4165 | 4 | 6 | 41–49 | 47.9 | 10: scan bevestigd |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 068-2025 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2025/02/LOLAYA-Resolucion-Metropolitana-068-2025.pdf) | nieuwste / sleutelbesluit |
| 389-2018 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2018/11/Resolucion-Metropolitana-389-18.pdf) | historisch; artikelen nader toetsen |
| 446-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/RESOL-446-13-LOLAYA.pdf) | historisch; artikelen nader toetsen |
| 405-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/RESOL-405-13LOLAYA.pdf) | historisch; artikelen nader toetsen |
| 295-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/RESOLUCIONN-295-13-TRANSPORTES-LOLAYA.pdf) | historisch; artikelen nader toetsen |
| 329-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/LOLAYA-1602-Resolucion-329-10.pdf) | historisch; artikelen nader toetsen |
| 328-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/LOLAYA-1604-Resolucion-328-10.pdf) | historisch; artikelen nader toetsen |
| 327-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/LOLAYA-B10-Resolucion-327-10.pdf) | historisch; artikelen nader toetsen |
| 463-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/LOLAYA-B10-D8-Resolucion-463-10.pdf) | historisch; artikelen nader toetsen |
| 326-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LOLAYA/LOLAYA-D8-Resolucion-326-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- LOL-01 2018 versus 2025 straattrajecten
- LOL-02 tijdelijke besluiten en eventuele opvolging
- LOL-03 actuele rittenkalender en haltes.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
