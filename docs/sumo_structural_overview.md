## Grand Sumo (*Ōzumō*): A Structural Overview

Professional sumo is a centrally administered competition in which wrestlers are arranged in a single ranking hierarchy, compete in regularly scheduled tournaments, and move upward or downward according to their results. Its basic structure is therefore a repeated cycle:

**ranking list → tournament bouts → win–loss records → revised ranking list**

All professional sumo is governed by the **Japan Sumo Association**. Wrestlers, known as *rikishi*, belong to training organizations called **stables** (*heya*), but they compete as individuals rather than as stable teams. Stable membership affects training, recruitment, and bout scheduling.

Grand Sumo, henceforth “sumo”, has many rules, but relatively few are absolute. Unless stated otherwise, declarative statements below should be understood as describing normal practice rather than inviolable rules.

### The tournament cycle

Sumo holds six official tournaments, or *honbasho*, each year. They begin in every odd-numbered month.

Each tournament lasts **15 consecutive days**. Wrestlers in the top two divisions normally compete once per day, giving them a final record over 15 bouts. Wrestlers in the lower four divisions normally compete in **seven bouts**, spread across the tournament.

A wrestler finishes with either a winning record, called *kachi-koshi*, or a losing record, called *make-koshi*. A winning record contains more wins than losses; a losing record contains more losses than wins. These records are the main inputs used to construct the ranking list for the next tournament.

### The ranking hierarchy

The official ranking list is called the **banzuke**. It places each active wrestler at a specific position in a single ordered hierarchy.

The hierarchy is divided into six divisions, from highest to lowest:

1. **Makuuchi**
2. **Jūryō** (`J`)
3. **Makushita** (`Ms`)
4. **Sandanme** (`Sd`)
5. **Jonidan** (`Jd`)
6. **Jonokuchi** (`Jk`)

The boundary between Jūryō and Makushita is particularly important. Wrestlers in Makuuchi and Jūryō are salaried professionals known collectively as **sekitori**. There is no corresponding collective noun for rikishi in the lower four divisions, but we sometimes use the term **sub-sekitori**.

Promotion and demotion can occur both within a division and between divisions. A strong winning record generally moves a wrestler upward, while a losing record generally moves them downward. The size of the movement is not fixed mechanically: it also depends on the wrestler’s starting position, the records of nearby wrestlers, and the number of places available in the relevant division.

### Rank positions

Most positions on the *banzuke* can be described using three components:

- a division or named rank;
- a numerical level;
- an **East** or **West** side.

These positions, or *chii*, are usually written in compressed form. For example, `Ms30w` means Makushita, level 30, West.

Within a given category, level 1 is highest, followed by level 2, level 3, and so on. At each level, East is ranked immediately above West. Thus `Ms5e` ranks immediately above `Ms5w`, while `Ms4w` ranks above `Ms5e`.

The top division, Makuuchi, contains two broad rank categories.

The majority of its wrestlers are **maegashira**, or rank-and-file wrestlers, abbreviated `M`. Their positions are ordered:

`M1e, M1w, M2e, M2w, …`

The lowest maegashira level varies according to the composition of the division. It is commonly around level 16 or 17, although level 18 may also occur.

Above maegashira are the title ranks, collectively known as **san’yaku**. In descending order, they are:

1. **Yokozuna** (`Y`)
2. **Ōzeki** (`O`)
3. **Sekiwake** (`S`)
4. **Komusubi** (`K`)

The same level-and-side notation applies throughout the hierarchy. The highest possible position is `Y1e`, followed by `Y1w`. If there are further yokozuna, they occupy `Y2e`, `Y2w`, `Y3e`, and so on.

The ōzeki positions then begin with `O1e`, followed by `O1w`, `O2e`, `O2w`, and so forth. The same pattern applies to sekiwake, komusubi, maegashira, and the lower divisions.

The named ranks do not all have the same promotion and demotion rules. Komusubi and sekiwake may be promoted or demoted according to tournament performance. Promotion to ōzeki depends on sustained high-level performance across several tournaments. An ōzeki who records a losing tournament becomes *kadoban* and is at risk of demotion after the following tournament.

### Bout scheduling

The Japan Sumo Association determines the pairing for each bout. A tournament is not a complete round-robin competition, and wrestlers do not face every other member of their division.

Early bouts are generally arranged between wrestlers of similar rank. As results accumulate, scheduling increasingly takes account of current performance. Wrestlers with strong records are increasingly likely to face other successful wrestlers, although rank and other scheduling constraints remain relevant.

This means that two wrestlers can finish with the same record after facing substantially different sets of opponents.

### The result of a bout

A bout takes place in the **dohyō**, a circular contest area approximately 4.55 metres in diameter.

A wrestler loses when either:

- any part of their body other than the soles of their feet touches the ground; or
- they touch the ground outside the contest circle.

The first wrestler to satisfy either condition loses, even if the opponent falls or steps out immediately afterward. Officials may call for a judges’ conference when the result is unclear. A bout may then be awarded to one wrestler or ordered to be fought again.

Winning actions are classified using an official set of techniques known as **kimarite**. These labels describe how the bout ended, but for ranking purposes every ordinary win has the same value: one win, regardless of technique or opponent.

### A model-ready summary

At its simplest, sumo can be represented as a dynamic ranking system with the following elements:

- a finite ordered population of wrestlers;
- division, rank, level, and side coordinates;
- six discrete tournament periods per year;
- unequal numbers of bouts across divisions;
- partially adaptive, non-random bout scheduling;
- binary bout outcomes;
- promotion and demotion based mainly, but not exclusively, on win–loss records;
- special transition rules governing the highest ranks.

The central mathematical complication is that rank affects scheduling, scheduling affects the difficulty of a wrestler’s opponents, results affect future rank, and future rank then affects subsequent scheduling. The competition is therefore not merely a sequence of independent bouts, but a feedback system linking performance, opponent selection, and position in the hierarchy.
