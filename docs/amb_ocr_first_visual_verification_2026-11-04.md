# Eerste visuele OCR-/broncontrole — 4 november 2026

De [nieuwe OCR-Action](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41786660704) heeft **6/6** originele scans technisch opgehaald en 61 pagina's met Spaanse OCR geëxtraheerd. Er zijn 48 originele paginabeelden voor visuele review bewaard. SHA-256 per PDF: [technisch extractieregister](../sources/amb/legal_validity_ocr_review/six_pdf_extraction_results.csv).

## Op originele pagina-afbeeldingen gecontroleerd

| Document | Originele PDF-pagina | Visueel bevestigde inhoud | Juridisch gevolg voor GTFS |
|---|---:|---|---|
| TRANSMECAR **324-2010** | 1, 7–8 | Officiële 324-2010-scan betreft Soledad – Murillo – Vivero, vervoerder TRANSMECAR. Artikel 1 (p.7) *restructureert* het betrokken vervoer en noemt uitvoering afhankelijk van bericht van AMB i.v.m. ingebruikname Transmetro-fase 1. Kaart p.8 vermeldt **C17** en historische routeomschrijving `Malambo – Vía 40 – Circular`. | Historische C17-routecode zichtbaar; gelijkstelling met volledig huidig **C17-4160**, exacte uitvoeringsdatum en later wijzigingsrecht nog niet bewezen. Niet zomaar active route noemen. |
| TRASALIANCO **408-2013** | 1, 10 | Officiële scan betreft **D18-4179**, vervoerbedrijf TRASALIANCO. Artikel 1 (p.10) **restructureert** de route; op de originele pagina staan kaart, routecode en straatvolgorde met titel Concord – Murillo – Circunvalar – Carrera 43 – Calle 76. | Een historische routewijziging is aangetoond; toekomstige wijzigingen en volledige technische tabel/duur vragen verdere bladzijdecontrole. |
| LA CAROLINA **067-2011** | 1, 7–8 | Officiële scan betreft **A16-4161** Terminal de Transportes – Miramar – Circular; p.7 heeft de routekaart en gedetailleerde straatlijst. **Artikel 2 p.8 wijzigt 173-2010 uitsluitend voor het routeverloop; artikel 3 behoudt de technische kenmerken en capaciteit uit 173-2010.** | **067-2011 is geen zelfstandige bron voor een nieuw spits-/dalinterval.** Voor historische frequenties moet de technische tabel uit **173-2010** worden gelezen; 204-2012 en 199-2019 moeten nog op latere juridische wijziging worden gecontroleerd. |
| TRASALIANCO **266-2010** | 1 | Originele scan is correct genummerd **266-2010** en betreft SIMÓN BOLÍVAR – MERCADO, TRASALIANCO. | Documentidentiteit/naam op voorblad gecontroleerd; overeenkomst met **B19-4176**, artikel en frequentietabel nog op latere PDF-pagina controleren. |

## Nog in visuele wachtrij (origineel nu wel gedownload)

- **TRASALIANCO 265-2010 / D12-4154:** 10 pagina's OCR; identiteit, beschikkende artikelen en kaart/straatlijst nog visueel na te lopen.
- **TRASALIANCO 268-2010 / D17-4158:** 10 pagina's OCR; identiteit en wijzigingsrelatie met 411-2010 nog visueel na te lopen.
- **TRASALIANCO 408-2013 / D18-4179:** technische intervallen en complete routekaart controleren tegen het originele tabellenblad.
- **TRANSMECAR 324-2010 / C17:** juridische inwerkingtredingsvoorwaarde en overgang van historische code C17 naar actuele route-ID C17-4160.
- **LA CAROLINA A16:** 173-2010, 204-2012, 199-2019 in juridische keten opnemen voordat actuele route/frequentie wordt besloten.

## Regels

1. *OCR volledig verwerkt* betekent **niet** dat routeverloop, tijdvakken of rechtsgeldigheid zijn goedgekeurd.
2. Het **orig. PDF + SHA-256 + pagina + artikel** blijft het bewijs; het GitHub-artifact bewaart de beelden, terwijl dit dossier alleen gevalideerde bevindingen registreert.
3. Alleen concrete routefrequenties uit het **toepasselijke** besluit gebruiken. Vloot/capaciteit blijft buiten de GTFS-scope.
4. Geen oorspronkelijke bronbestanden, historische cijfers, GTFS-route-ID's of productie-`gtfs/` gewijzigd.

## Primaire bron-PDF's

- [TRANSMECAR 324-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRANSMECAR/TRANSMECAR-C17-Resolucion-324-10.pdf).
- [TRASALIANCO 408-2013](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALIANCO/RESOLUCION-408-13-TRASALIANCO.pdf).
- [LA CAROLINA 067-2011](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/LA-CAROLINA/LA-CAROLINA-A16-Resolucion-067-11.pdf).
- [TRASALIANCO 266-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALIANCO/TRASALIANCO-B19-Resolucion-266-10.pdf).
