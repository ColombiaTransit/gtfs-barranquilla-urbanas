# SIU–KMZ: beoordeling haltevolgorde (run 41992183773)

Bron: GitHub Actions artifact 13398588656, `focused_review_candidates.csv`. 33 SIU-itineraries versus 93 KMZ-geometrieën; 9 gerichte reviews, 18 kandidaten. Afstandsdrempel 50 m. De cijfers hieronder gelden voor de geselecteerde kandidaten, niet voor alle routevarianten.

| SIU-route | KMZ-kandidaten | Dekking (%) | Richting(en) | Ringwraps | Volgordefouten | Beoordeling |
|---|---|---:|---|---:|---:|---|
| CIRCUNVALAR VIA 40 | PT4-4104 / PT5-4105 | 99,24 | forward / reverse | 1 | 0 | Sterke operationele geometrie; KMZ-code dubbelzinnig |
| VIA 40 CIRCUNVALAR | PT4-4104 / PT5-4105 | 100 | reverse / forward | 1 | 0 | Sterke operationele geometrie; KMZ-code dubbelzinnig |
| RIOMAR AMARILLA | B13-4128 / B13-B-4189 | 100 | forward / forward | 0 | 2 | Volledige dekking, twee teruglopen; variant onbeslist |
| JUAN MINA | PT1-4101 / PT2-4102 | 100 | forward / forward | 0 | 1 | Volledige dekking, één buitensporige sprong; variant onbeslist |
| CIRCULAR | C18-4141 / C9-4140 | 86,84 | reverse / reverse | 0 | 1 | Onvolledige dekking; variant onbeslist |
| MIRAMAR ALAMEDA DEL RIO | A16-4161 A / B | 86,54 | forward / forward | 1 | 3 | Onvolledige dekking, één terugloop en twee grote sprongen |
| LOS ROBLES CALLE 72 | C4-4135 | 84 | forward | 1 | 4 | Onvolledige dekking, twee teruglopen en twee grote sprongen |
| VILLA SAN PABLO | PT1-4101 / PT2-4102 | 81,56 | forward / forward | 0 | 3 | Onvolledige dekking, één terugloop en twee grote sprongen |
| LAS GAVIOTAS CALLE 76 | A16-4161 A / B | 66,22 | forward / forward | 0 | 0 | Slechts gedeeltelijke route passend; variant onbeslist |

## Besluiten
1. De twee VIA 40-richtingen zijn geografisch en qua volgorde bruikbaar als operationele geometriekandidaten. **Geen unieke toewijzing van PT4 versus PT5** uit deze gegevens alleen; de omgekeerde geometrie levert dezelfde score.
2. Voor RIOMAR AMARILLA en JUAN MINA blijft controle van de concrete probleemovergangen nodig, ondanks 100% dekking.
3. De overige vijf routes vereisen analyse van ontbrekende trajecten of haltepassages. Nul volgordefouten bij LAS GAVIOTAS bewijst geen volledige route.
4. De SIU-haltecoördinaten en volgorde blijven brongegevens; niet automatisch verplaatsen of overschrijven. Bestaande vastgestelde mappings niet vervangen.
5. Geen juridische bevestiging vereist voor operationele matching; dit rapport claimt geen juridische routecertificering.

**Status:** beoordeling voltooid; definitieve unieke KMZ-variantkoppelingen voor deze negen routes niet automatisch goedgekeurd. Bron: https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41992183773/artifacts/13398588656
