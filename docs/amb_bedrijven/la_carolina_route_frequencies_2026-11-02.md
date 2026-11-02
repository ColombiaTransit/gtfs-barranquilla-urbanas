# LA_CAROLINA — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-LA_CAROLINA`. **Manifest:** 10 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

D6 en D7 krijgen gewijzigde trajecten via Alameda del Río, beide 6/8 min en 48–58 voertuigen; de scans p7/9 tonen respectievelijk 77,7/79,3 km. A16-4161 staat in een afzonderlijke 2019-vergunning, niet in de 2023-herstructurering.

**Belangrijkste onderzochte besluiten:** 404-2023, A16 afzonderlijk 199-2019.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| D6-4150 | 6 | 8 | 48–58 | 77.7 | 7: scan bevestigd; Terminal–Centro–Base Naval–Villa Carolina–Alameda del Río |
| D7-4151 | 6 | 8 | 48–58 | 79.3 | 9: scan bevestigd; Terminal–Centro–Base Naval–Corredor Universitario |
| A16-4161 | 3.5 | 5 | 49–59 | 52.9 | 199-2019 p10: historische aparte A16-vergunning, latere actuele status niet bepaald |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 067-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-A16-Resolucion-067-11.pdf) | historisch; artikelen nader toetsen |
| 404-2023 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-MTC-N0.404-23-1.pdf) | nieuwste / sleutelbesluit |
| 199-2019 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2019/11/RESOLUCION-N-199-1920190820.pdf) | historisch; artikelen nader toetsen |
| 264-2019 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2019/10/RESOLUCION-METROPOLITANA-264-1920191008.pdf) | historisch; artikelen nader toetsen |
| 302-2014 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/RESOLUCION-302-14-LA-CAROLINA.pdf) | historisch; artikelen nader toetsen |
| 233-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-1502-Resolucion-233-10.pdf) | historisch; artikelen nader toetsen |
| 173-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-A16-Resolucion-173-10.pdf) | historisch; artikelen nader toetsen |
| 204-2012 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-A16-Resolucion-204-12.pdf) | historisch; artikelen nader toetsen |
| 174-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-D6-Resolucion-174-10.pdf) | historisch; artikelen nader toetsen |
| 175-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-D7-Resolucion-175-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- LC-01 A16 juridische voortzetting toetsen
- LC-02 D6/D7 geordende routegeometrie
- LC-03 echte diensttijden, haltes, recentere besluiten.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
