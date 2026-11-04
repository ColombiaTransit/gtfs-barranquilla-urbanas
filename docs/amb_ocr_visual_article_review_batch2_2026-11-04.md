# AMB — visuele OCR-artikelcontrole, tweede batch (4 november 2026)

## Werkwijze en reikwijdte
Bron: originele AMB-PDF's uit GitHub Actions-run [41803033009](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41803033009), artifact 13308193358. De originele PDF's zijn geopend en **elf geselecteerde pagina's** visueel vergeleken met `text.txt` (contactbladen in lokale onderzoeksomgeving). Dit is een gerichte artikelcontrole, **geen integrale pagina-voor-pagina-certificering van alle besluiten**. Paginanummers zijn PDF-paginanummers, niet noodzakelijk gedrukt paginanummer.

| Besluit | Visueel gecontroleerde pagina | Bevinding uit dispositief | Open juridische / GTFS-controle |
|---|---:|---|---|
| COOTRANTICO 462-2025 | 5 | Artikel 1 wijzigt A18-4183, B20-4180, B20-B-4191, B4-4120, B5-4121, B5-B-4190, B6-4122, B7-4123 | Alle varianttabellen p. 5–21 en kennisgeving; geen eerdere B20-dienst dubbelen |
| EMBUSA 231-2025 | 6 | Artikel 1 wijzigt B9-4125; gespecificeerd als itinerario A | Vergelijk A/B-tabellen en precieze rechtsgevolgen met latere 010-2026 |
| EMBUSA 010-2026 | 3 | Artikel 1 wijzigt opnieuw B9-4125 | Latere act heeft voorrang voor overlappende bepalingen; exact effect en datum na kennisgeving nog toetsen |
| COOTRAB 358-2024 | 3, 7 | Artikel 1 herstructureert COOTRAB C5-4136/C6-4137; artikel 2 herstructureert **COOLITORAL A1-4106**, niet een extra COOTRAB-route | Samenwerkingsrelatie uit considerans niet verwarren met twee identieke vergunde trips; routecodeconflict C5-4135/4136 open |
| COOTRAB 378-2023 | 5 | Originele kop bevestigt **resolutie 378-23** en artikel 1 COOTRAB C5-4136/C6-4137 | Bestandsnaam is geen reden om besluit verkeerd te identificeren; 358-2024 is later |
| COOCHOFAL 242-2025 | 4 | **Intern documentconflict:** titel en artikel 1 noemen A15-4129; routetabel direct onder artikel 1 toont **A15-4159**. Artikel 1 noemt ook C2-4133, C2-B-4187, C3-4134, C4-4135, C9-4140, C18-4141 en D20-4185 | **Geen automatische harmonisatie A15-4129/4159**; controleer rectificatie en originele KMZ; C2-B-codes ook controleren |
| TRASALIANCO 411-2010 | 8 | Artikel 3 wijzigt 268-2010 gedeeltelijk; artikel 6 onderscheidt rechtskracht vanaf ejecutoria en tijdelijke operationele voorwaarden totdat Transmetro start / AMB communiceert | Operationele ingangsdatum niet afleiden uit ondertekening; exacte D17-routefasen volgen |
| TRASALIANCO 408-2013 | 10 | Artikel 1 herstructureert **D18-4179**; routekaart en straattekst aanwezig | Latere wijzigingen en activering nog toetsen |
| TRANSMECAR 324-2010 | 10 | Artikel 5: gewijzigde route treedt operationeel in werking zodra AMB naleving aan bedrijf meedeelt, gekoppeld aan Transmetro-start | Datum ondertekening **niet** als operationele `calendar.start_date` gebruiken |
| LA CAROLINA 199-2019 | 9 | Artikel 1 herstructureert **A16-4161**; kaart met A/B-variantlijnen | Per-variant haltevolgorde/frequentie nog afzonderlijk verifiëren |

## Veiligheidsregels voor GTFS-bronnen
1. `legal_article_verified` betekent alleen dat het artikel op de genoemde pagina visueel is teruggevonden; niet dat volledige juridische keten of actuele exploitatie vaststaat.
2. Behoud conflicterende originele routecodes naast elkaar in het bewijsmateriaal; normaliseer ze niet zonder rectificatie.
3. Bij opvolgende besluiten route-/variant-specifiek vergelijken; geen dubbele diensten uit oudere en nieuwere versies.
4. Voor gezamenlijke exploitatie telt het **dispositieve artikel** en de specifieke vergunninghouder; de considerans alleen bewijst geen identieke gedeelde trip.
5. Onderscheid besluitdatum, kennisgeving, ejecutoria, operationele activering en einde pilot.

## Nog te inspecteren
- Alle afzonderlijke frequentie-/routegeometrietabellen van de grote 462-2025 en 242-2025 PDF's, met in het bijzonder het A15-4129/4159-conflict.
- EMBUSA 231-2025 versus 010-2026: A/B-waarden, vervanging en ingangsvoorwaarden.
- TRASALIANCO 411-2010: volledig overgangsregime voor D17 en eventuele latere wijzigingen.
- Overige besluitpagina's van de documenten: steekproef is geen volledige certificering.
