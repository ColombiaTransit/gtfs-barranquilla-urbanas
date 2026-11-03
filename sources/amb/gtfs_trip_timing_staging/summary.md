# SIU haltevolgorde -> GTFS trip templates + model-stop_times

**Staging only: geen echte busrit- of passagevertrektijden.** De 20 routekoppelingen blijven voorlopig. De 3.981 stop_sequence-waarden komen uit SIU, en ALLE verwijzingen behouden de bestaande fysieke SIU stop_id.

De trips worden als frequentie-gebaseerde sjablonen beschouwd: begin 00:00:00 in het stop_times-model is **een relatieve tijdreferentie**, geen echte eerste vertrek uit Barranquilla. De werkdagfrequenties volgen de officiële intervalresoluties waar al beschikbaar; begin/eind gebruikt het afgesproken provisorische **2020-vertrekvenster-model**.
Per halte de reistijd van het vorige punt naar het volgende wordt ruw geschat via SIU-punt-tot-puntafstand, model-snelheid, wegafstandsfactor en halte-vertraging.
Deze aannames zijn bewerkbaar in sources/amb/gtfs_timing_model_assumptions.csv.

## Resultaten

- 20 trip-sjablonen; 3981 geordende haltebezoeken met **uitsluitend modeltijden**.
- 2394 reeds bestaande fysieke SIU stop_id's hergebruikt (geen haltes per route aangemaakt).
- 17 trip-sjablonen beschikken over een officiële headway + voorlopig dispatchvenster; 68 periode-records.
- 0 trip-sjablonen met grote stop-tot-stopafstand die handmatige review vergen.
- Grootste berekende modelritduur: 336.6 minuten.

## Volgende validatie vóór echte GTFS stop_times

1. Leg echte of brononderbouwde begin-/eindritduur per route en richting vast om de modellen te ijken.
2. Bevestig SIU -> juridische AMB routecode, vooral gedeelde operators en wettelijke A/B-varianten.
3. Controleer dat elk stop_sequence werkelijk bij de gekozen trip-richting hoort, ook bij lussen en dubbele haltepassages.
4. Vervang of kalibreer per-trip rijtijd door een route-/periode-specifiek model; pas daarna kalender en shapes valideren.
5. Evalueer de verspreidings-/licentievoorwaarden van de SIU-data vóór GTFS-publicatie.

Geen enkel bestand is naar gtfs/stop_times.txt of gtfs/trips.txt geschreven.
