# AMB bronconforme wegengeometrie (geconsolideerde GraphHopper-buskandidaten)

Uit de 352 eerste KMZ-gebonden GH-wegroutes worden uitsluitend de 21 hergetoetste
wegengeometrieën ingevoegd die met dichtere KMZ-tussenpunten nu **voldoende overeenkomen**.
Alle andere GH-wegroutes blijven uit de oorspronkelijke 950m-ankerrouteanalyse behouden.
De 21 resterende afwijkingen blijven expliciet als onbevestigde brontrajecten gemarkeerd.

## Resultaat

- GH_road_segments_total: **352**
- GH_improved_450m_route_sections_selected: **21**
- GH_road_sections_aligned_after_merge: **331**
- GH_source_geometry_sections_still_unresolved: **21**
- SIU_stops_audited_against_selected_roads: **9020**
- SIU_stops_over_45m_from_best_candidate_road: **739**
- old_first_pass_SIU_stops_over_45m: **852**
- selected_geometries_count: **352**
- OSM_queries: **0**
- additional_GH_requests: **0**

## Grenzen

- Alle 9.020 SIU-fysieke haltebezoeken en hun stop_sequence blijven intact.
- Een route die overeenkomt met GraphHopper is **niet noodzakelijk de door de vervoerder werkelijk gereden route**.
- De resultaten zijn input voor een tweede controle van herhaalde wegpassages en bronhaltevolgorde.
- Geen GTFS stop_times, route-trips, reistijden of publieke shapes worden overschreven.
- Private GH via organisatievariabele; publieke API: https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md
