# Visueel bevestigde artikelen: SOBUSA 082-2026 en COOLITORAL 256-2026

Bronnen: GitHub Actions run 41803033009, artifact 13308193358. Beide originele PDF's zijn 7 pagina's lang. Controle van originele pagina-afbeeldingen én tekstextractie, 4 november 2026.

## SOBUSA — resolutie 082-2026
- Originele PDF SHA-256: fdfdfd5cd32277337ab0346abf1ecc46f677ae94d1d91c96c1e54459eb075dde.
- Besluit van 12 februari 2026, artikel 1: wijziging van vergunning **B18-4175**, Granabastos–Los Manantiales–Río Alto–Ciudad Mallorquín–La Playa–Circular.
- **Originele pagina 6 visueel gecontroleerd:** Itinerario A **10 minuten piek, 12 minuten dal**; Itinerario B **10 minuten piek, 12 minuten dal**. Gezamenlijke frequentie drukste corridor **5 minuten piek, 6 minuten dal**. Lengte A 73,6 km, B 75,6 km.
- Dienstvenster vermeldt 00:00–24:00 **afhankelijk van vraag**, dus geen bewijs van nachtelijke ritten. Artikel 2 schrijft persoonlijke kennisgeving voor; artikel 3 vermeldt reposición binnen tien dagen na kennisgeving.
- Juridische betekenis: B18 heeft een concreet gewijzigde routevergunning in 082-2026. De eerdere 466-2025 tabel niet als gelijktijdige B18-dienst dupliceren. De twee A/B-varianten elk op eigen interval; corridorwaarde niet als extra ritten tellen.
- Open: bewijs van kennisgeving, eventuele opvolgende wijziging, feitelijke exploitatie, piek/dal-uren en haltevolgorde.

## COOLITORAL — resolutie 256-2026
- Officiële PDF: https://www.ambq.gov.co/wp-content/uploads/2026/06/RESOLUCION-256-2026-PILOTO-COOLITORAL-1.pdf
- Originele PDF SHA-256: 8c6e8699038acdaa515ad53e47feb7697594492b21e62def4dcfb3d25b4d435e.
- Besluit gedateerd 19 juni 2026; **artikel 1** autoriseert een tijdelijk pilotproject voor **PT4-4104** en **PT5-4105** van COOLITORAL. Originele pagina's 4–7 visueel gecontroleerd.
- PT4: A **9 minuten piek / 14 minuten dal**; B **9/14**; gezamenlijke drukste corridor **4,5/7**; beide lengtes 34,5 km.
- PT5: A **9/14**; B **9/14**; gezamenlijke drukste corridor **4,5/7**; lengtes A 35,5 km en B 35,3 km.
- **Artikel 2, originele pagina 7:** pilot duurt **zes maanden vanaf 22 juni 2026**. Verlenging is mogelijk op grond van resultaten van de proef, maar wordt door deze bepaling **niet automatisch verleend**. Zonder afzonderlijk verlengingsbesluit is de pilot na **21 december 2026** niet langer op deze vergunning te baseren; technische eindgrens voor datumintervallen: **2026-12-22 exclusief**.
- De tekst noemt elders COOTRANSCO als technisch nabijgelegen vervoerder, maar het dispositieve artikel autoriseert expliciet COOLITORAL PT4/PT5. **Geen gezamenlijke exploitatie door COOTRANSCO afleiden** uit die considerans.
- Dienstvenster 00:00–24:00 afhankelijk van vraag is geen bewijs van 24-uursritten.
- Open: later verlengings- of vervangingsbesluit, operationele activering, exacte piek/dal-uren en haltes/geometrie.

## GTFS-interpretatie
1. Gebruik afzonderlijke A/B-headways; **geen extra corridortrips** voor de samengestelde frequentie.
2. PT4/PT5-pilot mag binnen het juridische pilotinterval als bron voor historische/voorwaardelijke dienst worden gemodelleerd, niet automatisch als actuele exploitatie.
3. Bij aflopen van de pilot vervalt **de pilotregeling**, niet automatisch de onderliggende routevergunning of elke eerdere dienstregeling.
4. Geen GTFS-releasegoedkeuring zonder exploitatie-, kalender-, halte- en geometriecontrole.
