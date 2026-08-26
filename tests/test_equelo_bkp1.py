from __future__ import annotations

import pytest

from src.analysis.equelo_bkp1.params import MODEL_Q, expected_score
from src.analysis.equelo_bkp1.recenter import recenter
from src.analysis.equelo_bkp1.run import _parser
from src.sumo_core.Chii import Chii


def test_model_contract_fixes_q_at_400_and_has_no_q_option():
    assert MODEL_Q == 400.0
    assert expected_score(1600.0, 1200.0) == pytest.approx(10.0 / 11.0)
    with pytest.raises(SystemExit):
        _parser().parse_args(["--q", "900"])


def test_model_contract_fixes_support_proportional_recentering():
    a = Chii.from_str("M1e")
    b = Chii.from_str("J1e")
    result = recenter(
        {a: 1600.0, b: 1200.0},
        base=1500.0,
        support={a: 3, b: 1},
    )

    assert result.ratings[a] == pytest.approx(1750.0)
    assert result.ratings[b] == pytest.approx(1250.0)
