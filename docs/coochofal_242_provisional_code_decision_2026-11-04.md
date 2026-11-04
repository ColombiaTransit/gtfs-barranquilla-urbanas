# COOCHOFAL 242-2025 — voorlopige routecodes en vrijgave verwerking

Besluitdatum registratie: 2026-11-04. Bron: https://www.ambq.gov.co/wp-content/uploads/2026/03/RES-M-242-2025-2.pdf

## Expliciete projectbeslissing
Op verzoek van de projecteigenaar gebruiken we voorlopig **A15-4159** en **C2-B-4188**. Het oorspronkelijke besluit heeft interne tegenstrijdigheden: artikel 1 noemt A15-4129 terwijl route-/wagenparktabellen A15-4159 noemen; artikel 1/routekop noemt C2-B-4187 terwijl de wagenparktabel C2-B-4188 vermeldt. Volgens de projectinformatie staat er geen later besluit op de AMB-website. Dit is **geen officiële rectificatie** en de broncodes blijven behouden.

## Vrijgegeven en nog niet vrijgegeven
- **Vrijgegeven:** route-identificatie voor onderzoeks-GTFS, KMZ/GraphHopper-shapes, haltevolgorde, varianten, geometrievalidatie en handmatige frequentiekoppeling.
- **Niet langer blokkeren op de codeconflicten:** A15-4159 en C2-B-4188 mogen als werkidentiteit worden gebruikt; voorkom dat A15-4129 en C2-B-4188 als extra routes/trips ontstaan.
- **Blijft apart te controleren:** of een routefrequentie per richting/variant geldt, kennisgeving/ejecutoria, feitelijke dienstregeling en gedeelde exploitatie. Een voorlopig route-ID is geen bewijs van operationele activering.
- **Bronvermelding:** bij publicatie van onderzoeksdata noteer `provisional_code_from_242_2025` en `legal_code_conflict_unresolved`; voor een definitieve juridische verklaring blijft rectificatie nodig.

## Mapping
| Broncodering | Werkcode | Status |
|---|---|---|
| A15-4129 (artikel 1) | A15-4159 | provisional_alias |
| A15-4159 (route- en wagenparktabel) | A15-4159 | preferred_working_code |
| C2-B-4187 (artikel 1 en routekop) | C2-B-4188 | provisional_alias |
| C2-B-4188 (wagenparktabel) | C2-B-4188 | preferred_working_code |

De wijziging heft uitsluitend de **code-identiteitsblokkade** op; er wordt geen ingangsdatum of exploitatie geclaimd.

## Aanvullend primair bewijs: Resolución 112-20 (2020)

Bron: https://www.ambq.gov.co/wp-content/uploads/2020/06/Resoluci%C3%B3n-Metropolitana-No.-112-20.pdf — PDF-pagina 3 (nulgebaseerd p2), geciteerde routeinventaris van Resolución 110-20: COOCHOFAL **C2-B-4188** en **A15-4159**. Resolución 112-20 wijzigt zelf uitsluitend de taxibepaling van de tijdelijke COVID-regeling; de routeinventaris is historische ondersteunende evidence en **geen formele rectificatie van 242-2025**. Daarom is C2-B-4188 de voorkeurswerkcode en C2-B-4187 een alias. Geometrie en haltevolgorde blijven vrijgegeven; geen dubbele route of rit.
