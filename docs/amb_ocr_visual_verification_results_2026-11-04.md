# Originele OCR- en beeldcontrole — 4 november 2026 (tweede controle)

**Bewijs:** GitHub Actions-run [41786660704](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41786660704), artifact ID 13301995991. ZIP daadwerkelijk opgehaald en originele `source.pdf`, OCR-pagina's en `review_page_images` geïnspecteerd. Bronhashes staan in `sources/amb/legal_validity_ocr_review/six_pdf_extraction_results.csv`. Visuele inspectie van de genoemde originele pagina's, niet uitsluitend OCR.

| Bedrijf | Resolutie | Routecode op origineel | Spits | Dal | Originele PDF-pagina's gecontroleerd | Conclusie |
|---|---|---|---:|---:|---|---|
| TRASALIANCO | 265-2010 | D12 (historisch) | 4 min | 6 min | 1, 6, 8, 9 | Artikel 1 herstructureert SOLEDAD 2000; tabel 4/6; artikel 5 voorwaardelijke uitvoering na AMB-bericht |
| TRASALIANCO | 266-2010 | B19 (historisch) | 4 min | 6 min | 1, 6, 8, 9 | Artikel 1 herstructureert SIMÓN BOLÍVAR–MERCADO; tabel 4/6; artikel 5 voorwaardelijke uitvoering |
| TRASALIANCO | 268-2010 | D17 (historisch) | 5 min | 7 min | 1, 6, 8, 9 | Artikel 1 herstructureert PASADENA; tabel 5/7; artikel 5 voorwaardelijke uitvoering |
| TRASALIANCO | 408-2013 | D18-4179 | 7 min | 10 min | 1, 8, 10, 11 | Artikel 1 herstructureert routeverloop; p11 bevat interval 7/10 en notificatie-/beroepsartikelen |
| TRANSMECAR | 324-2010 | C17 (historisch) | 4 min | 6 min | 7, 9, 10 | Artikel 1 herstructureert SOLEDAD–MURILLO–VIVERO; p9 tabel 4/6; p10 artikel 5 uitvoering na AMB-bericht |

**Nu visueel bevestigd:** bovenstaande getallen en historische codes staan op originele pagina-afbeeldingen; geen numerieke OCR-afleiding zonder beeldcontrole. De OCR van TRASALIANCO 408-2013 p11 is vervormd bij 'hora valle', maar originele tabel toont 10 minuten.

**Niet bevestigd:** gelijkheid van historische D12/B19/D17/C17 aan de huidige gesuffixeerde GTFS-IDs, daadwerkelijke datum van kennisgeving/uitvoering, wijzigingen door latere besluiten (o.a. D17/411-2010), dagsoorten en spits-/daluren. De 00:00–24:00 formulering in de 2010-besluiten is expliciet vraagafhankelijk en geen bewijs voor gegarandeerde nachtbediening. Historische intervals worden niet automatisch als actuele `frequencies.txt` gepubliceerd.

**LA CAROLINA 067-2011:** reeds eerder op originele p7–8 gecontroleerd: artikel 2 wijzigt traject, artikel 3 behoudt technische parameters uit 173-2010. Geen zelfstandig nieuw interval in 067. De volledige juridische keten 173/204/199 blijft open.

**GTFS-status:** geen productieaanpassing of juridische actuele-service-goedkeuring. De 2010-bronnen geven historische vergunningswaarden.

## Aanvullende LA CAROLINA-controle

Originele PDF-pagina's 1, 6, 8 en 9 van 067-2011 opnieuw visueel geïnspecteerd. P8 artikel 2 wijzigt alleen het A16-traject ten opzichte van 173-2010; artikel 3 behoudt de technische kenmerken en capaciteit uit 173-2010. P9 bevat kennisgevingsregistraties gedateerd **30 maart 2011**; dit bewijst kennisgeving aan de genoemde vertegenwoordigers, niet op zichzelf de actuele dienstuitvoering in 2026. Geen nieuwe frequentie uit 067-2011 afgeleid.
