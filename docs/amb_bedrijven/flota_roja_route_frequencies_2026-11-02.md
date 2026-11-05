# FLOTA_ROJA — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-FLOTA_ROJA`. **Manifest:** 6 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

## Inhoudelijke uitkomst

A8-4113 heeft een aangepast traject, 3/5 minuten en 35–42 Grupo C-voertuigen. De gescande tabel p5 is gecontroleerd. Historische A9 en oude A8-besluiten vergen aparte geldigheidscontrole.

**Belangrijkste onderzochte besluiten:** 260-2024.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| A8-4113 | 3 | 5 | 35–42 | 33.74 | 5: scan p5 gecontroleerd, besluit 30-09-2024 |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 260-2024 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2024/10/RESOLUCION-METROPOLITANA-N%C2%B0-260-2024-FLOTA-ROJA.pdf) | nieuwste / sleutelbesluit |
| 235-2014 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ROJA/Resolucion-235-14-flota-roja.pdf) | historisch; artikelen nader toetsen |
| 117-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ROJA/FLOTA-ROJA-A8-Resolucion-117-10.pdf) | historisch; artikelen nader toetsen |
| 145-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ROJA/FLOTA-ROJA-A8-Resolucion-145-11.pdf) | historisch; artikelen nader toetsen |
| 115-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ROJA/FLOTA-ROJA-A9-Resolucion-115-10.pdf) | historisch; artikelen nader toetsen |
| 148-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ROJA/FLOTA-ROJA-A9-Resolucion-148-11.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- FR-01 Historische A9-status en 2014-besluit controleren
- FR-02 oud/nieuw A8 traject op straatniveau vergelijken
- FR-03 diensturen en stopvolgorde.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).


## Archiefreconciliatie — 5 november 2026

Archiefhercontrole: A8-4113 260-2024 3/5 komt exact overeen met de reeds visueel gecontroleerde tabel op p5. Classificatie `confirmed_existing`; geen nieuwe OCR, geen wijziging van actuele GTFS.

Zie [route-voor-route classificatie](../../sources/amb/amb_archive_route_reconciliation_2026-11-05.csv) en [inhoudelijke vergelijking](../amb_archive_2020_2026_existing_register_comparison_2026-11-05.md).
