# TRANSOLEDAD — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-TRANSOLEDAD`. **Manifest:** 5 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

D13-4155 is herstructureerd naar 5/7 minuten, 32–37 voertuigen, 46 km. Scan p6 is gecontroleerd; de tekstextractie van p4 leest 32–87 en noemt ten onrechte COOTRAB, wat niet mag worden overgenomen.

**Belangrijkste onderzochte besluiten:** 188-2024.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| D13-4155 | 5 | 7 | 32–37 | 46 | 188-2024 p6: scan p6 bevestigd; p4 OCR 32-87 is fout |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 188-2024 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2024/08/RESOLUCION-M.-188-2024-TRANSPORTES-SOLEDAD.pdf) | nieuwste / sleutelbesluit |
| 338-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSOLEDAD/RESOLUCION-338-13-TRANSOLEDAD.pdf) | historisch; artikelen nader toetsen |
| 231-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSOLEDAD/TRANSOLEDAD-2202-Resolucion-231-10.pdf) | historisch; artikelen nader toetsen |
| 196-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSOLEDAD/TRANSOLEDAD-D13-Resolucion-196-10.pdf) | historisch; artikelen nader toetsen |
| 403-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSOLEDAD/TRANSOLEDAD-D13-Resolucion-403-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- TSOL-01 Historische 2013/2010 vergunningen en inwerkingtreding
- TSOL-02 het p4/p6 operator-/capaciteitsverschil auditten
- TSOL-03 actuele stops/kalender/geometrie.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
