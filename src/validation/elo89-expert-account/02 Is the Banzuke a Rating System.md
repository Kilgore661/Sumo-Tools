# 2. Isn't That What the Banzuke Does?

> **Draft status:** First continuous-prose draft. This chapter uses *rating
> system* in both an ordinary and a narrower technical sense. Chapter 3 will
> make the technical vocabulary precise.

## The short answer

In an ordinary sense, yes. The banzuke evaluates and orders rikishi. Bout
results are central to that process, and a rikishi placed higher on the
banzuke will generally be understood to have the stronger competitive
standing. It would be artificial to deny that the banzuke performs work which
is, in everyday language, a kind of rating.

But it does not follow that a banzuke position is a numerical rating of the
kind introduced in Chapter 1. The banzuke is an official institutional
ordering. It says where each rikishi stands in sumo at the publication of that
banzuke. Elo-89 constructs a scalar state whose *differences* have a declared
mathematical interpretation. The two systems overlap, but they are not two
ways of printing the same thing.

That distinction matters because Elo-89 is not an attempted correction to the
banzuke. If we treated the banzuke as a defective performance table, every
disagreement would invite the conclusion that one system had made a mistake.
The more useful starting point is that the systems have different purposes,
use information differently and preserve different aspects of a rikishi's
history.

## What the banzuke tells us

A chii such as Maegashira 3 West is a rikishi's official position on a
particular banzuke. Chii have a conventional order: rank classes, numbered
positions and east–west sides locate the rikishi within the published
hierarchy. The banzuke consequently tells us much more than an arbitrary list
would.

It records an authoritative competitive standing. It reflects results and
career history, determines important features of status, and helps define the
competitive setting in which the next basho will take place. It is also
strongly informative about likely bout outcomes. A Yokozuna will ordinarily
be favoured against a lower-ranked opponent, and movement through the
divisions is compelling evidence about the level at which a rikishi has been
able to compete.

None of this requires us to treat chii as “mere labels”. Chii contain valuable
information about performance. Elo-89 itself acknowledges that information:
its P1 table uses banzuke position when a rikishi first enters—or re-enters—the
represented rating population.

The narrower question is whether the information in chii already supplies the
kind of measure that Elo-89 is intended to construct.

## An order is not yet a scale

The banzuke gives us an order, but it does not declare numerical distances
between its positions. Numbering all occupied places from top to bottom would
not solve this problem. Such numbers would tell us which position comes first,
second or third; they would not establish that every one-place interval
represents the same difference in competitive performance.

This is the distinction between an **ordinal** and a **cardinal** or interval
interpretation. An ordinal tells us which item is above another. A cardinal
scale additionally gives meaning to the size of a difference. Elo-89 claims,
under its own model, that a given rating difference has the same effect on the
calculated win probability wherever that difference occurs on the scale. The
banzuke makes no corresponding claim about the distance from M2e to M2w, from
M2w to M3e, or from one rank class or division to another.

Indeed, its positions are not all objects of the same kind. Yokozuna and Ozeki
are statuses with special promotion and retention histories. Sekiwake and
Komusubi are named ranks. The divisions below them contain numbered positional
lists, while division boundaries can mark substantial institutional changes.
East and west distinguish places within nominal ranks. Writing all of these in
one sequence is useful for ordering and software, but it does not reveal a
uniform geometry of strength hidden inside the hierarchy.

The repository's `Chii.ordinal()` illustrates the point. It provides a
consistent machine ordering for banzuke positions. Arithmetic performed on
its codes does not thereby become arithmetic on competitive strength. To turn
chii into a numerical performance scale, we would have to decide the sizes of
the gaps within ranks, between rank classes and across divisions. Those would
be new modelling choices, not facts read directly from the banzuke.

## The banzuke preserves a path

A rikishi's present chii is not determined by an assessment of present
bout-winning capacity alone. It is reached from a previous chii through recent
results, the results and movements of other rikishi, the available places and
the institutional rules and judgements applicable to the case. At some ranks,
promotion, retention and demotion have special conditions.

The result is path-dependent. Two rikishi whom we would currently expect to
perform similarly need not occupy the same or adjacent positions, because
they arrived there by different routes. Conversely, two neighbours on a
banzuke need not be equally favoured against the same opposition. The banzuke
preserves status and history which a model aimed narrowly at current
bout-winning performance may choose to treat differently.

It must also produce a valid banzuke. Rikishi compete not for infinitely
divisible points but for places within a structured hierarchy. A promotion can
depend on which places are available and on what happened elsewhere in the
population. An Elo-like rating has no analogous obligation: any number of
rikishi can have similar ratings, and one rikishi's rating can pass another's
without a vacancy being created.

This does not show that the banzuke is defective. It shows why judging it as
though it were trying to maintain a continuously updated probability scale
would mistake the institution for a different object.

## Judgement, rules and mechanical calculation

It is tempting to contrast a “subjective” banzuke with an “objective” rating.
That contrast is too easy.

Constructing a banzuke requires the application of institutional rules,
conventions and informed judgement to particular circumstances. *Judgement*
does not mean whim or arbitrariness. Nor does the presence of judgement make
the resulting positions less official or less meaningful.

Elo-89 also embodies judgement. People chose its evidence, probability curve,
update rates, entrant policy, population policy and observation points. A
mechanical calculation does not escape those decisions. Its distinctive
property is that the decisions are fixed in advance as an explicit model.
Once the model version and input record are fixed, the same calculation can be
repeated without making a new case-by-case decision about each rikishi.

That gives the model a different kind of accountability. We can state exactly
how a result changes a rating, derive the probability implied by a difference,
reproduce the complete history and score forecasts against later outcomes. We
can also expose poor assumptions or poor predictions. This makes the model
inspectable and testable; it does not make its purpose or construction
value-free.

## Two related but non-independent views

Putting chii and Elo-89 side by side can reveal useful agreements and
disagreements.

If neighbouring rikishi have markedly different ratings, we can ask whether
the difference reflects opposition, longer competitive history, the timing of
the banzuke or a weakness in the rating model. If a promoted rikishi already
has a rating comparable with established members of the new division, the two
views together tell a richer story than either alone. No discrepancy, by
itself, identifies which explanation is correct.

The comparison also needs one important qualification: Elo-89 is not wholly
independent of chii. P1 uses banzuke position to initialise a rikishi on entry
or return. Early agreement between his rating and chii is therefore partly
built into the model. Subsequent eligible results can move the rating away
from that starting value, but agreement with the banzuke cannot be treated as
uncontaminated validation of Elo-89.

Conversely, disagreement is not automatically evidence in Elo-89's favour.
The rating may omit relevant context, respond at the wrong rate, rest on too
little evidence or force a multidimensional competitive relationship into one
number. The banzuke and Elo-89 are both objects to be understood, not a ground
truth and a challenger whose only task is to reproduce it.

## What, then, is the extra number for?

The case for Elo-89 cannot simply be that the banzuke fails to provide a
number. We could assign numbers to its positions. Nor can it be that a formula
is inherently superior to institutional judgement.

The proposed advantage is more specific. A numerical rating model can be
designed so that its state has one declared meaning, its differences generate
explicit comparisons, its treatment of evidence is reproducible, and some of
its claims can be tested against future results. Whether Elo-89 actually
succeeds depends on the quality of the model and the evidence for it.

Before introducing that model, we therefore need to answer a more fundamental
question. What, in fact, is a rating system? What must its numbers mean, what
work should they do, and by what standards should we call the system good?

That is the subject of the next chapter.

## Working sources

- `../../products/make_site89/prose/Why ratings.html`
- `../../products/make_site89/docs/Elo89 Account - 02 Why Ratings When We Already Have Chii.html`
- `../../analysis/docs/2026 09 26 Chii and the Measurement of Strength.md`
- `../../products/make_site89/prose/Elo-89 vs Chii.html`
