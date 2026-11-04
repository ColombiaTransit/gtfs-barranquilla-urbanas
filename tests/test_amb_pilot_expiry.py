#!/usr/bin/env python3
"""Regression tests for AMB pilot expiration and GTFS non-deletion."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/evaluate_amb_pilots.py"
spec = importlib.util.spec_from_file_location("evaluate_amb_pilots", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ROW = dict(agency="COOLITORAL", route_codes="PT4-4104;PT5-4105",
           resolution="256-2026", pilot_start="2026-06-22",
           pilot_end_exclusive="2026-12-22", end_date_confidence="provisional",
           extension_resolution="", base_resolution="192-2025")

class PilotTests(unittest.TestCase):
    def test_date_boundaries(self):
        for day, expected in [
            ("2026-06-21", "scheduled"),
            ("2026-06-22", "active_under_recorded_period"),
            ("2026-12-21", "active_under_recorded_period"),
            ("2026-12-22", "ended_no_extension_found"),
            ("2027-01-01", "ended_no_extension_found"),
        ]:
            with self.subTest(day=day):
                result = module.evaluate(ROW, dt.date.fromisoformat(day))
                self.assertEqual(result["pilot_status"], expected)
                self.assertFalse(result["route_cancelled"])
                self.assertFalse(result["legal_finalized"])
                self.assertEqual(result["base_resolution_to_reassess"], "192-2025")

    def test_extension_requires_article_review(self):
        row = dict(ROW, extension_resolution="999-2026")
        result = module.evaluate(row, dt.date(2027, 1, 1))
        self.assertEqual(result["pilot_status"], "extension_requires_article_review")
        self.assertFalse(result["legal_finalized"])

    def test_reject_invalid_dates(self):
        row = dict(ROW, pilot_end_exclusive="2026-06-22")
        with self.assertRaises(ValueError):
            module.evaluate(row, dt.date(2026, 11, 4))

if __name__ == "__main__":
    unittest.main()
