# 1. What Is This About?

*Part 1 of 5 — [Next: Base Model of Competition Over Time](02-base-model.md)*

## Purpose

This account develops a deliberately selective model of competition over time. It begins with an observational History and adds further concepts only when they become necessary for the constructions under consideration. The resulting framework is a lens adopted for a particular investigation, not a claim about everything that can matter in competition.

## The model as a lens

No model of competition can anticipate everything that somebody might consider important. One investigator may care about player strength; another about fatigue, injuries, tactics, institutional decisions, travel, rules, spectators or economic incentives. Any of these could be made primitive in a model designed for the corresponding purpose. A model containing every potentially relevant feature would not be a useful base model at all.

Our model therefore makes no claim to identify the fundamental ontology of competition. It establishes a particular observational lens. Through that lens, a competition over time is represented by who competed with whom, when they competed and what the result was. A History encapsulates those observations. Schedules and records are derived views of the same information.

Calling this the **base model** means only that it is the base for the present investigation. It does not mean that every possible theory of competition ought to begin with exactly these objects.

In particular, the omission of player strength from the base is not a claim that strength is unreal, unimportant or incapable of being studied independently. It means only that no player-strength value is needed to specify a History or derive its schedules. Up to that point, adding such a value would introduce a concept that the construction does not yet use.

Player strength first becomes relevant in our development when we consider one particular interpretation of schedule strength: the idea that a schedule is strong because it contains strong opponents. That interpretation requires a player-strength carrier and a player-strength operation. Their introduction is therefore visible and motivated rather than silently presupposed.

Another investigation might introduce player strength much earlier. For example, a theory concerned primarily with predicting results might take player strength as one of its first concepts. That would not show that our base model is wrong; it would show that the other theory has adopted a different lens and made different commitments.

Nor do we claim that every schedule-strength measure must use player strength. A schedule might instead be assessed through its length, timing, concentration, repetition or some other feature. Opponent-strength-based schedule strength is one extension of the abstract schedule-strength operation, selected because it has an intelligible sporting interpretation.

The purpose of separating these layers is consequently not to settle in advance what matters. It is to make clear when a new idea enters the model, what information it requires and what subsequent constructions depend upon it. The framework remains open to other extensions precisely because it does not pretend to predict every future question.

Accordingly, a statement such as “player strength is irrelevant” must be read locally:

> Player strength is not required by the observational base and does no work in the present construction until an opponent-strength-based account of schedule strength is chosen.

It must not be read as the universal claim that player strength can have no other importance.

## Why use algebraic signatures?

The account uses carriers, operations and function signatures to make its concepts and dependencies explicit. This is not an attempt to develop every object through universal algebra, nor a demand that every implementation turn every mathematical type into a class.

Ordinary mathematical infrastructure—natural numbers, Boolean values, times, sequences and option types—can remain in the background. Domain concepts such as bouts, histories and schedules are made explicit where doing so helps us see what information an operation requires.

The signatures therefore function as a conceptual type system. They allow us to distinguish, for example, a measure that uses only a selected schedule from one that also inspects the global history. The value of the notation lies in exposing these choices, not in formalisation for its own sake.

## Roadmap

The account is divided into five short notes:

1. **What Is This About?** explains the modelling stance and the limits of the claim being made.
2. **[Base Model of Competition Over Time](02-base-model.md)** defines players, bouts, histories and schedules without introducing player strength.
3. **[Performance Measures and Schedule Strength](03-performance-measures-and-schedule-strength.md)** defines direct and contextual measures and leaves schedule strength abstract.
4. **[Player-Strength-Based Schedule Strength](04-player-strength-based-schedule-strength.md)** adds a player-strength carrier and constructs one particular class of schedule-strength measures from it.
5. **[Mathematical Context](05-mathematical-context.md)** locates the framework among temporal networks, generalized tournaments, paired-comparison ranking and measurement theory.

These notes form one path through a much larger space of possible models. Their aim is not completeness but a clear account of the path actually taken.
