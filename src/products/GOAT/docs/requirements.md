# GOAT-o-Matic requirements

## 1. Make Your Own GOAT

The primary experience lets users define what greatness means to them and generate a personal ranking of eligible rikishi.

Users must be able to:

- choose any supported statistics as ranking criteria;
- assign weights or a priority order to those criteria;
- choose career-wide or fixed-window measures;
- decide whether longevity, availability, peak performance and strength of opposition matter;
- filter the eligible rikishi and historical period;
- include or exclude active and partial careers;
- see every rikishi's raw values, any normalization, and each criterion's contribution to the result; and
- save or share their criteria.

The interface should warn when closely related statistics may be counted more than once. For example, total wins, Makuuchi wins and Makuuchi longevity all give substantial weight to career length.

The site must not claim that one definition of greatness is objectively correct or present a site-endorsed definitive GOAT. The normalization method for combining unlike measurements remains an open design decision.

## 2. Data You Might Like to Consider

The supporting statistical explorer lets users examine the evidence before deciding which criteria matter.

Users must be able to:

- select eligible rikishi and dates;
- require a minimum number of Makuuchi-banzuke basho;
- include or exclude active and partial careers;
- add or remove columns;
- sort by multiple keys, with an independently chosen direction for each key;
- compare selected rikishi directly;
- inspect the basho and bouts underlying every statistic; and
- export the displayed table.

Useful starting views may include career achievement, peak dominance, championship efficiency, longevity, availability, strongest opposition and performance against san'yaku.

## 3. Historical scope and eligibility

The source period begins with Hatsu 1958.

The default complete-career cohort consists of rikishi whose first Makuuchi-banzuke appearance was in January 1958 or later. This avoids comparing complete careers with careers truncated at the beginning of the dataset.

- Active rikishi may be included but must be marked **career in progress**.
- Users may change the starting date.
- A rikishi whose Makuuchi career began before the selected date must be excluded by default or marked **partial career**.
- Canceled tournaments do not count as banzuke basho or championship opportunities.
- Exceptional events, including the May 2011 technical examination tournament, require an explicit tournament-status field rather than an implicit assumption.

## 4. Source data and provenance

The principal source is the available SumoDB dataset from 1958 onwards.

The data model must cover:

- rikishi;
- basho;
- banzuke appearances;
- scheduled and contested bouts;
- official basho records;
- championships and runner-up designations;
- absences; and
- playoffs.

Imported SumoDB data must remain distinguishable from manually supplemented data. Manually added records must retain their source.

## 5. Banzuke-basho denominators

The product must not describe a denominator as "tournaments entered." Entry is not a voluntary choice in this context.

The standard denominator is the number of non-canceled basho for which the rikishi appeared on the Makuuchi banzuke. It includes completed basho, partial kyujo, zen-kyu and retirement during a basho.

Equivalent rank-specific denominators must be available for:

- yokozuna-banzuke basho;
- ozeki-banzuke basho; and
- san'yaku-banzuke basho.

## 6. Bout classification

Every bout record must be classified as one of:

- contested scheduled bout;
- fusensho;
- fusenpai; or
- contested playoff bout.

### 6.1 Fusen treatment

Fusen results remain part of official tournament records, but are excluded from evidence about wrestling performance. A fusen result says nothing about the absent rikishi's strength on that day, and the recipient did not defeat the scheduled opponent on the dohyo.

Fusensho and fusenpai are excluded from:

- contested win rate;
- contested head-to-head records;
- strength-of-opposition calculations;
- records by opponent rank; and
- the average banzuke level of defeated opponents or opponents responsible for losses.

They remain included where required by the official record, including:

- official win and loss totals;
- official basho scores;
- kachi-koshi and make-koshi;
- yusho and jun-yusho determination; and
- scheduled-bout win rate.

### 6.2 Playoff treatment

Every contested playoff bout is included in contested head-to-head records, contested win rate, playoff records and strength-of-opposition calculations.

Two-person playoffs may be reconstructed from the tied scores and recorded champion. Multi-rikishi playoffs require a supplementary, sourced table containing at least:

```text
basho
sequence
winner_id
loser_id
source
```

## 7. Banzuke-level representation

Opponent strength is initially represented entirely by the opponent's level on the published banzuke for that basho.

The level mapping is:

\[
L(r)=
\begin{cases}
0 & Y \\
1 & O \\
2 & S \\
3 & K \\
n+3 & M_n
\end{cases}
\]

In plain form:

```text
Y=0, O=1, S=2, K=3, M1=4, M2=5, ...
```

Rules:

- East and west are treated equally.
- All occupants of the same san'yaku rank are treated equally.
- Y1e and Y4w are both level 0.
- O1e and O3e are both level 1.
- A yokozuna-ozeki is treated as yokozuna.
- A former ozeki currently listed at sekiwake is treated as sekiwake.
- No Elo, Bradley-Terry, BAR or other inferred or compensated ability score is used.

The site must call this measure **banzuke level**, not true or absolute ability. The numbers preserve the published ordering but do not establish that the ability difference between every adjacent pair of levels is equal.

## 8. Core statistics

### 8.1 Achievement

- Makuuchi yusho
- Zensho-yusho
- Jun-yusho
- Playoff appearances
- Playoff wins and losses
- Yusho at yokozuna
- Yusho at ozeki or below

### 8.2 Championship rates

\[
\text{Makuuchi yusho rate}
=
\frac{\text{Makuuchi yusho}}
{\text{Makuuchi-banzuke basho}}
\]

\[
\text{Yokozuna yusho rate}
=
\frac{\text{yusho while yokozuna}}
{\text{yokozuna-banzuke basho}}
\]

Equivalent rates may be provided for zensho-yusho and jun-yusho.

### 8.3 Winning performance

Official win rate:

\[
\frac{\text{official wins}}
{\text{official wins}+\text{official losses}}
\]

Contested win rate:

\[
\frac{\text{contested wins}}
{\text{contested wins}+\text{contested losses}}
\]

Scheduled-bout win rate:

\[
\frac{\text{official wins}}
{15\times\text{Makuuchi-banzuke basho}}
\]

The interface must always identify the definition being displayed.

### 8.4 Basho-result distribution

- Mean and median official wins per Makuuchi-banzuke basho
- Percentage of basho with 8+, 10+, 12+, 13+, 14+ and 15 wins
- Make-koshi rate
- Zen-kyu rate
- Partial-withdrawal rate

### 8.5 Longevity

- Makuuchi-banzuke basho
- Yokozuna-banzuke basho
- Makuuchi wins
- Span between first and last yusho
- Age at first and last yusho
- Number of basho producing 10+, 12+ and 13+ wins

### 8.6 Peak

- Best 6-basho period
- Best 12-basho period
- Best 24-basho period
- Best 36-basho period
- Best 60-basho period
- Longest winning streak
- Most consecutive yusho
- Most consecutive kachi-koshi

For every fixed window, the selected measure must be explicit: wins, win rate, yusho or another supported statistic.

## 9. Strength of opposition

All opposition measures use contested scheduled and playoff bouts only. Fusen results are ignored.

The principal measure is:

\[
\text{Average Opponent Banzuke Level}
=
\frac{\sum_j L(\text{opponent}_j)}
{\text{contested bouts}}
\]

Lower values indicate more highly ranked opposition.

Supporting statistics include:

- median opponent banzuke level;
- percentage of contested bouts against yokozuna;
- percentage against yokozuna or ozeki;
- percentage against san'yaku;
- contested record against each individual level;
- average banzuke level of defeated opponents; and
- average banzuke level of opponents responsible for losses.

Relative schedule difficulty may be reported separately:

\[
\text{Average Rank Gap}
=
\operatorname{mean}
\left[L(\text{opponent})-L(\text{rikishi})\right]
\]

A negative value indicates opponents formally above the rikishi; a positive value indicates opponents formally below him. Rank gap must not be presented as a substitute for absolute opponent level.

No compensation is applied to a win or loss because of opponent level.

## 10. Availability

Availability distinguishes an absent rikishi from the recipient of a fusensho:

\[
\text{Availability rate}
=
\frac{\text{contested bouts}+\text{fusensho received}}
{15\times\text{banzuke basho}}
\]

- A contested bout demonstrates availability.
- Receiving a fusensho demonstrates readiness to compete.
- A fusenpai demonstrates non-availability.
- The scheduled opponent's absence must not penalize the available rikishi.

## 11. Transparency and auditability

Every displayed statistic must expose:

- its plain-language definition;
- its numerator and denominator where applicable;
- whether lower or higher is better;
- the tournaments and bouts included;
- its treatment of absences, fusen and playoffs; and
- the source and provenance of supplementary data.

## 12. Initial non-requirements

The initial GOAT-o-Matic does not include:

- Elo or Bradley-Terry ratings;
- BAR or other compensated-result scores;
- estimated absolute era strength;
- medical or sports-science adjustments;
- hinkaku, popularity or cultural influence;
- retrospective opponent values based on eventual career achievements; or
- a site-endorsed definitive GOAT.

Medical progress and other era effects can instead be explored indirectly by allowing users to emphasize fixed-window performance, rates and contemporary banzuke opposition rather than cumulative career totals.
