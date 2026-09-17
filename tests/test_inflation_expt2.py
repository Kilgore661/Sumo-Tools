"""Conservation, indirect provenance, persistent gaps and saved replay."""

import json
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace as NS
import unittest

import numpy as np

from src.analysis.inflation.expt2.core import Holdings
from src.analysis.inflation.expt2.__main__ import generate, parser
from src.analysis.inflation.expt2.inspect import restore, profile, resolve_person, aggregate, export


def fixture():
    from src.sumo_core.BasicEnums import Outcome
    from src.sumo_core.Chii import Chii
    from src.analysis.elo_model_selection.model import AdoptedPrior

    def basho(ids, pairs):
        summary = {}
        for day, (a, b) in enumerate(pairs, 1):
            summary[day] = NS(results_lookup={(a, b): NS(
                rikishi1=a, rikishi2=b, outcome1=Outcome.W, outcome2=Outcome.L)})
        return NS(banzuke=NS(riks=set(ids), rikchii={i: Chii.from_str("M1e") for i in ids},
                            rikshik={i: f"Rikishi {i}" for i in ids}),
                  summary=summary)
    history = {"1989/01": basho([1, 2, 3, 4], [(2, 3), (1, 2)]),
               "1989/03": basho([1, 2, 4], [(1, 4)]),
               "1989/05": basho([1, 2, 3, 4], [(3, 1), (4, 2)]),
               "1989/07": basho([1, 2, 4], [])}
    prior = AdoptedPrior(source_path="fixture", sha256="fixture", rating_by_pair={"M1": 1000.}, fallback_rating=1000.)
    return history, prior


class ProvenanceTests(unittest.TestCase):
    def test_worked_example_and_departure(self):
        s = Holdings(4)
        for i in range(4):
            s.enter(i, 1000)
        s.transfer(1, 2, 20, 20)
        s.transfer(0, 1, 20, 20)
        self.assertAlmostEqual(s.matrix[0, 2], 20*20/1020)
        s.transfer(2, 3, 20, 20)
        np.testing.assert_allclose(s.matrix.sum(axis=0), [1000]*4)
        s.leave(2)
        frozen = s.matrix[2].copy()
        s.transfer(0, 3, 20, 20)
        np.testing.assert_array_equal(s.matrix[2], frozen)
        self.assertEqual(s.matrix[2, 3], 20)
        self.assertGreater(s.matrix[0, 2], 0)
        s.audit()

    def test_unequal_k_scales_same_origins(self):
        s = Holdings(3)
        for i in range(3):
            s.enter(i, 1000)
        s.transfer(1, 2, 20, 20)
        p = s.matrix[1].copy()/1020
        s.transfer(0, 1, 8, 10)
        np.testing.assert_allclose(s.matrix[0] - [1000, 0, 0], 8*p)
        np.testing.assert_allclose(s.created, -2*p)
        s.audit()

    def test_actual_bout_numbers(self):
        s = Holdings(4)
        for i, value in enumerate([1500, 1000, 1500, 1200]):
            s.enter(i, value)
        s.bout(0, 1, True, 35, 35)
        s.bout(2, 1, True, 35, 35)
        s.bout(1, 3, True, 35, 35)
        self.assertAlmostEqual(s.ratings[1], 1023.0187677061849)
        self.assertAlmostEqual(s.ratings[3], 1173.2732507185856)
        s.audit()

    def test_multiple_gaps_resume_without_allocation(self):
        s = Holdings(3)
        for i in range(3):
            s.enter(i, 1000)
        s.transfer(0, 1, 20, 20)
        row = s.matrix[0].copy()
        allocated = s.allocated.copy()
        for _ in range(2):
            s.leave(0)
            s.transfer(1, 2, 10, 10)
            s.resume(0)
            np.testing.assert_array_equal(row, s.matrix[0])
            np.testing.assert_array_equal(allocated, s.allocated)
            self.assertEqual(s.ratings[0], 1020)
        with self.assertRaises(ValueError):
            s.resume(0)
        s.audit()

    def test_fail_on_invalid_partition_domain(self):
        s = Holdings(2)
        s.enter(0, 1)
        s.enter(1, 1000)
        with self.assertRaises(ValueError):
            s.transfer(1, 0, 5, 5)
        with self.assertRaises(ValueError):
            s.enter(0, 10)

    def test_live_store_is_default(self):
        args = parser().parse_args([])
        self.assertIsNone(args.history_zip)
        self.assertIsNone(args.end)

    def test_full_fixture_and_postrun_reconstruction(self):
        h, prior = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = generate(h, prior, lambda ordinal: 40., root, None)
            self.assertEqual(summary["included_bouts"], 5)
            self.assertEqual(summary["excluded_return_bouts"], 0)
            self.assertEqual(summary["returner_ids"], 1)
            self.assertEqual(summary["gap_count"], 1)
            db = sqlite3.connect(root / "record.sqlite")
            db.row_factory = sqlite3.Row
            final = np.load(root / "holdings.npy")
            reconstructed = restore(db, 4, summary["events"])
            np.testing.assert_array_equal(reconstructed, final)
            jan = db.execute("SELECT event_id FROM observations WHERE date='1989/01' AND endpoint='end' LIMIT 1").fetchone()[0]
            old = restore(db, 4, jan)
            self.assertGreater(old[0, 2], 0)
            gap = db.execute("SELECT * FROM gaps").fetchone()
            gap_before = restore(db, 4, gap['start_event'])
            gap_after = restore(db, 4, gap['end_event'])
            np.testing.assert_array_equal(gap_before[2], gap_after[2])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events WHERE kind='enter' AND a=2").fetchone()[0], 1)
            # Independent scalar replay of all five bouts, without any reset.
            r = [1000.]*4
            for a, b in [(1, 2), (0, 1), (0, 3), (2, 0), (3, 1)]:
                d = 40*(1-1/(1+10**((r[b]-r[a])/400)))
                r[a] += d
                r[b] -= d
            np.testing.assert_allclose(final.sum(axis=1), r)
            p = profile(root, db, summary, resolve_person(db, "1"))
            self.assertAlmostEqual(sum(x["held"] for x in p["rows"]), p["rating"])
            c = next(x for x in p["rows"] if x["rikid"] == 3)
            self.assertEqual(c["status"], "departed non-donor")
            during_gap = profile(root, db, summary, resolve_person(db, "1"), "1989/03", "end")
            gap_c = next(x for x in during_gap["rows"] if x["rikid"] == 3)
            self.assertEqual(gap_c['status'], 'temporary gap')
            self.assertEqual(gap_c['removed'], 0)
            self.assertIsNone(gap_c['deficit'])
            self.assertAlmostEqual(sum(x["held"] for x in aggregate(p["rows"])), p["rating"])
            early = profile(root, db, summary, resolve_person(db, "1"), "1989/01", "start")
            self.assertTrue(all(x["status"] == "active" for x in early["rows"]))
            self.assertEqual(early["rating"], 1000)
            retired = profile(root, db, summary, resolve_person(db, "3"))
            self.assertEqual(retired["date"], "1989/05")
            export(root / "view", [p], {"model": "synthetic fixture", "start": "1989/01", "end": "1989/05"})
            html = (root / "view/explorer.html").read_text(encoding="utf-8")
            self.assertNotIn("/*DATA*/null", html)
            self.assertIn("Plotly.react", html)
            db.close()


if __name__ == "__main__":
    unittest.main()
