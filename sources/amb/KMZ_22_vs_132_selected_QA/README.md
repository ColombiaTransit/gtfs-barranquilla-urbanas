# Geselecteerde KMZ-first shapes — vergelijking 22 versus 132

**Status:** MobilityData 8.0.1 technisch gevalideerde **onderzoeksgeometrie**, niet publiceren als operationele GTFS-dienstregeling.

## Uitkomst

De reconstructie combineert bestaande officiële AMB-KMZ 2026 voor 63 onderzoeksritpatronen en eerder onderzochte GraphHopper-busvormen als fallback waar een bruikbare KMZ ontbreekt (7 patronen, voornamelijk COOLITORAL PT2 en LOLAYA D8). Van de 352 brontrajectdelen zijn er 340 afkomstig uit de officiële KMZ en 12 GH-fallback.

| Controle | Alleen 22 streng geaccepteerde delen | Alleen 132 KMZ-corridor-verfijnde delen | Geselecteerde combinatie |
|---|---:|---:|---:|
| MobiltyData ERROR | 0 | 0 | **0** |
| MobilityData WARNING | 2.378 | 2.379 | **2.374** |
| stop_too_far_from_shape | 1 | 1 | **1** |
| stops_match_shape_out_of_order | 0 | 0 | **0** |
| >400m stukken in 340 officiële KMZ-delen | 422 | 146 | **172** |

Uit de set met 132 kandidaatdelen zijn **101 trajectdeelversies** geselecteerd, waarvan **twee een bestaande versie uit de 22-set vervangen**. De resulterende onderzoeksgeometrie omvat **121 gewijzigde officiële KMZ-trajectdelen** ten opzichte van de oorspronkelijke bron-KMZ. In de oorspronkelijke 340 officiële KMZ-delen waren 457 lijnstukken langer dan 400 meter; de combinatie brengt dat terug tot 172.

Bij het selecteren geldt:

- officiële KMZ is de routecorridor; een voorgestelde GH-verfijning moet binnen maximaal 35 meter van de KMZ blijven;
- rijrichting en stops worden niet automatisch aangepast;
- meer wegdetails of betere nabijheid tot het gecontroleerde GH-net is nodig voordat een verfijning wordt overwogen;
- geen routepatroon met nieuwe validatorwaarschuwingen wordt automatisch gekozen;
- de **complete gecombineerde set** is opnieuw door MobilityData gegaan; er zijn geen nieuwe distance/order-waarschuwingen en het totaal aan waarschuwingen is met vier gedaald.

De bronkeuze is gecontroleerd op alle 352 deeltrajecten en vastgelegd in `per_section_22_vs_132_road_fidelity.csv`, met een route-overzicht in `per_route_22_vs_132_quality.csv`.

## Bestanden

- `shapes_RESEARCH_ONLY_NOT_FOR_PUBLICATION.txt`: complete geselecteerde GTFS `shapes.txt` voor de **67 kunstmatige QA-ritten** van de huidige proefpopulatie.
- `GraphHopper_bus_road_shapes_RESEARCH_ONLY.geojson`: de 352 corresponderende geografische onderzoekstrajectdelen.
- `selection_summary.json` en `MobilityData_final_comparison.json`: exact gecontroleerde cijfers.
- `GH_full_route_bus_segment_alignment.csv`: metadata voor opnieuw uitvoeren van de demonstratiebuild.

[Geslaagde definitieve vergelijking, inclusief GTFS-demonstratie-ZIP en volledige validatorrapporten](https://github.com/ColombiaTransit/gtfs-barranquilla-urbanas/actions/runs/41783603333).

## Nog niet afgehandeld

De enige resterende geografische afstandswaarschuwing is **LOLAYA D8-4165, Homecenter Calle 30 (SN)** (ongeveer 105,24 m vanaf de GH-fallback). De originele KMZ voor D8 bestaat uit ongeordende fragmenten; de huidige fallback is op oudere ArcGIS-informatie gebaseerd en niet geverifieerd als huidige routebediening.

De huidige onderzoekspopulatie bevat **67 synthetische QA-ritten, 59 bestaande route-ID's en 8.867 haltebezoeken**. COOLITORAL PT2 heeft nog geen overeenkomstige route-ID in `gtfs/routes.txt` en blijft buiten de testfeed. Kalender, tripgrenzen, tijden en haltebediening zijn nog **niet bewezen**. Geen productie-GTFS onder `gtfs/` aangepast.
