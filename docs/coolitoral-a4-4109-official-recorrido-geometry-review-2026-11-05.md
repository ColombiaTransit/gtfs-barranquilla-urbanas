# COOLITORAL A4-4109 — officiële straatvolgorde en geometriecontrole

## Herkomst en status
Door gebruiker overgenomen volledige Spaanse *recorrido* uit de getoonde AMBQ-resolutie (2026-11-05). De pagina/resolutienummer van het getoonde fragment moet bij latere juridische citatie nog worden gekoppeld. De beschrijving is een **geordende route**, niet slechts een verzameling straten. Geen automatische GTFS-publicatie.

## Letterlijke routebeschrijving
Saliendo de la nevada El Pueblo, ubicada en la Calle 120 con Carrera 10. Tomando la Carrera 10, por esta hasta la Av. Circunvalar, por esta hasta la Carrera 9G, por esta hasta la Diagonal 138, por esta hasta la calle 134, por esta hasta Pinar del Río, por esta hasta la Carrera 38, por esta hasta la Calle 120, por esta hasta la Carrera 37, empalmando con la Calle 123, por esta hasta la Carrera 31, por esta hasta la Av. Circunvalar, por esta hasta el retorno Carrera 28, por este hasta la Av. Circunvalar, por esta hasta la Carrera 52, por esta hasta la Calle 106, por esta hasta la Carrera 51B, por esta hasta la glorieta de la Universidad del Atlántico, por esta hasta la Carrera 51B, por esta hasta la Calle 96, por esta hasta la Carrera 46, por esta hasta la Calle 90, por esta hasta el Parque Venezuela, siguiendo por la Calle 90 hasta la Carrera 42B1. Por esta hasta la Calle 81, por esta hasta la Carrera 42A, por esta hasta la calle 80B, por esta hasta la Carrera 42, por esta hasta la Calle 75B, por esta hasta la Carrera 41D, por esta hasta la Calle 74, por esta hasta la Carrera 44, por esta hasta la Calle 37, por esta hasta la Carrera 43, para empalmar con la Carrera 42F hasta la Calle 75B, por esta hasta la Carrera 42, por esta hasta la Calle 80B, por esta hasta la Carrera 42B, por esta hasta la Calle 81, por esta hasta la Carrera 42B1, por esta hasta la Calle 93, por esta hasta la Carrera 51B, por esta hasta la glorieta de la Universidad del Atlántico, retornando por la Carrera 51B hasta la circunvalar, por esta hasta la Carrera 9G, retornando a la Nevada El Pueblo. Fin del recorrido.

## Geordende controlepunten
1. La Nevada El Pueblo (Calle 120 / Carrera 10) — begin
2. Carrera 10 → Avenida Circunvalar → Carrera 9G
3. Diagonal 138 → Calle 134 → Pinar del Río
4. Carrera 38 → Calle 120 → Carrera 37 → Calle 123 → Carrera 31
5. Avenida Circunvalar → retorno Carrera 28 → Avenida Circunvalar
6. Carrera 52 → Calle 106 → Carrera 51B → glorieta Universidad del Atlántico
7. Carrera 51B → Calle 96 → Carrera 46 → Calle 90 → Parque Venezuela
8. Calle 90 → Carrera 42B1 → Calle 81 → Carrera 42A → Calle 80B
9. Carrera 42 → Calle 75B → Carrera 41D → Calle 74 → Carrera 44
10. Calle 37 → Carrera 43 → Carrera 42F → Calle 75B
11. Carrera 42 → Calle 80B → Carrera 42B → Calle 81 → Carrera 42B1
12. Calle 93 → Carrera 51B → glorieta Universidad del Atlántico
13. Carrera 51B → Avenida Circunvalar → Carrera 9G → La Nevada El Pueblo — einde

## Consequenties voor geometrie
- AMBQ KMZ A4-4109 is de primaire geometrie. Het getoonde kaartbeeld in de resolutie is visueel grotendeels consistent, maar niet metrisch gevalideerd.
- ArcGIS OBJECTID 16 toont een ander traject: **ARCGIS_ROUTE_GEOMETRY_CONFLICT**. Niet als fallback gebruiken.
- KMZ bevat zes LineStrings, 657 punten; endpoint-analyse vond vier componenten bij 100m. Dit bewijst geen vier afzonderlijke routes.
- Behoud expliciete terugritten over Circunvalar en Carrera 51B, plus de lus in het centrum; niet dedupliceren.
- Geen sprongen over gescheiden rijbanen, niet verbinden op louter ruimtelijke nabijheid of lijnkruising.
- Volgende controle: map elk van de zes LineStrings op de opeenvolgende straten en bepaal de toegestane gerichtheid/overgangen, met bijzondere aandacht voor Puente de la 51B.
- Geen GraphHopper of ArcGIS-fallback voordat de officiële KMZ-segmenten op deze volgorde zijn getoetst.
