# EMBUSA B9-4125 — juridische wijzigingsketen 231-2025 → 010-2026

**Datum broncontrole:** 4 november 2026. **Scope:** beschikkende artikelen en technische routetabellen uit twee originele AMB-PDF's, visueel gecontroleerd op de aangeduide pagina's. Dit document beschrijft het **bewijsbare besluitverschil**; het bevestigt niet dat de route daadwerkelijk conform vergunning rijdt.

## Primaire documenten

1. [Resolución Metropolitana 231-2025, 9 p., 26 juni 2025](https://www.ambq.gov.co/wp-content/uploads/2026/03/RESOLUCION-M.-231-2025-L.pdf), originele **PDF p. 5, 6 en 8** (document-paginanummers 5, 6, 8). De dispositieve tekst op p.6 begint met `Artículo 1: Modificar el permiso de operación de la ruta B9-4125` en benoemt `B9-4125 – Itinerario A`.
2. [Resolución Metropolitana 010-2026, 5 p., 6 januari 2026](https://www.ambq.gov.co/wp-content/uploads/2026/01/RESOLUCION-REESTRUCTURACION-EMBUSA-ENE-2026.pdf), originele **PDF p. 3–5**. De dispositieve tekst op p.3 begint met `ARTÍCULO PRIMERO: Modificar el permiso de operación ... B9-4125`; routekaart/recorrido op p.4, tabel en ondertekening op p.5.

## Verschillen gecontroleerd op originele paginabeelden

| GTFS-relevant gegeven | 231-2025 | 010-2026 | Bron |
|---|---|---|---|
| Vervoerder | EMBUSA | EMBUSA | 231 p.6; 010 p.3 |
| Routecode | B9-4125 / **Itinerario A** | B9-4125 (geen A-aanduiding in tabel) | 231 p.6; 010 p.3 |
| Spits-/dalinterval | **3 / 5 min** | **4 / 6 min** | 231 p.5/8; 010 p.5 |
| Juridische routelengte | **42,5 km** | **53,9 km** | 231 p.5/8; 010 p.5 |
| Routenaam / dekking | El Boliche – Las Nieves – Carrera 8 – Calle 53D – Lucero – El Recreo – Carrera 58 – Calle 77 – Bellavista – Montecristo – Calle 54 – La Sierra – Carrera 8 – Calle 17 – Carrera 38 | Zona Franca – Las Nieves – Carrera 8 – Lucero – El Recreo – Carrera 58 – Calle 77 – Vía 40 – Río Alto – Las Flores – Circular | 231 p.6; 010 p.3 |
| Dienstvenster in besluit | 00:00–24:00 **afhankelijk van vraag** | 00:00–24:00 **afhankelijk van vraag** | 231 p.5/8; 010 p.5 |

**Concrete bronuitkomst:** 010-2026 is een latere wijziging van **dezelfde routecode B9-4125**, met andere lengte, routeomschrijving en minder frequente vergunde vertrekintervallen. Voor het voorlopige GTFS-planningsmodel moeten de expliciet in artikel 1 van 010-2026 genoemde routeparameters vóór die van 231-2025 worden gebruikt **voor zover geen nog later toepasselijk besluit bestaat**. Het 3/5-interval uit 231-2025 mag niet als actuele B9-waarde naast 4/6 worden opgeteld.

## Wat nog niet juridisch bewezen is

- **Ingang/uitvoering, rechtskracht en eventuele latere besluiten:** ondertekening en publicatie bewijzen niet op zichzelf dat er geen beroep, schorsing, afwijkende uitvoering of latere wijziging bestaat. De documenten bevatten bepalingen over kennisgeving en bezwaar; geen uitvoeringswaarneming is onderzocht.
- **Itinerario A uit 231-2025:** de 2026-beschikking noemt de route als B9-4125. Dit is geen bewijs dat een eventuele aparte B-variant, indien bestaand, is ingetrokken. Maak geen extra GTFS-A/B-ritten op basis van alleen het oude etiket.
- **Bediening van 00:00–24:00:** uitdrukkelijk afhankelijk van vraag; niet publiceren als gegarandeerde nachtbediening.
- **113-2012:** historische routewijziging moet nog tegen beide nieuwere besluiten worden geplaatst indien historische juridische reconstructie vereist is.
- **GTFS-timing:** 4 en 6 minuten zijn geautoriseerde headways; vertaalslag naar `frequencies.txt`, de diensturen en haltepassagetijden vereist de afzonderlijke projectmodellering en gecontroleerde ritgrenzen.

## Bronkwaliteit

De originele 231-2025 is een scan met onbetrouwbare automatische tekstextractie. De relevante pagina's zijn **visueel** gecontroleerd op routecode, titel, artikel, interval en lengte. De originele 010-2026 heeft een duidelijk leesbare tekstlaag/afbeeldingsweergave. De bronstukken worden niet bewerkt.

**Status:** `LEGAL_AMENDMENT_COMPARISON_REVIEWED; CURRENT_2026_OPERATION_UNVERIFIED`. Geen wijziging aan productie-`gtfs/` of vergunde frequentie-invoer.
