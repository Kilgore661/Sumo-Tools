# GOAT-o-Matic requirements

## 1. Make Your Own GOAT

The primary experience lets users define what greatness means to them and generate a personal ranking of eligible rikishi.

After the user chooses the determining factors, the result must be an ordered ranking of rikishi rather than a standalone declaration such as "Your GOAT is ...". The leading rikishi will be apparent from the ranking, while the complete result lets the user see how every other eligible rikishi compares.

Users must be able to:

- choose any supported statistics as ranking criteria;
- assign weights or a priority order to those criteria;
- choose career-wide or fixed-window measures;
- decide whether longevity, peak performance and strength of opposition matter;
- filter the eligible rikishi;
- include or exclude active and partial careers;
- see every rikishi's raw values, any normalization, and each criterion's contribution to the result;
- see the overall score or ordering, the gaps to the leader and adjacent rikishi, and each rikishi's position in the complete ranking; and
- save or share their criteria.

The interface should warn when closely related statistics may be counted more than once. For example, total wins, Makuuchi wins and Makuuchi longevity all give substantial weight to career length.

The site must not claim that one definition of greatness is objectively correct or present a site-endorsed definitive GOAT. The normalization method for combining unlike measurements remains an open design decision.

## 2. Data You Might Like to Consider

The supporting statistical explorer lets users examine the evidence before deciding which criteria matter.

Users must be able to:

- select eligible rikishi;
- require a minimum number of Makuuchi-banzuke basho;
- include or exclude active and partial careers;
- add or remove columns;
- sort by multiple keys, with an independently chosen direction for each key;
- compare selected rikishi directly;
- inspect the basho and bouts underlying every statistic; and
- export the displayed table.

Useful starting views may include career achievement, peak dominance,
championship efficiency, longevity, strongest opposition and performance
against san'yaku.

## 3. Historical scope and eligibility

The data epoch begins with Hatsu 1958. There is no single analytical start date
for every metric.

Each future metric must declare the facts on which it depends and the earliest
date from which those facts are complete. For example:

- a Makuuchi yusho count may use the complete Makuuchi record from 1958; and
- a measure requiring sub-sekitori bouts may use only January 1989 onwards,
  because earlier lower-division bout records are incomplete.

Career completeness is therefore metric-dependent. A rikishi may have a
complete represented Makuuchi-yusho career while having a partial represented
all-division win career.

- A rikishi is active for a banzuke if and only if he appears anywhere on that
  banzuke. For the full-history output, the current active cohort is therefore
  defined by the latest supplied banzuke, regardless of division.
- Active rikishi may be included but must be marked **career in progress**.
- A rikishi must be marked partial for a metric if the relevant part of his
  career begins before that metric's complete-data boundary.
- Users do not select a historical period. Initial statistics use the complete
  supplied History.
- Canceled tournaments do not count as banzuke basho or championship opportunities.
- Exceptional events, including the May 2011 technical examination tournament, require an explicit tournament-status field rather than an implicit assumption.

## 4. Source data and provenance

The principal source is the available SumoDB dataset from 1958 onwards.
Coverage boundaries differ by fact type and must be published explicitly.

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

The standard denominator is the number of non-canceled basho for which the
rikishi appeared on the Makuuchi banzuke, regardless of how many bouts he
subsequently fought or whether he retired during the basho.

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

Fusen results remain part of the recorded basho score, but are excluded from
evidence about wrestling performance. A fusen result says nothing about the
absent rikishi's strength on that day, and the recipient did not defeat the
scheduled opponent on the dohyo.

Fusensho and fusenpai are excluded from:

- win rate;
- contested head-to-head records;
- strength-of-opposition calculations;
- records by opponent rank; and
- the average banzuke level of defeated opponents or opponents responsible for losses.

They remain included where required by the recorded basho score, including:

- basho-score totals (`W + FS` and `L + FP`);
- kachi-koshi and make-koshi;
- yusho and doten-yusho determination; and
- scheduled-opportunity success rate.

### 6.2 Playoff treatment

Every contested playoff bout is included in head-to-head records, playoff
records and strength-of-opposition calculations. Playoff bouts are outside the
15-or-7 scheduled-opportunity denominator and therefore do not enter win rate.

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
- Doten-yusho
- Yusho at yokozuna

Zensho-yusho count is retained as descriptive data and may be displayed in the
statistical explorer, but it is not an initial GOAT ranking factor.

Yusho at yokozuna is an initial GOAT ranking factor. Yusho at ozeki or below is
retained as descriptive data but is not an initial ranking factor.

Jun-yusho (`J`) and the Kanto-sho, Gino-sho and Shukun-sho (`K`, `G`, `S`) are
retained as descriptive data but are not initial GOAT ranking factors.

Playoff appearances, playoff wins and playoff losses are retained as
descriptive data but are not initial GOAT ranking factors.

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

An equivalent rate may be provided for doten-yusho. Zensho-yusho rate, if
shown, is descriptive rather than an initial GOAT ranking factor.

### 8.3 Winning performance

Basho-record rate:

\[
\frac{\text{wins}+\text{fusen wins}}
{\text{wins}+\text{losses}+\text{fusen wins}+\text{fusen losses}}
\]

This reproduces the win proportion in the recorded basho scores, where a fusen
win contributes to the score without being treated as a win.

Contested-bout win rate:

\[
\frac{\text{wins}}
{\text{wins}+\text{losses}}
\]

A win is a contested `W` and a loss is a contested `L`. Fusen results are not
wins or losses for this measure. Wins and losses cover all represented
divisions. A winning streak may cross a divisional boundary.

Winning streaks follow the contender's wins and availability. A win (`W`)
extends the streak and a loss (`L`) ends it. A fusen win (`FS`) neither extends
nor breaks the streak because the contender was available but the opponent did
not appear. A fusen loss (`FP`), kyujo or other genuine absence by the
contender breaks the streak. A normal day on which the rikishi was not
scheduled, including days between lower-division bouts, does not break it.

Win rate:

\[
\frac{\text{wins}}
{\text{scheduled bout opportunities}}
\]

Scheduled bout opportunities are determined by the rikishi's banzuke division
for each basho: normally 15 for sekitori and 7 below Juryo. A banzuke-gai
period supplies no scheduled opportunity. Absence, fusen loss and fusen win do
not add to the numerator but consume the relevant scheduled opportunity.

The interface must always identify the definition being displayed.

### 8.4 Basho-result distribution

- Mean and median basho-score wins (`W + FS`) per Makuuchi-banzuke basho
- Percentage of basho with 8+, 10+, 12+, 13+, 14+ and 15 wins
- Make-koshi rate

A Makuuchi-banzuke basho is make-koshi when the rikishi has fewer than eight
basho-score wins (`W + FS`). Absences occupy the remaining positions in the
15-day result, so a 7-0-8 record is make-koshi.

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

The initial fixed-window measure is the number of wins (`W`) in the window.
Fusen wins (`FS`) do not increase it. Other fixed-window measures may be added
later but are not part of the initial GOAT ranking.

If several windows of the same length share the maximum win count, every
co-best window is retained. No earliest/latest tie-break is applied.

Fixed windows follow consecutive non-canceled banzuke in the supplied History.
A banzuke-gai period occupies a position in the window even though it supplies
no bouts or scheduled opportunities. Windows do not close up around such a
gap.

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

Recent opponent form is retained as a separate descriptive measure rather
than combined with banzuke level:

\[
\text{Trailing three-basho W rate}
=
\frac{\text{W outcomes in the preceding three banzuke}}
{\text{scheduled opportunities in those banzuke}}
\]

The current basho is never included. Absences consume opportunities, `FS` does
not enter the numerator, and cancelled basho occupy no position. A complete
three-basho history is required; otherwise the value is unavailable. No
Yokozuna/Ozeki expectation or other rank adjustment is subtracted from the
rate. The rate may be summarized for all opponents and separately for
Yokozuna-or-Ozeki opponents when investigating the quality of a rikishi's
schedule.

## 10. Transparency and auditability

Every displayed statistic must expose:

- its plain-language definition;
- its numerator and denominator where applicable;
- whether lower or higher is better;
- the tournaments and bouts included;
- its treatment of absences, fusen and playoffs; and
- the source and provenance of supplementary data.

## 11. Initial non-requirements

The initial GOAT-o-Matic does not include:

- Elo or Bradley-Terry ratings;
- BAR or other compensated-result scores;
- estimated absolute era strength;
- medical or sports-science adjustments;
- hinkaku, popularity or cultural influence;
- retrospective opponent values based on eventual career achievements; or
- a site-endorsed definitive GOAT.

Medical progress and other era effects can instead be explored indirectly by allowing users to emphasize fixed-window performance, rates and contemporary banzuke opposition rather than cumulative career totals.
