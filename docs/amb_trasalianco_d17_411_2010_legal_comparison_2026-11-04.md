# TRASALIANCO D17 — 268-2010 versus 411-2010

**Broninspectie 4 november 2026.** Originele [resolutie 411-2010 (9 PDF-pagina's)](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALIANCO/TRASALIANCO-D17-Resolucion-411-10.pdf) via visuele weergave van originele PDF-pagina's 5, 6 en 8 (1-gebaseerde paginanummers). Eerder visueel gecontroleerde [268-2010](https://www.ambq.gov.co/wp-content/uploads/2016/RESOLUCIONES-DE-RUTAS/TRASALIANCO/TRASALIANCO-D17-Resolucion-268-10.pdf), met historische frequentie 5 min spits / 7 min dal.

## Bevestigde rechtsgevolgen
- 411-2010 van **30 augustus 2010** is een besluit op het bezwaar (`recurso de reposición`) tegen 268-2010 van 1 juli 2010.
- PDF p.5: de gevraagde extra routeverlenging van circa 1 km naar het universiteitsgebied CUC / Simón Bolívar wordt technisch niet haalbaar geacht wegens al bestaand aanbod.
- PDF p.5–6: een **aangepaste volledige straatvolgorde van Ruta D17** is opgenomen. Gebruik deze latere geometrische beschrijving in plaats van ongecorrigeerd de geometrie uit 268-2010.
- PDF p.8 **Artículo Tercero**: 411 wijzigt 268 **gedeeltelijk**, niet een integrale intrekking van de route.
- PDF p.8 **Artículo Sexto**: rechtskracht vanaf ondertekening, maar exploitatie onder gewijzigde voorwaarden pas zodra Transmetro start; AMB moet dit aan het bedrijf communiceren.
- De visueel gecontroleerde dispositieve artikelen bevatten geen expliciet nieuw frequentiegetal. De in 268 vastgestelde **5/7 min blijft daarom historisch uitgangspunt**, onder voorbehoud van aanvullende technische artikelen en latere besluiten; niet als huidige dienstregeling bewezen.

## Gevolgen voor GTFS
1. `D17-4158` koppeling aan historische `D17` moet met actuele routecodebron worden bewezen.
2. Shape-constructie: neem de letterlijke straatvolgorde van **411-2010** als juridische referentie en match daarna met OSM/KMZ; geen shape vrijgeven zonder haltevolgorde.
3. Houd 5/7 als **historical_documented_headway**, niet als current_verified_headway.
4. Leg kennisgeving/operationele ingangsdatum en eventuele latere wijziging apart vast.

**Status:** `APPEAL_PARTIAL_ROUTE_AMENDMENT_VISUALLY_VERIFIED; CURRENT_SERVICE_UNVERIFIED`.
