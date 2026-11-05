# SIU zelfstandige haltequery — lokaal JavaScript-onderzoek afgesloten (2026-11-05)

## Vraag
Kan de publieke SIU GraphQL-client een zelfstandig halteregister ophalen, inclusief haltes zonder route?

## Onderzocht
Zes unieke, lokaal aanwezige JavaScript-bundles (zeven bestanden, waarvan twee identieke kopieën van chunk 37), samen circa 2,75 MB:
- `main.3437e7aa.chunk.js`
- `2.983e35a1.chunk.js`
- `7.fec28c5e.chunk.js`
- `11.9e070ff4.chunk.js`
- `32.17425079.chunk.js`
- `37.4ac577f1.chunk.js`

Lokale statische zoekactie naar benoemde GraphQL-query's, mutations, subscriptions en stop-/paradero-/station-gerelateerde tokens. Geen API-calls uitgevoerd.

## Aangetroffen GraphQL-operaties
- `ServiceMngCompressedItineraryListing($organizationId:String)`: retourneert itineraries met hun geordende `stops`.
- `OrganizationMngCompany`
- `OrganizationMngOrganizationListing`
- `OrganizationMngOrganizationWithoutAuthListing`
- Subscription `onServiceMngPisScheduleModified`.

Er is **geen zelfstandige Stops/StopListing/StopDetails/Paraderos-query** aangetroffen in de onderzochte lokale bestanden. UI-variabelen met 'stop' zijn geen bewijs voor een halte-API.

## Besluit
**Afsluiten als: niet aangetoond in beschikbare lokale JavaScript.** Er wordt geen afzonderlijke GraphQL-halte-extractor gebouwd op basis van een onbevestigde operatie. De huidige bevestigde bron blijft de routegebonden `ServiceMngCompressedItineraryListing`: elke daarin geëxtraheerde haltepassage hoort bij een itinerary en heeft een volgorde.

Dit is **geen bewijs dat SIU geen haltes zonder route opslaat** en evenmin dat geen andere (niet lokaal aanwezige of later geladen) bundle zo'n query bevat. Heropen dit onderzoek uitsluitend bij een concrete nieuwe bron of geobserveerde zelfstandige halteoperatie; niet op basis van speculatie. Geen juridische onderzoeksdossiers heropenen.
