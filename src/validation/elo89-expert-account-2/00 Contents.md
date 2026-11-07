# Elo-89 Ratings: Expert Account

## About this account

This account is written for readers familiar with rating theory. It explains
what Elo-89 is, how it works, why its principal choices were made, what
evidence supports them and where the model may fail or mislead.

It is a synthesis rather than a self-contained academic report: detailed
derivations, experiments and implementation records are not all reproduced
here. The entire project is
[open source](https://github.com/Kilgore661/Sumo-Tools). Where supporting
detail is omitted, the text or the
[Research and Implementation Guide](Appendix%20-%20Research%20and%20Implementation%20Guide.md)
points to the relevant work in the repository.

## Status

This is the current **top copy** of the expert-facing account. It incorporates
the accepted Elo-89 contract and is undergoing its final substantive and
publication review. Supporting research and implementation references are
collected in the appendix.

Once its definitions, argument, evidence and criticism are satisfactory,
relevant portions can be adapted for interested and casual readers and
integrated into the site.

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
   Specify the epoch, evidence domain, active population, `q`, divisional K,
   P89, population operations, frozen persistence and
   observation stages.

10. [Why Elo-89 Makes Those Choices](10%20Why%20Elo-89%20Makes%20Those%20Choices.md)
    Explain what is supported empirically, accepted as a modelling judgement,
    required for reproducibility or left as an open question.

11. [Critique of Elo-89](11%20Critique%20of%20Elo-89.md)
    Assess one-dimensional strength, point uncertainty, P89's future-
    informed fitting period, normalisation, drift, inactivity, immature
    ratings, historical interpretation and known limitations.

12. [What Has and Has Not Been Established?](12%20What%20Has%20and%20Has%20Not%20Been%20Established.md)
    Separate definitions, mathematical consequences, empirical findings,
    modelling judgements, assumptions and open questions.

13. [Other Choices Are Possible](13%20Other%20Choices%20Are%20Possible.md)
    Invite explicit alternatives without implying that untested alternatives
    have already been compared or that every choice is arbitrary.

## Appendix

[Appendix B: The Elo-89 Entrant Prior](Appendix%20B%20-%20The%20Elo-89%20Entrant%20Prior.md)
is a preliminary technical account of how P89 was fitted, why its construction
is not uniquely determined, and how evidence eligibility and support-weighted
aggregation are defined.

[Research and Implementation Guide](Appendix%20-%20Research%20and%20Implementation%20Guide.md)
collects the principal explanatory accounts, empirical findings,
implementation sources and reproducibility artifacts for the retained model.
It distinguishes current support from superseded development history.
