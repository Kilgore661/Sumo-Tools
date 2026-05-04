# 🧠 1. The starting point: what ratings actually are

At the most basic level, an Elo-style system gives you:

* a set of numbers (ratings)
* a rule that maps **differences in those numbers** to **probabilities of outcomes**

That’s it.

The key fact — which is easy to forget — is:

> **Only differences in ratings matter. Absolute levels do not.**

You can add +100 to every rating:

* nothing changes
* all predictions are identical

So in a strict sense:

> Ratings are not measurements of “skill” in an absolute sense.
> They are a coordinate system for representing *relative performance*.

---

# ⚖️ 2. Two fundamentally different ways to interpret ratings

From that starting point, there are two ways you can think about ratings.

---

## View 1 — Ratings are purely relational (Elo-pure view)

In this view:

* ratings are just a convenient way of encoding pairwise strengths
* only differences matter
* absolute values are arbitrary

So:

* “2700” does not *mean* anything in itself
* it only means “this player is stronger than others by X amount”

This implies:

> Ratings are an **instrument**, not a representation of reality.

---

### Consequences of this view

* You should not interpret rating levels as meaningful categories

* You should not expect a fixed mapping like:
  
  ```text
  2500 ⇔ yokozuna
  ```

* Any such mapping would be accidental or dataset-specific

Instead:

> The only thing you trust is the mapping:
> 
> ```text
> rating difference → probability
> ```

---

## View 2 — Ratings are a latent scale (anchored view)

In this view:

* ratings approximate an underlying continuous notion of ability
* absolute levels become meaningful
* categories (like rank) correspond to regions on that scale

So:

```text
rating ≈ latent ability
chii ≈ labelled regions of that ability scale
```

Now statements like:

```text
2500 ≈ yokozuna
```

start to look meaningful.

---

### Where this view comes from

This view does **not** come from Elo itself.

It comes from **adding structure**, for example:

* careful initialisation (Expt2)
* fixed-point constraints
* anchoring conventions
* assumptions about stability

Once you do that, you are no longer just using Elo — you are building a **model of the system**.

---

# 🔗 3. How Expt3 and Expt2 map onto these views

---

## Expt3 → View 1 (relational)

Expt3 deliberately avoids structure:

* all entrants start with the same rating
* no rank information is used
* the system is driven entirely by outcomes

So:

> Ratings emerge purely from results.

This means:

* no notion of chii is built into the model
* ratings are **independent of rank**

---

### What this gives you

A very important property:

> Ratings are a **pure outcome-derived object**

So you can meaningfully ask:

> “What is the relationship between ratings and chii?”

Because:

* chii is **external**
* ratings are **independent**

---

## Expt2 → View 2 (anchored)

Expt2 does something very different:

* it uses rank (chii) to initialise ratings

* it enforces self-consistency via fixed-point iteration

* it produces a mapping:
  
  ```text
  μ(chii) → rating
  ```

So:

> Ratings are constructed *using* chii.

---

### What this means

Now:

* ratings already encode a theory of rank

* the system contains a built-in relationship:
  
  ```text
  chii → rating
  ```

So when you later compare ratings to chii:

> you are partly comparing something to itself

---

# ⚠️ 4. The key asymmetry

This is the most important conceptual point.

---

## In Expt3:

```text
outcomes → ratings → compare to chii
```

* ratings come from outcomes only
* chii is external
* any agreement is **informative**
* any disagreement is **informative**

---

## In Expt2:

```text
chii → ratings → compare to chii
```

* ratings already depend on chii
* agreement is partly **built in**
* disagreement is harder to interpret

---

### This leads to a fundamental difference:

> Expt3 allows **discovery**
> Expt2 allows only **representation**

---

# 🧠 5. The “what is chii?” question

This is really the central question of your Grand Plan.

---

## With Expt3

You can ask:

> What structure in outcomes corresponds to chii?

For example:

* Is chii a discretisation of rating?
* Is it a smoothed version?
* Does it lag behind performance?
* Does it encode additional constraints?

Because:

> chii is not used in constructing ratings

---

## With Expt2

You cannot ask that question cleanly.

Instead you can only ask:

> Does the mapping we constructed behave like chii?

For example:

* is μ(chii) monotonic?
* are adjacent ranks separated?
* is the structure smooth?

But:

> you are analysing your own construction

---

# 🎯 6. The “2500 ≈ yokozuna” issue

This is where the two views collide most clearly.

---

## In Expt2

If you find:

```text
μ(Yokozuna) ≈ 2500
```

then yes:

> within that model, 2500 corresponds to yokozuna

But:

* this depends on:
  
  * aggregation method
  * normalisation
  * dataset
  * modelling assumptions

So:

> it is not a universal truth — it is a property of the construction

---

## In Expt3

If you observe that:

* wrestlers with ratings around 2500 behave like yokozuna

then:

> that is an empirical finding

Because:

* the system did not know about chii
* the correspondence emerged from outcomes

---

# 🧩 7. Why Expt3 is essential for the Grand Plan

The Grand Plan is based on this idea:

> Compare an outcome-only system to the institutional ranking (chii)

This only works if:

> the baseline system does **not already contain chii**

---

Otherwise:

* differences are contaminated
* agreement is partly circular

So:

> Expt3 provides a **clean baseline**

---

# 🔧 8. Where Expt2 still fits

Expt2 is not useless — it just has a different role.

---

## Expt2 is about:

* constructing a structured rating system
* understanding rank → rating mappings
* improving initialisation
* exploring stability and consistency

---

## But it is not:

* a neutral baseline
* a tool for discovering what chii is

---

# 🧠 9. The clean separation

The whole project becomes much clearer if you separate roles:

---

## Expt3

* outcome-only

* minimal assumptions

* used for:
  
  * comparison
  * discovery
  * epistemology

---

## Expt2

* structured

* rank-informed

* used for:
  
  * modelling
  * representation
  * internal consistency

---

# 🧾 10. Final statement

Putting it all together:

---

There are two fundamentally different ways to think about ratings.

In one view, ratings are purely relational objects. They encode differences in performance and are only meaningful insofar as they produce calibrated predictions. Absolute values have no intrinsic meaning, and any attempt to interpret them as corresponding to real-world categories is misguided. This view aligns with a minimal, outcome-driven system in which ratings emerge entirely from observed results.

In the other view, ratings are treated as a latent scale of ability. In this interpretation, absolute levels become meaningful, and categories such as rank correspond to regions on that scale. This requires additional structure — in particular, a way of anchoring ratings at entry — and leads to constructions in which ratings encode assumptions about the relationship between rank and performance.

These two views are not interchangeable. The first supports discovery: it allows the relationship between ratings and institutional rankings to be examined without prior assumptions. The second supports representation: it produces a coherent mapping between rank and rating, but does so by building that relationship into the model itself.

If the aim is to understand what the institutional ranking represents — what information it captures, what it discards, and how it relates to outcomes — then the first approach is essential. It provides a baseline that is independent of the institution and therefore suitable for comparison.

If, on the other hand, the aim is to construct a stable and interpretable rating system that incorporates known structure, then the second approach is appropriate. But it should be recognised that this comes at the cost of losing the ability to treat the institutional ranking as an external object of study.
