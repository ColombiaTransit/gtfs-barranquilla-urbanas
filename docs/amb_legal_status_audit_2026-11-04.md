# Juridische statuscontrole — 4 november 2026

Deze status is gebaseerd op eerdere originele AMB-PDF-controles en een nieuwe vergelijking met officiële AMB-publicaties. Het woord 'afgerond' is uitsluitend toegestaan voor een specifiek bewezen deelaspect. **Geen enkele keten is volledig juridisch afgesloten** zonder bewijs van alle relevante latere wijzigingen en toepasselijke inwerkingtreding.

## Nieuwe primaire bronnen
- [AMB TPC routeoverzicht](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/) met gepubliceerde routecodes.
- [AMB COOTRANTICO-resoluties](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrantico/): 462-2025 en 025-2011 staan in het officiële overzicht.
- [AMB COOLITORAL-resoluties](https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/): 192-2025, 199-2025, 210-2026 en 256-2026 vermeld.
- [AMB 378-2023 COOTRAB](https://www.ambq.gov.co/wp-content/uploads/2024/02/RESOLUCION-METROPOLITANA-No.-378-23-COOTRAB.pdf): C5-4136 en C6-4137.
- [AMB 146-2020](https://www.ambq.gov.co/wp-content/uploads/2020/07/Resoluci%C3%B3n-Metropolitana-No.-146-20.pdf): COOTRAB C5-4136, C6-4137; COOTRANTICO B20-4180, B20-B-4191.
- [AMB tijdelijke omleidingscirculaire 039-2025](https://www.ambq.gov.co/wp-content/uploads/2025/08/Circular-Externa-No.-039-2025-CIERRE-PARCIAL-DE-LA-CARRERA-58-1.pdf): noemt COOTRAB C5-4135, naast C6-4137 en meerdere andere routes. **Tijdelijke omleiding is geen permanente herstructurering.**
- [AMB COOTRAB KMZ archief](https://www.test2.ambq.gov.co/rutas-de-buses/COOTRAB/): C5-4136.kmz en C6-4137.kmz (historisch, gedateerd 2022).

## Resultaat
- Het conflict COOTRAB C5-4135/C5-4136 is **bevestigd als conflict tussen AMB-publicaties**. 378-2023 en de 2020-besluiten ondersteunen C5-4136; de 2025-omleidingscirculaire en huidige TPC-lijst vermelden C5-4135. Niet automatisch één code als definitief juridisch gecorrigeerd verklaren.
- De aanwezigheid van 462-2025 (COOTRANTICO) en 210-/256-2026 (COOLITORAL) in de officiële index is geverifieerd, **maar hun volledige dispositieve artikelen zijn in deze ronde niet integraal opnieuw gelezen**.
- Het onderscheid tussen tijdelijke omleiding, juridische routewijziging en actuele uitvoering is expliciet gemaakt.
- Routegebonden detailstatussen zijn machineleesbaar vastgelegd in `sources/amb/legal_validity_ocr_review/gtfs_legal_status_2026-11-04.csv`.
- Voertuigcapaciteiten en vlootverdeling zijn niet meegenomen als GTFS-criteria.

## Nog open
1. Integraal vergelijken van de latere dispositieve artikelen 462-2025, 210-2026, 256-2026, 082-2026 en 010-2026 met hun voorgangers.
2. Verifiëren van eventuele nog nieuwere AMB-rectificaties, activeringsmeldingen en pilotverlengingen.
3. Routecodeconflicten C5, A15 en C2-B oplossen met primair besluitbewijs.
4. Geldigheidsperiode per variant vaststellen; historische frequenties niet als actuele service presenteren.
5. Dienstkalender en feitelijke ritten los van juridische autorisatie valideren.

**Eindstatus:** juridische bronnen en deelconclusies geactualiseerd; `legal_chain_complete=false`, `current_operation_verified=false`, `gtfs_release_approved=false`.

## Vastgelegde routecodebesluiten — niet opnieuw als openstaand opvoeren

- **COOCHOFAL A15:** GTFS-code **A15-4159** aanhouden; **A15-4129** uitsluitend als afwijkende historische bronvermelding/alias registreren. Eerder onderzocht met Resolución 242-2025 en Circular 010-2025.
- **COOCHOFAL C2-B:** GTFS-code **C2-B-4188** aanhouden; **C2-B-4187** uitsluitend als afwijkende bronvermelding/alias registreren. De eerdere keuze 4187 is na aanvullend officieel bewijs vervangen door 4188.
- Geen extra routes, trips of frequenties voor deze aliassen genereren. Een verschil in een oudere resolutietabel is **geen nieuwe routecodeblokkade**. De juridische geldigheid, variantreikwijdte en latere werking van 242-2025 blijven afzonderlijke onderzoekspunten.
- Bij latere verwerking van `verified_462_242_route_headways_2026-11-04.csv` moet `C2-B-4187` expliciet naar canonieke `C2-B-4188` worden gekoppeld, met behoud van de originele broncode.

## Primaire PDF-verificatie 242-2025 en 462-2025 (4 november 2026)

Bronnen: [242-2025](https://www.ambq.gov.co/wp-content/uploads/2026/03/RES-M-242-2025-2.pdf) en [462-2025](https://www.ambq.gov.co/wp-content/uploads/2025/12/RESOLUCION-METROPOLITANA-No-462-2025-COOTRANTICO.pdf), beide 21 pagina's.

- **242-2025**: ondertekend op **4 juli 2025** (p.21). Titel en artikel 1 betreffen wijziging van de exploitatievergunning van acht COOCHOFAL-routes; artikel 2 schrijft persoonlijke kennisgeving voor en artikel 3 biedt bezwaar binnen tien dagen na kennisgeving (p.21). De originele p.20 noemt zowel A15-4129/C2-B-4187 in lopende tekst als A15-4159/C2-B-4188 in de capaciteitstabel. Eerder vastgelegde canonieke GTFS-codes **A15-4159** en **C2-B-4188** blijven staan.
- **462-2025**: ondertekend op **27 november 2025** (p.21). Titel en artikel 1 betreffen wijziging van de exploitatievergunning van acht COOTRANTICO-routes; artikel 2 schrijft persoonlijke kennisgeving voor en artikel 3 biedt bezwaar binnen tien dagen na kennisgeving (p.21). P.20 noemt de acht routes afzonderlijk in de capaciteitstabel.
- Beide besluiten bevatten op de gecontroleerde slotpagina's **geen vastgestelde datum van kennisgeving of bewijs van onherroepelijkheid**. Ondertekening is geen bewijs van actuele exploitatie in 2026. Er is geen vrijgave van staging-blokkades op grond van alleen deze controles.
- Nog afzonderlijk te controleren: precieze wijzigingen ten opzichte van eerdere vergunningen, latere besluiten/rectificaties, datum van kennisgeving en bezwaarafhandeling. De 00:00–24:00-formulering in de routetabellen is vraagafhankelijk en bewijst geen feitelijke 24-uursdienst.
