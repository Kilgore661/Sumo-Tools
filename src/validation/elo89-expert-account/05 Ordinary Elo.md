# 5. Ordinary Elo

> **Draft status:** Second continuous-prose draft. This chapter defines a
> binary, common-K form of ordinary Elo and develops properties which follow
> from its equations. Questions about what those equations assume about
> competition, and how they behave when applied to sumo, are deferred to
> Chapters 6 and 7.

## The mathematical object

Let two competitors, A and B, have ratings \(R_A\) and \(R_B\) immediately
before a contest. Define A's rating advantage by

\[
d=R_A-R_B.
\]

Ordinary Elo has two operations:

1. transform the rating difference into an expected result; and
2. compare that expectation with the observed result to update the ratings.

For the binary win/loss version used in this chapter, A's expected score is
also the model probability that A wins:

\[
p_A=F(d)=\frac{1}{1+10^{-d/q}},
\tag{5.1}
\]

where \(q>0\) is the probability-scale parameter.

Represent A's result by

\[
s_A=
\begin{cases}
1 & \text{if A wins},\\
0 & \text{if A loses}.
\end{cases}
\]

The rating update is

\[
R'_A=R_A+K(s_A-p_A),
\tag{5.2}
\]

where \(K>0\) is the common update-rate parameter. B is governed by the same
equations:

\[
p_B=F(R_B-R_A),
\qquad
R'_B=R_B+K(s_B-p_B).
\]

In a decisive contest, exactly one competitor wins, so

\[
s_B=1-s_A.
\tag{5.3}
\]

Equations (5.1)–(5.3), together with an initial rating state and a sequence of
results, define the process studied in this chapter.

## Complementary probabilities are a theorem

It is not necessary to impose \(p_B=1-p_A\) as a separate rule. It follows from
the probability equation.

Since B's rating advantage is \(-d\),

\[
p_B=F(-d)=\frac{1}{1+10^{d/q}}.
\]

Meanwhile,

\[
\begin{aligned}
1-p_A
&=1-\frac{1}{1+10^{-d/q}}\\
&=\frac{10^{-d/q}}{1+10^{-d/q}}\\
&=\frac{1}{1+10^{d/q}}\\
&=p_B.
\end{aligned}
\]

Therefore

\[
p_A+p_B=1.
\tag{5.4}
\]

The model's two probabilities are coherent for a binary outcome: whatever
probability is assigned to A is withheld from B.

Equation (5.4) also gives the symmetry

\[
F(-d)=1-F(d).
\tag{5.5}
\]

In particular, \(F(0)=1/2\). Equal ratings imply equal probabilities.

## The probability curve is monotone

Differentiating (5.1) gives

\[
F'(d)=\frac{\ln 10}{q}F(d)\bigl(1-F(d)\bigr).
\tag{5.6}
\]

For every finite \(d\), \(0<F(d)<1\). Because \(q>0\), equation (5.6) is
strictly positive. The assigned probability therefore increases strictly as
A's rating advantage increases.

The slope is greatest when \(F(d)=1/2\), which occurs at \(d=0\). Its maximum
is

\[
F'(0)=\frac{\ln 10}{4q}.
\tag{5.7}
\]

Thus the curve is most sensitive to rating changes near an even contest and
flattens towards both extremes. It approaches but never reaches its limiting
probabilities:

\[
\lim_{d\to-\infty}F(d)=0,
\qquad
\lim_{d\to+\infty}F(d)=1.
\tag{5.8}
\]

No finite rating difference makes either outcome impossible.

## `q` is the unit of the probability scale

Rearranging (5.1) gives the odds form

\[
\frac{p_A}{1-p_A}=10^{d/q}.
\tag{5.9}
\]

A rating advantage equal to \(q\) therefore gives A odds of ten to one and
probability

\[
F(q)=\frac{10}{11}\approx0.9091.
\]

Each additional \(q\) points multiplies the odds by ten. Conversely, a
disadvantage of \(q\) points gives odds of one to ten.

With \(q=400\), useful landmarks are:

| A's rating advantage | \(p_A\) |
| ---: | ---: |
| −400 | 9.1% |
| −200 | 24.0% |
| −100 | 36.0% |
| 0 | 50.0% |
| +100 | 64.0% |
| +200 | 76.0% |
| +400 | 90.9% |

A rating difference has no complete probability interpretation without its
q. The probability depends on the dimensionless ratio \(d/q\).

## The sign and size of an update

Write A's rating change as

\[
\Delta R_A=K(s_A-p_A).
\tag{5.10}
\]

If A wins, then \(s_A=1\), so

\[
\Delta R_A=K(1-p_A).
\tag{5.11}
\]

For finite ratings, \(0<p_A<1\). A win therefore gives

\[
0<\Delta R_A<K.
\tag{5.12}
\]

If A loses, then \(s_A=0\), so

\[
\Delta R_A=-Kp_A,
\tag{5.13}
\]

and hence

\[
-K<\Delta R_A<0.
\tag{5.14}
\]

The winner always rises and the loser always falls. The changes can approach
K in magnitude but cannot equal it at a finite rating difference.

Equations (5.11) and (5.13) also formalise “surprise”. A win receives more
credit when its pre-contest probability was smaller; a loss costs more when
the competitor was more strongly favoured.

## Equal-K updates are zero-sum

Using (5.3) and (5.4), B's update is

\[
\begin{aligned}
\Delta R_B
&=K(s_B-p_B)\\
&=K[(1-s_A)-(1-p_A)]\\
&=-K(s_A-p_A)\\
&=-\Delta R_A.
\end{aligned}
\tag{5.15}
\]

It follows that

\[
R'_A+R'_B=R_A+R_B.
\tag{5.16}
\]

The contest redistributes rating points between the two competitors without
creating or destroying them. Repeating the argument shows that bout updates
preserve the total rating of a fixed, closed set of competitors when every
contest occurs within that set and every update uses the same K.

The common-K condition is essential to this theorem. Replacing K with
competitor-specific values changes the equations, and (5.15) no longer follows
in general. The reasons for making such a change are not part of ordinary Elo
as defined here.

## The rating difference moves towards the winner

The post-contest difference is

\[
\begin{aligned}
d'
&=R'_A-R'_B\\
&=R_A-R_B+2K(s_A-p_A)\\
&=d+2K(s_A-p_A).
\end{aligned}
\tag{5.17}
\]

If A wins, \(s_A-p_A=1-p_A>0\), so \(d'>d\). If A loses,
\(s_A-p_A=-p_A<0\), so \(d'<d\). A's rating advantage always moves in the
direction of A's observed result.

Because \(F\) is strictly increasing, the next probability for an otherwise
unchanged rematch moves in the same direction:

\[
A\text{ wins}\implies F(d')>F(d),
\]

\[
A\text{ loses}\implies F(d')<F(d).
\]

The update does not ordinarily reverse the complete accumulated comparison
after one contest. Whether it can do so in a particular case follows from the
sizes of \(d\), K and the residual.

## Expected change under the model

Suppose, for this mathematical result, that A's outcome is generated as a
Bernoulli random variable \(S_A\) with the same probability \(p_A\) assigned by
the model. Then

\[
\operatorname{E}[S_A]=p_A.
\]

Consequently,

\[
\operatorname{E}[\Delta R_A\mid R_A,R_B]
=K\bigl(\operatorname{E}[S_A]-p_A\bigr)
=0.
\tag{5.18}
\]

When the model's probability governs the outcome, the next update has zero
conditional mean. This does not mean the realised update is normally zero. Its
conditional variance is

\[
\operatorname{Var}(\Delta R_A\mid R_A,R_B)
=K^2p_A(1-p_A).
\tag{5.19}
\]

It is largest at an even contest, where it equals \(K^2/4\), and becomes small
near the probability extremes.

Equations (5.18) and (5.19) are internal consequences of assuming that the
model probability is the data-generating probability. They do not establish
that real sumo results obey that assumption.

## A worked example

Let A have rating 2,300 and B rating 2,100, and choose \(q=400\) and a common
\(K=20\). Then \(d=200\), giving

\[
p_A=\frac{1}{1+10^{-200/400}}\approx0.7597,
\qquad
p_B\approx0.2403.
\]

If A wins,

\[
\Delta R_A=20(1-0.7597)\approx+4.8,
\]

and B loses 4.8. The ratings become approximately 2,304.8 and 2,095.2,
increasing the difference from 200 to about 209.6.

If B wins, A's change is

\[
\Delta R_A=20(0-0.7597)\approx-15.2,
\]

and B gains 15.2. The ratings become approximately 2,284.8 and 2,115.2,
reducing the difference to about 169.6.

The favourite's win produces the smaller change because its residual is about
0.2403. The upset produces the larger change because its magnitude is about
0.7597.

The particular value \(K=20\) is illustrative. Only the common-K property is
needed for the zero-sum results above.

## Translation invariance

Let \(c\) be any real constant and define shifted ratings

\[
\widetilde R_i=R_i+c
\]

for every competitor. Then

\[
\widetilde R_A-\widetilde R_B
=(R_A+c)-(R_B+c)
=R_A-R_B.
\]

Every probability is therefore unchanged. The residuals and updates are also
unchanged, so after the contest

\[
\widetilde R'_i=R'_i+c.
\tag{5.20}
\]

This is **translation invariance**. Adding a common offset changes the printed
ratings but changes none of the relationships or probabilities. The origin of
the rating scale is conventional.

It follows that 2,300 versus 2,100 expresses the same Elo relationship as
1,800 versus 1,600. It does not follow that a rating of 2,300 is twice a rating
of 1,150 in any competitive sense.

## Change of rating units

There is a second invariance. Let \(a>0\), and transform

\[
\widetilde R_i=aR_i,
\qquad
\widetilde q=aq,
\qquad
\widetilde K=aK.
\]

Then

\[
\frac{\widetilde R_A-\widetilde R_B}{\widetilde q}
=\frac{a(R_A-R_B)}{aq}
=\frac{R_A-R_B}{q},
\]

so the probabilities are unchanged. The transformed update is

\[
\widetilde K(s_A-p_A)=aK(s_A-p_A)=a\Delta R_A.
\]

Thus the transformed process is the same process expressed in different
rating units. The numerical sizes of q, K and the ratings must be interpreted
together; none supplies an independent physical unit.

Combining a positive rescaling with a common shift gives the general affine
change of coordinates

\[
\widetilde R_i=aR_i+c,
\qquad
\widetilde q=aq,
\qquad
\widetilde K=aK,
\]

under which the model's probabilities and relative evolution are unchanged.

## Sequential recurrence

For a chronological sequence of contests indexed by \(t\), the equations form
a recurrence. The pre-contest state determines

\[
p_{A,t}=F(R_{A,t}-R_{B,t}),
\]

and the result then determines

\[
R_{A,t+1}=R_{A,t}+K(s_{A,t}-p_{A,t}).
\]

The updated state is used in the next calculation. Because an update changes
later probabilities, the result sequence cannot in general be replaced by an
unordered collection of wins and losses. Processing order is part of the
mathematical definition of a sequential Elo history.

The equations therefore provide both a probability mapping and a deterministic
state-transition rule once the contest sequence and outcomes are supplied.

## What has—and has not—been established

The properties in this chapter follow from the specified equations. They do
not depend on whether the equations are a good representation of sumo.

We have established, among other things, complementary probabilities,
monotonicity, bounded updates, equal-K conservation, movement of the rating
difference towards the winner, zero conditional expected update under the
model, translation invariance and invariance to a change of rating units.

We have not established that one scalar rating is sufficient, that the
logistic probability curve describes sumo, that K should be constant, that
the resulting probabilities are calibrated, or that the model handles change
through time appropriately. Those are questions about the model of competition
embodied by the equations.

That is the subject of the next chapter.

## Working sources

- `../../products/make_site89/docs/Elo89 Account - 03 From Rating Differences to Winning Chances.html`
- `../../products/make_site89/docs/Elo89 Account - 04 Learning from Results - The Update Rule.html`
- `../../products/make_site89/prose/Elo Ratings.html`
- `../../analysis/docs/story/06 Draft Standard Elo Account for the STEM Reader.md`
