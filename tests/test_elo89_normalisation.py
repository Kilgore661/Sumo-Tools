"""Hand-calculated regressions for independent normalisation accounting."""

import json
import csv
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.analysis.elo89_normalisation.accounting import reconstruct, reconcile_site
from src.analysis.elo89_normalisation.inputs import safe_output, load_inputs
from src.analysis.elo89_normalisation.summary import build_summaries, describe
from src.analysis.elo89_normalisation.__main__ import build_parser, load_history
from src.analysis.elo89_normalisation.division_percentages import division_table, recent_sekitori_table


def fixture():
    dates = ["1989/01", "1989/03", "1989/05"]
    starts = {dates[0]: {"1": 110., "2": 90.}, dates[1]: {"2": 100., "3": 100.},
              dates[2]: {"1": 120., "2": 93., "3": 87.}}
    ends = {dates[0]: {"1": 120., "2": 80.}, dates[1]: {"2": 103., "3": 97.},
            dates[2]: {"1": 125., "2": 90., "3": 85.}}
    adjustments = {date: {"start_adjustment": pre, "end_adjustment": post}
                   for date, pre, post in zip(dates, (0., 20., -10.), (0., -1., -1.))}
    bouts = {(dates[0], "1"): 10., (dates[0], "2"): -10., (dates[1], "2"): 4.,
             (dates[1], "3"): -2., (dates[2], "1"): 6., (dates[2], "2"): -2.,
             (dates[2], "3"): -1.}
    metadata = {date: {rid: {"name": f"R{rid}", "chii": "M1e", "division": "makuuchi"}
                       for rid in values} for date, values in starts.items()}
    metadata[dates[0]]["2"]["division"] = "juryo"
    metadata[dates[2]]["3"]["division"] = "unclassified"
    return SimpleNamespace(dates=dates, starts=starts, ends=ends, adjustments=adjustments,
                           bouts=bouts, counts={key: 1 for key in bouts}, metadata=metadata)


class AccountingTests(unittest.TestCase):
    def test_continuous_and_returning_windows(self):
        frame, exclusions = reconstruct(fixture(), (1, 2))
        pair = frame[frame.window == 2].set_index("rikishi_id")
        b = pair.loc[2]
        self.assertEqual((b.bout, b.pre, b.post, b.reset, b.change), (2., 10., -2., 0., 10.))
        self.assertEqual(b.status, "continuous")
        self.assertFalse(b.makuuchi_throughout)
        a = pair.loc[1]
        self.assertEqual((a.bout, a.pre, a.post, a.reset, a.change), (6., -10., -1., 10., 5.))
        self.assertEqual(a.status, "reset")
        self.assertEqual(a.represented_basho, 1)
        self.assertEqual(a.reset_count, 1)
        self.assertEqual(frame.residual.abs().max(), 0)
        self.assertEqual(len(pair), 2)  # Debutant 3 has no January endpoint.
        self.assertEqual(exclusions.iloc[0].missing_start, 1)
        self.assertEqual(exclusions.iloc[0].missing_end, 1)

    def test_one_basho_excludes_start_endpoint_contributions(self):
        frame, _ = reconstruct(fixture(), (1,))
        row = frame[(frame.end_date == "1989/05") & (frame.rikishi_id == 2)].iloc[0]
        self.assertEqual((row.bout, row.pre, row.post, row.change), (-2., -10., -1., -13.))

    def test_no_bouts_and_common_gap_invariance(self):
        value = fixture()
        date = "1989/05"
        for rid in value.starts[date]:
            value.bouts[date, rid] = 0.
            value.counts[date, rid] = 0
            value.ends[date][rid] = value.starts[date][rid] - 1
        frame, _ = reconstruct(value, (1,))
        b = frame[(frame.rikishi_id == 2) & (frame.end_date == date)].iloc[0]
        self.assertEqual((b.bout, b.bout_count, b.change), (0, 0, -11))
        self.assertEqual(value.starts[date]["1"] - value.starts[date]["2"],
                         value.ends[date]["1"] - value.ends[date]["2"])

    def test_reconciliation_rejects_corrupt_rating(self):
        value = fixture()
        value.ends["1989/05"]["1"] += 0.01
        with self.assertRaisesRegex(ValueError, "Basho accounting"):
            reconstruct(value)

    def test_multiple_returns(self):
        value = fixture()
        value.dates += ["1989/07", "1989/09"]
        for date, ratings, pre in (("1989/07", {"2": 100., "3": 95.}, 10.),
                                   ("1989/09", {"1": 120., "2": 90., "3": 85.}, -10.)):
            value.starts[date] = ratings
            value.ends[date] = ratings.copy()
            value.adjustments[date] = {"start_adjustment": pre, "end_adjustment": 0.}
            value.metadata[date] = {rid: {"name": rid, "chii": "", "division": "unclassified"}
                                    for rid in ratings}
        frame, _ = reconstruct(value, (4,))
        row = frame[frame.rikishi_id == 1].iloc[0]
        self.assertEqual((row.reset_count, row.reset, row.change, row.residual), (2, 15, 0, 0))

    def test_site_reconciliation_and_rounding(self):
        frame, _ = reconstruct(fixture(), (1, 2))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for n, group in frame[frame.end_date == "1989/05"].groupby("window"):
                rows = group.rename(columns={"change": "delta", "start_rating": "rating_at_start",
                                             "end_rating": "rating_at_end"})
                rows.to_csv(root / f"1989-05 {n}-change.csv", index=False, float_format="%.3f")
            self.assertEqual(reconcile_site(frame, root), 4)
            path = root / "1989-05 2-change.csv"
            path.write_text(path.read_text().replace("125.000", "126.000"))
            with self.assertRaises(ValueError):
                reconcile_site(frame, root)


class SummaryAndInputTests(unittest.TestCase):
    def test_statistics_and_reset_separation(self):
        d = describe([-4, 0, 2, 10])
        self.assertEqual(d["p25"], -1)
        self.assertEqual(d["abs_p50"], 3)
        self.assertEqual(d["mean_absolute"], 4)
        frame, _ = reconstruct(fixture(), (1, 2))
        summaries, comparisons, exceptions = build_summaries(frame)
        row = comparisons[(comparisons.population == "all") & (comparisons.window == 2)
                          & (comparisons.endpoint == "all")].iloc[0]
        self.assertEqual(row["count"], 1)
        self.assertEqual(row.mean_ratio, 4)
        self.assertTrue((summaries.status == "reset").any())
        self.assertTrue((exceptions.reason == "reset").any())

    def test_zero_denominator(self):
        frame, _ = reconstruct(fixture(), (1,))
        frame["bout"] = 0.
        _, comparisons, _ = build_summaries(frame)
        self.assertTrue(comparisons.mean_ratio.isna().all())

    def test_output_overlap(self):
        root = Path(tempfile.gettempdir()) / "normalisation-test"
        for output in (root, root / "out", root.parent):
            with self.assertRaises(ValueError):
                safe_output(output, [root])
        safe_output(root / "out", [root / "inputs"])

    def test_live_default_and_explicit_zip(self):
        args = build_parser().parse_args([])
        self.assertIsNone(args.history_zip)
        self.assertEqual(args.output_root, Path("files/output/analysis/elo89_normalisation"))
        with patch("src.infra.live_store.api.get_history", return_value="live") as live:
            history, source = load_history(args)
            self.assertEqual((history, source["kind"]), ("live", "live_store"))
            live.assert_called_once_with()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "history.zip"
            path.write_bytes(b"test")
            args = build_parser().parse_args(["--history-zip", str(path)])
            with patch("src.infra.persistence.annotated_serialiser.load_history_with_annotations",
                       return_value="zip") as loader:
                history, source = load_history(args)
                self.assertEqual((history, source["kind"]), ("zip", "history_zip"))
                self.assertEqual(len(source["sha256"]), 64)
                loader.assert_called_once_with(str(path.with_suffix("")))


class DivisionPercentageTests(unittest.TestCase):
    def test_recent_selection_uses_start_date_and_end_division(self):
        import pandas as pd
        frame = pd.DataFrame({
            "window": [12, 12, 12, 12, 12, 6],
            "status": ["continuous", "continuous", "continuous", "continuous", "reset", "continuous"],
            "start_date": ["2015/11", "2016/01", "2016/03", "2016/01", "2016/01", "2016/01"],
            "end_date": ["2018/01"] * 6,
            "end_division": ["makuuchi", "makuuchi", "juryo", "makushita", "juryo", "juryo"],
            "end_rating": [1000.] * 6, "normalisation": [999., 10., -10., 999., 999., 999.],
        })
        table, selected = recent_sekitori_table(frame)
        self.assertEqual(len(selected), 2)
        self.assertEqual(set(table.division), {"makuuchi", "juryo"})
        self.assertEqual(table.observations.sum(), 2)
        self.assertEqual(table.within_1_count.sum(), 2)
        self.assertEqual(table.outside_1_count.sum(), 0)

    def test_signed_means_inclusive_thresholds_and_selection(self):
        import pandas as pd
        frame = pd.DataFrame({
            "window": [12] * 7 + [6], "status": ["continuous"] * 6 + ["reset", "continuous"],
            "end_division": ["makuuchi"] * 8, "end_rating": [1000.] * 8,
            "normalisation": [-50., -10., 10., 50., 60., -60., 900., 900.],
        })
        table, selected = division_table(frame)
        row = table[table.division == "all"].iloc[0]
        self.assertEqual(len(selected), 6)
        self.assertEqual(row.mean_signed_percentage, 0)
        self.assertEqual(row.within_1_count, 2)
        self.assertEqual(row.within_5_count, 4)
        self.assertEqual(row.below_minus_5_count, 1)
        self.assertEqual(row.above_plus_5_count, 1)
        frame.loc[0, "end_rating"] = 0
        with self.assertRaisesRegex(ValueError, "positive finite"):
            division_table(frame)


class ArtifactValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        dates = ["1989/01", "1989/03"]
        self.history = {date: SimpleNamespace(banzuke=SimpleNamespace(
            riks={1, 2}, rikchii={}, rikshik={1: "A", 2: "B"})) for date in dates}
        self.snapshots = {date: {"1": 100., "2": 100.} for date in dates}
        for name in ("basho_start_ratings", "basho_end_ratings"):
            (self.root / f"{name}.json").write_text(json.dumps(self.snapshots))
        with (self.root / "basho_adjustments.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=("date", "active_count", "new_rikishi_count",
                "departing_rikishi_count", "target_mean", "raw_start_mean", "start_adjustment",
                "raw_end_mean", "end_adjustment"))
            writer.writeheader()
            for i, date in enumerate(dates):
                writer.writerow(dict(date=date, active_count=2, new_rikishi_count=2 if i == 0 else 0,
                    departing_rikishi_count=0, target_mean=100, raw_start_mean=100,
                    start_adjustment=0, raw_end_mean=100, end_adjustment=0))
        (self.root / "bout_ledger.csv").write_text("date,day,rikishi_a,rikishi_b,a_won\n")
        self.manifest = {"model_id": "elo-89", "history": {"start": dates[0], "end": dates[-1]},
            "target_mean": 100, "selection": {"rated_bout_count": 0}, "files": {
                name: f"{name}.{'json' if 'ratings' in name else 'csv'}" for name in
                ("basho_start_ratings", "basho_end_ratings", "basho_adjustments", "bout_ledger")}}
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))
        patcher = patch("src.analysis.prediction.bouts.select_rated_bouts",
                        return_value=SimpleNamespace(bouts=[]))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_valid_inputs_and_unchanged_check(self):
        value = load_inputs(self.root, self.history)
        self.assertEqual(len(value.history_digest), 64)
        (self.root / "manifest.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "Input changed"):
            value.verify_unchanged()

    def test_mismatched_history_coverage(self):
        del self.history["1989/03"]
        with self.assertRaisesRegex(ValueError, "different represented dates"):
            load_inputs(self.root, self.history)

    def test_invalid_artifact_path(self):
        self.manifest["files"]["bout_ledger"] = "../elsewhere.csv"
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "outside input root"):
            load_inputs(self.root, self.history)

    def test_mismatched_active_population(self):
        self.history["1989/03"].banzuke.riks = {1}
        with self.assertRaisesRegex(ValueError, "Active snapshots differ"):
            load_inputs(self.root, self.history)


if __name__ == "__main__":
    unittest.main()
