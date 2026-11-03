# Werkvoorraad: AMB KMZ-varianten zonder eigen SIU-haltevolgorde

**De 60 vermeldingen zijn geen 60 unieke route_id's.** A/B blijven als aparte patronen onder dezelfde basisroute.
Er zijn geen officiële SOBUSA-haltes uit geografische nabijheid afgeleid.

## Prioriteiten

- P1_SOBUSA_AB_and_base_routes: 9 varianten
- P2_review_nearby_OSM_platforms_and_SIU_cross_route_stops: 28 varianten
- P2_fix_official_KMZ_link_conflict: 2 varianten
- P3_seek_extra_TPC_stops_and_cross_route_evidence: 21 varianten

## Nieuwe controlebronnen en opvolging

1. SOBUSA C12/C16/B18: vergelijk de afzonderlijke A/B-geometrieën met de originele vergunningen; controleer waar de trajecten werkelijk uiteenlopen.
2. Bestaande SIU-stops langs dezelfde straat zijn hooguit kandidaat-instaplocaties voor andere lijnen, nooit automatisch een SOBUSA-halte.
3. Controleer OSM-platformen op netwerk/transitoperator en bewijs van instap langs de route; huidige Overpass-export bevat **0 bevestigde traditionele TPC-haltes**.
4. Markeer de vier foutieve gedeelde KMZ-URL's en valideer de correcte geometrie eerst.
5. Pas na bewijs van daadwerkelijke haltebediening en richting/volgorde mag een variant naar GTFS stop_times.txt.

De 20 bestaande SIU-haltevolgorde-kandidaten blijven behouden; de afzonderlijke ambiguïteitsreview voor 13 SIU-itineraries gebruikt de KMZ-corridors als tweede bron.
