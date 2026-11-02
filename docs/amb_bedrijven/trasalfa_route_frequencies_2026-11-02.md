# TRASALFA — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-TRASALFA`. **Manifest:** 8 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

139-2013 verandert D14-4156 en D15-4157 en noemt 112–135 voertuigen voor B2B, D14 en D15 samen. Het technisch rapport vermeldt ontwerpintervallen, maar de nieuwe juridisch bindende tijdvakken zijn niet afzonderlijk bewezen.

**Belangrijkste onderzochte besluiten:** 139-2013, 111-2012, 285–287-2010.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| B2-B-4118 | **onbevestigd** | **onbevestigd** | 16–20 | ? | 139-2013 p20: vloot in artikel 2, interval niet als definitieve 2013-vergunning bewezen |
| D14-4156 | **onbevestigd** | **onbevestigd** | ?–? | 53 | 139-2013 p15,19–20: route in art1 gewijzigd; ontwerp bevat spits 5 min; niet automatisch actueel |
| D15-4157 | **onbevestigd** | **onbevestigd** | 48–58 | 55 | 139-2013 p15,19–20: vloot art2, ontwerp noemt 3/5, maar juridisch operationeel toepasbaarheid niet bewezen |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 111-2012 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-B2B-Resolucion-111-12.pdf) | historisch; artikelen nader toetsen |
| 139-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/resolucion-139-13.pdf) | nieuwste / sleutelbesluit |
| 282-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-2502-Resolucion-282-10.pdf) | historisch; artikelen nader toetsen |
| 283-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-2504-Resolucion-283-10.pdf) | historisch; artikelen nader toetsen |
| 284-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-2505-Resolucion-284-10.pdf) | historisch; artikelen nader toetsen |
| 287-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-B2B-Resolucion-287-10.pdf) | historisch; artikelen nader toetsen |
| 286-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-D14-Resolucion-286-10.pdf) | historisch; artikelen nader toetsen |
| 285-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALFA/TRASALFA-D15-Resolucion-285-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- TA-01 139-2013 art2 D14 slecht leesbare vlootwaarden tegen scan
- TA-02 ontwerpintervallen versus rechten 285/286/287
- TA-03 intrekkingen 282/283/284 en daadwerkelijke ritten.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
