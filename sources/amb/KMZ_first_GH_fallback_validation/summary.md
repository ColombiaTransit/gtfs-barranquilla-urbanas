# Barranquilla: officiële 2026 KMZ-first vs GraphHopper-busweg in GTFS

De GTFS-gegevens behalve shapes.txt zijn identiek; kalender, trips en tijden zijn nog steeds synthetisch.
KMZ wordt alleen gebruikt als er een bruikbare AMB-KMZ 2026-figuur is; GraphHopper-buswegen blijven
fallback voor onbruikbare of ontbrekende route-KMZ, en moeten op de echte route worden gevalideerd.

## Gelijke testpopulatie

- Routes: **59**
- Voorbeeldritten: **67**
- Haltebezoeken: **8867**
- KMZ-bronpatronen: **63**
- GraphHopper-fallbackbronpatronen: **7**

## MobilityData 8.0.1 — feitelijke resultaten

| Code | Alleen GraphHopper | KMZ eerst / GH fallback | Verschil |
|---|---:|---:|---:|
| ERROR | 0 | 0 | 0 |
| alle WARNING | 2433 | 2381 | -52 |
| stop_too_far_from_shape | 64 | 1 | -63 |
| stops_match_shape_out_of_order | 4 | 0 | -4 |

## Beoordeling

- Kleinere halte-afstand betekent NIET automatisch betere rijrichting, echt lijntracé of dienstregeling.
- Bij een herhaalde passage op dezelfde straat kunnen loopvormige KMZ's validator-volgordewaarschuwingen geven.
- PT2 zonder bestaande route-ID blijft uit beide testfeeds, precies als voorheen.
- Geen SIU-haltes verplaatst of verwijderd, geen ritgrenzen bepaald, geen productie-GTFS aangepast.

**Afstandsconclusie:** KMZ-first vermindert de geometrische halteafstandfouten in deze test.
