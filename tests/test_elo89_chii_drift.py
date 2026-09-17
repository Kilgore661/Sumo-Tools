"""Contract tests for drift, weighting, missing support and calendar sensitivity."""

from copy import deepcopy
from types import SimpleNamespace
import unittest

import numpy as np
import pandas as pd

from src.analysis.elo89_normalisation.chii_drift import (
    build_parser, build_tables, calendar_year, make_observations, period_start,
)
from src.sumo_core.Chii import Chii


def observations(dates, upper, lower=None):
    """Two equally sized divisions with a preserved mean of 100 points."""
    if lower is None:
        lower = 200 - np.asarray(upper)
    rows = []
    for i, (date, a, b) in enumerate(zip(dates, upper, lower)):
        for rid, rating, literal, group, division, ordinal in (
            (1, a, "M1e", "M1", "makuuchi", 1), (2, b, "J1e", "J1", "juryo", 2),
        ):
            rows.append(dict(date=date, basho_index=i, rikishi_id=rid, name=f"R{rid}",
                             literal=literal, numbered=group, title="", ordinal=ordinal,
                             rank_number=1, division=division, start=rating, end=rating,
                             first_observed=i == 0, returning=False, duplicate_position=False))
    return pd.DataFrame(rows)


class DriftTests(unittest.TestCase):
    def test_fixed_mean_with_divergent_groups_and_irregular_dates(self):
        dates = ["1989/01", "1991/07", "1999/01", "2004/01"]
        ratings = [100 + 2 * (calendar_year(d) - 1989) for d in dates]
        tables = build_tables(observations(dates, ratings), dates, 100.)
        trend = tables.trends.query("level == 'numbered' and group == 'M1' and endpoint == 'end' and selection == 'full'").iloc[0]
        self.assertAlmostEqual(trend.slope_points_per_decade, 20.)
        self.assertFalse(trend.eligible)
        self.assertLess(tables.population.query("division == 'all'").mean_residual.abs().max(), 1e-9)
        self.assertAlmostEqual(tables.gaps.query("endpoint == 'end'").gap.iloc[-1], 60.)

    def test_reversal_is_visible_despite_zero_net_slope(self):
        dates = ["1989/01", "1994/01", "1999/01", "2004/01", "2009/01"]
        tables = build_tables(observations(dates, [100, 120, 140, 120, 100]), dates, 100.)
        trend = tables.trends.query("level == 'numbered' and group == 'M1' and endpoint == 'end' and selection == 'full'").iloc[0]
        self.assertAlmostEqual(trend.slope_points_per_decade, 0., places=8)
        self.assertEqual(trend.first_last_period_change, 0.)
        self.assertEqual(trend.period_range, 40.)

    def test_basho_weighting_not_occupant_weighting(self):
        dates = ["1989/01", "1989/03"]
        frame = observations(dates, [100., 130.])
        extra = frame.iloc[[2]].copy()
        extra["rikishi_id"], extra["literal"] = 3, "M1w"
        frame = pd.concat([frame, extra], ignore_index=True)
        frame.loc[(frame.date == dates[1]) & (frame.numbered == "J1"), ["start", "end"]] = 40.
        tables = build_tables(frame, dates, 100.)
        period = tables.periods.query("level == 'numbered' and group == 'M1' and endpoint == 'end'").iloc[0]
        self.assertEqual(period["mean"], 115.)  # Occupant-weighted would be 120.
        self.assertEqual(period.occupant_observations, 3)
        self.assertEqual(period.basho_count, 2)
        self.assertEqual(period.distinct_rikishi, 2)

    def test_missing_positions_and_rolling_support(self):
        dates = [f"{1989+i//6}/{1+2*(i%6):02d}" for i in range(14)]
        frame = observations(dates, [100.] * 14)
        # Retain population membership but remove the rank for eight basho.
        absent = (frame.rikishi_id == 1) & frame.basho_index.isin(range(2, 10))
        frame.loc[absent, ["literal", "numbered"]] = ""
        tables = build_tables(frame, dates, 100.)
        series = tables.basho.query("level == 'numbered' and group == 'M1' and endpoint == 'end'")
        self.assertEqual(len(series), 6)
        self.assertTrue(series.rolling_mean.isna().all())  # Never six in a 12-basho window.
        self.assertEqual(series.rolling_count.iloc[-1], 4)
        self.assertEqual(tables.population.query("division == 'all'")["count"].min(), 2)

    def test_six_observations_required_and_endpoints_separate(self):
        dates = [f"1989/{m:02d}" for m in (1, 3, 5, 7, 9, 11)]
        frame = observations(dates, [110.] * 6)
        frame.loc[frame.rikishi_id == 1, "start"] = 100.
        frame.loc[frame.rikishi_id == 2, "start"] = 100.
        tables = build_tables(frame, dates, 100.)
        end = tables.basho.query("level == 'numbered' and group == 'M1' and endpoint == 'end'")
        start = tables.basho.query("level == 'numbered' and group == 'M1' and endpoint == 'start'")
        self.assertTrue(end.rolling_mean.iloc[:5].isna().all())
        self.assertEqual(end.rolling_mean.iloc[-1], 110.)
        self.assertEqual(start.rolling_mean.iloc[-1], 100.)

    def test_additive_shift_invariance(self):
        dates = ["1989/01", "1994/01", "2001/01", "2007/01"]
        frame = observations(dates, [100., 105., 115., 130.])
        base = build_tables(frame, dates, 100.)
        shifted = frame.copy()
        shifted[["start", "end"]] += 9876.5
        change = build_tables(shifted, dates, 9976.5)
        for column in ("slope_points_per_decade", "first_last_period_change", "period_range"):
            np.testing.assert_allclose(base.trends[column], change.trends[column], atol=1e-8)
        np.testing.assert_allclose(base.population.spread_90, change.population.spread_90, atol=1e-8)
        np.testing.assert_allclose(base.gaps.gap, change.gaps.gap, atol=1e-8)

    def test_period_boundaries_missing_period_and_sensitivity(self):
        dates = ["1989/01", "1993/11", "2004/01", "2026/07"]
        tables = build_tables(observations(dates, [100.] * 4), dates, 100.)
        self.assertEqual(period_start("1993/11"), 1989)
        self.assertEqual(period_start("1994/01"), 1994)
        self.assertEqual(period_start("2026/07"), 2024)
        recent = tables.trends.query("selection == 'since_2000'")
        self.assertTrue((recent.basho_count == 2).all())
        self.assertTrue((tables.trends.query("selection == 'exclude_first_12'").basho_count == 0).all())
        self.assertTrue(tables.periods.query("period_start == 2024").partial_calendar_period.all())
        missing = tables.periods.query("period_start == 1994")
        self.assertTrue(missing["mean"].isna().all())
        self.assertTrue((missing.basho_count == 0).all())
        self.assertTrue((missing.represented_basho_available == 0).all())

    def test_slope_eligibility_needs_both_count_and_span(self):
        dates = [f"{1989+i//6}/{1+2*(i%6):02d}" for i in range(61)]
        tables = build_tables(observations(dates, [100.] * 61), dates, 100.)
        self.assertTrue(tables.trends.query("selection == 'full'").eligible.all())
        short = build_tables(observations(dates[:-1], [100.] * 60), dates[:-1], 100.)
        self.assertFalse(short.trends.query("selection == 'full'").eligible.any())

    def test_wrong_global_mean_fails(self):
        dates = ["1989/01", "1989/03"]
        with self.assertRaisesRegex(ValueError, "Population reconciliation"):
            build_tables(observations(dates, [100., 101.], [100., 100.]), dates, 100.)

    def test_chii_identity_duplicates_numbered_titles_and_returns(self):
        dates = ["1989/01", "1989/03", "1989/05"]
        starts = {dates[0]: {"1": 100., "2": 100., "3": 100.}, dates[1]: {"2": 100.}, dates[2]: {"1": 100., "2": 100.}}
        labels = {dates[0]: {1: "Y1e", 2: "Y2w", 3: "Y1e"}, dates[1]: {2: "Y2w"}, dates[2]: {1: "Y1w", 2: "Y2w"}}
        history = {d: SimpleNamespace(banzuke=SimpleNamespace(rikchii={r: Chii.from_str(c) for r, c in labels[d].items()})) for d in dates}
        inputs = SimpleNamespace(dates=dates, starts=starts, ends=deepcopy(starts), metadata={d: {str(r): {"name": str(r), "chii": c, "division": "makuuchi"} for r, c in labels[d].items()} for d in dates})
        before = deepcopy(starts)
        frame = make_observations(inputs, history)
        self.assertEqual(set(frame.numbered), {"Y1", "Y2"})
        self.assertEqual(set(frame.title), {"Y"})
        self.assertEqual(frame.duplicate_position.sum(), 2)
        returned = frame[(frame.date == dates[-1]) & (frame.rikishi_id == 1)].iloc[0]
        self.assertTrue(returned.returning)
        self.assertFalse(returned.first_observed)
        self.assertEqual(returned.literal, "Y1w")
        self.assertEqual(starts, before)

    def test_cli_keeps_live_store_default(self):
        self.assertIsNone(build_parser().parse_args([]).history_zip)


if __name__ == "__main__":
    unittest.main()
