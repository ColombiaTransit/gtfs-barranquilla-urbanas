# TRANSURBAR — analyse OCR-batch 41480204032

Bron: artifact `amb-pdf-TRANSURBAR` (ID `13162560906`), 12 documenten / 126 pagina's. Alle twaalf status `extracted_requires_review`; geen extractiefouten. Historische vergunningen, geen geverifieerde actuele exploitatie.

| Resolutie | Pagina's | Resultaat |
|---|---:|---|
| 717-2018 | 9 | Maatregel voor diensten; eerder geanalyseerd: A14/D16/D19, totale capaciteit 100–121 en mogelijk aanvullend padrón; 15-minuten Circunvalar is voorstel, geen bestaande dienstregeling |
| 279-2010 | 6 | Trekt vergunning Urbanización Estadio–Circunvalar–Calle 47/45–Vía 40–Las Flores in |
| 051-2017 | 11 | **Herstructureert A14-4116, D16-4173 en D19-4184**; OCR bevat onder meer spits 6 en dal 8 minuten bij een van de routetabellen; afzonderlijke route-toewijzing vereist |
| 322-2016 | 17 | Herstructurering van meerdere routes; OCR noemt 14 minuten spits en 16 minuten dal in een tabel; routetoewijzing nog verifiëren |
| 180-2015 | 11 | Verklaart verlies van uitvoerbaarheid van besluit 279-2010; herverdeelt capaciteit. **Niet simpelweg als herroeping van de herroeping behandelen** |
| 142-2015 | 7 | Herstructureert route(s) van Transurbar; traject en parameters nog gedetailleerd uitwerken |
| 241-2015 | 8 | Wijzigt A14-4116; spits 4 minuten, dal 7 minuten, lengte 51,7 km, minimumcapaciteit 45 |
| 155-2013 | 19 | Wijzigt D16-4173; ontwerp noemt dalinterval 6 minuten, maximumcapaciteit 56; actuele vervanging via 051-2017 onderzoeken |
| 280-2010 | 6 | Trekt vergunning María Modelo–Estadio in |
| 225-2010 | 10 | Herstructureert María Modelo–Murillo–Soledad 2000–Vía 40–Las Flores; capaciteit 45–54 |
| 320-2011 | 12 | Herstructureert A14-4116; spits 4, dal 7 minuten; behoudt capaciteit uit 225-2010 |
| 224-2010 | 10 | Herstructureert María Modelo–Manuela Beltrán–Vivero; capaciteit 46–56 |

## Belangrijkste conclusies

- **051-2017 is de belangrijkste gezamenlijke wijziging voor A14/D16/D19** binnen deze batch. Een per-route matrix uit de artikel-1-tabellen is nodig voordat historische intervallen worden toegewezen.
- **180-2015 en 279-2010 hebben een juridische afhankelijkheid**: 180-2015 verklaart 279-2010 niet meer uitvoerbaar. Geen route automatisch als operationeel markeren zonder volledige juridische toets.
- 717-2018 bevat een voorstel voor gezamenlijke Circunvalar-dienst (met andere vervoerders), maar bewijst niet dat die dienst daadwerkelijk reed.
- Bij de extractie zijn alle 12 PDF's gelukt; OCR-hercontrole blijft nodig voor tabellen, exacte routecodes en straatvolgordes.
- **Geen productie-GTFS gewijzigd**; de frequenties zijn historische vergunningsparameters zonder tijdvakken of actuele dienstbevestiging.

## Open acties

1. Visuele controle en route-voor-route extractie van tabellen in 051-2017 en 322-2016.
2. Uitwerken van volledige trajecten en richtingen voor A14, D16 en D19.
3. Juridische chronologie 279-2010 → 180-2015 en 2015/2016 → 051-2017 → 717-2018.
4. Verificatie van huidige operatie en concrete piek-/daltijden.
