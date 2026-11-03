# SOBUSA — brongebonden frequenties en routebesluiten

**Bronpeildatum:** 2 november 2026. **Technische bron:** GitHub Actions-run [41480204032](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41480204032), artifact `amb-pdf-SOBUSA`. **Manifest:** 21 documenten. Deze gegevens zijn **vergunningsparameters**, geen aangetoonde uitvoering van de actuele dienstregeling.

**Update 3 november 2026 — SOBUSA 307-2014 teruggevonden.** [20 pagina's bronanalyse](../sobusa_307_2014_analysis_2026-11-03.md) | [zes historische routefrequenties (CSV)](../../sources/amb/sobusa_307_2014_historical_route_parameters.csv). De 2014-lacune is opgelost. Voertuigcapaciteit blijft buiten GTFS-scope.

## Inhoudelijke uitkomst

466-2025 wijzigt zes routes, vlootmatrix totaal 381–456; 082-2026 wijzigt B18 naar twee itinerarios A/B, elk 10/12 minuten, gezamenlijk 5/6 op drukste traject. 307-2014 was eerder 404, maar de **volledige originele PDF is op 3-11-2026 hersteld en met 20/20 pagina's geëxtraheerd**; zie [aparte juridische/frequentieanalyse](../sobusa_307_2014_analysis_2026-11-03.md). De zes intervallen uit 2014 zijn uitsluitend historische vergunningswaarden, geen actuele GTFS-vervangingen.

**Belangrijkste onderzochte besluiten:** 466-2025 en B18-wijziging 082-2026.

## Routefrequenties en wagenpark

| Route | Spits (min) | Dal (min) | Vloot | Lengte (km) | PDF-pagina / bijzonderheid |
|---|---:|---:|---|---:|---|
| B18-4175 | 5 | 6 | 52–62 | ? | 082-2026 p6: gecombineerd drukste traject; itinerary A/B elk 10/12; lengte A 73.6, B 75.6 km |
| C11-4168 | 3.5 | 5 | 60–72 | 62.7 | 466-2025 p8: scan gecontroleerd |
| C12-4169 | 3 | 5 | 56–68 | ? | 466-2025 p11: effectief gedeeld; A 6/9 (47.8 km), B 3/6 (48.6 km) |
| C13-4143 | 3 | 5 | 56–68 | 48 | 466-2025 p13: scan gecontroleerd |
| C14-4170 | 2 | 4 | 90–108 | 56.3 | 466-2025 p15: scan gecontroleerd |
| C16-4167 | 3.5 | 6 | 67–80 | ? | 466-2025 p18: effectief drukste traject; aparte itinerarios niet volledig gecontroleerd |


De waarden met **onbevestigd** mogen niet worden ingevuld op basis van OCR-gissingen. Waar een interval voor een *gemeenschappelijke drukste sectie* staat, is dit **geen** interval per afzonderlijke itinerary. Historische vlootmatrixwaarden zijn geen nieuwe routefrequenties.

## Geregistreerde bronbesluiten

| Besluit | Bron | Controleomvang |
|---|---|---|
| 082-2026 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-M-082-2026.pdf) | historisch; artikelen nader toetsen |
| 466-2025 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2026/03/Permiso-de-operacion-subusa-2.pdf) | nieuwste / sleutelbesluit |
| 225-2025 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2025/06/RESOLUCION-No.-225-2025-REESTRUCTURACION-SOBUSA-B18-4175.pdf) | historisch; artikelen nader toetsen |
| 173-2025 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2025/05/Sobusa-RESOLUCION-METROPOLITANA-No.-173-2025.pdf) | historisch; artikelen nader toetsen |
| 389-2023 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2026/03/SG04122023RESOLUCION-METROPOLITANA-No.pdf) | historisch; artikelen nader toetsen |
| 349-2024 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2024/12/RESOLUCION-METROPOLITANA-349-24.pdf) | historisch; artikelen nader toetsen |
| 050-2017 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/11/SOBUSA-C12-C13-Resolucion-050-17.pdf) | historisch; artikelen nader toetsen |
| 399-2015 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/resolucion-399-15.pdf) | historisch; artikelen nader toetsen |
| 307-2014 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/307-RESOLUCION-SOBUSA.pdf) | historisch; artikelen nader toetsen |
| 341-2013 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/RESOLUCION-341-13-SOBUSA.pdf) | historisch; artikelen nader toetsen |
| 232-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-1806-Resolucion-232-10.pdf) | historisch; artikelen nader toetsen |
| 398-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-1806-Resolucion-398-10.pdf) | historisch; artikelen nader toetsen |
| 093-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-B18-Resolucion-093-11.pdf) | historisch; artikelen nader toetsen |
| 180-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-B18-Resolucion-180-10.pdf) | historisch; artikelen nader toetsen |
| 281-2011 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-B18-Resolucion-281-11.pdf) | historisch; artikelen nader toetsen |
| 176-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C11-Resolucion-176-10.pdf) | historisch; artikelen nader toetsen |
| 210-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C11-C12-C13-C14-C16-Resolucion-210-10.pdf) | historisch; artikelen nader toetsen |
| 177-undated | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C12-Resolucion-177.pdf) | historisch; artikelen nader toetsen |
| 185-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C13-Resolucion-185-10.pdf) | historisch; artikelen nader toetsen |
| 178-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C14-Resolucion-178-10.pdf) | historisch; artikelen nader toetsen |
| 179-2010 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/SOBUSA/SOBUSA-C16-Resolucion-179-10.pdf) | historisch; artikelen nader toetsen |

De bronbestanden zijn technisch geëxtraheerd, behalve specifieke mislukte downloads die in de bestaande batchrapporten worden vermeld (bij SOBUSA: 307-2014). **Dit overzicht betekent niet dat ieder historisch document volledig juridisch is gevalideerd.** De recentste relevante routebladen en hun numerieke parameters zijn geselecteerd; oudere besluiten blijven voor effect-/intrekkingsvergelijking geregistreerd.

## Ontbrekend werk (zelfstandig vervolg)

- SOB-01 307-2014 opgelost; historische juridische werking vergelijken
- SOB-02 artikelketen 173/225/466-2025 versus 082-2026
- SOB-03 pattern-varianten C12/C16 en B18 nauwkeurig uiteenhouden
- SOB-04 actuele rittenkalender en haltes.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
