# A4-4109 — QA van de eerste private-Overpass-run

Bron: GitHub Actions run [42034897530](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/42034897530), artifact `A4-4109-OSM-recorrido-candidate-QA` (ID 13417886835), gegenereerd op 5 november 2026. Officiële routevolgorde: `docs/coolitoral-a4-4109-official-recorrido-geometry-review-2026-11-05.md`.

## Vastgestelde resultaten
- Privé-Overpass-query geslaagd: 7.977 OSM-ways.
- 50 geordende vermeldingen; 230 kandidaten; 45 eerste kandidaten op maximaal 35 m.
- Geen GTFS-productiebestanden aangepast.

## Vijf vermeldingen zonder match binnen 35 m

| Volgnummer | Vermelding | Oorzaak of aanwijzing | Vervolg |
|---:|---|---|---|
| 7 | Pinar del Río | Wijk-/gebiedsnaam; niet als wegnaam gevonden | Zoek place/area/POI en leg verbinding Diagonal 138–Calle 134–Carrera 38 vast |
| 19 | Universidad del Atlántico | Rotonde bij universiteit is een plaatsbeschrijving, geen straatnaam | Georeferentieer rotonde op Carrera 51B |
| 22 | Carrera 46 | Beste gevonden wegmatch op **221,0 m** van KMZ segment 6 | Controleer wegnaamvarianten, werkelijk kruispunt Calle 96/Carrera 46, routekaart en segmentligging; niet automatisch overbruggen |
| 24 | Parque Venezuela | Park/oriëntatiepunt; geen gewone wegnaam | Georeferentieer park en Calle 90-passage |
| 46 | Universidad del Atlántico | Zelfde rotonde, terugpassage | Koppel aan juiste terugrichting op Carrera 51B |

## Sterke kandidaatgroepen uit CSV
- Volgnummers 1–15 (westelijke lus): vooral segment 1, maar herhaalde straten zijn niet automatisch dezelfde positie.
- Volgnummers 16–21: Carrera 52 op segment 3; Calle 106, Carrera 51B, Calle 96 op segment 2.
- Volgnummers 23–25: Calle 90 op segment 4.
- Volgnummers 26–32 en 38–43: centrumlus, grotendeels segment 5.
- Volgnummers 33–37: segment 6.
- Volgnummer 44: Calle 93 op segment 4.
- Volgnummers 45–47: Carrera 51B op segment 2.
- Volgnummers 48–50: Circunvalar, Carrera 9G, Calle 120 op segment 1.

**Belangrijk:** de huidige matcher zoekt per straatnaam de dichtstbijzijnde OSM-wegvertex bij *ieder* KMZ-segment, niet de opeenvolgende kruispunten. Daardoor kunnen meerdere vermeldingen van dezelfde straat dezelfde plek krijgen en kan de geometrisch dichtstbijzijnde match op een onjuist deel van de route liggen. Deze groepsindeling is **niet** de definitieve rijvolgorde.

## Volgende verificatie
1. Breid OSM-query uit met `place`, `leisure=park`, `amenity=university`, `junction=roundabout` en relevante naamvarianten; beperk resultaten geografisch.
2. Bepaal per opeenvolgend paar straatnamen de echte kruising en de bijbehorende KMZ-edge, niet alleen naamnabijheid.
3. Verifieer midden-op-lijn-koppelingen tussen segmenten 2–4, 4–5 en 5–6 met afstanden en toegestane verkeersrichting; deze verbindingen zijn visueel/geografisch plausibel maar nog niet juridisch en topologisch goedgekeurd.
4. Leg het Carrera 46-conflict expliciet vast als blocker totdat het brontracé is gecontroleerd.
5. Reconstrueer pas daarna de officiële heen-/terugvolgorde als gerichte graaf, zonder ArcGIS en zonder automatische sprongen.
