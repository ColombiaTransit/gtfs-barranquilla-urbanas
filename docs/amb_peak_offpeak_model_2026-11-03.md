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

## Externe historische bron: eerste/laatste vertrek (2020)

De [AMB-routekaarten van 17 juli 2020](https://www.ambq.gov.co/continuan-las-rutas-y-frecuencias-del-transporte-publico-colectivo/) bevatten per route de eerste en laatste vertrektijden. We hebben **24 kaarten en 84 routevermeldingen** gecontroleerd, waarvan **83 unieke bedrijf-routes**. [Geverifieerde CSV](../sources/amb/amb_2020_first_last_dispatch_times_verified.csv) en [match met 44 routekandidaten](../sources/amb/amb_2020_vs_resolution_route_dispatch_matching.csv).

De eerste/laatste vertrekuren uit **2020 worden niet automatisch als huidige diensturen voor 2026 gebruikt**. Eerst afzonderlijk besluiten of deze als transparante modelaanname dienen of er recenter SIU/SIBUS-materiaal is. Een AMB-publicatie kan op verschillende momenten technisch zijn bijgewerkt zonder dat de routeschema's uit 2020 zijn vervangen.

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
