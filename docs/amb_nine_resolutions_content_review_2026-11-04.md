# AMB negen besluiten — inhoudelijke eerste controle (2026-11-04)

## Status en methode
Bron: `sources/amb/legal_validity_ocr_review/article_verification/operative_article_candidates.csv` (85 OCR-kandidaten, 9 PDF's met overeenkomende SHA-256). Dit is een **inhoudelijke controle van de beschikbare OCR-passages**, niet de voltooide controle van alle 121 originele paginabeelden. Geen actuele dienst of GTFS-release wordt hiermee goedgekeurd.

| Besluit | Inhoudelijk aangetroffen | Controle / resterend |
|---|---|---|
| TRASALIANCO 267-2010 | p6 art. 1 herstructureert route MANUELA BELTRÁN; p9 art. 2 vervangt oudere routevergunningen. | Exacte D18-codering, frequentietabel, voorwaarden en 408-2013 op beeld vergelijken. |
| TRASALIANCO 411-2010 | p7 art. 1 bevestigt 268-2010 gedeeltelijk; art. 2 corrigeert D17/PASADENA-route, met Transmetro-startvoorwaarde. | Corrigeerde geometrie naast 268-2010 en latere besluiten leggen. |
| LA CAROLINA 173-2010 | p6 art. 1 herstructureert route TERMINAL DE TRANSPORTES–ZONA HOTELERA–CENTRO–NORTE. | Dienstregeling/routevoorwaarden vergelijken met 067-2011. |
| LA CAROLINA 204-2012 | p12 art. 1 bevestigt Circular AMB-STT 001 van 18 mei 2012. | **Niet** zonder meer behandelen als zelfstandige A16-frequentiewijziging; volledige motivering en art. 2 controleren. |
| LA CAROLINA 199-2019 | p9 art. 1 herstructureert expliciet A16-4161; p10 OCR bevat '5 Minutos', 49–59 voertuigen en 52,9 km. | OCR-tabel/uurtype en kaart op beeld verifiëren; 5 minuten niet zonder context als huidige frequentie publiceren. Nummer op omslag niet automatisch herkend. |
| COOLITORAL 137-2011 | OCR-kandidaten op p7–8. | Volledige operationele tabel en eventuele A1-vergunning visueel controleren. |
| COOLITORAL 192-2025 | p34: capaciteiten per route, inclusief A1 23–28, PT2 36–44, PT3 37–44, PT4/PT5 27–32; verplicht SIBUS RCC. | Tabellen en latere besluiten 199-2025, 210-2026 en 256-2026 vergelijken. |
| COOTRAB 358-2024 | p10 noemt gedeelde exploitatie A1-4106 met COOLITORAL en COOTRAB; OCR-tabel gezamenlijke capaciteit min. 44, max. 56, elk 22–28. | **Potentieel verschil** met COOLITORAL 192-2025 (A1 23–28): definities, latere wijziging en scan van tabel controleren; geen dubbele GTFS-frequentie. Nummer op omslag niet automatisch herkend. |
| COOTRANTICO 025-2011 | p16 art. 3 noemt het enige titelbesluit voor de route en intrekking eerdere routevergunningen; p17 art. 6 koppelt operationele ingang aan AMB-bericht/Transmetro-start. | Betreft alleen de hier beschreven route; toets tegen 331-2010 en latere 462-2025. Activatiebericht niet aangetoond. |

## Verificatieprotocol voor afronding
1. Open per besluit originele PDF en controleer besluitnummer, datum, ondertekening, routecode, artikel 1 t/m slotartikel en alle relevante tabellen/kaartbijlagen op paginabeeld.
2. Leg per wijziging vast: oud artikel, nieuw artikel, routevariant, geometrie, haltevolgorde, piek/dal-interval, voorwaarden, ingangsdatum en expliciete intrekkingen.
3. Zoek vervolg-/wijzigingsbesluiten en controleer de juridische keten. Een nieuwe resolutie is geen bewijs van feitelijke huidige exploitatie.
4. Leg gedeelde A1-exploitatie als één routevariant vast met afzonderlijke operator-attributies, zodra artikeltekst en de onderlinge capaciteitstabel visueel overeenkomen.
5. Houd `source_identity_verified`, `operative_articles_verified`, `current_operation_verified` en `gtfs_release_approved` op `no` tot de betreffende controle is afgerond.

**Open:** 121 paginabeelden en ontbrekende vervolgdocumenten zijn niet in deze notitie volledig visueel geverifieerd.
