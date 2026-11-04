# AMB vervolgcontrole — 4 november 2026

## Brongrenzen
Dit is een vergelijking van reeds in de repository gedocumenteerde broncontroles, **geen nieuwe visuele inspectie**. De zes originele scans zijn als GitHub Actions-artifact beschikbaar (run 41786660704); de 48 geselecteerde beelden en OCR-tekst zijn nog niet opnieuw inhoudelijk nagekeken. Geen productie-GTFS aangepast.

## 1. TRASALIANCO — pagina-voor-pagina reviewplan
| Resolutie | Route | Bevestigd | Eerstvolgende originele PDF-pagina's | Blokkade |
|---|---|---|---|---|
| 265-2010 | D12-4154 | 10 OCR-pagina's; bronhash aanwezig | 1 identiteit; 6 dispositief artikel; 8–9 kaart/tabel | Geen visueel bevestigde frequentie of actuele geldigheid |
| 266-2010 | B19-4176 | Voorblad p1 visueel gecontroleerd | 6 dispositief artikel; 8–9 kaart/tabel | Routecode B19 en interval nog niet visueel geverifieerd |
| 268-2010 | D17-4158 | 10 OCR-pagina's; bronhash aanwezig | 1 identiteit; 6 dispositief artikel; 8–9 kaart/tabel | Relatie met 411-2010 en geldigheid open |
| 408-2013 | D18-4179 | Voorblad p1 en herstructurering p10 gecontroleerd | 8, 10–11 volledige tabel en slotartikelen | Nieuwe frequentie en latere besluiten open |

De OCR-index bevat voor elk van deze pagina's het exacte artifact-pad en de SHA-256. OCR-markers zoals FRECUENCIA zijn **geen** bewijs van de daadwerkelijke tabelwaarden.

## 2. LA CAROLINA A16-4161
De originele 067-2011 p7–8 toont wijziging van het traject en behoud van technische parameters uit 173-2010. Daarom: technische uitgangswaarden uit 173-2010; de wijzigingen van 204-2012 en 199-2019 artikel voor artikel vergelijken vóór een actueel interval of routevorm wordt vrijgegeven. Geen nieuw frequentiegetal uit 067-2011.

## 3. SOBUSA
466-2025: C12-A 6/9 min, C12-B 3/6 min; C16-A en C16-B elk 7/9 min. Gecombineerde drukste-corridorwaarden (C12 3/5, C16 3,5/6) zijn **niet** extra GTFS-diensten. Voor B18 geldt later 082-2026: A en B afzonderlijk 10/12, gedeeld traject 5/6. Nog nodig: geometrie, ritgrenzen, piek-/dalvensters en inwerkingtreding. Bron: docs/amb_bedrijven/sobusa_466_2025_analysis_2026-11-03.md.

## 4. COOTRAB / COOLITORAL gezamenlijke A1
COOTRAB 358-2024: C5 en C6 elk 8/10 min; A1-4106 gezamenlijke exploitatie met COOLITORAL, COOTRAB-aandeel 22–28 voertuigen (géén GTFS-frequentie). COOLITORAL 192-2025 is later en moet op A1-artikelen, exploitanten en verdeling worden vergeleken. Geen dubbel A1-serviceaanbod genereren; pas na gelijkheid van variant en interval samengestelde agency/attributions toepassen. Bronnen: sources/amb/cootrab_resolution_legal_index_2026-11-02.csv en sources/amb/coolitoral_resolution_legal_index_2026-11-02.csv.

## 5. COOTRANTICO 025-2011 — identiteitsblokkade
De als 025-2011 geregistreerde PDF heeft **dezelfde SHA-256** als 331-2010: `7d1f47ba99930a14` (verkorte hash zoals in het historische register). De documenttekst noemt 331-2010. Daarom 025-2011 niet als apart rechtsgeldig besluit of als bron voor B20 behandelen. De recente 462-2025 omvat B20-4180 en B20-B-4191, maar dat repareert de historische bronidentiteit niet. Correcte originele 025-2011 afzonderlijk zoeken en aan documentnummer, datum, handtekening en artikel koppelen; tot die tijd status WRONG_SOURCE_BLOCKER.

## 6. Vervolgcriteria
1. Visueel artikel en tabel per originele PDF-pagina vastleggen, met SHA-256.
2. Latere wijzigingen per route/variant en ingangsvoorwaarden expliciet controleren.
3. Autorisatie voor GTFS pas na routegeometrie, haltevolgorde en tijdvensterverificatie.
4. Geen fleet/capacity als ritfrequentie gebruiken; geen dubbele gezamenlijke exploitatie.
