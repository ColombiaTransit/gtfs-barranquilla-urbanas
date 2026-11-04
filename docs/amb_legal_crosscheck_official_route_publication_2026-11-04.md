# Juridische kruiscontrole AMB versus routepublicatie — 2026-11-04

## Uitgevoerde controle
De officiële AMB-pagina's voor TPC, COOTRANTICO, COOLITORAL en TRASALIANCO zijn naast het bestaande resolutieregister en de negen visueel gecontroleerde PDF's gelegd. **Een webindex of KMZ-bestandsnaam is bewijs van publicatie/route-identiteit, niet van rechtskracht, inwerkingtreding of actuele frequentie.**

Bronnen:
- https://www.ambq.gov.co/transporte/transporte-publico-colectivo/
- https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-cootrantico/
- https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-coolitoral/
- https://www.ambq.gov.co/transporte/transporte-publico-colectivo/resoluciones-trasalianco/
- https://www.ambq.gov.co/ruta-de-buses/COOTRANTICO/
- https://www.ambq.gov.co/ruta-de-buses/COOLITORAL/

## Bevindingen en besluiten
1. **COOTRANTICO B20**: officiële AMB-routepublicatie noemt zowel `B20-4180` als `B20-B-4191`; beide hebben eigen KMZ. De AMB-resolutielijst bevat 331-2010, 025-2011 en 462-2025. Het oude 025-2011 trekt eerdere vergunningen voor *zijn route* in, maar dat bewijst niet welke A/B-variant door 462-2025 is toegestaan. **B20-B niet wegfilteren; beide geometrieën afzonderlijk vergelijken.**
2. **COOLITORAL**: officiële resolutielijst bevestigt de aanwezigheid van 192-2025, 199-2025 (foutcorrectie), 210-2026 en 256-2026 (pilot). De officiële routekaartlijst heeft A1-4106 A/B, PT2, PT3, PT4, PT5 en C19-4178. **C19-4178 is de publicatiecode**. Pilots en wijzigingen niet stilzwijgend als permanente 192-2025-parameters beschouwen.
3. **COOCHOFAL**: AMB-routepublicatie geeft `A15-4159` en `C2-B-4187`, overeenkomstig de individuele 242-2025-routebladen. **Gebruik die codes als gepubliceerde route-identificaties**, met de tegenstrijdige codes in het besluit (A15-4129, C2-B-4188) expliciet geregistreerd. Dit is **geen juridisch bewijs** van een formele rectificatie.
4. **COOTRAB**: officiële AMB-routepublicatie vermeldt `C5-4135` terwijl het 358-2024-resolutieregister `C5-4136` noemt. **Nieuw, GTFS-relevant codeconflict.** Niet automatisch normaliseren; C5-4135 overlapt bovendien de gepubliceerde COOCHOFAL C4-4135. Onderzoek primaire artikelen en kaartbestanden.
5. **LA CAROLINA**: officiële AMB-routepublicatie heeft `A16-4161 A` en `A16-4161 B`. Resolutie 199-2019 geeft A16-4161 met 3,5/5 minuten maar bewijst niet zonder meer dat die frequentie per A/B-variant geldt. Splits de frequentie niet willekeurig.
6. **TRASALIANCO**: officiële resolutielijst toont 267-2010, 268-2010, 411-2010 en 408-2013, passend bij de bestaande D17/D18-ketens. D17-geometrie moet de gedeeltelijke correctie uit 411-2010 respecteren.
7. **SOBUSA**: officiële AMB-routepublicatie heeft B18 A/B, C12 A/B en C16 A/B; consistent met bestaande A/B-bronregistratie, maar bewijst geen actuele ritten of kloktijdvensters.
8. **EMBUSA**: officiële AMB-routepublicatie bevestigt `B9-4125`, in lijn met 010-2026; juridische vergelijking 231-2025 blijft open.
9. **TRANSMECAR**: officiële AMB-routepublicatie vermeldt `C17-4160`; een publicatie van de route bewijst niet dat het historische 324-2010-interval nog geldt.

## Juridische status
- `document_identity`: negen PDF's visueel/technisch gecontroleerd in eerder rapport.
- `article_effect`: alleen de expliciet geïnspecteerde artikelen als bevestigd.
- `supersession_complete`: **nee**, niet alle latere besluiten volledig gelezen.
- `effective_date_verified`: **nee** voor voorwaardelijk geactiveerde besluiten.
- `current_operation_verified`: **nee**.
- `gtfs_release_approved`: **nee**.

## Concrete open acties
- Lees primaire operationele artikelen van 462-2025, 210-2026, 256-2026 en 082-2026 volledig en vergelijk oude/nieuwe A/B-trajecten.
- Los COOTRAB C5 4135/4136 op met het originele artikel en officiële KMZ.
- Onderzoek COOCHOFAL codecorrecties zonder een rectificatie te verzinnen.
- Controleer LA CAROLINA A/B-frequenties per variant en eventuele latere besluiten.
- Leg per route een artikelbron en ingangsvoorwaarde vast; ga niet van indexpublicatie naar juridisch 'vigente' zonder artikelcontrole.
