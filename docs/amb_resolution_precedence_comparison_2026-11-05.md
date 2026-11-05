# Gerichte vergelijking latere AMB-besluiten met oorspronkelijke routevergunningen — 2026-11-05

**Methode:** uitsluitend bestaande tekstbestanden uit OCR-artifacts van GitHub Actions run 41480204032 (TRANSMECAR artifact 13161906062; TRASALFA artifact 13160854287). Geen nieuwe OCR. Paginanummers zijn de `page_XXX.txt`-nummers. Historische besluiten bewijzen geen actuele exploitatie in 2026.

## TRANSMECAR D10-4172: 220-2010 tegenover 325-2010

- **220-2010 p8:** D10 (Malambo–Vía Caracolí–Centro–Circular), spits **4 min**, dal **8 min**, capaciteit 27–32.
- **325-2010 p5:** beroep tegen 220-2010; technische toelichting: gecorrigeerd intern traject Malambo, wijziging heeft geen belangrijke gevolgen voor operationele kenmerken; `diseño operacional se mantiene`. De verwijzing naar **120-2010** in dezelfde zin botst met de herhaaldelijk genoemde 220-2010 en is vermoedelijk een schrijffout; **niet stilzwijgend corrigeren in brontranscriptie**.
- **325-2010 p7:** artikel 1 bevestigt 220-2010 **gedeeltelijk**; artikel 2 wijzigt het **recorrido**. **p8:** overgangsbepaling gekoppeld aan start Transmetro.
- **Conclusie:** historische 4/8 min uit 220-2010 is **behouden als operationele frequentiekandidaat**, met 325-2010 als wijziging van route en voorbehoud over overgangssituatie. Geen expliciet nieuwe headway gevonden in dispositief van 325-2010. Geen uitspraak over actuele 2026-waarde.

## TRASALFA B2-B-4118: 287-2010 tegenover 111-2012

- **287-2010 p8:** spits **5 min**, dal **8 min**, capaciteit 16–20 voertuigen.
- **111-2012 p9–10:** artikel 1 herstructureert het **recorrido** van B2B; artikel 2 zegt uitdrukkelijk dat 287-2010 **gedeeltelijk wordt gewijzigd ten aanzien van het traject**, en dat de **capacidad transportadora se mantiene**. Geen nieuwe dispatchinterval in de dispositieve artikelen.
- **Conclusie:** 5/8 min blijft de laatst gevonden expliciete **route-specifieke historische intervalwaarde**; 111-2012 geeft geen expliciete vervanging. Niet verwarren met bevestiging van actuele 2026-dienstregeling. Let op: **139-2013 p20** bevat ook B2B in capaciteitstabel, met `Int. Pais` OCR als **5**; die waarde is niet zonder meer een spits/dal-paar en vervangt de expliciete 5/8 niet.

## TRASALFA D14-4156 en D15-4157: 286/285-2010 tegenover 139-2013

- **286-2010 p8:** D14 **5/8 min**. **285-2010 p7:** D15 **3/5 min**, dal door gebruiker visueel bevestigd op 2026-11-05.
- **139-2013 p5 en p7:** in sectie `situación actual` staan respectievelijk D14 spits 5 en D15 spits/dal **3/5**; het besluit kent de oorspronkelijke intervallen dus expliciet.
- **139-2013 p15:** in `cálculo del diseño operacional` voor **beide** herstructureringsroutes staat nieuw ontwerp: **4 min spits / 6 min dal**; berekende gezamenlijke voertuigbehoefte.
- **139-2013 p16 en p20:** samenvatting en artikel 2 bevatten `Int. Pais` / interval **4** bij D14 en D15 (de tabel is voor D14 gedeeltelijk rommelig OCR, maar p16 en p15 ondersteunen het ontwerp). Artikel 1 p19 wijzigt de trajecten, artikel 3 p20 wijzigt 285/286-2010 **gedeeltelijk**.
- **Conclusie:** 4/6 is de **latere expliciete operationele ontwerpwaarde** voor D14 en D15, sterker onderbouwd dan een los voorstel omdat artikel 2 naar de technische berekening verwijst en de gewijzigde capaciteiten vastlegt. Het dispositief noemt echter geen afzonderlijke dalwaarde van 6 minuten; registreer daarom als **later ontwerp met juridische toepassingskanttekening**, niet als onvoorwaardelijk huidig vergund interval. Bewaar de oorspronkelijke 5/8 en 3/5 als historische voorgangers.

## Verwerkingsregels

- Historische waarden en later ontwerp apart bewaren met resolutie en pagina; geen waarden uit latere besluiten overschrijven zonder provenance.
- D10 4/8 en B2-B 5/8 zijn historisch onderbouwde kandidaten; markeer latere trajectwijziging, en toets afzonderlijk of GTFS-variant met die historische route overeenkomt.
- D14/D15: 4/6 als latere ontwerp-kandidaat, **niet automatisch** de 2010-waarden als huidige frequenties publiceren.
- Geen nieuwe OCR of beeldanalyse nodig voor deze vergelijking.
