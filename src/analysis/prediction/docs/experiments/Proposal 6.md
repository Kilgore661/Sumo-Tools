# Proposal 6: Fair-coin Bookmaker Null

## Status

Completed over the represented 1989/01–2026/07 results using the declared
2,000 fair-coin histories.

## Question

Is the positive return produced by Proposal 1's Basic Elo forecasts larger
than could reasonably arise if every represented bout were in truth a 50–50
event?

This gives the 50–50 proposition a concrete role. A bookmaker offers evens on
either rikishi because the bookmaker says that every bout is 50–50. A bettor
uses Basic Elo. Positive historical profit is evidence against the
bookmaker's proposition; the null histories show how much positive or negative
profit this procedure creates merely by chasing random sequences.

## Historical betting rule

Retain Proposal 1 exactly:

```text
epoch = 1989/01
q = 400
k = 35
initial rating = equal 1500
eligible result = W/L, irrespective of kimarite
ratings persist for the complete pass
forecast precedes update
```

For a pre-bout Elo forecast, let `p` be the larger of the two predicted win
probabilities. Bet on that favourite at evens and stake £p. A win earns £p and
a loss loses £p. If the forecast is exactly 50–50, do not bet and record zero
stake and zero profit.

The thought experiment chooses one eligible bout uniformly on every
represented day. It is unnecessary to make an additional random selection:
average stake and profit over all eligible bouts on that day. Sum the daily
averages within each basho, then average those basho totals over the epoch.
The primary statistic is therefore mean profit in pounds per notional 15-day
basho. Mean stake and return on stake are descriptive companions.

The all-bout population is primary. Bouts with two sekitori and bouts with two
sub-sekitori are predeclared secondary populations. Every eligible bout still
updates the single all-bout rating state.

## Fair-coin null histories

Retain the actual ordered bout schedule, RikIds, dates, days and evaluation
memberships. Replace every W/L result by a new independent outcome having
probability 0.5 for either participant. Rank, ability, the actual winner and
the current Elo forecast have no influence on a simulated result.

For every complete simulated 1989–end history, start again from equal ratings
and rerun Basic Elo chronologically. Later simulated forecasts must therefore
arise from earlier simulated results. Holding the historical forecasts fixed
would not represent the procedure being tested.

Generate 2,000 histories from Python's `random.Random` using seed 20260807 and
one continuous pseudorandom stream. The seed is an audit and reproducibility
device; it does not change the fair-coin hypothesis.

## Comparison

For each population, report:

- the historical mean profit per basho;
- the null median and the 50th and 1,950th ordered profits as the empirical
  95% range for 2,000 histories;
- the number of null histories whose profit is at least the historical profit;
- the one-sided Monte Carlo p value
  `(1 + count) / (2,000 + 1)`.

The add-one convention prevents a claim of zero probability from a finite
simulation. This experiment asks whether the observed directional betting
return is compatible with independent 50–50 results. It does not establish
that Elo probabilities are calibrated, that the return is commercially
available, or that prospective sumo betting is possible.

## Required artifacts

Write the observed population scores, all null-history scores, the comparison
summary, a manifest, a Markdown report, a responsive Plotly CDN histogram and
the total wall-clock execution time. Print progress, elapsed time and ETA after
every historical or simulated Elo pass.

## Result

The all-bout historical strategy stakes a mean £8.6096 and earns a mean
£1.2229 per represented 15-day basho, a return on stake of 14.20%. The 2,000
fair-coin histories have median complete-epoch mean profit -£0.0004 per basho
and an empirical 95% range from -£0.0231 to £0.0233. None reaches the
historical value.

The two secondary populations agree: the historical mean profits are £1.4440
for sekitori and £1.1830 for sub-sekitori, while their fair-coin 95% ranges
remain close to zero. Each population therefore has the add-one Monte Carlo
value `1 / 2,001 = 0.00049975`.

Under this experiment, the represented historical return is incompatible
with independent 50–50 outcomes. Basic Elo contains clear directional
predictive information even though its complete-epoch reduction in average
log loss is numerically small. This does not establish probability
calibration: hypothetical evens reward choosing the correct favourite, and
the experiment does not compare Elo probabilities with real market odds.
