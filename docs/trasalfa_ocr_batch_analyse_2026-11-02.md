# TRASALFA — inhoudelijke analyse OCR-batch 41480204032

Bron: GitHub Actions artifact `amb-pdf-TRASALFA` (ID `13160854287`), acht resoluties, 80 pagina's. De OCR-tekst is gecontroleerd op de bepalende artikelen; details van slecht herkende tabellen blijven voor beeldcontrole. Alle acht documenten hebben status `extracted_requires_review`, geen technische extractiefout.

| Resolutie | Pagina's | Inhoud | Verwerking |
|---|---:|---|---|
| 111-2012 | 11 | Wijzigt traject B2B (Barranquillita–Calle 72–Vía 40–circulair) | Historische geometrie, geen zelfstandig nieuw interval |
| 139-2013 | 20 | Wijzigt D14-4156 en D15-4157; artikel 2 vervangt capaciteit, artikel 3 wijzigt 285/286-2010 gedeeltelijk | Laatste bekende wijziging in deze batch; beide trajecten en capaciteit controleren |
| 282-2010 | 6 | **Trekt vergunning Urbanización El Carmen–Centro in** | Niet als actieve route behandelen |
| 283-2010 | 7 | **Trekt vergunning Terminal–Zona Franca in** | Niet als actieve route behandelen; vergelijken met nieuwe herstructurering 287-2010 |
| 284-2010 | 7 | **Trekt vergunning Murillo–Delicias in** | Niet als actieve route behandelen |
| 287-2010 | 10 | Herstructureert Terminal–Zona Franca (Ruta 4), spits 5 min, dal 8 min, capaciteit 16–20 voertuigen | Historisch; relatie tot ingetrokken 283-2010 en latere B2B wijzigingen controleren |
| 286-2010 | 10 | Herstructureert Urbanización Bellavista–Centro, spits 5 min, dal 8 min, capaciteit 37–44 | Gedeeltelijk gewijzigd door 139-2013 |
| 285-2010 | 9 | Herstructureert Urbanización La Luna–Centro, spits 3 min, capaciteit 59–71; dalinterval onduidelijk in OCR | Gedeeltelijk gewijzigd door 139-2013 |

## Belangrijke uitkomst 139-2013

- Routes: B2B-4118, D14-4156 en D15-4157.
- Artikel 2: totale bedrijfscapaciteit **112 minimaal, 135 maximaal**; individuele tabel bevat OCR-ruis. B2B 16–20 en D15 48–58 zijn leesbaar; D14-cijfers vereisen visuele tabelcontrole.
- Technisch ontwerp noemt **4 minuten spits en 6 minuten dal** voor de aangepaste D14/D15. De definitieve tabel noemt een interval van 4 minuten voor beide routes. De tijdgrenzen van spits en dal zijn niet gegeven.
- Het besluit wijzigt resoluties 285-2010 en 286-2010 gedeeltelijk. Daarom zijn de oorspronkelijke capaciteiten en trajecten niet automatisch de geldige parameters na 2013.
- OCR van de titelpagina geeft soms foutieve besluitnummers (zoals 147 of 439); de latere pagina's bevestigen de indexnummers 111-2012 en 139-2013.

## GTFS-status

**Geen productie-GTFS aangepast.** De resoluties zijn historisch en geven geen geverifieerde actuele operationele dienstregeling. De routegeometrieën kunnen als historische bron worden verwerkt, na controle van straatnamen en richting. Voor frequenties ontbreken concrete spits-/dal-tijdvakken en verificatie van de huidige exploitatie.

## Nog te controleren

1. OCR-tabel en routebeschrijving van 139-2013, vooral D14-capaciteit en de volledige straatvolgorde van D14/D15.
2. Het onduidelijke dalinterval van 285-2010.
3. De juridische relatie tussen intrekking 283-2010 en herstructurering 287-2010; geen automatische gelijkstelling van routenamen.
4. Recente wijzigingen na 2013 en operationele geldigheid.
