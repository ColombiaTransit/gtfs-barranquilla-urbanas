# JUAN MINA — PT1/PT2 resolutiecontrole (5 november 2026)

## Bronnen en bevindingen
- SIU: JUAN MINA, 170 haltepassages, originele volgorde in `sources/siu/public_extract/siu_route_stop_sequences.csv`.
- AMB KMZ-manifest: PT1-4101 en PT2-4102 verwijzen **naar exact dezelfde PT1-4101.kmz URL en SHA-256** (`980cfa94668f42e87dc0de8441232ff59109aa8839053dffe4c5bab28339ad98`). Dus deze KMZ's bevatten geen richting- of variantonderscheid; 100% SIU-dekking bij beide is dezelfde meting.
- Resolución 192-2025 p.25–26: PT1-4101, *Villas de San Pablo – Juan Mina – Carrera 38 – Centro – Circular*, 55,4 km; gezamenlijke exploitatie COOLITORAL + TRANSDIAZ volgens gecureerde registratie. De naam **Juan Mina** komt expliciet in de PT1-routetitel voor.
- Resolución 210-2026 p.3–5,8: PT2-4102, *Ciudadela Metropolitana – Universidad del Atlántico – Circular*, A 52,9 km en B 57,2 km; twee aparte itinerarios met elk 10/12 minuten (effectief gezamenlijk 5/6). Dit is het nieuwere PT2-besluit.
- SIU noemt voor JUAN MINA COOLITORAL, TRANSDIAZ én SODETRANS; deze exploitantenset is nog niet met de PT1-resolutie gereconcilieerd.

## Operationele conclusie
**PT1-4101 is op basis van officiële routebenaming en de SIU-naam een sterkere baseroutekandidaat voor JUAN MINA dan PT2-4102.** Dit is een *voorlopige operationele identificatie*, niet een bewijs van volledige straatvolgorde of exploitantenverdeling. PT2 A/B is op basis van de twee gedupliceerde KMZ-vermeldingen niet vast te stellen.

## Onopgeloste straatvolgorde
De bestaande CSV-extracten bevatten titel, lengtes en frequenties, maar **niet de volledige geordende stratenreeksen** van PT1 (192-2025 p.25–26) en PT2-A/B (210-2026 p.3–5). De officiële PDF-links leverden bij deze controle geen direct leesbare pagina's. Daarom is **geen** verzonnen straat-voor-straatvergelijking met de 170 SIU-haltes uitgevoerd.

Heropen alleen dit concrete geometriedeel zodra de betreffende PDF-pagina's als tekst of afbeelding beschikbaar zijn; juridische geldigheid hoeft niet opnieuw onderzocht te worden. Bewaar de originele SIU-volgorde, en wijzig nog geen GTFS route_id/stop_times.

## Nieuwe primaire KMZ-bron — 5 november 2026

Gebruiker heeft de rechtstreeks geconstrueerde URL `https://www.ambq.gov.co/ruta-de-buses/COOLITORAL/PT2-4102.kmz` succesvol gedownload en het KMZ-bestand aangeleverd. Lokale inspectie bevestigt `doc.kml` met Placemark **PT2-4102**, één coördinatenreeks van **964 punten**, bestandsgrootte **23.270 bytes**, SHA-256 **`912e3afbd7b55dae5010831ac8de4b45f9bd1281fa54bac02114da8849d3b39a`**. De eerdere PT1-bron heeft SHA-256 `980cfa94668f42e87dc0de8441232ff59109aa8839053dffe4c5bab28339ad98`. Dit bewijst dat een afzonderlijk PT2-bestand bestaat en dat het oorspronkelijke AMB-paginamanifest de verkeerde PT2-link gebruikte. **De eerdere PT1/PT2-identieke-KMZ-score mag niet langer worden gebruikt om PT2 te beoordelen.** De geometrische vergelijking met PT1 en de SIU-stopvolgorde moet opnieuw worden uitgevoerd na import van het echte PT2-bestand. Dit is geen bewijs dat beide routes tegengestelde richtingen zijn.
