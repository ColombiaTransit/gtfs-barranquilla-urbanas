# GraphHopper bus: 125 kandidaat-haltes beoordeeld zonder GTFS te wijzigen

De uitkomsten zijn hypotheses gebaseerd op bestaande GraphHopper bus-analyses en de officiële KMZ-routecorridor.
Een lage omweg bevestigt geen formele haltebediening of instapzijde. Een grote omweg bewijst niet op zichzelf een eenrichtingsweg.

## Aantallen

- toevoegkandidaat: **65**
- mogelijk_richtingsconflict: **24**
- onzeker: **36**

Van de oorspronkelijk als KMZ-naamrichtingsconflict gemarkeerde 80 SIU-kandidaten zijn 47 opnieuw toevoegkandidaat dankzij de busrouteanalyse.

## Regels

- Toevoegkandidaat: bestaande SIU fysieke stop-ID; GraphHopper bus A→halte→B langs KMZ-waypoints met maximaal 300m extra, maximaal 1,12x, minimaal 70% binnen 50m van KMZ, weg-snap maximaal 15m en halte maximaal 35m van KMZ. Geen onzekere officiële bron.
- Mogelijk richtingsconflict: via de kandidaat wordt de busroute substantieel langer (minimaal 500m en factor 1,18; of minimaal 1200m en factor 1,13) of er is grote corridor-afwijking. Andere wegbeperkingen blijven mogelijk.
- Onzeker: grensgeval, oudere ArcGIS-geometrie, twijfelachtig officieel A/B-label, OSM-only zonder fysieke SIU-ID of onvoldoende netwerk-/corridorbewijs.
- Bij een vermoedelijk tegengestelde SIU-naamrichting kunnen goede busroute-resultaten die voorlopige afwijzing heropenen.
- Geen curbside-test uitgevoerd; busroute langs haltepunt is geen bewezen instap aan de juiste kant van de weg.

## Stagingbestanden

- GH_bus_stop_candidate_decisions_125.csv: volledige classificatie, afstand, omweg en benodigde verificatie.
- proposed_insertion_order_NO_TIMES_REVIEW_ONLY.csv: voorlopige geografische haltepositie tussen bestaande stop-ID's, nooit automatisch GTFS stop_sequence.
- GH_bus_stop_classification_by_route.csv: prioriteiten per route.

Geen nieuwe GraphHopper-aanvragen, geen Overpass-aanvragen, geen wijziging in trips.txt, stop_times.txt of stops.txt.
