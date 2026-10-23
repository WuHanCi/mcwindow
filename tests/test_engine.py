import copy
from datetime import datetime
import unittest

from mcwindow.demo import demo
from mcwindow.engine import plan, calendar, report, ValidationError


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.data = demo()

    def one(self):
        self.data["offers"] = [self.data["offers"][0]]
        return self.data["offers"][0]

    def test_demo_recommendation_and_timeline(self):
        result = plan(self.data)
        self.assertEqual([x["id"] for x in result["feasible"]], ["lunch-a", "lunch-b"])
        self.assertEqual(result["recommendation"]["price_fen"], 1990)
        self.assertEqual(result["recommendation"]["return_at"], "2026-10-23T12:32+08:00")
        self.assertEqual(result["recommendation"]["unspent_fen"], 510)
        self.assertEqual(len(result["excluded"]), 3)

    def test_budget_filter(self):
        self.data["budget_fen"] = 1000
        self.assertIsNone(plan(self.data)["recommendation"])

    def test_short_break_returns_no_plan(self):
        self.data["free_until"] = "2026-10-23T12:20+08:00"
        self.assertFalse(plan(self.data)["feasible"])

    def test_exact_boundary_includes_full_buffer(self):
        self.one()
        self.data["free_until"] = "2026-10-23T12:42+08:00"
        self.assertIsNotNone(plan(self.data)["recommendation"])
        self.data["free_until"] = "2026-10-23T12:41+08:00"
        self.assertIsNone(plan(self.data)["recommendation"])

    def test_future_start_waits_without_skipping_queue(self):
        offer = self.one()
        offer["valid_from"] = "2026-10-23T12:10+08:00"
        result = plan(self.data)["recommendation"]
        self.assertEqual(result["order_at"], "2026-10-23T12:10+08:00")
        self.assertEqual(result["wait_minutes"], 12)

    def test_coupon_end_is_exclusive(self):
        offer = self.one()
        offer["valid_to"] = "2026-10-23T12:04+08:00"
        self.assertIsNone(plan(self.data)["recommendation"])
        offer["valid_to"] = "2026-10-23T12:05+08:00"
        self.assertIsNotNone(plan(self.data)["recommendation"])

    def test_overnight_window_from_previous_day(self):
        offer = self.one()
        self.data.update(now="2026-10-24T00:10+08:00", free_until="2026-10-24T01:10+08:00")
        offer.update(valid_from="2026-10-23T00:00+08:00", valid_to="2026-10-25T23:59+08:00", daily_windows=[["22:00", "02:00"]])
        self.assertEqual(plan(self.data)["recommendation"]["order_at"], "2026-10-24T00:24+08:00")

    def test_second_daily_window_used(self):
        offer = self.one()
        offer["daily_windows"] = [["07:00", "10:00"], ["12:10", "14:00"]]
        self.assertEqual(plan(self.data)["recommendation"]["order_at"], "2026-10-23T12:10+08:00")

    def test_timezone_normalization(self):
        self.data["now"] = "2026-10-23T03:50:00Z"
        self.assertEqual(plan(self.data)["recommendation"]["return_at"], "2026-10-23T12:32+08:00")

    def test_unverified_real_offer_is_excluded(self):
        offer = self.one()
        self.data["source"] = "mcp"
        offer["verified"] = False
        result = plan(self.data)
        self.assertIsNone(result["recommendation"])
        self.assertTrue(any("尚未核对" in x for x in result["excluded"][0]["reasons"]))

    def test_missing_price_and_evidence_not_filled_in(self):
        offer = self.one()
        self.data["source"] = "mcp"
        offer.update(price_fen=None, evidence="")
        reasons = plan(self.data)["excluded"][0]["reasons"]
        self.assertIn("尚未确认价格", reasons)
        self.assertIn("缺少 MCP 原文依据", reasons)

    def test_zero_price_and_budget_valid(self):
        offer = self.one()
        self.data["budget_fen"] = 0
        offer["price_fen"] = 0
        self.assertIsNotNone(plan(self.data)["recommendation"])

    def test_sort_price_vs_earliest_return(self):
        self.data["offers"] = self.data["offers"][:2]
        self.data["offers"][0]["valid_from"] = "2026-10-23T12:10+08:00"
        self.assertEqual(plan(self.data)["recommendation"]["id"], "lunch-a")
        self.data["strategy"] = "time"
        self.assertEqual(plan(self.data)["recommendation"]["id"], "lunch-b")

    def test_invalid_numbers_rejected(self):
        for key, value in [("budget_fen", 25.01), ("travel_minutes", -1), ("meal_minutes", True), ("meal_minutes", 0)]:
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(self.data)
                data[key] = value
                with self.assertRaises(ValidationError):
                    plan(data)

    def test_invalid_dates_and_duplicate_ids(self):
        for key, value in [("now", "bad"), ("free_until", "2026-10-23T11:00+08:00"), ("free_until", "2026-10-25T13:00+08:00")]:
            data = copy.deepcopy(self.data)
            data[key] = value
            with self.assertRaises(ValidationError):
                plan(data)
        self.data["offers"][1]["id"] = self.data["offers"][0]["id"]
        with self.assertRaises(ValidationError):
            plan(self.data)

    def test_input_is_not_mutated(self):
        before = copy.deepcopy(self.data)
        plan(self.data)
        self.assertEqual(before, self.data)

    def test_ics_utc_time_buffer_and_line_folding(self):
        offer = self.one()
        offer["name"] = "中文逗号,分号;反斜杠\\换行\n" * 5
        text = calendar(plan(self.data))
        self.assertIn("DTSTART:20261023T035000Z", text)
        self.assertIn("DTEND:20261023T044200Z", text)
        self.assertTrue(all(len(line.encode()) <= 75 for line in text.split("\r\n")))
        unfolded = text.replace("\r\n ", "")
        self.assertIn("\\,", unfolded)
        self.assertIn("\\;", unfolded)
        self.assertIn("\\n", unfolded)
        self.assertIn("[演示]", unfolded)
        self.assertTrue(text.endswith("END:VCALENDAR\r\n"))

    def test_no_calendar_without_feasible_plan(self):
        self.data["budget_fen"] = 1
        with self.assertRaises(ValidationError):
            calendar(plan(self.data))

    def test_report_preserves_source_and_exclusion(self):
        text = report(plan(self.data))
        self.assertIn("演示数据", text)
        self.assertIn("优惠已过期", text)


if __name__ == "__main__":
    unittest.main()
