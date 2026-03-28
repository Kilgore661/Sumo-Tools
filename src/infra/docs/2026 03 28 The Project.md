## What the Tracker Is (and Why It Exists)

### A Typical Use Case

You’re working on a new analysis — say Elo ratings.

You load the history zip and start coding. It works.

You run it again later and now:

* new results have appeared (because a basho is ongoing), or
* results you expected aren’t there, or
* something has changed and you’re not sure why

At that point you have to stop and ask:

* is my code wrong?
* is the data incomplete?
* is the system out of date?

You don’t want to keep answering those questions.

What you want is:

> At any moment, the data is either OK to use, or clearly not — and you can tell which.

That’s what the tracker is for.

---

### The Basic Idea

The tracker is a program that runs continuously and keeps the data up to date.

It maintains:

* downloaded source data
* a reconstructed history (the zip)
* a small set of derived outputs

It does this automatically, without you having to think about it most of the time.

---

### The Problem It Solves

Sumo data doesn’t arrive all at once:

* results appear day by day during a basho
* a basho isn’t complete until it ends
* sometimes data is late or temporarily missing

But your tools expect a single, coherent dataset.

So there’s a mismatch:

* the world is messy and incremental
* your code wants something stable

The tracker sits in the middle and keeps things consistent.

---

### What the Tracker Maintains

At any time, the tracker tries to keep three things in sync:

1. The raw downloaded data
2. The reconstructed history (zip)
3. Some basic derived outputs (e.g. CSV/JSON views)

Most of the time this should just work in the background.

---

### The Zip File

The zip is the main thing you care about.

It should always be:

* internally consistent
* usable by your tools
* not silently wrong

If that holds, you can start writing or running code against it at any time.

---

### Two Kinds of “Good Enough”

There are two slightly different ideas of “valid”:

**Good for the tracker**
The system managed to:

* download what it needed
* rebuild the history
* update outputs

**Good for you**
The data is usable for whatever you’re working on

These usually line up, but not always. For example:

* data might be slightly out of date but still fine for testing
* or it might be technically complete but not useful for a specific idea

---

### States of the Data

From your point of view, the data is in one of three states:

* **Current** — everything is up to date
* **Stale but OK** — still consistent, but missing recent updates
* **Not trustworthy** — something has gone wrong

The tracker’s job is:

* to keep things current when it can
* and to make it obvious when it can’t

---

### When the Tracker Stops

The tracker should stop when continuing would be misleading.

In practice, that means:

* data that should exist by now
* still isn’t there
* after repeated attempts

There needs to be a cutoff. In this system, that cutoff is the end of the current basho.

If the data still isn’t complete by then, something is wrong and the tracker should stop rather than carry on as if everything is fine.

---

### What This Is Not

This isn’t:

* real-time data
* a guarantee that everything is always perfect
* a full analysis system

It’s just a way to keep a dataset in a usable state.

---

### Why Bother

Without this, you’d have to:

* manually update data
* rebuild things yourself
* or risk working with something broken

With it, you can just assume:

* either the data is fine
* or the system has told you it isn’t

