# GTFS-beleid: tijdelijke AMB-pilots

**Beslisregel:** een pilot met expliciete einddatum of looptijd is uitsluitend geldig binnen die termijn. Na het verstrijken daarvan wordt de pilot in onze **GTFS-bronmodellering** als beëindigd behandeld, tenzij een aantoonbaar later officieel besluit de termijn verlengt of de maatregel permanent maakt.

- `pilot_start`: datum uit besluit, niet automatisch de publicatiedatum.
- `pilot_end_exclusive`: eerste datum buiten de vergunde looptijd; bereken op basis van de expliciete tekst, eventuele kalendermaanden en ingangsvoorwaarden.
- `extension_resolution`: uitsluitend invullen met verifieerbaar besluit en artikel.
- `pilot_status`: `scheduled`, `active`, `ended_no_extension_found`, `extended_verified`, `superseded` of `dates_unverified`.
- Geen verlenging gevonden is **geen bewijs dat feitelijke bussen niet meer rijden**. Het betekent alleen dat we de pilotregeling niet langer als juridische basis gebruiken.
- Als de pilot een oudere, nog geldige basisvergunning tijdelijk wijzigt, moet na afloop opnieuw die basisregeling en latere besluiten worden beoordeeld. Niet automatisch de route schrappen.
- Een nieuwe verlenging mag later met terugwerkende kracht in het register worden verwerkt zodra de bron is geverifieerd.

## COOLITORAL 256-2026 — PT4/PT5
Het bestaande dossier registreert een pilot van **zes maanden vanaf 22 juni 2026**. Voor de werkadministratie is de **geverifieerde eindgrens 22 december 2026 (exclusief)** volgens artikel 2 van het originele besluit 256-2026. Op **4 november 2026** is deze termijn nog niet verstreken. Status: `active_under_recorded_period`; feitelijke exploitatie en latere verlenging zijn niet bewezen. Als na afloop geen officieel verlengingsbesluit is aangetroffen: `ended_no_extension_found`; gebruik de tijdelijke PT4/PT5-parameters niet voor latere GTFS-datums.

Artikel 2 en de zesmaandentermijn zijn visueel gecontroleerd; kennisgeving, feitelijke activering en latere verlengingen blijven afzonderlijke open vragen.

## GTFS calendar-uitwerking en PT4/PT5 crosswalk (4 november 2026)

- Voor de pilot 256-2026: `calendar.txt.start_date=20260622`, `end_date=20261221` (**inclusief**). De weekdagen volgen het afzonderlijke AMB-weekdagmodel; deze datums alleen bewijzen geen zeven dagen per week. Gebruik `calendar_dates.txt` alleen voor aangetoonde uitzonderingen of verlenging, niet om de pilot stilzwijgend voort te zetten. Na 21 december de basisvergunning 192-2025 afzonderlijk beoordelen; niet automatisch de routes verwijderen.
- Bron: `sources/amb/details/coolitoral_256_2026_pilot_street_variants_verified.csv` (originele 256-2026 p.4 en p.6): PT4 A/B vertrekken juridisch vanaf Calle 17/Carrera 30; PT5 A/B vanaf Vía 40 No. 51-310.
- **PT4-B herkenningsstraten**: Carrera 44, Calle 10, Carrera 41B, Calle 8. **PT5-B**: Calle 8, Carrera 41B, Calle 10, Carrera 43. Alleen de combinatie met richting, volgorde en beginpunt kan een A/B-match ondersteunen; gedeelde straten alleen zijn niet onderscheidend.
- Publieke SIU-onderzoekstabel (`sources/siu/open_route_review/summary.md`): `CIRCUNVALAR VIA 40` (132 haltes) suggereert qua titel PT5 maar qua juridisch beginpunt PT4; `VIA 40 CIRCUNVALAR` (124 haltes) omgekeerd. **Geen van de vier A/B-koppelingen bevestigd.** Historische KMZ zonder expliciete variant bewijst dit evenmin.
- Vereiste vervolgcontrole: leg de geordende SIU-haltes/geometrie langs de vier juridische stratenreeksen; controleer de daadwerkelijke rijrichting, de twee dispatch-terminals en de exclusieve B-zijstraten. Koppel pas na overeenstemming op basisroute én variant; behoud tot dan de afzonderlijke `pilot_SIU_to_legal_AB_mapping_unresolved`-blokkade. De headways 9/14 minuten per variant zijn wel juridisch geverifieerd.
