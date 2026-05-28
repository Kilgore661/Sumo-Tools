# Banzuke Position Model Work Plan

## Status

Discussion/work-plan note.

This document proposes a clearer conceptual model for what the code currently
calls `Chii`.

No code rename is proposed yet.

---

## 1. Problem

The project uses `Chii` as the formal model value for a rikishi's banzuke
position.

That name has become awkward because "chii" is overloaded:

- it can mean the formal object;
- it can mean a display/input string such as `M3e`;
- it can mean a reduced display category such as `M3`;
- it can appear in public-facing text where readers expect ordinary sumo
  language rather than implementation vocabulary.

The word "rank" is also overloaded and has historically been avoided in
technical documentation for that reason.

The result is that discussion of probability charts, ratings, standings, and
site labels can become ambiguous exactly where precision matters.

---

## 2. Proposed Conceptual Name

Use:

```text
BP
Banzuke Position
```

as the conceptual name for the formal model value currently represented in code
by `Chii`.

The current `Chii` class can be understood as:

```text
Chii == BP implementation, current legacy class name
```

This lets documentation and design discussion move toward clearer vocabulary
without requiring an immediate large rename.

---

## 3. Core Idea

A BP is a formal banzuke-position model value.

It is not a display string.

Its canonical machine identity and ordering remain:

```text
BP.ordinal()
```

Strings such as the following are display/input forms only:

```text
Y2eYO
Y2e
Y2
Y
```

They may correspond to different derived views of a BP, but they are not the
same thing as the formal BP value.

---

## 4. Derived BP Views

In principle, a BP model could expose explicit derived values such as:

```text
BP.annotation_free
BP.sideless
BP.position_title
BP.public_category
BP.ordinal
```

The exact API is deferred.

The conceptual distinctions are:

```text
full BP
  Y2eYO

annotation-free BP
  Y2e

sideless BP
  Y2

position title / designator
  Y

public category
  sanyaku: title/designator
  non-sanyaku: sideless BP

ordinal
  canonical comparable integer
```

These names are provisional. The important point is that every reduction is an
explicit model transformation, not an incidental string manipulation.

`BP.public_category` is a provisional public-reader category. It is defined as:

```text
if BP is sanyaku:
  BP.position_title
else:
  BP.sideless
```

For example:

```text
Y1e -> Y
O2w -> O
K2e -> K
M10w -> M10
J7e -> J7
```

`BP.public_category` is a conceptual value, not a string. If it is implemented,
it should live in the BP model family alongside any implemented forms of BP,
annotation-free BP, sideless BP, and position title. Display strings such as
`O`, `M10`, or `J7` are renderings of those values.

This mirrors ordinary reader expectations: users understand Yokozuna, Ozeki,
Sekiwake and Komusubi as titles within Makuuchi, but expect numbered categories
for maegashira and lower divisions.

---

## 5. Sanyaku and Makuuchi

The BP model must preserve the awkward but important distinction between:

- formal banzuke-position structure; and
- ordinary public sumo language.

In formal structure, sanyaku positions have title/designator, number, side, and
possibly annotation:

```text
Y1e
O2w
K2e
```

This resembles the wider pattern used by maegashira and lower divisions:

```text
M3e
J7w
Ms60e
```

But public language normally treats `Y`, `O`, `S`, and `K` as titles within
Makuuchi, not as separate divisions.

The model must therefore distinguish:

```text
public division: Makuuchi
formal BP title/designator: Y, O, S, K, M
formal BP number: 1, 2, ...
formal BP side: east, west, none
```

---

## 6. Why This Matters for Public Pages

The 6.3.1 `Win Probability by Standing` chart was the first pressure case.
The same issue now appears elsewhere, for example page 5.1, where a Chii
dropdown can expose full or unusual BP values that are too raw for public
selection.

For 6.3.1, the page needs to compare:

```text
p_obs(c1 beats c2)
p_rating(c1 beats c2)
```

The unresolved question is what `c1` and `c2` are.

With BP vocabulary, possible answers can be stated more clearly:

```text
diagnostic sideless BP
  Y1, O1, O2, K1, M3, J7

BP.public_category
  Y, O, S, K, M1, M2, J1

canonical displayed BP category
  Y1, O1, S1, K1, M1, M2, J1
```

Each option has consequences for:

- observed aggregation;
- representative rating source;
- chart labels;
- support counts;
- public readability;
- diagnostic/audit usefulness.

The chosen category must be the same in the observed and Equelo-derived views.

The current working hypothesis is that BP-derived public categories produce the
kind of result an ordinary site user expects. In requirements language, this is
an inferred stakeholder requirement: if stakeholders had been asked whether a
public "Ozeki" category should include `O1`, `O2`, and other Ozeki-numbered
positions rather than exposing every technical banzuke slot number, we expect
they would have said yes.

This remains a hypothesis until validated, but it is strong enough to guide
pressure-case review. It also explains why public pages may need a different
category layer from diagnostic/developer artifacts.

There is also a pragmatic category that describes the current 6.3.1 display:

```text
canonical displayed BP category
```

Under that approach, the data may contain sideless BP categories such as
`O1` and `O2`, but the public chart displays only canonical-numbered sanyaku
categories:

```text
Y1, O1, S1, K1
```

and ignores rarer numbered sanyaku categories such as `O2`, `O3`, `S2`, or
`K2`.

This is not the same as `BP.public_category`. It is a display-domain category:
the charts are comparable because Observed and Equelo apply the same domain,
but `O1` means `O1`, not "all Ozeki". This is acceptable as a description of
current behavior, but it is not the target public specification.

Do not conflate this selected-BP display policy with curated-domain exclusions.
Historical or low-support BP slots such as `M18`-`M22` or `J13`-`J24` may be
excluded from a comparison domain. Ordinary numbered sanyaku slots such as `O2`
or `K2` are different: they remain meaningful BPs, and the open public-design
question is whether to display selected canonical BPs such as `O1` or aggregate
all ozeki BPs into a public category rendered as `O` or `Ozeki`.

---

## 7. Stress Test Plan

Use 6.3.1 to stress-test the BP model before changing wider code.

Also use other public controls that expose BP-like values, such as the 5.1 Chii
dropdown, to test whether `BP.public_category` needs to become a shared
producer/model concept rather than a local chart policy.

Questions to answer:

1. Can BP vocabulary cleanly describe the current observed data preparation?
2. Can it distinguish annotation collapse from side removal?
3. Can it distinguish sideless BP categories from title bins?
4. Can it explain why `O2` is not the same as `O1`, unless an explicit binning
   policy says otherwise?
5. Can `BP.public_category` express the user-facing public domain without hiding diagnostic
   categories needed by developers?
6. Can it specify the required representative rating source for every chosen
   category?

If the model cannot answer these questions clearly, it is not ready.

---

## 8. Adoption Survey Plan

If the BP vocabulary passes the 6.3.1 stress test, survey the rest of the app
for places where it could or should be used.

Candidate areas:

- Basho Results;
- Banzuke Changes;
- Standings by Wins;
- Typical Equelo Ratings;
- Finish by Chii;
- first Chii appearance;
- retirement/career lifecycle views;
- navigation/page labels and notes;
- producer CSV schemas;
- table sorting metadata;
- public glossary/methodology text.

The survey should classify each use as:

```text
formal BP value
BP display string
annotation-free BP
sideless BP
position title/designator
public category
public label/category
legacy wording only
```

---

## 9. Non-Goals

Do not rename the `Chii` class yet.

Do not mechanically replace every mention of "chii" in docs or code.

Do not change public labels until the BP model has been stress-tested against
6.3.1 and the user-facing category policy is settled.
