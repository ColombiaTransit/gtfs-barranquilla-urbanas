# Uitgestelde geometriecorrecties — 5 november 2026

Deze twee routes zijn **bewust uitgesteld**. Niet automatisch opnieuw laten blokkeren of een ArcGIS-/GraphHopper-vervangende geometrie publiceren. Heropenen zodra de gebruiker de geometrische herstelronde hervat.

| Route | Bedrijf | Status | Openstaande correctie |
|---|---|---|---|
| A4-4109 | COOLITORAL | DEFERRED_GEOMETRY_REVIEW | Officiële AMBQ-recorrido koppelen aan zes KMZ-segmenten; Carrera 46 ligt in eerste OSM-match 221 m van KMZ; Pinar del Río, Parque Venezuela en Universidad del Atlántico (heen/terug) als oriëntatiepunten georefereren; midden-op-lijn-aansluitingen, rijrichting, retourlussen en Puente de la 51B controleren. ArcGIS-geometrie wijkt af en is geen vervanger. |
| D8-4165 | LOLAYA | DEFERRED_GEOMETRY_REVIEW | AMBQ KMZ met 237 segmenten / 1014 vertices vormt één endpoint-component; ArcGIS heeft 7 segmenten / 634 vertices met meerdere componenten. Topologische en inhoudelijke routevergelijking afronden voordat een definitieve GTFS-shape wordt gekozen. |

## Herkomst
- A4 officiële route: `docs/coolitoral-a4-4109-official-recorrido-geometry-review-2026-11-05.md`
- A4 KMZ-segmentanalyse: `docs/coolitoral-a4-4109-six-segment-mapping-2026-11-05.md`
- A4 Overpass-run: `docs/coolitoral-a4-4109-overpass-run-42034897530-review.md`
- A4 QA artifact: https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42034897530/artifacts/13417886835
- Beide routes kwamen uit de AMBQ–ArcGIS-vergelijking als `GEOMETRY_UNRESOLVED`.

## Werkafspraak
Onderzoek naar andere routes en GTFS-brondata gaat door. Deze twee blijven op de herstelwerklijst; `DEFERRED_GEOMETRY_REVIEW` betekent **niet** dat hun geometrie is gevalideerd of het conflict is opgelost.
