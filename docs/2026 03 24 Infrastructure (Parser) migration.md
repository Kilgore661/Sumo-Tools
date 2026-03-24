Here is a scoped list of what the migration task entails, without getting into solutions yet.

## Overall task

Convert the old infrastructure modules — `memory`, `persistence`, `parser`, `bios`, and `FSM` — from the **old/annotated hybrid model** to the **new core model**, where the canonical top-level object is `History` and the canonical rank object is `Chii`. In the new model, `History` maps `Date -> BashoState`, `BashoState` contains `Banzuke` and `Summary`, and `Banzuke` contains `Riks`, `RikChii`, and `RikShikona`.     

That means the task is not just “fix imports.” It is a model migration across five infrastructure areas.

## 1. Establish the model delta clearly

Before changing code, the migration has to account for the fact that the old infrastructure was built around:

* `HistoryWithAnnotations` instead of `History`
* `BashoStateWithAnnotations` instead of `BashoState`
* `BanzukeWithAnnotations` instead of `Banzuke`
* `RikNewFoo` instead of `RikChii`
* `NewFoo` instead of `Chii`  

Whereas the new core model now defines:

* `History`
* `BashoState`
* `Banzuke`
* `RikChii`
* `Chii`    

So one part of the task is to enumerate every old-model assumption embedded in the infrastructure code.

## 2. Update the type and object contracts module by module

Each infrastructure module currently assumes certain types at its boundaries. The task entails identifying, for each module:

* what it accepts
* what it returns
* what classes it instantiates
* what methods/fields it expects on those classes

Then those assumptions need to be rewritten against the new model.

At minimum, that means checking every reference to:

* `HistoryWithAnnotations`
* `BashoStateWithAnnotations`
* `BanzukeWithAnnotations`
* `RikNewFoo`
* `NewFoo`
* `FinalBanzukeEntry.chii` as a `NewFoo`  

and mapping each one to the new canonical class or deciding whether a compatibility layer is needed.

## 3. Migrate persistence

The persistence task entails replacing the old annotated serializer assumptions with the new canonical model.

Concretely, this includes:

* changing the top-level serialized object from old HWA-style history to the new `History`
* changing serialization of rank mappings from `RikNewFoo`/`NewFoo` to `RikChii`/`Chii`
* checking whether the existing old serializer already matches the new model closely enough to reuse
* checking whether date serialization still matches `Date.__str__()` in the new model, which is `YYYY/MM` 
* checking whether unchanged reused types such as `Summary` still serialize the same way under the new definitions 

Since the new `Chii` has `ordinal()` and `from_ordinal()`, the persistence layer may still be able to use ordinal-based rank serialization, but that is something to verify rather than assume. 

## 4. Migrate memory

The memory task entails updating the shared-memory runtime layer so that it now loads, publishes, and returns the new canonical `History` object instead of the old HWA object.

That includes:

* changing imports from old annotated-history classes to the new `History`
* ensuring the object graph rooted at `History` remains picklable
* ensuring any consumer code expecting `.banzuke.rikchii` or `.summary` still works with the new concrete classes
* checking whether any naming/version conventions for the shared memory segment have drifted and should be normalized separately from the model migration

This is probably the smallest semantic migration, but it still depends on persistence returning the new model correctly.

## 5. Migrate parser

The parser task is larger. It entails changing the parser’s output target from the annotated model to the new canonical model.

That includes:

* changing one-basho assembly so it constructs `Banzuke`, `BashoState`, and `History` instead of the old annotated variants
* changing any logic that expects `entry.chii` to be a `NewFoo` so that it now yields or converts to `Chii`
* checking whether the parser still needs `NewFoo` internally as a parsing aid, or whether it can move fully to `Chii`
* checking whether old adapter/FSM logic depends on `NewFoo`-only features such as extra annotation richness beyond the new `Annotation` enum
* checking whether the parser still relies on any now-obsolete compatibility classes from the old annotated layer

The key point is that parser migration is both a model-construction problem and a rank-model problem.

## 6. Migrate FSM

FSM has its own report, but at task level the migration entails:

* replacing any dependence on `NewFoo` with the new canonical `Chii`, if possible
* checking whether the old FSM logic relied on annotations or conversions that existed only in `NewFoo`
* changing intermediate and final output types so they align with the new parser target model
* checking whether rank parsing, rank comparison, and rank reconstruction can now use `Chii.from_str`, `Chii.ordinal()`, and `Chii.from_ordinal()` directly 

This may be the most intricate part because FSM was the main consumer of rank semantics.

## 7. Migrate bios

The bios task entails updating the enrichment pipeline so it works against the new canonical history and rank model.

That includes:

* changing the history loader and any type assumptions from HWA to `History`
* checking whether the rikishi traversal logic still works against the new `Banzuke` and `RikShikona`
* changing debut-rank handling from `NewFoo` ordinals to `Chii` ordinals if that field is still meant to be stored
* checking whether the bios JSON schema should remain unchanged or be updated to reflect canonical `Chii` instead of old `NewFoo`

Because bios is downstream of the parser, it also depends on the parser and persistence migrations being coherent.

## 8. Reconcile enum and rank-model differences

A distinct part of the task is to identify semantic differences between the old annotated rank model and the new core rank model.

The new model’s `Annotation` enum includes `TD`, `OB`, `HD`, `YO`, and `EMPTY`, and `Chii` is now explicitly described as the authoritative rank object with ordinal semantics.  

So the migration must determine:

* whether everything formerly carried by `NewFoo` is representable by `Chii`
* whether conversion code from legacy `Chii` to `NewFoo` is now obsolete
* whether any parser/FSM logic still assumes annotation cases or behaviors that are not present in the new model in the same form

This is a semantic-audit task, not just a mechanical rename task.

## 9. Reconcile moved or renamed core definitions

The new model also changes where some things are defined.

Examples:

* `Date`, `Year`, and `Month` now live together with `History` in `History.py` and `BasicPrimitives.py` rather than in the old split you described  
* `Shikona` is in `BasicPrimitives.py`, while `RikShikona` is in `Banzuke.py`  
* `Performance` is now its own module, while `Summary` expects a `Performances()` default that will need checking because the uploaded `Summary.py` references `Performances` but the provided `Performance.py` only defines `Performance`  

So part of the task is to identify and resolve “defined where” mismatches introduced by the new model layout.

## 10. Audit the new core model for gaps that block migration

Before migrating infrastructure, the new model itself needs a quick compatibility audit, because some issues are already visible in the files you uploaded.

Examples that need checking:

* `Summary.py` refers to `Performances()` but does not import or define it in the file shown 
* infrastructure code may still expect convenience methods or legacy validation methods that no longer exist
* some old import paths may no longer line up with the reorganized core-model files

So the task includes identifying blockers in the new model that must be fixed before or during infrastructure migration.

## 11. Define the migration boundary for each module

For each of the four modules plus FSM, the task entails deciding whether to:

* rewrite directly to the new model,
* introduce temporary adapters/compatibility wrappers,
* or preserve some transitional old-model code while the rest is ported

That is a planning task, not yet an implementation task, but it is necessary because not all five modules need the same migration strategy.

## 12. Verify the end-to-end object lifecycle

Finally, the task entails making sure the full old lifecycle still works under the new model:

* parser constructs `History`
* persistence saves and loads `History`
* memory publishes and reconnects `History`
* bios consumes `History`
* FSM supports parser internals consistently

That end-to-end chain is the real migration target.

## Concise task list

In plain terms, the task entails:

1. catalog old annotated-model assumptions across infrastructure
2. map them to the new canonical core model
3. migrate persistence to `History`/`BashoState`/`Banzuke`/`Chii`
4. migrate memory to load and publish the new `History`
5. migrate parser output assembly to the new model
6. migrate FSM rank logic from `NewFoo` assumptions to `Chii` assumptions
7. migrate bios to consume the new history and rank model
8. audit semantic differences between `NewFoo` and new `Chii`
9. fix any gaps or inconsistencies in the new core model that block migration
10. verify the whole pipeline works as one coherent model

