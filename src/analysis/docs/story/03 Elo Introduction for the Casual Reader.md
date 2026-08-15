# Elo Introduction for the Casual Reader

An Elo rating system uses previous results to give each competitor a running
rating. The rating is mainly useful when compared with somebody else's rating:
the difference between the two numbers determines which competitor Elo favours
and by how much.

For example, one implementation might give a yokozuna a rating of 2500 and an
M1 a rating of 2100 (a difference of 400 points). On that implementation's
scale, Elo might estimate that the yokozuna has about a 74% chance of winning.
This does not guarantee the result: it means that, in repeated comparable
contests, the lower-rated rikishi would still be expected to win roughly one
time in four.

Ratings change after every result. Beating someone with a much lower rating
changes little because Elo already expected that result. An unexpected win
against a much higher-rated opponent changes the ratings by more. Elo therefore
does more than count wins: it also takes account of the ratings of the
opponents.

A rating such as 2500 does not represent 2500 units of "strength" and has no
useful meaning by itself. The useful information is the difference between
ratings and the estimated probability produced from that difference. Saying
that one rikishi has a higher Elo rating means that Elo would favour him in a
bout against the lower-rated rikishi.

The same comparison can arise between lower ratings. On the same illustrative
scale, a lower-ranked maegashira might have a rating of 1900 and a mid-juryo
rikishi a rating of 1500. This is also a difference of 400 points, so Elo would
again estimate that the higher-rated rikishi had about a 74% chance of winning.
The absolute ratings are different, but the comparison is the same because the
difference between them is the same.

Elo is not an explanation of why a rikishi wins. It does not by itself know
about injuries, fighting styles, absences or other circumstances. It is a
calculation that summarizes previous results and uses them to distinguish
between the competitors in a future contest.

Applied to historical sumo, one specified Basic Elo calculation produced
probabilities that scored slightly better overall than treating every bout as
having a 50--50 outcome. That is a limited result: it shows that the calculation
found some useful pattern in previous results, not that every rating or forecast
was reliable. As with the 74% estimate above, however, how well any particular
Elo model predicts actual results is a separate question, to which we will
return later.
