# TRASALIANCO D18-4179 — OCR-straatvolgorde als shape-input (NIET GEVALIDEERD)

**Bron:** originele [AMB-resolutie 408-2013](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALIANCO/RESOLUCION-408-13-TRASALIANCO.pdf), pagina's 10–11; Spaanse OCR uit [Actions-run 41786660704](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41786660704), artifact 13301995991. De frequentie 7/10 min en capaciteit Grupo B 27–33 zijn eerder op de originele pagina-afbeeldingen bevestigd. Onderstaande straatvolgorde is **OCR-transcriptie**, geen gegeorefereerde shape; verkeersrichtingen en segmenten nog niet via kaart gecontroleerd.

## Traject zoals uit OCR getranscribeerd
**Begin/eind:** Calle 26 × Carrera 23 (El Concord, Malambo), terminal. **Routenaam:** Concord – Murillo – Circunvalar – Carrera 43 – Calle 76.

1. Calle 26 → Carrera 25 → Calle 22 → Carrera 24 → Calle 18 → Carrera 26B → Calle 17 → Carrera 27 → Vía Oriental
2. Carrera 8 → Calle 11 → Vía Caracolí → Calle 63 (prolongación Av. Murillo, sexta entrada) → Avenida Circunvalar
3. Calle 19 → Glorieta Carrera 8 → Calle 17 → Carrera 15 → Calle 26 → Carrera 21B → Calle 30 → Carrera 25 → Calle 38 → Carrera 43
4. Calle 53 → Carrera 54 → Carrera 58 → Calle 76 → Carrera 54 → Calle 70 → Carrera 41 → Calle 40 → Carrera 38 → Calle 30
5. Carrera 21B → Calle 26 → Carrera 15 → Calle 17 → Glorieta Carrera 10 → Calle 19 → Avenida Circunvalar
6. Calle 46 → Carrera 1 → Calle 45 (Murillo) / Calle 63 prolongación → Vía Caracolí → Calle 10 → Carrera 8 → Vía Oriental
7. Carrera 27 → Calle 17 → Carrera 26B → Calle 18 → Carrera 24 → Calle 22 → Carrera 25 → Calle 26 → terminal

## Controles vóór shapes.txt
- Leg kruispunten vast en controleer dat elke opeenvolgende straat een berijdbare verbinding heeft; vooral `Calle 45 / Calle 63` is een OCR- en topologiegevoelig segment.
- Match de route met OSM/GraphHopper, rijrichtingen en eventuele KMZ; geen lineaire verbinding door ontbrekende straten heen tekenen.
- Koppel haltevolgorde pas na verificatie van stop-coördinaten en rijrichting.
- Vergelijk de historische 267-2010 met de latere 408-2013: voor 2013+ heeft 408 de gedocumenteerde routevolgorde, maar actuele uitvoering is nog onbewezen.
- 00:00–24:00 mag niet als gegarandeerde diensttijd worden aangenomen.

**Status:** `OCR_STREET_SEQUENCE_EXTRACTED_NOT_MAP_MATCHED`; **geen** productie-`shapes.txt` of `stop_times.txt` gewijzigd.
