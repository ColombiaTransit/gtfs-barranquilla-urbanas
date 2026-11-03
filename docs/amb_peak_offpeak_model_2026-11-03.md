# AMB TPC — aangenomen spits- en daluren voor de statische GTFS

**Vastgesteld voor ColombiaTransit op 3 november 2026.** **Model-ID:** `AMB_WEEKDAY_0709_1720_V1`.

De gebruikerskeuze is om de hieronder vermelde **uniforme modeltijdvakken** toe te passen zolang een specifieke AMB-resolutie geen expliciete, afwijkende geldige tijdvakken vastlegt. Het zijn **projectaannames, geen officieel door AMB vastgestelde piek- en dalgrenzen**.

| Dag | Tijd (lokale tijd Barranquilla, `America/Bogota`, UTC-5) | Intervalbron |
|---|---|---|
| Maandag t/m vrijdag | **07:00–09:00** | `hora pico` uit toepasselijke resolutie |
| Maandag t/m vrijdag | **09:00–17:00** | `hora valle` uit toepasselijke resolutie |
| Maandag t/m vrijdag | **17:00–20:00** | `hora pico` uit toepasselijke resolutie |
| Maandag t/m vrijdag | **Vóór 07:00 en ná 20:00**, uitsluitend voor zover de route rijdt | `hora valle` uit toepasselijke resolutie |
| Zaterdag, zondag, Colombiaanse feestdag | **Nog niet bepaald** | aparte kalender-/dienstvensterbeslissing nodig |

## Definitief projectbesluit 3 november 2026 — historische vertrekuren als voorlopig dienstvenster

De gebruiker heeft **expliciet gekozen om de eerste en laatste vertrekken op de AMB-routekaarten van juli 2020 voorlopig te gebruiken voor de huidige model-GTFS**. Dit is een **reversibele projectaanname**. Het betekent niet dat AMB deze tijden als actueel 2026 heeft bevestigd; de nieuwste geldige AMB-routebesluiten blijven de leidende bron voor de **spits- en dalfrequenties**.

**Prioriteitsregel bij nieuwe informatie:** een nieuwere, duidelijke officiële bron voor een routevenster vervangt alleen de modelstart/eindtijd van die specifieke route, met behoud van de oude waarde, bronlink, geldig jaar en vervangingsdatum als historie. Wijzig de al geverifieerde vergunningsfrequentie niet tenzij een nieuwere toepasselijke resolutie dat interval verandert. Een specifieke spits-/dalindeling in een geldige resolutie krijgt voorrang op het uniforme model.

**Stand van de modeldata:**
- [83 unieke routevensters uit 24 kaarten](../sources/amb/amb_dispatch_window_assumptions_2026-11-03.csv), **78** voorlopig aanvaard; vijf hebben een ongeldig/onbruikbaar afgedrukt laatste vertrek en blijven open.
- [44 route- en variantkandidaten gekoppeld aan het voorlopige model](../sources/amb/gtfs_route_service_windows_assumed_2026-11-03.csv): **38** met bruikbaar eerste én laatste vertrek, waarvan **35** met volledig spits-/dalinterval uit de resoluties.
- [138 voorgestelde werkdagfrequentieperioden](../sources/amb/gtfs_weekday_frequency_period_candidates_2026-11-03.csv) berekend door het eerste/laatste vertrek te kruisen met **07:00–09:00 en 17:00–20:00 spits**, daarbuiten dal. **15 van de 138** periodevoorstellen hebben een gecombineerd corridorgegeven, niet het interval van een enkele itinerary, dus die zijn niet direct naar een patroonspecifieke `frequencies.txt` te exporteren.

**Correctie vijf bronfouten:** voor TRASALFA **D14/D15** en COOCHOFAL **C3/C9/C18** kan geen verantwoord eindtijdmodel uit de oorspronkelijke kaart worden overgenomen, omdat de als laatste `PM` gelabelde kolom een `AM`-waarde heeft. We houden hun eindtijd leeg tot een andere bron of een later **afzonderlijk expliciet** gekozen invulregel beschikbaar is. Een ontbrekende B2-B-regel blijft apart open.

**Eindgrens GTFS:** de AMB-kolom `último despacho` bevat het laatste **vertrekmoment**. `frequencies.txt.end_time` is in GTFS een **exclusieve bovengrens**: de laatste modeldeparture mag niet zonder controle als exclusieve `end_time` worden overgenomen en dus verloren gaan. In onze berekende kandidaatbestanden heten de tijden daarom bewust `period_*_boundary_local` in plaats van definitieve GTFS-`start_time/end_time`. Tijdens het genereren van concrete ritten stemmen we de vertreksfase af en plaatsen we indien nodig het laatste vertrek expliciet.

**Nog niet vastgesteld:** zaterdag/zondag/feestdagen, stopvolgorde, geometrie, trip-templates, en waar relevant het verschil tussen A/B itinerarios of de actuele geldigheid van pilotbesluiten. De voorlopig aangenomen vensters gelden in dit eerste model **maandag–vrijdag** (`America/Bogota`).

## Externe historische bron: eerste/laatste vertrek (2020)

De [AMB-routekaarten van 17 juli 2020](https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/) bevatten per route de eerste en laatste vertrektijden. We hebben **24 kaarten en 84 routevermeldingen** gecontroleerd, waarvan **83 unieke bedrijf-routes**. [Geverifieerde CSV](../sources/amb/amb_2020_first_last_dispatch_times_verified.csv) en [match met 44 routekandidaten](../sources/amb/amb_2020_vs_resolution_route_dispatch_matching.csv).

De eerste/laatste vertrekuren uit **2020 zijn op 3 november 2026 uitdrukkelijk geaccepteerd als voorlopige huidige GTFS-modeldiensturen**; de bron blijft als historisch geregistreerd en is niet opnieuw officieel bevestigd. Een AMB-publicatie kan op verschillende momenten technisch zijn bijgewerkt zonder dat de routeschema's uit 2020 zijn vervangen.

De kaart met COOCHOFAL C3, C9 en C18 drukt foutief `5:30 AM` af in de `último despacho (PM)`-kolom. Bij TRASALFA D14 en D15 is dat `6:00 AM`. Laatste vertrektijden voor deze vijf routes zijn in de data **onbekend**; niet corrigeren door AM naar PM om te zetten zonder bewijs.

## Toepassingsregels

1. **De AMB-resolutie is leidend voor de frequentie** (bijv. `6 min / 9 min` betekent 360 seconden tijdens `peak` en 540 seconden tijdens `offpeak`). Geen realtime-feed of ritwaarneming vereist.
2. **Dit model geeft uitsluitend piek-/dalgrenzen, géén eerste of laatste vertrek.** Een buslijn zonder bevestigd of later bewust gekozen dienstvenster wordt niet automatisch als 24-uursdienst in GTFS gepubliceerd.
3. Bouw `frequencies.txt` pas nadat per route/richting/itinerary de service-`start_time` en `end_time` vastgesteld of expliciet als afzonderlijke *modelaanname* zijn vastgelegd. Bereken voor ieder interval het snijvlak tussen het modeltijdvak en het route-dienstvenster. **Lege snijvlakken genereren geen GTFS-rijen.**
4. **Bij routegebonden officiële spits-/daltijden gaat de bron boven dit model.** Leg de uitzondering en resolutiepagina vast.
5. **Gedeelde corridors:** gecombineerde frequenties niet toepassen op één afzonderlijke A/B-variant; kies voor elk `trip_id` de passende itinerary-specifieke intervaltabel.
6. **Kalender:** `America/Bogota` is de tijdzone. `Monday–Friday` is voorlopig als werkdagtype geconfigureerd; Colombiaanse feestdagen en weekendbediening vereisen nog een aparte regel. `calendar_dates.txt` kan daarvoor nodig zijn.
7. **Voertuigcapaciteit blijft buiten scope**.

## Voorbeeld (uitsluitend om de methode te laten zien)

Een routevergunning noemt **4 minuten spits** en **6 minuten dal**. Stel dat we voor die route apart een geldig dienstvenster van **06:00–21:00** hebben onderbouwd of bewust als diensturen-aanname hebben vastgelegd. Dan ontstaan maandag t/m vrijdag:

| Begin | Einde | `headway_secs` |
|---|---|---:|
| 06:00 | 07:00 | 360 |
| 07:00 | 09:00 | 240 |
| 09:00 | 17:00 | 360 |
| 17:00 | 20:00 | 240 |
| 20:00 | 21:00 | 360 |

**06:00–21:00 is alleen een rekenvoorbeeld, niet het dienstvenster van een concrete route.**

Machineleesbare tijdvakken: [`sources/amb/gtfs_peak_offpeak_period_model_2026-11-03.csv`](../sources/amb/gtfs_peak_offpeak_period_model_2026-11-03.csv). `00:00–07:00` en `20:00–24:00` in dat bestand **beschrijven uitsluitend categorieën van de klok**, geen daadwerkelijke exploitatie.
