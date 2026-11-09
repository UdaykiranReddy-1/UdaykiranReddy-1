"""Layout, caption, and SVG invariants for the Silk Board board."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import silk_board as sb


def window_ending(end: date, counts: dict[date, int]) -> list[dict]:
    days = []
    for offset in range(27, -1, -1):
        day = end - timedelta(days=offset)
        days.append({"date": day.isoformat(), "count": counts.get(day, 0)})
    return days


class TrafficTests(unittest.TestCase):
    def setUp(self):
        # Monday 9 Nov 2026. Saturday the 7th is the busy day.
        self.days = window_ending(
            date(2026, 11, 9),
            {date(2026, 11, 1): 1, date(2026, 11, 6): 2, date(2026, 11, 7): 7},
        )
        self.week = self.days[-7:]

    def test_status_is_clearing_when_the_jam_was_yesterday(self):
        self.assertEqual(sb.status_of(self.week), "CLEARING")
        info = sb.caption(self.week)
        self.assertIn("Saturday left 7", info["detail"])
        self.assertIn("pothole", info["detail"])
        self.assertIn("CLEARING", info["headline"])
        self.assertNotIn("Google", info["detail"])

    def test_empty_week_is_a_cow_not_a_fleet(self):
        days = window_ending(date(2026, 11, 9), {})
        self.assertEqual(sb.status_of(days[-7:]), "EMPTY")
        self.assertIn("cow", sb.caption(days[-7:])["detail"].lower())

    def test_sunday_gets_the_cow_and_a_busy_sunday_does_not(self):
        cows = sb.cow_indexes(self.week)
        sunday = next(
            i for i, day in enumerate(self.week) if date.fromisoformat(day["date"]).weekday() == 6
        )
        self.assertEqual(cows, {sunday})

        busy = window_ending(date(2026, 11, 9), {date(2026, 11, 8): 3, date(2026, 11, 4): 0})
        cows = sb.cow_indexes(busy[-7:])
        self.assertNotIn(sunday, cows)
        self.assertEqual(len(cows), 1)

    def test_glyphs_fit_their_day_slot(self):
        slot = sb.slot_geometry()[0]["w"]
        for count in range(0, 30):
            spec = sb.spec_for(count, "cow" if count == 0 else "pothole")
            self.assertLessEqual(sb.packed_width(spec), slot - 8, msg=count)
        self.assertEqual(sb.spec_for(1, "pothole")[0][0], "bike")
        self.assertEqual(sb.spec_for(2, "pothole")[0][0], "auto")
        self.assertIn("bus", [name for name, _ in sb.spec_for(7, "pothole")])

    def test_layout_stays_on_the_carriageway(self):
        placed = sb.layout(self.week)
        self.assertEqual(len(placed), 7)
        for group in placed:
            for glyph in group["glyphs"]:
                self.assertGreaterEqual(glyph["x"], sb.SLOT_LEFT - 1)
                self.assertLessEqual(glyph["x"] + glyph["w"], sb.SLOT_RIGHT + 1)

    def test_svg_is_animated_and_self_contained(self):
        for name in ("light", "dark"):
            svg = sb.render_svg(self.days, name, date(2026, 11, 9))
            self.assertIn("<animateTransform", svg)
            self.assertIn("SILK BOARD", svg)
            self.assertIn("CLEARING", svg)
            self.assertNotIn("<script", svg)
            self.assertNotIn("foreignObject", svg)
            self.assertNotIn("@import", svg)
            self.assertNotIn("fonts.googleapis", svg)
            self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg)
        light = sb.render_svg(self.days, "light", date(2026, 11, 9))
        dark = sb.render_svg(self.days, "dark", date(2026, 11, 9))
        self.assertNotEqual(light, dark)
        self.assertIn("#f4eee4", light)
        self.assertIn("#0c1016", dark)

    def test_readme_block_replacement(self):
        text = "before\n<!-- silk-board:start -->\nold\n<!-- silk-board:end -->\nafter\n"
        updated = sb.replace_block(text, "silk-board", "<picture></picture>")
        self.assertIn("<picture></picture>", updated)
        self.assertNotIn("old", updated)
        self.assertTrue(updated.startswith("before\n"))
        self.assertTrue(updated.endswith("after\n"))


if __name__ == "__main__":
    unittest.main()
