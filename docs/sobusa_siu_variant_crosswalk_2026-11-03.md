# SOBUSA — SIU A/B routevariant-crosswalk (3 november 2026)

## Doel en primaire uitkomst

Vraag: komen de officiële A/B-itinerarios van SOBUSA **C12-4169 en C16-4167** als **afzonderlijke route-/itineraryrecords** voor in het publieke **SIU**-portaal, ook als het verschil tussen de trajecten beperkt is?

**Antwoord op basis van de huidige dataset: niet vast te stellen.** De complete beschikbare anonieme SIU-GraphQL-extractie van **3 november 2026 om 07:28:14 UTC** bevat **36 itineraryrecords: 33 reguliere en 3 testrecords; 0 records met SOBUSA** (ook geen verwijzing naar de volledige SOBUSA-naam) en **0 records met C12 of C16 als naam**. Daarmee is er geen SOBUSA-lijst om te vergelijken. Dit is een **dekkingstekort van de specifieke publieke SIU-extractie**, geen bewijs dat SOBUSA of de A/B-diensten niet bestaan.

- **Dataset:** [SIU public extract](../sources/siu/public_extract/siu_itineraries.csv).
- **Reproduceerbare, geauthenticeerde-vrije methode:** [script](../scripts/extract_siu_public_itinerary_stops.py); publiek SIU-portaal `https://siu.ambq.gov.co/siu/schedule-mng/schedules`.
- **Ruwe haltevolgorde wanneer route wél aanwezig is:** [6.873 route-halteposities](../sources/siu/public_extract/siu_route_stop_sequences.csv).
- **Per wettelijke variant ingevoerde open koppelingen:** [crosswalk CSV](../sources/siu/analysis/sobusa_variant_to_siu_crosswalk_2026-11-03.csv).

De SIU-GraphQL-oproep gebruikt `ServiceMngCompressedItineraryListing`. Het bestaande script kijkt naar de automatisch door de publieke webpagina opgevraagde lijst, niet naar alle mogelijke organisatie-specifieke datasets of interne SIBUS-gegevens. We mogen dus niet concluderen dat de echte SIU-backend nergens SOBUSA bevat.

## Welke verschillen zijn in het AMB-besluit wél bevestigd?

[Resolutie 466-2025](https://www.ambq.gov.co/wp-content/uploads/2026/03/Permiso-de-operacion-subusa-2.pdf), oorspronkelijke pagina's 9–11 en 16–18, vermeldt bij **beide lijnen twee afzonderlijk voorgeschreven volledige itinerarios**. Ze gebruiken dezelfde terminal (Calle 63 #3-75), maar de vertrekken lopen via **verschillende toegangsstraten**:

| Route | Itinerario A — vertrekzijde | Itinerario B — vertrekzijde | Frequentie spits/dal A | Frequentie spits/dal B |
|---|---|---|---|---|
| C12-4169 | Vía Granabastos en vervolgens Carrera 3/Transversal 14A | Calle 58E, Calle 56 en Carrera 6 | 6/9 min | 3/6 min |
| C16-4167 | Vía Granabastos en vervolgens Carrera 3/Transversal 14A | Calle 58E, Calle 56 en Carrera 6 | 7/9 min | 7/9 min |

De routebeschrijvingen bevatten grotendeels dezelfde lange corridor. **Het zijn daarom niet zonder meer twee volledig tegengestelde rijrichtingen**: bij de beoordeling moeten we het **gehele geordende traject** vergelijken en verschillen in één straat of korte lus niet wegmiddelen.

Een SIU-haltelijst die deze afwijkende straten niet bij naam toont, is onvoldoende om A en B uit elkaar te houden. Gebruik dan GPS-geometrie of een afzonderlijk officieel routepatroon-ID.

**B18** hoort ook in de dekkingstest: twee A/B-itinerarios onder het latere besluit **082-2026**, elk spits 10 min/dal 12 min; zij ontbreken eveneens uit de huidige SIU-extractie.

## Onafhankelijke bron: Moovit (niet verwarren met SIU)

Moovit toont zes SOBUSA-lijnen en voor zowel C12 als C16 twee zichtbare **reisrichtingen**:

| Lijn | Richting 1 | Stops | Richting 2 | Stops |
|---|---|---:|---|---:|
| C12 | Vía 40 con Calle 79 → Nevada Sobusa | 31 | Nevada Sobusa → Vía 40 con Calle 79 | 25 |
| C16 | La Playa → Nevada Sobusa | 32 | Nevada Sobusa → La Playa | 28 |

- [Moovit SOBUSA-routelijst](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-lines-Barranquilla-2883-860179)
- [Moovit C12 heen](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-c12-Barranquilla-2883-860179-155472669-0) en [terug](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-c12-Barranquilla-2883-860179-155472669-1)
- [Moovit C16 heen](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-C16-Barranquilla-2883-860179-155472672-1) en [terug](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-c16-Barranquilla-2883-860179-155472672-0)

Deze **richting-1/richting-2**-informatie is géén bewijs dat zij precies overeenkomen met **AMB-itinerario A/B**. Eén A/B-variant kan meerdere door Moovit getoonde directionele ritpatronen omvatten, en een deel van de zijstraten kan ontbreken bij een tussengelegen halte. Publiceer niet automatisch Moovit-richting 0 als juridische A.

Moovit vermeldt wel haltevolgordes en operationele tijdvensters, maar die kunnen van de vergunning afwijken; leg die gegevens apart als derde-partij-verificatie vast. Hergebruik/licentie apart toetsen.

## Beslissingsregels voor toekomstige SIU-vergelijking

1. **Nieuwe publieke SIU-lijst aanwezig?** Verifieer eerst of bedrijf SOBUSA, of een aantoonbaar bij SOBUSA behorende gecombineerde operator, voorkomt; vraag of de lijst een volledige, niet-gefilterde catalogus is.
2. **Twee aparte route/itinerary UUID's?** Vergelijk de volledige haltevolgorde (inclusief herhaalde coördinaten en rijrichting), niet alleen routenaam of ruimtelijke nabijheid.
3. **Differentiërende terminalstraten en lussen?** Vergelijk zowel eerste en laatste haltes als doorlopende GPS-segmenten op p9–10 en p16–18 van 466-2025. Niet automatisch een verschil van één straat negeren.
4. **Maar één gedeelde SIU-route-UUID?** Niet A en B uit dezelfde stoplijst dupliceren zonder bewijs. Houd twee wettelijke dienstvarianten administratief apart; markeer `SIU_variant_match_status=unresolved`.
5. **Geen volledige match:** `GTFS export approved = no` voor variantgebonden `stop_times` en `shapes`; individuele officiële headways wel behouden in vergunningstaging.
6. **Weergaverichting ≠ A/B:** Gebruik `direction_id` alleen als de echte reisrichting is vastgesteld, niet als synoniem voor wettelijke itineraryletter.

## Status

- ✅ Juridische A/B-beschrijvingen en intervallen voor C12 en C16 vastgelegd en van bronpagina's voorzien.
- ✅ Aanwezigheid in de huidige SIU-catalogus gecontroleerd: **SOBUSA 0/36**.
- ✅ Beschikbare Moovit-richtingen als *onafhankelijke, niet-equivalente* controlebron gevonden.
- ⏳ Werkelijk verband SIU/AMB A/B: **onbeslist**, omdat de SIU-SOBUSA-bronregels ontbreken.
- ⏳ Werkelijke haltes, verschillen in de detailstraten en GTFS-stopvolgordes per A/B-variant: nog niet definitief bekend.
