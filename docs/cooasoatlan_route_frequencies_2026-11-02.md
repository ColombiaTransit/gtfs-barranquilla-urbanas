# COOASOATLAN — juridische route- en frequentieanalyse

Bron: originele pagina-extracties uit GitHub Actions-artifact `amb-pdf-COOASOATLAN` (run 41480204032). **9 manifestdocumenten.** Deze analyse controleert de operationele artikelen van 369-2025 tegen de historische 305-2014. Andere historische besluiten blijven voor artikelvergelijking open.

## Laatste aangetroffen herstructurering: 369-2025 (30 september 2025)

**Artikel 1, p. 5:** herstructureert vier routes: **C1-4132, C1-B-4186, C20-4181, C20-B-4187**. De tabellen volgen achtereenvolgens op p. 7, 9, 11 en 13. De tabelwaarden horen bij de route die vóór de betreffende tabel wordt geïntroduceerd, **niet** bij de nieuwe routecode die eronder begint.

| Route | Spitsinterval | Dalinterval | Min. voertuigen | Max. voertuigen | Lengte | Bron |
|---|---:|---:|---:|---:|---:|---|
| C1-4132 | 10 min | 12 min | 16 | 19 | 55,2 km | p. 5–7 |
| C1-B-4186 | 9,5 min | 12 min | 15 | 18 | 48,9 km | p. 7–9 |
| C20-4181 | 10 min | **OCR onduidelijk** | 14 | 16 | 47,5 km | p. 9–11 |
| C20-B-4187 | 10 min | 12 min | 15 | 18 | 51 km | p. 11–13 |

**Kwaliteit:** de C20-4181 dalwaarde is in de OCR-pagina niet betrouwbaar leesbaar; niet invullen als 12 zonder scancontrole. Het samenvattende vlootoverzicht op p. 13–14 is gedeeltelijk corrupt door OCR; individuele tabellen hierboven zijn leidend tot scanverificatie.

**Artikel 2, p. 14:** verplaatst de dispatchterminal van alle vier routes naar **Diagonal 36 nr. 38A-91, lote A1, Malambo**. Dit is een concrete route-/operationele wijziging die voor GTFS relevant kan zijn, maar geen bewezen nieuwe haltepositie.

**Artikel 1, p. 7/9/11/13:** vermeldt een mogelijk venster 00:00–24:00 *afhankelijk van vraag*. Dit bewijst geen nachtelijke dienst.

## Vergelijking met 305-2014
- Op p. 13 staat een historische routevariant met **4 min spits / 6 min dal**, **32–39 voertuigen**.
- Op p. 14 staat een tweede historische routevariant met **4 min spits / 6 min dal**, **26–32 voertuigen**.
- De exacte historische routecode bij iedere tabel moet via de voorafgaande pagina worden bevestigd. Deze oudere waarden **niet** overschrijven op de 2025-routes.
- Resolutie 218-2010 is expliciet een *recurso de reposición* tegen 172-2010; voor juridische chronologie moeten beide samen gelezen worden.

## Open vervolgwerk
1. **COOA-01:** visuele controle p. 11 (dalinterval C20-4181), p. 13–14 (samenvattende vlootmatrix).
2. **COOA-02:** alle 2010–2014 besluiten juridisch vergelijken met 369-2025; intrekkingen, bezwaren en oude routecodes per artikel vastleggen.
3. **COOA-03:** de vier volledige straattrajecten uit p. 5–13 omzetten naar controleerbare segmentreeksen; routevariant en richting valideren.
4. **COOA-04:** onafhankelijke bron voor feitelijke spits-/dalvensters en actuele ritten zoeken.

**Status:** `369-2025 ARTICLE_REVIEWED_WITH_OCR_EXCEPTION`; historische besluitketen `OPEN`; actuele dienstregeling `UNVERIFIED`; `GTFS_READY=no`.
