"""Regression checks: only verified spelling errors may merge SIU physical stops."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("siu_staging",ROOT/"scripts/build_siu_gtfs_stop_staging.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def sample(uuid,name,lat,lon,seq=1):
    return {
        "siu_stop_uuid":uuid,
        "siu_itinerary_uuid":"siu-test-itinerary",
        "siu_base_route_uuid":"siu-base-id",
        "siu_display_name":"TEST REGULAR ITINERARY",
        "siu_companies":"TEST_OPERATOR",
        "siu_stop_sequence":str(seq),
        "stop_name":name,
        "stop_lat":str(lat),
        "stop_lon":str(lon),
        "likely_test_itinerary":"false",
    }


class NameCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.rules=mod.spelling_rules(mod.load(mod.CORRECTIONS))

    def test_only_two_explicit_reviewed_rules(self):
        self.assertEqual(len(self.rules),2)
        self.assertEqual(self.rules["LOS MANATIALES - GIRASOL (CARRERA 12 - OE)"],
                         "LOS MANANTIALES - GIRASOL (CARRERA 12 - OE)")
        self.assertEqual(self.rules["COLEGIO LA ENSE?ANZA (CALLE 87 -SN)"],
                         "COLEGIO LA ENSEÑANZA (CALLE 87 -SN)")

    def test_direction_modifying_rule_is_rejected(self):
        with self.assertRaises(ValueError):
            mod.spelling_rules([{
                "source_name_exact":"PARADA (NS)",
                "canonical_name":"PARADA (SN)",
                "review_status":"approved_clear_typo"
            }])

    def test_typo_merges_with_same_name_same_coordinate(self):
        rows=[
            sample("stop-aa","LOS MANATIALES - GIRASOL (CARRERA 12 - OE)",10.9029438,-74.8112695,1),
            sample("stop-bb","LOS MANANTIALES - GIRASOL (CARRERA 12 - OE)",10.9029438,-74.8112695,2),
        ]
        stops,visits,conflicts=mod.build_stop_candidates(rows,{},self.rules)
        self.assertEqual(len(stops),1)
        self.assertEqual(stops[0]["stop_name"],"LOS MANANTIALES - GIRASOL (CARRERA 12 - OE)")
        self.assertEqual(stops[0]["siu_uuid_occurrences"],2)
        self.assertEqual(visits[0]["stop_name_source"],"LOS MANATIALES - GIRASOL (CARRERA 12 - OE)")
        self.assertEqual(visits[0]["stop_name_normalized"],"LOS MANANTIALES - GIRASOL (CARRERA 12 - OE)")
        self.assertEqual(visits[0]["candidate_stop_id"],visits[1]["candidate_stop_id"])
        self.assertEqual(len(conflicts),0)

    def test_encoding_repaired_but_directionless_stays_separate(self):
        rows=[
            sample("stop-aa","COLEGIO LA ENSE?ANZA (CALLE 87 -SN)",11.0080993,-74.8203543,1),
            sample("stop-bb","COLEGIO LA ENSEÑANZA (CALLE 87)",11.0080993,-74.8203543,2),
        ]
        stops,visits,conflicts=mod.build_stop_candidates(rows,{},self.rules)
        self.assertEqual(len(stops),2)
        self.assertEqual(len(conflicts),1)
        self.assertEqual(visits[0]["stop_name_normalized"],"COLEGIO LA ENSEÑANZA (CALLE 87 -SN)")
        self.assertNotEqual(visits[0]["candidate_stop_id"],visits[1]["candidate_stop_id"])

    def test_opposing_directions_never_merge(self):
        rows=[
            sample("stop-aa","PARADA (EO)",10.905671,-74.775596,1),
            sample("stop-bb","PARADA (OE)",10.905671,-74.775596,2),
        ]
        stops,visits,conflicts=mod.build_stop_candidates(rows,{},self.rules)
        self.assertEqual(len(stops),2)
        self.assertEqual(len(conflicts),1)
        self.assertNotEqual(visits[0]["candidate_stop_id"],visits[1]["candidate_stop_id"])


if __name__=="__main__":
    unittest.main()
