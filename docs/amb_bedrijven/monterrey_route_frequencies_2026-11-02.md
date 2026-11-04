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
| 437-2016 | [officiële PDF](https://www.ambq.gov.co/wp-content/uploads/2017/01/REOLUCION-437-16-MONTERREY..pdf) | historisch; originele 15 pagina's en artikelen gecontroleerd op 4 november 2026 |
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

## Afgesloten juridische bronkeuze (4 november 2026)

- **390-2018 is het nieuwste gepubliceerde MONTERREY-besluit volgens de vastgestelde onderzoeksafspraak.** Geen vervolgonderzoek naar hypothetische latere MONTERREY-resoluties; MON-01 gesloten als onderzoeksopdracht. De tijdelijke werking en SITP-voorwaarde uit artikel 3 blijven als expliciete bronvoorwaarde, niet als nieuwe zoekopdracht.
- **437-2016 is inhoudelijk gecontroleerd:** originele 15 pagina's, artikel 1 en historische B8/B11/B12-tabellen; zie `docs/amb_monterrey_437_2016_original_review_2026-11-04.md`. De 2016-codes zijn historische brongegevens; voor de GTFS-bronselectie prevaleert 390-2018 met vier routes, inclusief B11-B-4192. MON-02 gesloten voor deze bronselectie.
- **MON-03 is GTFS-uitvoerwerk:** haltes, routegeometrie, dienstperioden en kalender; geen juridisch brononderzoek.

**Juridische dossierstatus: gesloten voor verder resolutieonderzoek op basis van de afgesproken bronset.** Geen bewering dat daadwerkelijke huidige exploitatie of een definitieve juridische geldigheidsdatum is bewezen.

## GTFS-status

**Niet vrijgegeven** voor `calendar.txt`, `frequencies.txt`, `stop_times.txt` of `shapes.txt`. Diensturen van 00:00–24:00 zijn doorgaans **vraagafhankelijk** geformuleerd en impliceren niet dat er 's nachts daadwerkelijk bussen rijden. Voor opname eerst de werkelijke weekkalender, spits-/dalvensters, richtingen, haltes en georeferentie vaststellen.

Machineleesbare routegegevens: [13-bedrijven-register](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/blob/main/sources/amb/remaining_13_route_parameters_2026-11-02.csv).
