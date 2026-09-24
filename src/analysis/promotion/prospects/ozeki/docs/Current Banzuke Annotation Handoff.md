# Ozeki promotion annotation hand-off

## Status

Historical hand-off retained to show how the current-banzuke-only idea
developed. It is not an implementation and not a revision of the existing
Ozeki32 policy document.

The later, authoritative product contract is
`src/products/make_site89/docs/Promotion Annotations - Final Proposal.md`.
That proposal retains the fixed Ozeki32 annotation on The Banzuke and adds a
countdown on current Basho Results only. Its companion `Here Be Dragons`
document records why no probability or in-progress Yokozuna feasibility
calculation is added.

No producer, site manifest, runtime, prose artifact or test was changed by this
historical note.

## Revised purpose

The promotion annotation is now conceived as a prospective aid attached to
the current banzuke, not as a timeless classification to be reconstructed for
every historical basho.

The public page remains named **The Banzuke**. The phrase "new banzuke" may
describe the point in the basho cycle at which the page is most useful, but it
does not reopen the settled page-name decision.

The intended requirement is:

> Show Ozeki32 promotion-prospect annotations beside shikona on The Banzuke.
> The annotations describe the position on entry to the forthcoming/current
> basho. Do not add them retrospectively to historical Basho Results pages.

## Ozeki32 remains the indicator rule

The revised presentation scope does not change the Ozeki32 calculation.

For a rikishi on the current banzuke:

- the current rank must be komusubi or sekiwake;
- the two immediately preceding held basho must also have been at komusubi or
  sekiwake;
- the annotation is shown when the rikishi can reach at least 32 wins across
  those three consecutive basho; and
- the annotation communicates the number of wins required in the current
  basho.

The annotation is a site-defined indication of an Ozeki run. It is not a
prediction, guarantee or claim that the Japan Sumo Association applies an
automatic 32-win rule.

## Why the analytical decision need not be reopened

The available evidence for Ozeki32 is not confined to a short recent period.
The recorded analysis gives an F1 score of 78% over the complete population
and 83% from the beginning of Onokuni's March 1985 run onward. Comparisons with
the traditional 33-win benchmark were also broadly stable across the periods
examined.

This differs from the developing yokozuna analysis, where a short modern
period may need its own rule and explicit date boundary. There is no present
reason to impose the yokozuna period on the ozeki evidence. Different ranks
may have rules supported by different historical populations.

The existing public-facing Ozeki32 account remains the analytical explanation
for choosing 32 rather than the traditional 33. Restricting display to the
current banzuke changes the product purpose, not the evidence that led to the
rule.

## No probability in the annotation

The annotation should communicate the required result, not a probability of
promotion. Historical percentages depend on the selected population, period
and definition of a qualifying run. Those belong in analysis and explanatory
prose, where interested readers can inspect or reproduce them; they should not
be presented beside a shikona as though they were a forecast for that rikishi.

## Historical and Basho Results scope

The revised position removes the following from the intended implementation:

- promotion annotations on Basho Results;
- reconstruction of annotations for arbitrary historical banzuke;
- day-by-day recalculation during a basho;
- a shared annotation data contract across the Banzuke and Basho Results
  producers; and
- acceptance tests whose only purpose is to establish identical annotations
  across current, in-progress, final and historical Basho Results states.

Historical analysis remains relevant as evidence for the rule and should not
be deleted merely because historical pages do not display the annotation.

## Temporal wording

The Banzuke remains current throughout the tournament and until its successor
is published. An annotation such as "12 required" may therefore still be
visible after the rikishi's actual result has settled the question.

The legend, accessible label or Notes must make clear that the number records
what was required **at the start of the basho**. It must not look like a live
remaining-wins calculation.

The annotation itself does not depend on daily result publication. Removing
the Basho Results display consequently removes daily site refresh as a
dependency of this feature.

## Expected later implementation consequences

When implementation is authorised, the work is expected to include:

1. calculate Ozeki32 prospects for the current banzuke only;
2. add structured annotation data to the Banzuke producer contract only;
3. render the required-win annotation without changing the canonical shikona
   or its existing actions;
4. add concise Notes or a legend, including accessible wording and the
   start-of-basho qualification;
5. link the explanation to the Ozeki32 policy prose artifact;
6. test the current-banzuke calculation and rendering; and
7. verify that Basho Results and historical views remain unannotated.

## Documents requiring later reconciliation

The following records may still embody the earlier requirements and should be
updated together when the revised scope is adopted for implementation:

- `src/products/make_site89/docs/Promotion Annotations Proposal.md`;
- the production-site open-issues/TBD entry;
- `src/analysis/promotion/prospects/ozeki/docs/Ozeki32.md`; and
- the independently maintained site prose artifact
  `src/products/make_site89/prose/Ozeki32.html`.

The Markdown policy document and HTML prose artifact are independent maintained
inputs. There is no conversion or synchronisation producer between them, and
possible drift is accepted under the current site-input policy. Any later
revision must therefore consider each explicitly rather than assuming that one
will regenerate the other.
