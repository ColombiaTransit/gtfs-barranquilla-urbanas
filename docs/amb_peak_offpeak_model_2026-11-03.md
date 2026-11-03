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
