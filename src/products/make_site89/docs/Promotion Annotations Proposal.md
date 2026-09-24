# Promotion Annotations Proposal

## Status

Historical product proposal arising from the September 2026 discussion about
The Banzuke and Basho Results. It is retained because it records important
product context and rejected alternatives, but it is no longer the operative
implementation specification.

The authoritative requirements are now in
[Promotion Annotations - Final Proposal](Promotion%20Annotations%20-%20Final%20Proposal.md).
Before changing or extending them, read
[Promotion Annotations - Here Be Dragons](Promotion%20Annotations%20-%20Here%20Be%20Dragons.md),
which preserves the analytical and domain reasons not to turn the annotations
into probabilities or attempt an in-progress Yokozuna feasibility calculation.

No promotion-annotation implementation has yet been completed.

The rules and UI below are preserved as the initial hypothesis to be evaluated,
not as an operative implementation specification. A later product decision may
retain, revise or reject them independently for Yokozuna and Ozeki promotion.

The initial proposal treated the following conventional promotion guidelines
as rules to present on the public site:

- promotion to yokozuna requires two consecutive Makuuchi yusho while ranked
  ozeki; and
- promotion to ozeki requires at least 33 wins over three consecutive held
  basho, with the rikishi ranked sekiwake or komusubi in all three.

The repository also contains retrospective promotion-classification research
which documents historical exceptions, sparse categories and alternative
classifiers. The new statistical proposal makes review of that evidence a
prerequisite to choosing whether the public site should present a rule,
historical digest, qualified annotation, separate analysis page or nothing.

## Product context

The site has two related pages with different primary purposes.

### The Banzuke

The page formerly called **Most Recent Banzuke**, now **The Banzuke**, presents the current official
banzuke and its changes from the preceding banzuke. It is the go-to page after
a new banzuke is published, when there are not yet any results for the new
basho. Its East/West layout and movement context are designed to answer:

> What is the banzuke, and what changed when it was published?

The permanent navigation label and page title should be changed from **Most
Recent Banzuke** to **The Banzuke**. "New Banzuke" describes the page well only
for part of the cycle, while "Most Recent Banzuke" is accurate but less natural
as a destination label. **The Banzuke** remains meaningful throughout the
cycle. The rename and placement of The Banzuke before Basho Results in the Home
menu have been implemented.

### Basho Results

Basho Results is a date-selectable historical and current results browser. Its
primary question is:

> How is each rikishi doing, or how did each rikishi do, in the selected basho?

The optional Previous Basho view provides rank and result context. It also lets
a knowledgeable reader infer the changes into the selected banzuke, but that is
not the page's primary purpose.

The current public production does not refresh results during a basho. The
underlying daily result data is believed to be available; the missing part is
the production/publication path which makes the site use and refresh it. This
proposal assumes that a later implementation will publish Basho Results daily.

## Basho-cycle context

The public emphasis changes naturally during the cycle without changing the
identity of either navigation entry:

1. A new banzuke is published roughly two weeks before the basho. The Banzuke
   is the useful destination because the new basho has no results.
2. During the 15 days of competition, a daily-updated Basho Results page becomes
   the useful destination. Previous Basho may be enabled for context.
3. After the basho, Basho Results contains the final records.
4. Promotion announcements may be reported in the press, but the site does not
   currently ingest those announcements. The factual promotion outcome is known
   to the site when the following banzuke is published, returning the cycle to
   step 1.

The promotion annotations proposed here describe the opportunity a rikishi had
**on entering the displayed basho**. They do not claim that a promotion has
been decided, announced or predicted. This fixed meaning remains correct before,
during and after the basho, and on historical pages.

## Proposed presentation

Add sparse promotion annotations next to the displayed shikona on both The
Banzuke and Basho Results.

The annotation must be a separate rendered element associated with the shikona.
It must not be appended to the canonical shikona stored in producer data. This
preserves identity, SumoDB links, chart actions, text sorting and reuse of the
name elsewhere.

The initial compact notation is:

- `!` for a yokozuna promotion opportunity; and
- `(n)` for an ozeki promotion opportunity, where `n` is the number of wins
  required in the displayed basho to reach 33 over the three-basho window.

For example:

```text
Ozeki A !
Sekiwake B (12)
```

The final typography may use badges or superscript markers rather than literal
plain-text suffixes. Whatever visual treatment is chosen must have an accessible
text label and an on-page explanation. Suggested meanings are:

```text
!    Yokozuna opportunity: won the preceding yusho as ozeki.
(12) Ozeki opportunity: needs 12 wins here to reach 33 over three K/S basho.
```

No dedicated promotion column is proposed. Almost every cell in such a column
would be empty, and the information is naturally read as context about the
named rikishi. No separate promotion page is proposed at this stage.

## Yokozuna annotation rule

For a rikishi on the banzuke for basho `B`, show the yokozuna-opportunity
annotation when all of the following are true:

1. the rikishi is ranked ozeki at `B`;
2. the immediately preceding held basho `B-1` exists in the represented
   History;
3. the rikishi was ranked ozeki at `B-1`; and
4. the rikishi won the Makuuchi yusho at `B-1`.

Only the yusho marker counts for this public rule. Doten-yusho, jun-yusho and
broader retrospective classification rules are out of scope.

There is only one yusho winner, so this requires at most one annotation in the
ordinary case. The annotation says that a second consecutive yusho in `B` would
complete the adopted rule. The result shown alongside it records whether that
happened.

Example:

- Ozeki A wins the May yusho.
- A is still ozeki on the July banzuke and is shown as `A !`.
- During July, the daily score shows the progress of the attempt.
- After July, `A !` remains historically correct: it describes the opportunity
  on entering July, while the final result shows the outcome.

## Ozeki annotation rule

For a rikishi on the banzuke for basho `B`, consider the three consecutive held
basho `B-2`, `B-1` and `B`. Show an ozeki-opportunity annotation when:

1. all three basho exist in the represented History;
2. the rikishi is ranked sekiwake or komusubi in all three;
3. the recorded wins for `B-2` and `B-1` are available; and
4. `33 - wins(B-2) - wins(B-1)` is no greater than the maximum wins available
   in `B`.

Define:

```text
required_wins = 33 - wins(B-2) - wins(B-1)
```

Display the annotation as `(required_wins)`. It is fixed at the start of `B`;
it does not count down during the basho. The adjacent live score supplies the
progress.

Example:

- Sekiwake B records 10 wins and then 11 wins in the preceding two basho.
- B remains sekiwake or komusubi for the selected basho.
- The displayed annotation is `B (12)`.
- A final 8-7 record shows that the target was missed; a final 12-3 record shows
  that the numerical rule was achieved.

The literal initial rule does not impose a minimum number of wins in each of the
first two basho beyond what follows from the 33-win total and the 15-win maximum
in the third. Thus a mathematically possible unusual sequence is not excluded
merely because it looks unlike historical promotion runs. Any additional rule,
such as requiring three kachi-koshi or at least nine wins in a component basho,
must be an explicit later policy decision supported by a separate historical
review; it must not be introduced implicitly during implementation.

Wins should follow the repository's established promotion-analysis convention:
regular wins including fusensho and excluding playoffs. Cancelled tournaments
are not synthetic basho; "consecutive" means consecutive held basho represented
in History.

Immediate ozekiwake reinstatement is a different mechanism and is not represented
by this annotation.

## Temporal and historical semantics

Annotations must be calculated strictly **as of the start of the displayed
basho**. They may use the displayed banzuke and earlier banzukes/results, but
must not use the displayed basho's eventual result or any later banzuke to
decide whether to show the annotation.

This no-lookahead rule gives current and historical pages the same meaning:

- before a basho, the annotation identifies an opportunity;
- during a basho, the annotation remains fixed while the score changes daily;
- after a basho, the annotation records the opportunity which existed on entry
  and the final score records the outcome; and
- on a historical Basho Results selection, the annotation reconstructs only
  what was knowable on entering that basho.

Historical Basho Results should therefore show the annotations by default when
the required prior evidence is present. They are historical context, not a
present-day prediction. If prior evidence is absent or incomplete at a History
boundary, omit the annotation rather than guessing.

## Relationship to Next Basho

The Basho Results `Next Basho` group is reserved for observed facts from the
following banzuke. Its Chii and Div movement values answer what actually
happened, when a following banzuke is available.

Promotion annotations must not write to, relabel or overload those fields. In
particular:

- a possible promotion is not a Next Basho division value;
- an achieved numerical guideline is not proof of the later promotion; and
- while the selected basho is current, Next Basho must remain blank because the
  next banzuke does not yet exist.

The current placeholder Notes for Next Basho movement documentation are a
separate documentation defect and should not be treated as a promotion surface.

## Data and implementation boundary

`make_site89` validates and assembles already-produced site data; it does not
load History or perform analysis. Promotion annotations must preserve that
boundary.

The preferred implementation shape is:

1. Add one shared, site-facing promotion-context derivation upstream of the site
   assembler. It should consume a History and return structured annotations for
   a `(basho, rikishi)` pair.
2. Reuse that derivation in both `src.analysis.site89.banzuke_changes` and
   `src.analysis.site89.basho_results`.
3. Publish structured fields in both page datasets rather than asking browser
   JavaScript to reconstruct promotion rules independently.
4. Render the structured fields beside shikona in the two table renderers.
5. Keep the existing retrospective classifier outputs separate. The public
   annotation producer may reuse low-level, tested result-counting primitives,
   but it must not select a rule by classifier score.

A suitable producer-facing value would distinguish semantics from typography,
for example:

```text
promotion_annotation.kind = yokozuna_opportunity | ozeki_opportunity
promotion_annotation.required_wins = null | integer
promotion_annotation.as_of_basho = YYYY/MM
```

Evidence fields for prior basho, ranks and wins may also be retained in the
producer model or provenance for testing and audit, even if they are not sent
to the browser.

## Interaction requirements

- The shikona itself remains the link/action target currently used for SumoDB
  and career charts.
- Sorting by shikona ignores the annotation.
- The annotation has accessible text, not only punctuation or colour.
- A concise legend or Note defines both annotation forms.
- The same notation and wording are used on both pages.
- The annotation does not require users to enable Elo-89, Previous Basho, Next
  Basho or any research option.
- In banzuke-style view, the annotation appears consistently on both East and
  West sides. In scan-table view, it appears in the same Shikona cell.

## Daily results dependency

Promotion annotations do not themselves require in-basho updating: the
opportunity and required-win target are fixed on entry. Their principal live
value on Basho Results does, however, depend on scores being refreshed after
each day.

Completing daily publication is therefore related work but not part of the
annotation calculation. Until daily refresh exists, the annotations can still
be correct, but the current-basho page will not show the attempt's up-to-date
progress.

## Acceptance criteria

An implementation is acceptable when automated tests and rendered-page checks
establish all of the following:

1. A current ozeki who won the immediately preceding Makuuchi yusho as ozeki is
   annotated; other rikishi are not.
2. An eligible K/S rikishi with prior wins of 10 and 11 is annotated with a
   required-win value of 12.
3. A K/S rikishi whose required total cannot be reached within the selected
   basho is not annotated.
4. Missing or incomplete prior evidence causes omission, not inference.
5. Changing the displayed basho recalculates annotations using only information
   available before that basho's results began.
6. The annotation remains the same for day 0, an in-progress day and the final
   result of the same basho.
7. The Banzuke and Basho Results use the same producer semantics and display
   vocabulary.
8. Shikona links, alternate chart actions and name sorting continue to work.
9. Next Basho Chii and Div remain factual, blank without a following banzuke,
   and unaffected by promotion annotations.
10. The public navigation label and page title are **The Banzuke**, or the
    uncompleted rename appears on an explicit TBD list.

## Open presentation decisions

The following choices do not change the semantic proposal and can be settled
during UI design:

- literal `!` and `(n)` text versus compact styled badges;
- the exact accessible and Notes wording;
- whether the legend is always visible or appears in the collapsible Notes;
- spacing and placement in the East/West banzuke layout; and
- whether an annotation should link to a future general explanation of
  promotion rules.

The following is not merely a presentation decision and requires an explicit
policy change if desired:

- adding per-basho minimum wins, three winning-record requirements, equivalent
  performance, discretionary exceptions or press-announcement state to the
  adopted public rules.

## Initial implementation checklist

- [x] Rename the navigation entry and page title to **The Banzuke**, and place
      it before **Basho Results** in the Home menu.
- [ ] Define and test the shared as-of-basho promotion annotation model.
- [ ] Add the structured fields to both site89 producers and their CSV/data
      contracts.
- [ ] Render annotations without altering canonical shikona values.
- [ ] Add shared Notes/legend text and accessible labels.
- [ ] Verify current, in-progress, final and historical basho states.
- [ ] Verify that Next Basho remains observed-only.
- [ ] Track daily Basho Results publication as related work if it is not already
      implemented when annotations are added.
