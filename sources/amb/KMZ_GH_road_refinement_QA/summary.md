# Gecontroleerde verfijning AMB KMZ: rechte segmenten met GraphHopper bus

Zelfde agency, routes, trips, stops, stop_times, calendar en testkalender. Alleen shapes.txt verschilt.
**Let op: dit is onderzoeks-GTFS met synthetische vertrektijden. Niet publiceren.**

## Verwerking

- KMZ-trajectdelen met bron-vertex-sprongen >400m: **144**
- Oorspronkelijke lange KMZ-verbindingen >400m: **457**
- GraphHopper bus-verzoeken: **457**
- Geografisch lokaal passende GH-wegstukken: **414**
- Aangepaste KMZ-routedelen na validatorcontrole: **22**
- Wegens QA teruggedraaide routedelen: **114**

## Feitelijke MobilityData GTFS Validator 8.0.1

| Bevinding | KMZ-first | KMZ + veilige GH-wegverbindingen |
|---|---:|---:|
| ERROR | 0 | 0 |
| alle WARNING | 2381 | 2378 |
| Haltes te ver van shape | 1 | 1 |
| Haltes buiten volgorde | 0 | 0 |

**Geen validatieregressie:** ja

## Bronnen/waarschuwingen

- Officiële AMB KMZ 2026 blijft de lijn- en volgordeautoriteit.
- GraphHopper bus-route wordt alleen voor ontbrekende bocht-details tussen bestaande KMZ-punten getoetst.
- Originele KMZ-punten blijven behouden; geen SIU-stop verplaatst of vervallen.
- PT2 en D8 zonder betrouwbare KMZ houden bestaande GH bus-fallback als onderzoeksgeometrie.
- Een GH-wegroute die de validator passeert, bewijst nog niet dat vervoerders die exacte straat in de concessie rijden.
- Geen nieuwe vertrek- en aankomsttijden en geen productiefeedwijzigingen.
