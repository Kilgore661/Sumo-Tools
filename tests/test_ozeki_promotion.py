from types import SimpleNamespace

from src.analysis.promotion.ozeki.analysis import analyse_history, classify
from src.sumo_core.BasicEnums import Outcome
from src.sumo_core.Chii import Chii
from src.sumo_core.History import History, Date


def window(wins=(11, 11, 11), ranks=(True, True, True), bouts=(15, 15, 15)):
    return [dict(rank='S1e' if rank else 'M1e', sanyaku=rank,
                 wins=win, recorded_bouts=count)
            for win, rank, count in zip(wins, ranks, bouts)]


def test_predicate_distinguishes_rank_total_and_missing_evidence():
    assert classify(window()) == 'true_positive'
    assert classify(window((10, 11, 11))) == 'false_negative'
    assert classify(window((13, 12, 12), (False, True, True))) == 'false_negative'
    assert classify(window((10, 11, 11), bouts=(14, 15, 15))) == 'unknown'
    assert classify(window()[:2]) == 'unknown'
    assert classify(window(bouts=(11, 11, 11))) == 'true_positive'


def state(rank, wins=0, fusen=False, playoff=False):
    days = {}
    if wins:
        for day in range(1, 16 + int(playoff)):
            outcome = Outcome.W if day <= wins or day == 16 else Outcome.L
            if fusen and day == 1:
                outcome = Outcome.FS
            bout = SimpleNamespace(rikishi1=1, rikishi2=2, outcome1=outcome,
                                   outcome2=Outcome.L if outcome in {Outcome.W, Outcome.FS} else Outcome.W)
            days[day] = SimpleNamespace(results_lookup={1: bout})
    return SimpleNamespace(banzuke=SimpleNamespace(
        riks={1}, rikchii={1: Chii.from_str(rank)}, rikshik={1: 'Example'}), summary=days)


def test_events_use_held_basho_include_fusen_exclude_playoff_and_split_returns():
    history = History()
    for month, rank, wins in [(1, 'K1e', 11), (3, 'S1e', 11),
                              (7, 'S1e', 11), (9, 'O1e', 0),
                              (11, 'S1e', 10)]:
        history[Date(2020, month)] = state(rank, wins, fusen=True, playoff=True)
    history[Date(2021, 1)] = state('O1e')
    result = analyse_history(history)
    first, = result['events']
    returned, = result['excluded']
    assert first['classification'] == 'true_positive'
    assert first['wins_observed'] == 33
    assert first['decision_after_basho'] == '2020/07'
    assert first['kind'] == 'qualification'
    assert all(r['fusensho'] == 1 for r in result['evidence'][:3])
    assert returned['kind'] == 'immediate_reinstatement'
    assert returned['classification'] == 'excluded'


def test_initial_ozeki_is_not_a_promotion_and_reinstatement_needs_only_two_prior_basho():
    history = History()
    history[Date(1958, 1)] = state('O1e')
    history[Date(1958, 3)] = state('S1e', 12)
    history[Date(1958, 5)] = state('O1e')
    result = analyse_history(history)
    assert len(result['boundary']) == 1
    assert not result['events']
    assert result['excluded'][0]['kind'] == 'immediate_reinstatement'


def test_later_requalification_is_retained():
    history = History()
    for month, rank, wins in [(1, 'O1e', 0), (3, 'S1e', 9),
                              (5, 'K1e', 11), (7, 'S1e', 11),
                              (9, 'S1e', 11), (11, 'O1e', 0)]:
        history[Date(2020, month)] = state(rank, wins)
    result = analyse_history(history)
    assert not result['excluded']
    event, = result['events']
    assert event['kind'] == 'qualification'
    assert event['classification'] == 'true_positive'


def test_32_win_threshold_does_not_change_rank_conditions():
    from src.analysis.promotion.ozeki.candidates import qualifying_windows
    history = History()
    for month, rank, wins in [(1, 'K1e', 10), (3, 'S1e', 11),
                              (5, 'S1e', 11), (7, 'O1e', 0)]:
        history[Date(2020, month)] = state(rank, wins)
    assert not qualifying_windows(history)
    rows = qualifying_windows(history, minimum_total_wins=32)
    assert len(rows) == 1 and rows[0]['classification'] == 'true_positive'
    history[Date(2020, 1)] = state('M1e', 10)
    assert not qualifying_windows(history, minimum_total_wins=32)
    assert len(qualifying_windows(history, minimum_total_wins=32,
                                  allow_maegashira_start=True)) == 1


def test_evaluator_scores_and_orchestrator_saves_seven_json_files():
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from src.analysis.promotion.ozeki.evaluate_rule import evaluate_rule
    from src.analysis.promotion.ozeki.score_rules import run_comparison
    history = History()
    for month, rank, wins in [(1, 'K1e', 10), (3, 'S1e', 11),
                              (5, 'S1e', 11), (7, 'O1e', 0)]:
        history[Date(2020, month)] = state(rank, wins)
    result = evaluate_rule(history, 'A', 32)
    assert (result['tp'], result['fp'], result['fn'], result['f1']) == (1, 0, 0, 1.0)
    result = evaluate_rule(history, 'A', 33)
    assert (result['tp'], result['fp'], result['fn'], result['f1']) == (0, 0, 1, 0.0)
    with TemporaryDirectory() as directory:
        report = run_comparison(history, directory, source='synthetic_test')
        assert {p.name for p in Path(directory).glob('*.json')} == {
            'A31.json', 'A32.json', 'A33.json', 'B31.json', 'B32.json', 'B33.json', 'C33.json'}
        saved = json.loads((Path(directory) / 'A32.json').read_text(encoding='utf-8'))
        assert saved['source'] == 'synthetic_test'
        assert saved['f1'] == 1.0
        assert 'A31, A32, B31, B32' in report.read_text(encoding='utf-8')
    for rule, threshold in [('D', 33), ('A', -1), ('A', 46), ('A', 32.5)]:
        try:
            evaluate_rule(history, rule, threshold)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid rule or threshold accepted')


def test_kotogahama_user_supplied_boundary_record():
    history = History()
    for month, rank, wins in [(1, 'S1e', 11), (3, 'S1e', 13), (5, 'O1e', 0)]:
        item = state(rank, wins)
        item.banzuke.riks = {3910}
        item.banzuke.rikchii = {3910: Chii.from_str(rank)}
        item.banzuke.rikshik = {3910: 'Kotogahama'}
        for daily in item.summary.values():
            daily.results_lookup[1].rikishi1 = 3910
        history[Date(1958, month)] = item
    result = analyse_history(history)
    event, = result['events']
    assert event['wins_observed'] == 34
    assert event['classification'] == 'true_positive'
    assert result['evidence'][0]['source'] == 'user_supplied'
    assert result['evidence'][0]['rank'] == 'S'
    assert result['evidence'][0]['fusensho'] is None


def test_qualifying_windows_keep_overlaps_and_do_not_infer_future_promotion():
    from src.analysis.promotion.ozeki.candidates import qualifying_windows
    history = History()
    for month, rank, wins in [(1, 'K1e', 10), (3, 'S1e', 14),
                              (5, 'S1e', 10), (7, 'S1e', 9),
                              (9, 'S1e', 14)]:
        history[Date(2020, month)] = state(rank, wins)
    rows = qualifying_windows(history)
    assert [r['wins'] for r in rows] == [34, 33, 33]
    assert [r['classification'] for r in rows] == ['false_positive', 'false_positive', 'unresolved']
    strict = qualifying_windows(history, minimum_basho_wins=10)
    assert len(strict) == 1
    assert strict[0]['wins'] == 34
    assert strict[0]['classification'] == 'false_positive'
    history[Date(2020, 11)] = state('O1e')
    rows = qualifying_windows(history)
    assert [r['classification'] for r in rows] == ['false_positive', 'false_positive', 'true_positive']
    history[Date(2020, 1)] = state('M1e', 10)
    assert len(qualifying_windows(history)) == 2
    assert len(qualifying_windows(history, allow_maegashira_start=True)) == 3
    history[Date(2020, 3)] = state('M1e', 14)
    expanded = qualifying_windows(history, allow_maegashira_start=True)
    assert len(expanded) == 2  # M in the second basho still disqualifies a run.
