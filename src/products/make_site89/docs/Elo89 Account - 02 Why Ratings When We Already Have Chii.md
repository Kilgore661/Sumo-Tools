# 2. Why Ratings When We Already Have Chii?

## 2.1 What chii tell us

A chii such as M3w is a rikishi’s official place on the banzuke. Results are central to that position, but the institution making the decisions has wider responsibilities. The JSA describes its mission as preserving and developing sumo’s traditions and order, and promoting sumo culture. That provides the setting in which official rank should be understood. [JSA mission](https://www.sumo.or.jp/IrohaKyokai/organization/)

These considerations become particularly explicit at the highest rank. The JSA’s account of yokozuna promotion names outstanding *hinkaku*—dignity or character—alongside outstanding competitive ability. Such a criterion requires judgement: a win–loss record alone cannot determine whether it has been met. [JSA explanation of yokozuna promotion](https://www.sumo.or.jp/Entertainment/quiz/1081)

There is therefore a subjective element to official ranking: informed judgement about how sumo’s standards apply to a particular wrestler and his circumstances. Here, “subjective” means that the decision requires interpretation, not that it is arbitrary.

Elo89 has a narrower purpose. It supplies a numerical account of competitive performance under explicit assumptions. Those assumptions embody choices, but once they and the inputs are fixed, the calculation requires no further judgement about an individual wrestler. This makes ratings a useful complementary tool alongside chii.

Although chii and ratings are not interchangeable, the following reference values give a rough guide to Elo89’s numerical scale. They associate a rating with the highest chii in each of the six divisions.

| Division  | Top chii | Elo89 reference rating |
| --------- | -------- | ----------------------:|
| Makuuchi  | Y1e      | 2,428                  |
| Juryo     | J1e      | 2,101                  |
| Makushita | Ms1e     | 1,979                  |
| Sandanme  | Sd1e     | 1,688                  |
| Jonidan   | Jd1e     | 1,480                  |
| Jonokuchi | Jk1e     | 1,326                  |

These are reference points, rounded to whole numbers, rather than ratings that every wrestler at those chii will have. Where the numbers come from, and how individual ratings develop, will be explained as this account proceeds.

## 2.2 What results tell us

Results are the starting evidence: who faced whom, and who won. A win–loss record summarises those outcomes, but leaves out the opposition.

That omission matters. A 10–5 record contains more wins than an 8–7, but it does not automatically provide evidence of stronger performance. The wrestler with eight wins may have faced substantially more demanding opponents. Before deciding what the records tell us about the two rikishi, we need to consider whom they fought.

The same applies across several basho. Twenty-nine wins is more than twenty-four, but the totals alone do not establish which wrestler performed better against the opposition he faced. Nor does a fall in a wrestler’s win total necessarily indicate decline: he may have moved up and encountered stronger opponents.

Choosing the period introduces another consideration. Sumo has individual basho champions, but no season-ending championship that supplies a natural endpoint for an overall assessment. We can examine the last six or twelve basho, for example, but the window is our choice. Different windows answer different questions about recent and sustained performance.

To go beyond counting wins, we therefore need a way to account for the opposition and to carry evidence forward through time. Elo89 provides one such tool.

## 2.3 What ratings add

Elo89 uses each opponent’s rating to put a result in context. A win against a highly rated opponent provides different evidence from a win against someone rated much lower. The calculation applies the same principle throughout the population, updating both wrestlers’ ratings after each eligible bout.

This may seem circular: we assess a wrestler using his opponents’ ratings, which themselves depend on their opponents’ ratings. But those relationships are precisely what the system records. Each wrestler’s results connect him to others, whose results connect them to still others. The ratings develop together as bouts supply new evidence.

That also explains why an interest in makuuchi leads us into the lower divisions. A wrestler arriving in makuuchi brings a competitive history with him. His rating already reflects his results against earlier opponents; promotion does not start his rating afresh. (The divisions are also connected directly by bouts: lower-ranked maegashira occasionally face higher-ranked juryo.)

Ratings also carry evidence forward through time. Elo89 does not reset at the start of a calendar year or discard a result when it falls outside a six-basho window. Earlier results have helped shape the current ratings, and new results modify them. How quickly the calculation responds is a modelling choice that we will examine later.

We can therefore compare two current ratings without first choosing a period over which to count wins. We can also follow how those ratings change through a career. This does not remove the choices involved in assessing performance: it makes them explicit in the rating system.

The resulting number is a running assessment, informed by the opposition and the sequence of results. Whether that assessment is useful is a further question—one that requires evidence as well as an explanation of the calculation.
