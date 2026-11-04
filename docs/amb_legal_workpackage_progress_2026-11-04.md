# Werkpakket juridische afronding — voortgang 2026-11-04

## Uitgevoerd in deze ronde
1. Officiële AMB-resolutiepagina's voor COOTRANTICO en COOLITORAL opnieuw gecontroleerd. De pagina's tonen respectievelijk 462-2025 en 210-2026/256-2026 in de actuele online index.
2. Vastgesteld dat de webindex niet de integrale dispositieve artikelen toont; de webindex mag daarom niet als bewijs van exacte wijziging, pilotverlenging of ingangsdatum worden gebruikt.
3. De algemene TPC-pagina vermeldt óók resolutie 448-2025 als 'Plan Piloto'. **Niet aan een route of operator koppelen zonder de PDF en artikelen te controleren**; de eerdere niet-geverifieerde ALL_OPERATORS-koppeling blijft ongeldig.
4. Het juridische statusregister en de fail-closed auditworkflow zijn de basis voor verdere verificatie.

## Directe PDF-artikelwerkvoorraad
| Prioriteit | Besluit | Te vergelijken met | Te bewijzen |
|---|---|---|---|
| P1 | COOTRANTICO 462-2025 | 025-2011, 331-2010 | B20/B20-B varianten, exacte wijzigingsartikelen, ingangsvoorwaarden |
| P1 | COOLITORAL 210-2026 | 192-2025 | PT2/PT3 A/B, routegeometrie, frequenties, ingangsdatum |
| P1 | COOLITORAL 256-2026 | 192-2025 | PT4/PT5 pilot, einddatum, mogelijke verlenging |
| P1 | SOBUSA 082-2026 | 466-2025 | B18 A/B en gedeelde corridor versus variantintervallen |
| P2 | EMBUSA 231-2025 | 010-2026 | B9 vervangen artikelen en frequenties |
| P2 | COOTRAB 358-2024 | 378-2023, COOLITORAL 192-2025 | C5-4135/4136 conflict, gezamenlijke A1 |
| P2 | COOCHOFAL 242-2025 | 387-2018, eventuele rectificatie | A15-4129/4159, C2-B-4187/4188 |
| P2 | LA CAROLINA 067-2011, 199-2019 | 173-2010, 204-2012 | A16 A/B en latere toepasselijkheid |
| P3 | TRASALIANCO 408-2013, 411-2010 | 267/268-2010 | D17/D18 precieze geometrie |
| P3 | TRANSMECAR latere besluiten | 324-2010 | C17 actuele juridische basis |

## Harde publicatievoorwaarden
Een route krijgt geen 'juridisch afgerond' zolang niet zijn vastgelegd: originele PDF + paginanummer, dispositief artikel, expliciet effect op eerdere besluiten, datum en voorwaarden van inwerkingtreding, eventuele latere besluiten en A/B-toepassing. Juridische vergunning ≠ actuele rituitvoering.

## Status
**Werkpakket gestart; PDF-artikelcontrole van bovenstaande nog niet voltooid.** Deze notitie claimt geen toekomstige autonome uitvoering of voltooide inspectie. Geen GTFS release.

## Aanvullende controle officiële AMB-routecatalogus (4 november 2026)
De actuele AMB-TPC-catalogus is opnieuw gelezen: https://www.ambq.gov.co/transporte/transporte-publico-colectivo/ . De gepubliceerde lijst bevat:
- **COOCHOFAL C2-B-4187 én COOASOATLAN C20-B-4187**: hetzelfde numerieke suffix **4187** voor twee verschillende operators en verschillende routecodes. Dit is een **route-ID-collision-risico** als software alleen het suffix als GTFS route_id gebruikt. Behoud daarom altijd de volledige code en een stabiele operator-/agency-namespace. Dit is geen bewijs dat de twee routes juridisch identiek zijn.
- **COOTRAB C5-4135** in de catalogus versus **C5-4136** in het historische besluitregister. Conflict blijft open en moet met origineel wijzigingsartikel worden opgelost; geen stilzwijgende correctie.
- **COOTRANTICO B20-4180 én B20-B-4191** staan afzonderlijk gepubliceerd; niet samenvoegen zonder identieke variantgeometrie.
- **LA CAROLINA A16-4161 A/B**, **SOBUSA B18/C12/C16 A/B**, en **COOLITORAL A1-4106 A/B** zijn afzonderlijk gepubliceerd; de bronfrequenties blijven aan het juiste variantniveau gekoppeld.
- De COOTRANTICO-index https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrantico/ noemt 462-2025. De COOLITORAL-index https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/ noemt 210-2026 en 256-2026. **Indexvermelding is geen artikelverificatie**.

### Veiligheidsregel voor GTFS-identiteiten
Maak nooit `route_id` op basis van alleen het numerieke suffix (zoals `4187`). Gebruik de volledige routecode plus operator-/composite-agency-identiteit indien nodig. Een numerieke suffix-collision betekent niet dat de vergunningen dezelfde route betreffen.

### Voortgang
De AMB-route-identiteitscontrole is uitgevoerd en bovenstaande bronconflicten zijn aangetroffen. **De volledige PDF-artikelen van 462-2025, 210-2026 en 256-2026 zijn nog niet integraal beoordeeld**; geen statuswijziging naar juridisch afgerond.
