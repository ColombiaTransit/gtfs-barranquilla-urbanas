# SIU/SIBUS — twee MHT-browseropnames van de route- en halteschermen

**Onderzoek:** 3 november 2026. **Gebruikersbestanden:** `SIU.mht` (vastgelegd 06:57:11 GMT) en `SIU (1).mht` (06:57:36 GMT). Beide zijn Chromium-MHTML-opnamen van het openbare portaal `https://siu.ambq.gov.co/siu/schedule-mng/schedules`.

**Geen ruwe MHT-bestanden in GitHub opgeslagen.** De MHTML-opnamen bevatten website-HTML, CSS en afbeeldingen, maar géén bruikbare JavaScriptbundels, XHR-/fetch-response-bodies of complete opgevraagde API-antwoorden. Daarom publiceren we alleen hieronder geëxtraheerde route-/haltegegevens en technische analyse, niet sessie-informatie.

## 1. Eerste scherm: routeoverzicht

De eerste opname toont **7 zichtbare routekaarten**, waaronder een kennelijke testregel `1234 — PRUEBAS AMB`. De zes zichtbare reguliere routes zijn:

| SIU-weergavenaam | Bedrijf |
|---|---|
| ALAMEDA DEL RIO | FLOTA ANGULO |
| CALLE 17 | LA CAROLINA |
| CALLE 30 | LA CAROLINA |
| CALLE 72 VIA 40 | COOLITORAL |
| CENTRO CIRCUNVALAR | TRANSURBAR |
| CENTRO PUEBLO SAN PABLO | COOLITORAL |

De HTML gebruikt een virtueel gescrolde lijst met rijen van 130 px en een binnencontainer van **4.680 px**. Dit is **consistent met ongeveer 36 route-items** (4.680 / 130), maar **geen bewezen volledig aantal of volledige route-inventaris**; slechts zeven items staan in het MHT-DOM.

**[Routekaart-CSV met zeven weergaven en interne UUID's](../sources/siu/siu_visible_route_list_2026-11-03.csv).**

De SIU-route `ALAMEDA DEL RIO` van FLOTA ÁNGULO heeft route-UUID:

`6948fedb-74b6-4a1f-9c33-dcac379a736b`

Deze UUID komt **exact overeen** met de route-ID in de tweede pagina, zodat we de pagina's aantoonbaar kunnen koppelen. FLOTA ÁNGULO heeft in de toepasselijke vergunning route **A7-4112** via Alameda del Río, maar **de SIU-pagina vermeldt geen GTFS/AMB-routecode**. De koppeling `SIU ALAMEDA DEL RIO → A7-4112` blijft een *onderbouwde kandidaat*, niet een expliciete codekoppeling.

## 2. Tweede scherm: stoplijst voor ALAMEDA DEL RIO

De tweede opname bevat **10 daadwerkelijk zichtbare haltekaarten** onder de kop `ALAMEDA DEL RIO`. Elke haltekaart bevat een unieke samengestelde HTML-ID met de vorm:

`js-stops-wrapper-{siu_route_uuid}/{siu_stop_uuid}`

De tien aparte stop-UUID's en de namen zijn vastgelegd in het [SIU-stoplijst-CSV](../sources/siu/siu_visible_flota_angulo_stops_2026-11-03.csv).

| Geschatte positie in volledige lijst | Haltenaam (letterlijk uit SIU) |
|---:|---|
| **75** | ARA CALLE 109 (CARRERA 38 - OE) |
| **76** | CALLE 108 CON CARRERA 36 (NS) |
| **77** | CALLE 107 CON CARRERA 36 (NS) |
| **78** | CONJUNTO ALTOS DE LA COLINA (CARRERA 35B) |
| **79** | CALLE 100 CON CARRERA 37A (SN) |
| **80** | CALLE 84B CON CARRERA 39 (SN) |
| **81** | CALLE 84B CON CARRERA 40A (SN) |
| **82** | CALLE 84B CON CARRERA 41B (SN) |
| **83** | CONJUNTO ALTO DE CAMPO ALEGRE (CALLE 84B) |
| **84** | CALLE 84 CON CARRERA 42A3 (SN) |

De positie is **afgeleid uit de lijst-offsets**: eerste zichtbare rij `top=7844px`, vervolgens telkens 106px, dus `7844/106+1=75`. Deze positie is géén officieel stopvolgnummer in de response en hangt af van de actuele SIU-lijstsortering.

De virtuele lijst heeft een binnencontainer van **11.670 px** en rijen van 106px. Dit lijkt op ruwweg **110 stops** (`11670/106 ≈ 110`), maar het volledige aantal is niet bewezen; de pagina bewaart slechts **10 zichtbare** elementen. Het is daarom onjuist om tien stops als het hele A7-traject te gebruiken.

**Er zijn in de MHTML-pagina's géén `lat/lon`-waarden of fysieke GPS-coördinaten van de haltes gevonden**, noch officiële busvertrek- of aankomsttijden. De 'room'-icoontjes zijn interactieve knoppen zonder in het archief ingesloten coördinaten; de route- en stop-UUID's kunnen ons wel helpen om de gekoppelde gegevens via SIU te achterhalen.

## 3. Technische betekenis

Het SIU-portaal gebruikt een **React-webapplicatie** met een virtueel gescrolde lijst. Een vanuit Chrome/Edge opgeslagen `MHTML` bevat de DOM-elementen van dat moment, niet automatisch alle overige lijstitems en niet de achterliggende API-responses. Dit is wél concreet bewijs dat SIU **routegebonden stopnamen en stop-ID's** toont, wat eerder nog onbekend was.

Voor een volledige GTFS-extractie ontbreken op dit moment:
- een volledige geordende SIU-stoplijst per route;
- GPS-coördinaten per SIU-stop-UUID;
- expliciete match tussen de SIU-weergavenaam/-UUID en de nieuwste AMB-routecode;
- de precieze A/B-richting of itinerary per volledige stopvolgorde.

**Beschikbare analysetools:**
- [Lokale MHT-HTML-extractor](../scripts/extract_siu_mht_snapshot.py) reproduceert CSV's uit browseropnamen, zonder netwerk of inlogcookies.
- [Passive scan public SIU JS assets](../.github/workflows/research-siu-public-assets.yml) zoekt **alleen in openbaar beschikbare sitebestanden** naar route- en stopservicepaden. Deze inspectie doet geen geauthenticeerde requests, en de gevonden strings zijn tot verificatie geen bewezen API.
- Beter nog: haal in het browser-Network-tabblad na het klikken op een route het **Response**-JSON van de route-/stoprequest op; daarbij nooit `Authorization`, `Cookie`, access/refresh tokens of een volledige HAR met geheime headers publiceren.

## 4. Aanpak voor onze GTFS

De nieuwe SIU-stopnamen en UUID's zijn **veel sterker bewijs voor echte routegebonden TPC-haltevolgorde** dan de ongeclassificeerde OSM-punten. Gebruik ze daarom als eerste keuze voor een toekomstig bronregister. Daarna GPS-coördinaten aan dezelfde interne stop-ID koppelen en de stopvolgorde tegen de actuele vergunning en GIS-route beoordelen.

Nog **geen `gtfs/stops.txt` of `stop_times.txt` genereren** uit deze twee onvolledige snapshots, en de interne SIU-UUID niet als bevestigde AMB-routecode presenteren.
