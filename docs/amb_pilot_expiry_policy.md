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
