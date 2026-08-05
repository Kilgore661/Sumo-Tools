# 3. Performance Measures and Schedule Strength

*Part 3 of 5 — [Previous: Base Model of Competition Over Time](02-base-model.md) · [Next: Player-Strength-Based Schedule Strength](04-player-strength-based-schedule-strength.md)*

## Relationship to the base model

This note extends the observational framework in [*A Base Model of Competition Over Time*](02-base-model.md). It does not replace that model or add a fundamentally more sophisticated observational base.

The base model supplies

\[
\mathsf{Player},\qquad
\mathsf{Bout},\qquad
\mathsf{Schedule},\qquad
\mathsf{History},
\]

together with times and results. The notions introduced here are derived views and functions over that information.

In particular, this note still introduces no latent or independently existing notion of player skill.

## Player records as a derived view

A schedule records opponent-time pairs:

\[
\mathsf{Schedule}
=
\operatorname{Seq}
(\mathsf{Player}\times\mathsf{Time}).
\]

For performance measurement, it is convenient to package a player's schedule together with the corresponding results:

\[
\mathsf{PlayerRecord}
=
\operatorname{Seq}
(\mathsf{Player}\times\mathsf{Time}\times\mathbf 2).
\]

This need not be a new primitive of the base model. It can be derived from a history:

\[
\operatorname{record}:
\mathsf{History}\times\mathsf{Player}
\to\mathsf{PlayerRecord}.
\]

The schedule is recovered by projection:

\[
\operatorname{schedule}:
\mathsf{PlayerRecord}
\to\mathsf{Schedule}.
\]

Thus `PlayerRecord` is a convenient local view of information already present in the global history.

## Direct and contextual measures

The useful primary division is by information dependence.

### Direct performance

A direct performance measure inspects only a player and that player's selected record:

\[
DP:
\mathsf{Player}\times\mathsf{PlayerRecord}
\to V.
\]

Possible direct measures include:

- wins;
- win proportion;
- competition points;
- number of bouts;
- variety of opponents;
- other properties of the record or its projected schedule.

The value carrier \(V\) need not be numerical or totally ordered.

### Contextual performance

A contextual performance measure may additionally inspect the global history:

\[
CP:
\mathsf{Player}\times
\mathsf{PlayerRecord}\times
\mathsf{History}
\to W.
\]

This permits the interpretation of a player's results to depend on evidence lying outside that player's own record. For example, the significance of defeating an opponent may depend on how that opponent performed against everyone else.

The signature only makes contextual information available. It does not by itself guarantee that a particular function uses that information, or uses it specifically as strength of schedule.

## Temporal selection is an independent issue

Direct versus contextual describes whose records a measure may inspect. It is separate from the temporal question of which portion of those records is selected.

Possible temporal selectors include

\[
\operatorname{at}:
\mathsf{Time}\times\mathsf{PlayerRecord}
\to\mathsf{PlayerRecord},
\]

\[
\operatorname{upTo}:
\mathsf{Time}\times\mathsf{PlayerRecord}
\to\mathsf{PlayerRecord},
\]

and

\[
\operatorname{last}:
\mathbb N\times\mathsf{PlayerRecord}
\to\mathsf{PlayerRecord}.
\]

An instantaneous or current measure can therefore be obtained by composition. For example,

\[
IP(i,t,h)
=
DP\left(
i,
\operatorname{at}\bigl(t,\operatorname{record}(h,i)\bigr)
\right),
\]

where the exact selector depends on what is intended by “instantaneous.”

A statement made at time \(t\) may nevertheless be computed from a longer evidential window. For example, a current league position is indexed by the present time but usually depends on results accumulated before that time. It is therefore helpful to distinguish:

- **evaluation time**: when the value is asserted;
- **evidential window**: which observations are used to calculate it.

Current or instantaneous versus historical is a temporal classification. Direct versus contextual is an information-dependence classification. The two axes are independent.

## Three meanings of schedule difficulty

A player record supplies a schedule by projection. Consequently, some schedule measures arise entirely within the direct context. However, the conventional strength of opponents usually requires wider history. The phrase “strength of schedule” therefore admits several distinct meanings.

### 1. Intrinsic schedule properties

An intrinsic schedule measure uses only the schedule:

\[
D_{\mathrm{intrinsic}}:
\mathsf{Schedule}\to U.
\]

It may measure such features as:

- schedule length;
- repetition or diversity of opponents;
- concentration of bouts;
- structural properties independent of recorded outcomes.

Such a measure can be incorporated into a direct measure through composition:

\[
D_{\mathrm{intrinsic}}
\circ
\operatorname{schedule}:
\mathsf{PlayerRecord}\to U.
\]

### 2. Difficulty evidenced by the focal player's record

A focal-player difficulty measure uses the player's own results:

\[
D_{\mathrm{focal}}:
\mathsf{Player}\times\mathsf{PlayerRecord}
\to U.
\]

For example, an opponent whom player \(i\) repeatedly loses to may be empirically difficult for \(i\), even if that opponent is not generally successful. This allows matchup-specific or nonseparable difficulty without consulting other players' records.

This notion remains direct because only the focal player's record is inspected.

### 3. General strength of opponents

The conventional sporting notion of strength of schedule normally asks how strong the opponents are in general. The schedule identifies the opponents but does not contain their records against other players. That information must be obtained from the global history:

\[
D_{\mathrm{opponent}}:
\mathsf{Player}\times
\mathsf{Schedule}\times
\mathsf{History}
\to U.
\]

An elementary construction first assigns each opponent a record-based value:

\[
Q:
\mathsf{Player}\times\mathsf{History}
\to X.
\]

It then aggregates those values over the opponents in the focal schedule:

\[
D_{\mathrm{opponent}}(i,s,h)
=
\operatorname{aggregate}
\{Q(j,h):(j,t)\text{ occurs in }s\}.
\]

This form of schedule strength is contextual because it depends on evidence outside the focal player's record.

If an opponent-strength assignment has already been supplied independently,

\[
q:\mathsf{Player}\to X,
\]

then the corresponding schedule measure could instead have signature

\[
D:
\mathsf{Schedule}\times
(\mathsf{Player}\to X)
\to U.
\]

When \(q\) is itself derived from history, the contextual dependence reappears through composition.

## Making schedule adjustment explicit

A contextual-performance signature does not show exactly how history affects the resulting value. To make schedule adjustment explicit, separate three functions.

First, direct performance:

\[
R:
\mathsf{Player}\times\mathsf{PlayerRecord}
\to V.
\]

Second, schedule difficulty:

\[
D:
\mathsf{Player}\times
\mathsf{Schedule}\times
\mathsf{History}
\to U.
\]

Third, an adjustment rule:

\[
A:V\times U\to W.
\]

The resulting contextual performance is

\[
C(i,r,h)
=
A\left(
R(i,r),
D\bigl(i,\operatorname{schedule}(r),h\bigr)
\right).
\]

This factorisation makes the dependence on schedule strength visible rather than hiding it within an opaque contextual-performance function.

## Retaining rather than collapsing the dimensions

There is no requirement to combine direct performance and schedule difficulty into a single scalar. A cautious contextual value is the ordered pair

\[
C(i,r,h)
=
\left(
R(i,r),
D\bigl(i,\operatorname{schedule}(r),h\bigr)
\right),
\]

with carrier

\[
W=V\times U.
\]

This can express that a player has high direct performance but has faced a weak schedule. Turning the pair into a single value requires an additional rule specifying how schedule difficulty should compensate for, reinforce, or otherwise modify direct performance.

The ordering on \(V\times U\) is also an additional choice. It might be partial, lexicographic, or induced by an adjustment function. None is forced by the observational data.

## Layered view

The complete construction can be organised into three layers.

### 1. Observational base

\[
\mathsf{Player},
\mathsf{Bout},
\mathsf{Schedule},
\mathsf{History},
\mathsf{Time},
\mathsf{Result}.
\]

### 2. Derived views and selections

\[
\operatorname{record},
\operatorname{schedule},
\operatorname{at},
\operatorname{upTo},
\operatorname{last}.
\]

### 3. Measurement functions

\[
DP,
IP,
D_{\mathrm{intrinsic}},
D_{\mathrm{focal}},
D_{\mathrm{opponent}},
CP.
\]

Accordingly,

\[
\boxed{\text{observational base}}
\longrightarrow
\boxed{\text{selected player record}}
\longrightarrow
\boxed{\text{direct or contextual measure}}.
\]

Everything discussed here is definable over the original base model. A genuinely richer base would be required only if the theory introduced information not recoverable from the recorded competition, such as latent skill, external player attributes, venue conditions, or independently assigned opponent strengths.
