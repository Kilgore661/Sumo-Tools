# The Grand Plan 2.0

This note records the current shape of the project after the Equelo work,
probability experiments, standings work, banzuke comparison work, and
presentation-layer thinking.

The point is not to replace the earlier Grand Plan. The point is to say what
survives after the exploratory work has taught us what can actually be
delivered.

---

# 1. The project

The project is:

> Build tools and exhibits that make professional sumo more legible through
> data.

That includes:

* operational tools, where a user wants to inspect current or generated data
* public facts, where a chart or table makes a stable pattern visible
* research work, where an idea is explored deeply enough to decide whether it
  can support a public claim

These are related, but they are not all the same kind of output.

---

# 2. The main distinction

The important distinction is now:

```text
interesting analysis
public deliverable
```

An analysis can be valuable without becoming a public deliverable.

A public deliverable has a different standard. It should have:

* a clear question
* a clear audience
* a stable interpretation
* an honest statement of what it does and does not show
* a form that someone else can use or revisit

This means that the final public surface should be curated. It should not be a
complete history of everything that was investigated.

---

# 3. What "analysis" means in this repo

In this repository, `analysis` is not just a miscellany of dives into the data.

It is becoming the place where data is turned into shareable public artefacts.

That does not mean every subfolder under `analysis` is public-facing. It means
that this is the layer where public-facing work is expected to emerge.

The current broad layers are:

```text
sumo_core   domain model
infra       data acquisition, parsing, persistence, live store
analysis    derived views, tools, facts, experiments, presentation
misc        loose scripts and older exploratory work
```

Later, `analysis` may need internal structure that separates polished
deliverables from research and abandoned lines of thought. For now, the
important thing is to understand the role of the layer.

---

# 4. Tools

Tools are operational public pages.

They let a user inspect or work with generated sumo data.

Current first-pick tools:

* Standings
* Banzuke Compare

These are good public candidates because they answer practical questions:

* Who has performed best over a recent rolling period?
* What changed on this banzuke?

They also already have a plausible publication model:

```text
Python computes static data
browser page presents and filters it
```

This is a strong pattern for the project.

---

# 5. Sumo Facts

Sumo Facts are public-facing exhibits.

They are not tools in the same operational sense. They are stable facts,
charts, tables, or arguments that make some part of sumo visible.

Current candidates:

* Finish by Chii
* Average Finish by Chii
* Banzuke Division by Era
* Makuuchi Rank by Era
* First Chii Appearance
* Observed Chii Matchup Probability Distribution

These should be judged by whether they make a clear pattern visible, not by
whether they are complex.

In many cases, a simple descriptive result is stronger than a more elaborate
modelled result.

---

# 6. Research

Research work is where the project explores ideas before knowing whether they
can be delivered.

This includes much of the Equelo work.

Equelo produced useful ideas:

* outcome-derived ratings
* calibration and probability evaluation
* the distinction between prediction and representation
* the danger of building chii into a model and then treating agreement with
  chii as discovery
* the value of simple baselines

But not every part of Equelo is a public deliverable.

The key lesson is:

> A model can be interesting without being the thing to publish.

If a usable system depends on teleological reasoning, then it should not be
presented as a clean empirical discovery. It can still be retained as research,
as supporting machinery, or as a record of what was learned.

---

# 7. What graduates

An output graduates into the public surface when it is useful without needing
the whole history of the project to justify it.

Good candidates have this shape:

```text
question -> data -> method -> result -> interpretation
```

The result should be understandable to someone who did not sit inside the
exploratory process.

This is why an observed chii matchup probability distribution is a better
first-pick public fact than an Expt3 model-predicted probability distribution.

The observed distribution says:

> Here is what happened in the data.

The model-predicted distribution says:

> Here is what one modelling construction implies.

Both may be interesting, but the first is a cleaner public fact.

---

# 8. Presentation layer

The public surface should be a single lab-style site:

```text
main title bar
main options | main content
```

The main navigation should initially distinguish:

```text
Tools
Sumo Facts
```

Each selected page can itself have the same shape:

```text
page title bar
page options | page content
```

The presentation primitive is therefore:

```text
title
options
content
```

This is the shared grammar for future pages. The goal is not merely to reduce
CSS duplication. The goal is to create a consistent public surface where new
tools and facts can be added without inventing a new page style each time.

---

# 9. Refactoring direction

The final repo may need a clearer distinction between:

* public deliverables
* supporting analysis
* research archives
* old exploratory scripts

That refactor should be product-led, not just tidy-up-led.

The question should not be:

> How do we make the folders look neat?

The question should be:

> What does the project want to present, and what structure best supports that?

Possible future structure:

```text
analysis/
  tools/
  facts/
  research/
  common/
```

or:

```text
analysis/
  public/
  research/
  common/
```

The exact shape can wait. The important point is that the public surface should
be curated.

---

# 10. Grounding principle

The project should keep this rule close:

> No tool is the point. The point is what it makes visible.

That means:

* models are useful when they clarify something
* charts are useful when they make a pattern visible
* tools are useful when they let someone inspect something worth inspecting
* public pages are useful when they can be understood without private context

The final product is not a record of all the work.

The final product is the set of things worth showing.

---

# 11. Current plan

The immediate public direction is:

1. Keep Standings and Banzuke Compare as the first operational tools.
2. Gather the strongest descriptive outputs into Sumo Facts.
3. Keep Equelo and probability work available as research unless a narrow,
   clean public claim emerges.
4. Build a shared presentation grammar around title, options, and content.
5. Let later refactoring follow the public surface rather than precede it.

This is the Grand Plan 2.0:

> A curated Sumo Lab, built from exploratory work, but not burdened by every
> path the exploration took.
