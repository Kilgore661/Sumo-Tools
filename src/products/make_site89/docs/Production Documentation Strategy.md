# Production documentation strategy for The Sumo '89 Lab

**Status after scope clarification:** The agreed writing requirements are now recorded in [Elo89 Account Requirements](Elo89%20Account%20Requirements.html). They supersede this proposal's site-wide scope, three reading routes, chapter arrangement and writing budgets. This document remains a repository review and source map. Its proposed website overview and local tool documentation are outside the present writing task; its findings about Elo89 and its evidence remain useful source material.

Prepared 11 September 2026. Proposal based on repository inspection, including the saved production bundle. This is a strategy for a new account, not a revision of earlier drafts, a fresh model appraisal, or a certification of the deployed website.

The recommendation is **one editorial account with three independently useful reading routes**: using the tools, understanding Elo-89, and examining its foundations and evidence. Publish it as a short guide with linked chapters and an optional continuous reading view. Keep concise explanations alongside the tools. This accommodates substantial material without requiring every visitor to read a book, or making expanding menus carry the argument.

The central subject is what the site helps us understand about sumo. Elo-89 deserves a substantial account because it contributes an interpretation to the record. It should neither swallow the account of the other tools nor be introduced apologetically as something the reader must first learn to distrust.

**What has reached the production candidate**

The development has moved from a broad exploratory workbench, through the mixed assembly-and-analysis architecture of `make_site2`, to a separate production chain. `src.analysis.site89` produces a coherent bundle; `make_site89` validates and presents it. Seven rating-dependent producers consume the same Elo-89 run. Model-independent outputs are also produced from the selected post-1988 History.

The saved bundle inspected here covers January 1989–July 2026 and contains 579,426 rated bouts. Its source archive's filename ends in `2026_11`, but the manifest's actual represented endpoint is July. That is a useful example of why public coverage statements must come from the represented data. “Current” should mean current to the displayed update, not implicitly current to the reader's visit.

The implementation record reports automated checks, local deployment and a broad human sanity check. This inspection has not repeated those checks. It supports treating the package as the candidate described by the user; it does not establish that replacement of `make_site2` has occurred.

The site definition and producers supply the following product story. Some items sit in research navigation or have legacy status, so the final public tour must follow the actual published navigation rather than advertise every registered artifact.

| Reader's question | Existing tools to explain | Essential interpretation |
| --- | --- | --- |
| What happened, and where do rikishi stand? | Basho Results; Most Recent Banzuke | Results and official placement, with additional rating fields where offered. Distinguish the date of the banzuke from the date of the results and ratings. |
| How has my favourite developed? | Rikishi History / Career Comparisons | Rank and rating trajectories, selectable wrestlers and time coordinates. Explain truncated careers and the meaning of the chosen axis. |
| Who has done particularly well? | Rolling Wins-Based Ranking; Rating Changes; Highest Elo-89 Rating | Different questions: accumulated wins, change in rating, and peak rating. State the window and denominator instead of calling all three “form”. |
| What records and career patterns can we see? | Consecutive bouts, career wins/losses, longest careers, career length, rank at retirement | These are calculations over a represented record with explicit inclusion and retirement conventions. “Observed since 1989” is not necessarily a complete lifetime record. |
| How has sumo's structure changed? | Banzuke and Makuuchi Structure by Era; Division Persistence; First Chii Appearance | Counts, positions and historical coverage have context. First observed appearance is not necessarily historical invention. |
| What usually happens from a given rank? | Finish Chances by Wins; Win Probability by Ranks | Empirical frequencies need their population, period and sample sizes. Modelled traces need a separate explanation. |

The last distinction is especially concrete: the current Win Probability by Ranks producer compares observed rank-pair outcomes with probabilities computed from the fixed entrant-prior map. The modelled curve is not an average of actual pre-bout Elo-89 forecasts. Likewise, Typical Elo-89 Ratings is a legacy-status artifact: an entrant landmark and an empirical average of established wrestlers' ratings must not be treated as interchangeable.

The current GOATs shortcut opens a selected career comparison. It should not be described as publishing the separate GOAT research package. Highest Elo-89 is specifically a maximum over recorded day-end ratings.

**The lesson from earlier accounts**

The earlier writing has already identified most of the right distinctions. `Reader Layers` says that deeper reading should never reveal that the simple account was false. `Narrative and Validation Structure` separates construction from evidence of usefulness. The consolidated-story proposal offers three reading routes. The local Notes and Gloss design reserves short explanations for the immediate chart or table. Those principles should survive.

What should change is the organizing story. Much of the previous material introduces ordinary Elo, follows problems into Equelo, visits successive experiments, and eventually reaches a selected model. That was useful while the decision was moving. A production reader needs the selected answer first, with the history available when it explains a choice.

The latest appraisal and normalisation investigation also record decisions that should remain settled in the new account: retain Elo-89; accept the measured normalisation effects with disclosure; distinguish inactivity from leaving the represented population; regard prospective evaluation as additional evidence rather than an unmet permission to publish. Old “next steps” and doubts should not be carried forward just because they appear in a compelling earlier passage.

The foundational essays contribute a useful philosophical discipline: make each interpretive addition to the observations visible. Their formal vocabulary need not become the opening language of a sumo website.

**Three reading routes, with a common vocabulary**

Do not label visitors “casual”, “fan” or “expert” in the navigation. Offer tasks: “Read the tools”, “Understand the ratings”, and “Examine the method and evidence”. A knowledgeable sumo follower may want only a quick result today; a newcomer may be a statistician.

| Route | Reader should be able to do afterwards | Proposed reading budget |
| --- | --- | --- |
| Read the tools | Choose a useful view; interpret rank, rating and rating change; understand the coverage boundary | A 600–900-word site introduction and a 500–800-word rating guide, independently readable |
| Understand the ratings | Follow the update calculation, interpret the probability curve, explain the K policy, priors and common mean | About 2,500–3,500 words across two or three chapters, with worked examples |
| Examine the method and evidence | Reconstruct the model, assess the empirical claims and challenge its assumptions | About 3,000–5,000 words of specification and appraisal, supported by separately linked evidence |

These are editorial budgets, not a requirement to write to length. A compact monograph of roughly 7,000–10,000 words is plausible. The reading routes allow a visitor to use a few hundred words of it. Three entirely separate accounts would multiply maintenance and encourage contradictions; a single compulsory progression would make experts wade through elementary material and ordinary readers abandon the account.

Use a shared sequence of questions at each depth: what is being compared, how does new evidence change it, how does a wrestler enter, how is time handled, and why should we use the result? Each route should reach a useful stopping point rather than end with “you must read the next chapter”.

**The first route: begin with sumo and a usable comparison**

The opening account should describe the site as a collection of ways to examine results, careers, records and the changing banzuke from January 1989 onward. Credit SumoDB prominently. Then distinguish recorded facts, summaries calculated from those facts, and estimates added by Elo-89. Even a model-independent summary has choices about population, elapsed time, absences and incomplete careers; it deserves a clear definition, although not a rating-theory essay.

Introduce ratings beside a reader's likely question: two rikishi have similar records, but did they face comparable opposition? Explain that chii gives an official position with institutional meaning, while Elo-89 supplies an opponent-sensitive account of the represented results. A rating disagreement is something to investigate, not an automatic verdict on the banzuke.

Use one explicitly illustrative pair throughout the guide. With q=400, a 200-point advantage gives about a 76% model probability; a 400-point advantage gives about 91%. Showing 2300 versus 2100 and then 1800 versus 1600 demonstrates why the gap matters. Do not inherit numerical examples from drafts written around other probability scales.

The short account must also say:

- A probability allows an upset; it is not a promise or a confidence interval for the rating.
- A bout win raises the winner's rating through the bout update. A displayed change over a longer interval also includes the model's common adjustments and, where applicable, reinitialisation.
- No new eligible bouts means no individual bout update. A retained rating is not a report on an inactive wrestler's physical condition.
- Historical comparisons use the same model and its anchor; they are conditional comparisons, not measurements of absolute ability across eras.

These qualifications can be short. They cannot be hidden exclusively in the technical route because they change how the visible numbers should be read.

**The second route: explain Elo-89 directly**

Teach the ordinary Elo update inside the explanation of the deployed model. Give the probability equation, a graph against rating difference, and one win/loss example. Explain q as the unit scale of the probability curve and K as the size of the response to new evidence. Larger K produces faster response and more fluctuation; division is the chosen proxy, not a measured uncertainty attached to each person.

Then introduce the open population. A makuuchi-focused display does not define a makuuchi-only calculation. Wrestlers bring earlier results with them as they move through divisions, and bouts and careers connect the groups. The same network that makes lower-division evidence relevant also limits what can be inferred when connections or observations are weak. Connectedness alone is not proof that every comparison is equally well supported.

Explain P1 as a fixed table used when a wrestler first enters the represented population, including the initial January 1989 population and later re-entries. Explain its construction only after its function is clear. Rank supplies starting evidence; subsequent ratings are not continually forced back onto a rank curve.

Next explain the two basho-boundary common shifts. At a given instant a common shift changes neither ordering nor rating gaps nor model probabilities. Across time, however, the policy affects survivors' relationship to future entrants assigned fixed P1 values. It also contributes to displayed rating changes. This distinction supplies an intelligible reason for normalisation without calling it either harmless bookkeeping in every respect or a fatal distortion.

Distinguish equal-K zero-sum bouts from cross-K updates. The production equations are:

`p = 1 / (1 + 10^((R_b - R_a)/400))`

`delta_a = K_a * (s_a - p)` and `delta_b = -K_b * (s_a - p)`.

The sum is zero when the K values agree; it need not be zero otherwise. A table of the deployed K values and a cross-boundary example should accompany this explanation.

Finish with what the evidence says, in ordinary language, and links to the exact evaluation. Do not require the reader to learn the succession of historical model names to understand the current one.

**The third route: specification and critical account are different jobs**

Provide a concise exact specification that a specialist can reach directly. It should define the eligible outcomes, treatment of defaults and blank kimarite, identity, event ordering, initialisation, fallback, departure and return, K schedule, and snapshots used by each publication. Define the represented population exactly: the replay uses the banzuke population plus participants in selected rated bouts. “Active” here does not mean “fought today”.

Record the fixed mean as the mean of the first initialized represented population. Identify the frozen P1 artifact and its construction settings separately from the replay settings. Canonical P1 comes from the maintained q=400 BKP1 construction; the earlier contextual M/J blending policy in story document 10 is historical evidence, not a substitute specification. Explain fixed-point iteration, support-dependent recentering and retained anomalies from the applicable P1 sources, including what was observed to converge and what has not been proved unique.

The critical account should then address five questions without treating every question as a demand to redesign the model:

| Question | Required answer |
| --- | --- |
| What does “strength” mean here? | An operational interpretation through ratings and model probabilities. Separate the precision of the calculation from uncertainty about ability and the purposes of the comparison. |
| What does the anchor establish? | The convention used for a common scale, its instantaneous invariances, and the assumptions behind comparisons over time. A fixed mean alone does not establish invariant physical ability across eras. |
| How informed are the initial ratings? | Their exact provenance, historical information used, construction choices and demonstrated sensitivity. Stable iteration is not proof of a uniquely true rank-to-ability curve. |
| What evidence favours Elo-89? | Declared metrics and comparable runs, including less favourable diagnostics and relevant population differences. Separate retrospective selection from future validation. |
| What does this compact model leave unrepresented? | Individual estimate uncertainty, contextual influences and alternative meanings of performance. Explain the relevance of uncertainty-aware alternatives without claiming an unperformed comparison with Glicko. |

Do not attempt an encyclopaedia of rating systems. A reader asking about another system deserves a precise statement of what Elo-89 maintains and what has actually been compared. Claims about external mathematical results or other systems should be checked against primary sources when those passages are written; this repository review is not that literature verification.

**Presenting what is known, and how it is known**

The internal writing process should classify substantive statements as definitions, mathematical consequences, empirical findings, modelling judgements or open questions. The public prose can express these naturally: “we define”, “this shift preserves”, “in this comparison”, “we chose”, and “we have not tested”. These distinctions are more useful than repeatedly describing everything as experimental.

The selected model's recorded comparison reports log loss 0.675629 against 0.682753 for Basic Elo and 0.693147 for 50–50. Present these as results of the specified 574,863-bout retrospective comparison. Brier loss supports the selection; the earlier informed-prior model retains a slightly better aggregate calibration-error result. Do not translate log loss into a percentage of correct predictions, or transfer predecessor-model maturity diagnostics to Elo-89 without matching their provenance.

The production manifest contains 579,426 rated bouts. The chii-baseline account explicitly records the source-snapshot difference and the additional exclusions used in that probe. Keep evaluation snapshots distinct from production snapshots. If a later publication wants a new matched comparison, run and identify it separately; accurately describing the existing comparison does not require reopening model selection.

Following chii is an obvious baseline and the repository now measures it. That winner-selection probe does not establish that Elo-89 picks more winners than chii on a matched sample. Giving a deterministic rule probabilities of zero and one also does not create a fair general test of whether rank contains useful predictive information. The documentation should not claim “Elo beats the banzuke” from the existing results.

For normalisation, lead with the settled judgement: its observed effects were accepted, while some individual rating changes can be appreciably affected. The documented May 1992 Konishiki example is excellent teaching material: approximately -26.132 bout points plus +30.363 adjustment points gives +4.231 overall. This makes the distinction tangible without arguing that the model should be replaced.

Keep the recent ±1% result in the evidence account, with its denominator and scope. It concerns net signed contributions divided by ending ratings over 51 overlapping 12-basho windows, not percentages of the rating change, predictive error, or lifetime contribution. Include the full-history context. Subtracting contributions from an observed history is accounting, not a replay of the counterfactual model without normalisation.

**Handling all divisions without overwhelming the visitor**

Use makuuchi as the opening example and usual starting view where appropriate, while making the selected division visible. Let readers expand to juryo, a neighbouring division, or all divisions. A display filter must never appear to change the rating population or refit the model.

Use three recurring examples: an established makuuchi pair for rating differences; a wrestler crossing a divisional boundary for history, priors and K; and a lower-division example for limited evidence. This keeps the explanation concrete while showing why the full population matters. Choose real examples from the saved run during authoring and preserve their dates and observation stages.

For historical structure, introduce distinctions only when needed: chii labels, order within a particular banzuke, and positions relative to a changing division boundary. Avoid describing rank positions as evenly spaced units of strength. Describe formal rules, customary patterns and discretionary judgements separately rather than asserting that sumo has no rules or implying that the JSA follows a fully published numerical algorithm.

The lowest-division presentation deserves an explicit editorial decision. My recommendation is to retain access for continuity and inspection, but avoid presenting fine rating differences there as a validated precise hierarchy. The normalisation investigation expressly leaves the rationale for publishing ratings in the difficult lowest region open. Keeping those wrestlers in the calculation and promoting a fine-grained public ranking are separate decisions; recording this distinction does not require removing data or changing Elo-89.

Explain the 1989 boundary proportionately. Earlier records contain substantial information; their completeness varies by division and period. The historical extension encountered difficulties relating incomplete lower-division evidence to the common rating scale. The production choice limits scope to the better-supported period while that work is on hold. Neither “nothing is known before 1989” nor “everything after January 1989 is perfectly complete” is justified by the repository's audit.

**Publication shape and authoring sequence**

Use six chapter destinations: the site's tools; reading ratings; how Elo-89 works; the exact model; evidence and judgement; data and definitions. Give each a short opening answer, a contents list and direct links to deeper sections. Offer continuous reading or printing from the same content if convenient. Use expandable material for ancillary derivations or examples, not to hide qualifications essential to the main claim.

Local help has a separate role. Each table or chart needs a question, its population and period, the definition of its values, and a route to the relevant explanation. Examples include the distinction between raw day-end and normalized basho-end ratings; what “normalised” means for a particular rating-change column; treatment of absences and defaults; and whether career totals are truncated. Most of this should take sentences, not chapters. Reuse the existing Notes and Gloss experience without duplicating the guide in tooltips.

Write in this order:

1. Assemble a compact source-and-claim register for the current model and published tools. Include actual run identifiers, snapshot dates, definitions and the source of every numerical example.
2. Draft the exact model specification and evidence account first, as internal working chapters. This fixes the meaning that shorter explanations must preserve.
3. Write the site introduction and short rating guide around the reader's questions. Then write the fan-level explanation linking the two depths.
4. Add a small, deliberate set of illustrations: rating gap versus probability; one annotated career crossing a boundary; and a worked breakdown of rating change. Add an empirical calibration figure only with its specific model and sample identified.
5. Put short explanations beside the actual published tools and connect them to the chapters. Check direct entry, rather than assuming readers arrive via Home.
6. Review each reading route for comprehension and consistency, then publish the documentation with its model and data version recorded.

Completion means a reader can correctly interpret a rating, distinguish an official rank from a model estimate, understand a displayed change, find the coverage boundary, and follow a quantitative claim to its evidence. A specialist should be able to identify the precise model without searching the research chronology. Check the illustrative arithmetic, the published links and the correspondence between captions and selected views.

This writing programme does not require new rating research, a Glicko implementation, a prospective evaluation, or a general site redesign. Such work can extend the evidence later. The present task is to express a selected and usable model clearly, including the reasons for accepting its limitations.

**Source map for the writing work**

- Production scope and development: [Implementation Plan](Implementation%20Plan.md), [production handoff](../../../analysis/docs/story/21%20Elo-89%20Website%20Production%20Handoff.md), [site definition](../site_definition.py), and [saved bundle manifest](../../../../files/output/analysis/site89_bundle/manifest.json).
- Earlier editorial experience: [Reader Layers](../../../analysis/docs/story/01%20Reader%20Layers.md), [Narrative and Validation Structure](../../../analysis/docs/story/02%20Narrative%20and%20Validation%20Structure.md), [consolidated-story proposal](../../../analysis/docs/story/13%20Proposal%20for%20the%20Consolidated%20Elo-like%20Ratings%20Story.md), [Notes and Gloss](../../make_site2/docs/11%20Notes%20and%20Gloss.md), and [legacy site overview](../../../../docs/Elo%20v.9%20Site%20Overview.md).
- Current mechanics: [production replay](../../../analysis/elo89/replay.py), [prior producer account](../../../analysis/equelo_bkp1/README.md), [Tranche 1 decisions](../../../analysis/docs/story/15%20Tranche%201%20-%20Population%20Normalisation%20Policy.md), and [saved rating manifest](../../../../files/output/analysis/site89_bundle/sources/elo89/manifest.json).
- Interpretation and accepted limitations: [Elo-89 appraisal](../../../analysis/docs/story/22%20Elo-89%20Rating%20System%20Appraisal.md), [normalisation investigation](../../../analysis/elo89_normalisation/docs/Normalisation%20Investigation.md), and [foundational account](../../../../docs/Foundations/01-what-is-this-about.md).
- Historical scope and comparison discipline: [completeness audit](../../../analysis/docs/story/17%20Pre-1989%20Bout-Data%20Completeness%20and%20Rating%20Persistence.md), [Elo-58 status](../../../analysis/docs/story/20%20Elo-58%20and%20the%20Reserved%20Equelo2%20Name.md), and [chii baseline findings](../../../analysis/chii_prediction/docs/Findings.md).
- Display semantics: [rank-probability producer](../../../analysis/site89/win_probability.py), [rating-change producer](../../../analysis/site89/rating_changes.py), and [peak-rating producer](../../../analysis/site89/highest_rating.py).
