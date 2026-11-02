# TRANSMECAR — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-TRANSMECAR`. **Manifest:** 8 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

In 324-2010 krijgt de historische route C17 4/6 min en 40–48 voertuigen. 325-2010 wijzigt de historische D10-route na bezwaar tegen 220-2010. Beide uit 2010; uitvoering was afhankelijk van Transmetrostart en autoriteitskennisgeving.

**Belangrijkste onderzochte besluiten:** 324-2010 en bezwaarbesluit 325-2010.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| C17-4160 | 4 | 6 | 40–48 | ? | 324-2010 p8–9: 2010-vergunning; daadwerkelijke inwerkingtreding onbekend |
| D10 | **onbevestigd** | **onbevestigd** | ?–? | ? | 325-2010 p7–8: aangepaste historische Malambo–Vía Caracolí–Centro, parameters niet afleidbaar uit deze bezwaarpagina |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 324-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-C17-Resolucion-324-10.pdf) | nieuwste / sleutelbesluit |
| 241-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-2101-Resolucion-241-10.pdf) | historisch; artikelen nader toetsen |
| 239-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-2106-Resolucion-239-10.pdf) | historisch; artikelen nader toetsen |
| 240-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-2106-Resolucion-240-10.pdf) | historisch; artikelen nader toetsen |
| 221-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-D9-Resolucion-221-10.pdf) | historisch; artikelen nader toetsen |
| 220-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-D10-Resolucion-220-10.pdf) | historisch; artikelen nader toetsen |
| 325-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-D10-Resolucion-325-10.pdf) | historisch; artikelen nader toetsen |
| 219-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-D11-Resolucion-219-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- TMEC-01 2010 ingangsdata/2026 operationele status
- TMEC-02 samenhang 219/220/221 en 239/240/241/324/325 juridisch controleren
- TMEC-03 D10 technische tabel en huidige routecodes.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
