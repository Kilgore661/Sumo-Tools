"""Infer promotion events from banzuke; evaluate the preceding evidence."""

from collections import Counter

from src.sumo_core.BasicEnums import MSD, Outcome


def classify(window):
    """Three-valued predicate: missing evidence is not a negative observation."""
    if len(window) != 3 or any(row['rank'] is None for row in window):
        return 'unknown'
    if not all(row['sanyaku'] for row in window):
        return 'false_negative'
    # Observed wins alone can prove >=33, even if some bouts are missing.
    if sum(row['wins'] for row in window) >= 33:
        return 'true_positive'
    if not all(row['recorded_bouts'] == 15 for row in window):
        return 'unknown'
    return 'false_negative'


def analyse_history(history):
    dates = sorted(history)
    if not dates:
        raise ValueError('Promotion analysis requires a non-empty History')
    events, evidence, boundary, excluded = [], [], [], []
    for index, date in enumerate(dates):
        banzuke = history(date).banzuke
        previous = history(dates[index - 1]).banzuke if index else None
        for rid in sorted(banzuke.riks):
            if banzuke.rikchii[rid].level != MSD.OZEKI:
                continue
            prior_chii = previous.rikchii.get(rid) if previous else None
            if prior_chii is None:
                boundary.append(dict(rikishi_id=int(rid), shikona=str(banzuke.rikshik[rid]),
                                     basho=str(date), reason='No adjacent prior rank; entry is not a confirmed promotion'))
            elif prior_chii.level not in {MSD.OZEKI, MSD.YOKOZUNA}:
                event_id = f'{date}:{int(rid)}'
                window = []
                for prior_date in dates[max(0, index - 3):index]:
                    state = history(prior_date)
                    chii = state.banzuke.rikchii.get(rid)
                    counts = Counter()
                    for day, daily in state.summary.items():
                        if int(day) > 15:
                            continue  # Championship playoffs do not add record wins.
                        outcomes = []
                        for bout in daily.results_lookup.values():
                            if bout.rikishi1 == rid:
                                outcomes.append(bout.outcome1)
                            elif bout.rikishi2 == rid:
                                outcomes.append(bout.outcome2)
                        if len(outcomes) > 1:
                            raise ValueError(f'Multiple regular results: {prior_date}, day {day}, rikishi {rid}')
                        counts.update(outcomes)
                    row = dict(event_id=event_id, rikishi_id=int(rid), basho=str(prior_date),
                               rank=str(chii) if chii is not None else None,
                               sanyaku=chii is not None and chii.level in {MSD.KOMUSUBI, MSD.SEKIWAKE},
                               wins=counts[Outcome.W] + counts[Outcome.FS],
                               fusensho=counts[Outcome.FS],
                               losses=counts[Outcome.L] + counts[Outcome.FP],
                               draws=counts[Outcome.DRAW], recorded_bouts=sum(counts.values()),
                               source='history')
                    window.append(row)
                # Explicit user-supplied boundary evidence; do not alter History
                # or invent a rank number/side or a fusensho breakdown.
                if (int(rid) == 3910 and str(date) == '1958/05'
                        and [r['basho'] for r in window] == ['1958/01', '1958/03']):
                    window.insert(0, dict(event_id=event_id, rikishi_id=int(rid),
                                          basho='1957/11', rank='S', sanyaku=True,
                                          wins=10, fusensho=None, losses=5, draws=0,
                                          recorded_bouts=15, source='user_supplied'))
                status = classify(window)
                pre_demotion = history(dates[index - 2]).banzuke.rikchii.get(rid) if index >= 2 else None
                reinstatement = (pre_demotion is not None
                                 and pre_demotion.level == MSD.OZEKI
                                 and prior_chii.level == MSD.SEKIWAKE
                                 and window[-1]['wins'] >= 10)
                event = dict(event_id=event_id, rikishi_id=int(rid),
                                   shikona=str(banzuke.rikshik[rid]),
                                   decision_after_basho=str(dates[index - 1]),
                                   first_ozeki_banzuke=str(date),
                                   kind=('immediate_reinstatement' if reinstatement else
                                         'qualification'),
                                   prior_rank=str(prior_chii),
                                   sequence='; '.join(f"{r['basho']} {r['rank']} {r['wins']}-{r['losses']}" for r in window),
                                   wins_observed=sum(r['wins'] for r in window),
                                   three_sanyaku=len(window) == 3 and all(r['sanyaku'] for r in window),
                                   complete_45_bouts=len(window) == 3 and all(r['recorded_bouts'] == 15 for r in window),
                                   classification='excluded' if reinstatement else status)
                if reinstatement:
                    excluded.append(event)
                else:
                    events.append(event)
                    evidence.extend(window)
    return dict(events=events, evidence=evidence, boundary=boundary, excluded=excluded,
                basho_dates=[str(d) for d in dates])
