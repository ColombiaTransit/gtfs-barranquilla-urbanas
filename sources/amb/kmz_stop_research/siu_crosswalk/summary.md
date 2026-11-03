# SIU → AMB KMZ: kandidaten per itinerary

**Geen automatische hernummering van SIU-itinerary naar AMB-route-ID:** een hoge geografische match bewijst geen juridische A/B-variant.

- 33 SIU-itineraries beoordeeld.
- 13 nog onzekere SIU-itineraries krijgen een KMZ-ranking.
- 296 routegeometrie-kandidaatcombinaties doorgerekend.

## Onzekere SIU-koppelingen

| SIU-itinerary | GIS-basiscode | Beste KMZ-kandidaat | Binnen 30 m | Nummer 2 | Binnen 30 m nr.2 |
|---|---|---|---:|---|---:|
| MAKRO | B17-4163 | COOLITORAL / B17-4163 | 98.9% | TRANSDIAZ / A10-4114 B | 76.4% |
| MIRAMAR ALAMEDA DEL RIO | A16-4161 | LA-CAROLINA / A16-4161 A | 86.5% | LA-CAROLINA / A16-4161 B | 86.5% |
| VIA 40 MURILLO | PT3-4103 | COOLITORAL / PT3-4103 | 98.6% | COOLITORAL / PT4-4104 | 60.2% |
| CIRCUNVALAR VIA 40 | PT4-4104 | COOLITORAL / PT4-4104 | 98.5% | COOLITORAL / PT5-4105 | 98.5% |
| VIA 40 CIRCUNVALAR | PT4-4104 | COOLITORAL / PT4-4104 | 82.3% | COOLITORAL / PT5-4105 | 82.3% |
| RIOMAR AMARILLA | B13-4128 | SODETRANS / B13-4128 | 100.0% | SODETRANS / B13-B-4189 | 100.0% |
| ROJA RIOMAR | B13B-4189 | SODETRANS / B14-4174 | 100.0% | SODETRANS / B13-4128 | 67.2% |
| SOLEDAD 2000 CORREDOR UNIVERSITARIO | C21-4182 | SODETRANS / C21-4182 B | 100.0% | SODETRANS / C21-4182 A | 77.0% |
| JUAN MINA | PT1-4101 | COOLITORAL / PT1-4101 | 100.0% | COOLITORAL / PT2-4102 | 100.0% |
| SOLEDAD CALLE 84 VILLA CAROLINA | A10-4114 | TRANSDIAZ / A10-4114 A | 100.0% | TRANSDIAZ / A10-4114 B | 39.6% |
| VILLA SAN PABLO | PT1-4101 | COOLITORAL / PT1-4101 | 81.6% | COOLITORAL / PT2-4102 | 81.6% |
| LAS GAVIOTAS CALLE 76 | A16-4161 | LA-CAROLINA / A16-4161 A | 66.2% | LA-CAROLINA / A16-4161 B | 66.2% |
| SOLEDAD CALLE 84 | B17-4163 | TRANSDIAZ / A10-4114 B | 100.0% | TRANSDIAZ / A10-4114 A | 66.1% |

## Gebruik

- Controleer eerst operatoren, originele wettelijke straatverlopen en mogelijke A/B-varianten.
- PT4/PT5 en gedeelde vervoerders mogen bij overlappende geometrie niet op rang 1 worden toegewezen.
- De 12 sterke en 8 voorlopige SIU-stopvolgordes worden **niet vervangen** door KMZ-kandidaten.
- Output bevat geen GTFS-stop_times of shapes-publicatie.
