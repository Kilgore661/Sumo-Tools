# Elo-89 Ratings: Expert Account

## Status

Working contents for a new, separate expert-facing account. This workspace is
not part of the public website and does not replace or revise the existing
Elo89 account files.

The aim is to write a complete account first. Once its definitions, argument,
evidence and criticism are satisfactory, relevant portions can be adapted for
interested and casual readers and considered for integration into the site.

## Intended outcome

The finished account should leave a technically critical reader able to say:

- what a rating system is intended to do;
- how a rating differs from a count, descriptive statistic, institutional rank
  or forecast;
- in what senses the banzuke is and is not a rating system;
- what model of competitive sumo is implicit in ordinary Elo;
- which difficulties arise when Elo is applied to sumo;
- which decisions define Elo-89, what alternatives were considered and why
  the retained choices were made;
- what the available evidence supports; and
- which assumptions, weaknesses and open questions remain.

The intended conclusion is not that Elo-89 is definitive. The project has made
one explicit set of choices, can explain and test many of them, and invites
other investigators to make and evaluate different choices.

## Narrative spine

```text
What is Elo-89?
    -> Isn't that what the banzuke already does?
    -> What is a rating system?
    -> Why construct a mechanically derived numerical system?
    -> How does ordinary Elo work?
    -> What model of competition does Elo embody?
    -> What problems arise in chess and, especially, sumo?
    -> What choices define an Elo-like system?
    -> Which choices define Elo-89, and why?
    -> What evidence supports those choices?
    -> What remains conditional, contestable or unresolved?
    -> What other choices could reasonably be made?
```

## Chapters

1. [What is Elo-89?](01%20What%20is%20Elo-89.md)
   Give the short descriptive answer without prejudging the later definition
   of strength or overstating what the number measures.

2. [Isn't That What the Banzuke Does?](02%20Is%20the%20Banzuke%20a%20Rating%20System.md)
   Examine the banzuke fairly as a result-informed institutional ordering and
   establish why Elo-89 is intended as a second lens, not a corrected banzuke.

3. [What is a Rating System?](03%20What%20is%20a%20Rating%20System.md)
   Define ratings as states or coordinates inside a model. Separate
   observations, counts, statistics, orderings, model states and forecasts.

4. [Why a Mechanically Derived Numerical System?](04%20Why%20a%20Mechanical%20Numerical%20System.md)
   Use wins per basho, wins per bout and unequal opposition to show why simple
   methods only appear simple and why no neutral scalar falls directly out of
   the results.

5. [Ordinary Elo](05%20Ordinary%20Elo.md)
   Explain rating differences, the logistic probability equation, `q`, the
   update equation, `K`, translation invariance and worked examples.

6. [The Model of Competition in Elo](06%20The%20Model%20of%20Competition%20in%20Elo.md)
   Make the underlying one-dimensional, pairwise, probabilistic and dynamic
   model explicit rather than presenting Elo as two free-standing formulae.

7. [Problems Applying Elo to Chess and Sumo](07%20Problems%20Applying%20Elo%20to%20Chess%20and%20Sumo.md)
   Critique changing ability, entry, departure, initialisation, scale drift,
   inactivity, uncertainty, schedules, connectivity, missing history and
   possible non-transitive effects.

8. [From Elo to Elo-like Systems](08%20From%20Elo%20to%20Elo-like%20Systems.md)
   Identify the common Elo idea and the choices by which different members of
   the family define materially different models.

9. [The Exact Elo-89 Model](09%20The%20Exact%20Elo-89%20Model.md)
   Specify the epoch, evidence domain, represented population, `q`, divisional
   K, P1, chronology, population operations, persistence rules and observation
   stages.

10. [Why Elo-89 Makes Those Choices](10%20Why%20Elo-89%20Makes%20Those%20Choices.md)
    Explain what was selected by evidence, accepted as a modelling judgement,
    inherited for continuity or left unresolved.

11. [Critique of Elo-89](11%20Critique%20of%20Elo-89.md)
    Assess one-dimensional strength, point uncertainty, future-informed P1,
    normalisation, drift, reinitialisation, immature ratings, historical
    interpretation and known defects.

12. [What Has and Has Not Been Established?](12%20What%20Has%20and%20Has%20Not%20Been%20Established.md)
    Separate definitions, mathematical consequences, empirical findings,
    modelling judgements, assumptions and open questions.

13. [Other Choices Are Possible](13%20Other%20Choices%20Are%20Possible.md)
    Invite explicit alternatives without implying that untested alternatives
    have already been compared or that every choice is arbitrary.

## Research-audit principle

The structure is expected to force questions which the project has not yet
answered. Each chapter should distinguish:

```text
settled definition
mathematical consequence
empirical finding
modelling judgement
thin evidence
TBD
outside present scope
```

A chapter must not fill a gap with plausible generalities. A complete account
can state that work has not been done and decide whether that gap is a
publication blocker, an accepted limitation or a future research programme.

The presently visible pressure points include:

- the exact real-world target denoted by “competitive performance” or
  “strength”;
- a formal account of what makes a rating model good for the project's stated
  purpose;
- individual evidential uncertainty and an uncertainty-aware comparator;
- non-transitive style or matchup effects;
- genuinely prospective evaluation of a frozen model and prior;
- primary-source support for claims about Elo and institutional chess rating
  practice; and
- comparison with materially different, non-Elo model families.

## Chapter method

Every chapter file begins with:

1. its purpose in the argument;
2. the questions it must answer;
3. existing repository work and evidence;
4. known gaps or TBDs; and
5. the next writing or research step.

The chapters should eventually read as one argument, not an encyclopaedia and
not a chronology of every experiment. Research history belongs where it
explains a retained choice.

## Existing material remains separate

The existing HTML account drafts and public prose remain unchanged. They are
sources to mine, not files governed by this contents page. The principal
orientation note for this workspace is the adjacent
[Elo-89 Ratings Narrative Handoff](../../products/make_site89/docs/2026%2010%2019%20Elo-89%20Ratings%20Narrative%20Handoff.md).

## Next

All thirteen chapters now have first continuous-prose drafts. The next step is
an end-to-end editorial review for repetition, terminology, transitions and
claims which later chapters have qualified or superseded. Website integration
remains a separate subsequent decision.
