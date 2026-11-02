# EMBUSA — resolutie 010-2026, inhoudelijke validatie

**Officiële bron:** https://www.ambq.gov.co/wp-content/uploads/2026/01/RESOLUCION-REESTRUCTURACION-EMBUSA-ENE-2026.pdf  
**Besluitdatum:** 6 januari 2026. **Document:** vijf pagina's. **Status:** officieel besluit geanalyseerd; huidige exploitatie niet onafhankelijk bevestigd.

## Juridische handeling
Artikel 1 **wijzigt** de exploitatievergunning van **B9-4125**, geëxploiteerd door Empresa de Buses del Atlántico Ltda. (EMBUSA). Technische onderbouwing: rapport 014-2025 van 18 december 2025. De wijziging verbetert de dekking richting Río Alto.

## Geautoriseerde route en kenmerken (artikel 1, pagina 3–5)
- **Routecode:** B9-4125.
- **Naam:** Zona Franca – Las Nieves – Carrera 8 – Lucero – El Recreo – Carrera 58 – Calle 77 – Vía 40 – Río Alto – Las Flores – Circular.
- **Start/eind:** Calle 8 nr. 41N-70.
- **Straattraject:** volledige tekst staat op pagina 4–5; onder meer Calle 8, Carrera 38, Calle 6/Corredor Portuario, Carrera 30, Calle 17, Carrera 15, Avenida Calle 30, Carrera 8, Calle 51B, Carrera 8G, Calle 50A, Carrera 10, Calle 54, Carrera 14, Calle 53D, Diagonal 31, Carrera 25, Calle 57, Carrera 26/27/30/31, Calle 53C, Carrera 33, Calle 52, Carrera 42, Calle 53, Carrera 53, Calle 64, Carrera 58, Calle 77, Vía 40, Calle 98, Carrera 65A, Calle 106, Carrera 72A, Avenida Circunvalar, Vía 40, Calle 75, Carrera 68, Calle 74, Carrera 61, Calle 68, Carrera 66, Calle 52, Carrera 54, Calle 58/59, Carrera 47, terug via Carrera 30, Calle 56/57, Calle 53D, Carrera 16, Calle 46/54, Carrera 10, Carrera 8 en Calle 30 naar beginpunt. **De exacte opeenvolging is leidend zoals in het PDF, niet deze verkorte samenvatting.**
- **Lengte:** 53,9 km.
- **Voertuigklasse:** Grupo C (busetón/buseta).
- **Spitsinterval:** 4 minuten.
- **Dalinterval:** 6 minuten.
- **Capaciteit:** minimaal 47, maximaal 56 voertuigen. Het besluit zegt expliciet dat de totale bedrijfscapaciteit niet wordt aangepast.
- **Dienstvenster:** 00:00–24:00 **afhankelijk van vraag**, dus geen bewijs van feitelijke nachtbediening.
- **Overlapping:** troncal 10,7%, alimentador 51%.

## GTFS-besluit
- `agency_id=EMBUSA`, `route_id=B9-4125`: bruikbare juridische route-identificatie.
- **Niet** automatisch een actuele `frequencies.txt` genereren: spits-/daltijdvakken en feitelijke exploitatie zijn niet vastgesteld.
- **Niet** automatisch `shapes.txt` genereren uit vrije straattekst zonder georeferentie en volgordecontrole.
- **Geen productie-GTFS aangepast.**

## Nog te doen
1. Besluit 231-2025 vergelijken op juridische samenhang.
2. Exacte straatsegmenten uit artikel 1 omzetten naar route-segmentenregister.
3. Concrete diensttijden en actuele werking onafhankelijk verifiëren.
