# Elo89 documentation hand-off

Updated 12 September 2026. **Documentation work is postponed until the proposed
per-chii drift study has been run and its findings reviewed.** The next step is
the [analysis proposal](../../../analysis/elo89_normalisation/docs/Proposal%20-%20Per-Chii%20Rating%20Drift.md),
not further drafting. The study has not yet been implemented or run. This
pause does not imply a decision to change the model.

## Where we are

The deliverable is an account of Elo89, not of the whole Sumo Tools website.
The website overview will sit elsewhere and reference this account. Readers
self-select through descriptive headings as the narrative progresses from
simple interpretation through mathematics to evidence and open questions.

The [contents](Elo89%20Account%20-%20Contents.html) is the maintained outline.
[Requirements](Elo89%20Account%20Requirements.html) records the writing policy.
Sections 1–4 are saved. Section 7, [Where Do Initial Ratings Come
From?](Elo89%20Account%20-%2007%20Where%20Do%20Initial%20Ratings%20Come%20From.html),
is now saved and explicitly labelled **draft**. It preserves the agreed
opening and the construction/evidence discussion reached in conversation;
it is not a completed specification. Sections 5, 6 and 8–11 are not drafted.

## Next work

1. Implement and run the proposed per-chii drift study, including its
   verification checks, then review the findings and their limits.
2. Resume the normalisation account using that evidence. The proposed
   standalone section on connected divisions has been dropped: treating the
   banzuke as one population needs no separate argument here. Organise the
   material around pre-basho, post-basho and post-iteration normalisation;
   settle headings and numbering when drafting resumes.
3. Revisit draft section 7 in light of those explanations. Resolve its draft
   dependency paragraph into reader-facing prose and cross-references, and
   complete the construction details as needed.

This order is intentional: initial ratings are calculated with population
handling and mean adjustments already in place. Explaining them afterwards
would leave a dependency unexplained. Do not proceed directly with section 7
as though the preceding normalisation material had already settled its
presentation. Section 7 retains its current number while the outline is paused.

The specific unresolved empirical question is whether ratings at individual
chii trend through historical time after population mean preservation. The
completed contribution study and prior-iteration convergence do not answer
that question. A preserved global mean establishes no drift in that mean;
it does not establish stable ratings at each chii. The new study should
inform the wording without being presented as a causal test of normalisation.

## Decisions to preserve

- Initialisation delay is a problem even in a fixed population. Keep that
  argument separate from arrivals and departures. The yokozuna-versus-lowest-
  jonokuchi example illustrates the implications of equal starting ratings.
- Discuss the effect of entrants' initial ratings on rating mass in section 6;
  explain their construction in section 7. The user's inflation question is
  about sumo; use the recorded evidence to distinguish total, mean and drift.
- Use “revised estimate”, not an assertion that every fixed-point pass is an
  improvement in accuracy. Self-consistency, plausibility and forecast
  performance are different claims.
- The new map pools **basho-start** ratings at each chii across the replay; it
  is not the map from the final basho alone.
- The retained producer starts all chii at 1517. The saved run stopped after
  18 passes, with maximum consecutive-map change 9.574785971992469, below a
  ten-point tolerance. Do not turn this into a theorem about indefinite
  iteration, a unique limit or distance from that limit.
- Small changes between passes do not establish stability across historical
  periods, datasets or modelling policies. Claims about those need separate
  evidence.
- The production table gives rounded values Y 2428, O 2301, S 2253, K 2213,
  M1 2258 and J1 2101. It is not strictly decreasing with chii. Use the saved
  production table, not an earlier experimental table, for public examples.
- Retrospective forecast evidence exists, but the priors use the history
  being scored. Do not describe this as unseen-data or prospective validation.
  Numerical findings are reproducible; judging adequacy involves judgement.

## Crucial model distinction for sections 6 and 7

The retained prior producer and the subsequent Elo89 replay use different
population operations. Do not silently treat them as the same algorithm.

The producer in `src/analysis/equelo_bkp1/` uses departure redistribution during
each replay. Between passes it restores the unweighted chii-map mean to 1517,
allocating the correction in proportion to each chii's observation count.
That operation can change map differences; it is not a uniform shift.

The subsequent Elo89 replay in `src/analysis/elo89/replay.py` holds the
converted prior table fixed and preserves the active population mean with
common shifts. The recorded target mean is approximately 1569.6961, not 1517.
The producer's map also undergoes grouping and averaging before consumption;
the ten-point stopping criterion belongs to the producer, before conversion.

The authority is the [Tranche 1 record](../../../analysis/docs/story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md),
especially its final decision to retain the externally constructed prior while
selecting whole-population preservation for Elo89. Earlier
`10 Initial Rating Policy.md` describes an older contextual blend and must not
be mistaken for the production construction.

Useful sources:

- [Producer README](../../../analysis/equelo_bkp1/README.md),
  [solver](../../../analysis/equelo_bkp1/solve.py),
  [replay](../../../analysis/equelo_bkp1/simulate.py) and
  [recentering](../../../analysis/equelo_bkp1/recenter.py).
- [Producer manifest](../../../../files/output/analysis/equelo_bkp1/manifest.json)
  and [iteration record](../../../../files/output/analysis/equelo_bkp1/iterations.csv).
- [Conversion](../../../analysis/equelo_population_policy/predict_candidate.py),
  function `load_alpha_prior`, with rank grouping defined through
  `rank_pair` in `src/analysis/elo_model_selection/model.py`.
- [Saved production prior](../../../../files/output/analysis/site89_bundle/sources/elo89/prior.csv)
  and [production manifest](../../../../files/output/analysis/site89_bundle/sources/elo89/manifest.json).
- [Normalisation investigation](../../../analysis/elo89_normalisation/docs/Normalisation%20Investigation.md).

## Research discussion retained for later use

Do not attribute to Élő a theorem that arbitrary starting ratings converge to
true ability in a permanent, fixed-skill population. The passages checked in
his book support a more qualified account:

- §1.67, printed page 14, describes a self-correcting process and discusses
  new entrants: [source](https://gwern.net/doc/statistics/order/comparison/1978-elo-theratingofchessplayerspastandpresent.pdf#page=30).
- §3.41, printed page 44, repeatedly fits an existing collection of results
  from equal starting ratings. This differs from the ongoing update process:
  [source](https://gwern.net/doc/statistics/order/comparison/1978-elo-theratingofchessplayerspastandpresent.pdf#page=60).
- The project's [fixed-skill forgetting investigation](../../../analysis/forgetting/docs/Completed%20Investigation%20-%20Forgetting%20in%20a%20Fixed-Skill%20Toy%20World.md)
  distinguishes loss of sensitivity to initialisation from ratings settling
  at true values. Its finite experimental results are conditional on its toy
  world, not automatically transferable to historical sumo.
- [Cortez and Tossounian](https://arxiv.org/html/2410.09180v2) study a stationary
  distribution under specified assumptions. This is another meaning of
  convergence, distinct from convergence of the prior-construction passes.

These distinctions belong in the later scientific account as needed; do not
overload the accessible opening. FIDE's use of Elo provides precedent, not
validation of Elo89's particular choices.

## Editorial and persistence notes

Files whose names begin `Elo89 Account` are maintained as HTML with CDN
MathJax. Other documents, including this hand-off, remain Markdown. Use
sans-serif text, centred borderless tables and right-aligned numerical cells.
Section 3 already has the CDN Plotly logistic curve.

Section 4 retains the k discussion; there is no separate rate-of-change
section. The contents retains eleven numbered positions pending reorganisation.
Its former section 5 topic is withdrawn; the space for preceding normalisation
material and its eventual numbering will be resolved after the study.

The conversation also proposed explicitly adding `p(d) + p(-d) = 1` to section
3 and connecting probability to expected score. The former is not yet saved
there; section 4 already gives the expected-score calculation. This is a
pending editorial item, not a reason to interrupt the agreed work on 5 and 6.

Historical worked examples were deferred. Do not reinsert the discussed
Kirishima–Fujinokawa example as evidence that probabilities are accurate
because they feel plausible. Keep peripheral questions and personal JSA
skepticism in [Matters Arising](Elo89%20Account%20-%20Matters%20Arising.html).

The documentation checkpoint includes the saved sections 4 and 7, the analysis
proposal, and this postponement decision. The unrelated untracked root file
`teleological.txt` belongs to the user and must be left alone.
