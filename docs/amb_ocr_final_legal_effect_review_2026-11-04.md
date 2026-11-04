# Afsluiting gerichte AMB-OCR-controle — 4 november 2026

Bronnen: bestaande GitHub Actions OCR-run 41803033009 (18 PDF's); artikelkandidaten-run 41812960855 (283 treffers, 6 besluiten). Geen nieuwe OCR uitgevoerd. De acht technische tabellen van COOTRANTICO 462-2025 en acht van COOCHOFAL 242-2025 zijn tegen de reeds beschikbare pagina-afbeeldingen gecontroleerd. Waarden staan in [verified_462_242_route_headways_2026-11-04.csv](../sources/amb/legal_validity_ocr_review/verified_462_242_route_headways_2026-11-04.csv).

## COOTRANTICO 462-2025
Artikel 1 bevat acht routetabellen (PDF-pagina's 5–20). Per route: A18 8/10, B4 7/9, B5 8/10, B5-B 8/10, B6 7/9, B7 6/8, B20 7/9, B20-B 7/9 minuten spits/dal. Artikel 2 op pagina 21 schrijft persoonlijke kennisgeving voor; artikel 3 vermeldt beroep binnen tien dagen na kennisgeving. **Geen kennisgevingsdatum of daadwerkelijke operationele start aangetoond.** Routecodes B20 en B20-B blijven afzonderlijke routes; geen automatische A/B-dubbeling van frequenties.

## COOCHOFAL 242-2025
Artikel 1 en tabellen op PDF-pagina's 4–20: A15 2,5/4, C2 6/9, C2-B 4,5/7, C3 7/10, C4 3/5, C9 7/10, C18 7/10, D20 2,5/4 minuten spits/dal. De originele tekst is **intern inconsistent**: artikel 1 A15-4129 versus route-/wagenparktabel A15-4159; artikel 1 en routekop C2-B-4187 versus wagenparktabel C2-B-4188. De frequenties zijn leesbaar maar **de route-identiteit blijft juridisch geblokkeerd** totdat een officieel rectificatiebesluit beschikbaar is. Artikel 2 schrijft kennisgeving voor en artikel 3 beroep binnen tien dagen.

## EMBUSA 231-2025 → 010-2026
231-2025 p. 8: B9-4125 3/5 min spits/dal. Het **Parágrafo Transitorio** geeft één jaar **vanaf ejecutoria** om aan de *minimale vervoerscapaciteit* te voldoen. Dit is geen uitstel van de frequentie of een bekende operationele startdatum. De datum van ejecutoria is niet aangetoond.

010-2026 art. 1 (p. 3–5): B9-4125 4/6 min spits/dal; minimale/maximale voertuigcapaciteit blijft 47/56 (p. 5). Artikel 2: persoonlijke kennisgeving. Artikel 3: beroep binnen tien dagen na kennisgeving. Besluit gedateerd **6 januari 2026**; dit is **niet** bewezen als datum van kennisgeving, ejecutoria of operationele activering. Voor overlappende B9-scope prevaleren de latere 4/6-parameters als **vergunningsreferentie**, niet als bewezen actuele dienstregeling. De voorwaardelijke 00:00–24:00-formulering bewijst geen nachtservice. Exacte variant-/routewijziging vraagt vergelijking van geometrie.

## TRASALIANCO 268-2010 → 411-2010
411-2010 p. 7 art. 1 bevestigt 268-2010 **gedeeltelijk**. Art. 2 **corrigeert de routebeschrijving van PASADENA / D17**, met onder a) een beschrijving gekoppeld aan de aanvang van Transmetro. Art. 3 p. 8 wijzigt 268-2010 gedeeltelijk. Art. 4 schrijft kennisgeving voor; art. 5 meldt geen administratief rechtsmiddel. Art. 6 onderscheidt rechtskracht **vanaf ejecutoria** van de operationele toepassing en noemt een overgang **totdat Transmetro begint**, te communiceren door AMB. De tekst bevat een spanningsveld tussen art. 2a (vanaf start Transmetro) en art. 6 (tot aan start Transmetro). **Niet stilzwijgend oplossen:** exacte fasering blijft juridisch ambigu; vraag originele officiële verduidelijking of vervolgact.

## GTFS-veiligheidsbesluit
- De **16 frequentietabellen zijn uit de OCR-werklijst gehaald**; hun numerieke waarden zijn nu controleerbaar.
- Alle 16 records hebben `scope=whole_route_unverified` en `release_approved=no`; ze mogen **niet** zonder routevariant-toewijzing worden gebruikt om trips te verdubbelen.
- EMBUSA: gebruik geen automatisch startdatum op basis van besluitdatum en geen overgangstermijn van een jaar voor frequenties.
- TRASALIANCO: geen fasewissel of kalenderdatum verzinnen; registreer `transmetro_transition_amb_notice_unverified`.
- COOCHOFAL: beide broncodeconflicten behouden; geen stille alias of route-merge.
- Resterende blokkades zijn **ontbrekende externe rechts-/exploitatiebewijzen**, geen onleesbare OCR-tabellen. Een definitieve GTFS-publicatie blijft daarom uit.
