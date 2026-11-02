# FLOTA ÁNGULO — analyse OCR-run 41488216079 (2 november 2026)

## Technische extractie

- Run: https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41488216079
- Artifact: `amb-pdf-FLOTA_ANGULO`, ID `13163535622`.
- Manifest bevat één directe PDF: resolutie **301-2014**, 16 pagina's.
- `report.json`: `extracted_requires_review`, geen fout; alle 16 pagina's native PDF-tekst (geen Tesseract OCR nodig).
- De vijf andere officieel geregistreerde Flota Ángulo-resoluties zijn **nog niet verwerkt**: 232-2025, 265-2019, 242-2010, 157-2010, 242-2012. Eerst hun directe PDF-links vaststellen.

## Resolutie 301-2014 — inhoudelijk gecontroleerd

Bron: https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/FLOTA-ANGULO/301-14-RESOLUCION-FLOTA-ANGULO.pdf

| Veld | Waarde | Bronpagina |
|---|---|---|
| Bedrijf | FLOTA ÁNGULO LTDA | 1, 14–16 |
| Route | **A7-4112** | 14–15 |
| Benaming | **Barranquillita – La Pradera – Circular** | 14 |
| Voertuigklasse | **Grupo C (Busetón – Buseta)** | 14 |
| Spitsinterval | **3 minuten** | 14 |
| Dalinterval | **5 minuten** | 14 |
| Routelengte | **27 km** | 14 |
| Minimale vloot | **33 voertuigen** | 14–15 |
| Maximale vloot | **40 voertuigen** | 14–15 |
| Dienstvenster | **00:00–24:00 afhankelijk van vraag** | 14 |
| Overlap troncal/alimentación | **32% / 42%** | 14 |

**Let op:** het 00:00–24:00-venster is een voorwaardelijke vergunningstekst en geen bewijs van feitelijke 24-uursbediening. Ook de intervallen zijn vergunde historische waarden zonder exact gedefinieerde piek- en daluren.

### Routebeschrijving (pagina 14)

Terminal aan **calle 8, nr. 41n-70**. Via onder andere carrera 43, carrera 42f, calle 79b, carrera 42h, calle 84b, carrera 38, calle 100, carrera 36, calle 85, carrera 34, calle 107a, calle 108, Avenida Circunvalar, carrera 31, calle 123, calle 114 en via terugkerende straten naar de terminal. Dit is een circulair traject met heen- en terugsegmenten; voor GTFS-shapes moeten de volledige volgorde en eventuele OCR-verwisselingen (42bl/42b1, 42a3/42a4, enz.) worden nagekeken.

### Juridische kanttekeningen

- Artikel 3: gefaseerde implementatie gekoppeld aan instroom van Transmetro-voertuigen en voorafgaande kennisgeving.
- Artikel 7: vervangt strijdige oudere besluiten; latere besluiten uit 2019 en 2025 kunnen de geldige parameters wijzigen.
- Niet aannemen dat de 2014-gegevens de actuele exploitatie vertegenwoordigen.

## Vervolg

1. Vijf overige officiële resoluties koppelen aan verifieerbare PDF-URL's en aan OCR-manifest toevoegen.
2. Nieuwste 232-2025 en 265-2019 eerst vergelijken met 301-2014.
3. Straatvolgorde van A7-4112 en haltepunten verifiëren voordat `shapes.txt` wordt gebouwd.
4. Actuele frequenties en diensttijden afzonderlijk verifiëren; **geen productie-GTFS gewijzigd**.
