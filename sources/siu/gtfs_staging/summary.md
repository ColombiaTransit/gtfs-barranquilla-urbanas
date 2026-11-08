# SIU route-code crosswalk and conservative stop clustering

**33 non-test SIU itineraries**, 6407 ordered stop visits.
**3117 candidate physical stops** grouped only by SAME direction-preserving normalized name and all points within 5.0m.
**53 same-coordinate/different-name cases left separate**.
**2 reviewed spelling corrections**, 2 SIU occurrences corrected; originals preserved.
**1 historical stop ID aliases** retained after merge.
**2213 stop visits have a provisional AMB route ID**, with no timetable fields.
**11 high-confidence geographic/operator route links**; NO legal code mappings automatically confirmed.

Route crosswalk status:
- gis_coverage_below_80pct: 4
- high_confidence_provisional: 11
- overlapping_routes_margin_below_15pct: 4
- shared_multi_operator_itinerary: 7
- test_excluded: 3
- top_gis_code_absent_in_gtfs_routes: 1
- top_gis_operator_does_not_match_siu: 1
- variant_A_B_unresolved: 5

No synthetic GPS, no invented arrivals/departures, no test routes, no vehicle fleet values.
The final official AMB route and stop mapping remains subject to latest resolution and itinerary-variant review.
A stop ID anchored to the minimum SIU UUID is stable for a fixed snapshot; preserve this mapping when updating SIU data.
Do not publish the derived SIU stops until public data reuse rights are checked.
