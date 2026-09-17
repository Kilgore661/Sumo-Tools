"""Transition accounting distinguishes gaps, final departures and initial stock."""
import tempfile
from pathlib import Path
import unittest
import csv
from test_inflation_expt2 import fixture
from src.analysis.inflation.expt2.__main__ import generate
from src.analysis.inflation.expt1.__main__ import report


class TurnoverTests(unittest.TestCase):
    def test_gap_and_departure_reconciliation(self):
        history, prior=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            generate(history,prior,lambda _:40.,root,None)
            s=report(root,root/'views',{d:set(h.banzuke.riks) for d,h in history.items()})
            with (root/'views/transitions.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(float(rows[0]['points_added']),4000)
            self.assertEqual(float(rows[1]['donor_points']),0)
            self.assertEqual(float(rows[1]['gap_points_out']),980)
            self.assertEqual(float(rows[2]['gap_points_in']),980)
            self.assertEqual(float(rows[2]['new_allocations']),0)
            self.assertEqual(s['final_departures'],1)
            self.assertEqual(s['points_added'],980)
            self.assertEqual(s['donor_points_new_cohort'],0)
            self.assertLess(s['max_reconciliation_error'],1e-6)
            self.assertEqual(s['non_banzuke_observations'],0)


if __name__=='__main__': unittest.main()
