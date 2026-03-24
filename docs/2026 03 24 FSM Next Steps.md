# 2026 03 24 FSM Next Steps

## Purpose

This note records the current assessment of what is required to migrate the old FSM layer onto the new core model. It is intended as a planning document, not an implementation document.

The goal is to adapt the FSM so that it fits into the new parser stack without breaking the already-working new serializer/shared-memory path.

## Current understanding

The entry point to FSM execution is still the `.run()` method on a concrete FSM instance, called from `parse_and_validate_body(...)` in `parser2_body.py`.

Operationally, the parser does:

- construct `GruntFSM`, `OSK_FSM`, or `YokozunaFSM`
- call `fsm.run(fsm_body_stream)`
- read `fsm.output`
- for Makuuchi, also read `fsm.rows_processed`

So the migration target is not just class definitions. It is the full parser-facing FSM contract.

## Confirmed straightforward substitutions

These changes appear conceptually sound:

- `NewFoo` -> `Chii`
- `NewAnn` -> `Annotation`
- `IntDate` -> `Date`

The new `Chii` model appears to be the intended full replacement for `NewFoo`, not a downgraded compatibility type.

In particular, the new model provides:

- `Chii.level`
- `Chii.number`
- `Chii.side`
- `Chii.ann`
- `Chii.from_str(...)`
- `Chii.ordinal()`
- `Chii.from_ordinal(...)`

and the new `Annotation` enum includes:

- `TD`
- `OB`
- `HD`
- `YO`
- `EMPTY`

That means the old annotated rank concepts have been absorbed into the new canonical rank model.

## What the FSM migration is not

The migration is **not** just a global search-and-replace.

The risky parts of FSM are not the imports; they are the technical recovery rules that depend on exact rank behavior.

## Parser-facing FSM contract to preserve

Whatever internal changes are made, the parser still expects the FSM layer to provide:

- constructible concrete FSM classes:
  - `GruntFSM`
  - `OSK_FSM`
  - `YokozunaFSM`
- a `.run(fsm_body_stream)` method
- a populated `.output` after running
- a `.rows_processed` count after running

The parser also expects the output to remain compatible with its assembly logic.

## Main migration work items

### 1. Replace direct model references

Audit all FSM files for:

- imports of `NewFoo`
- imports of `NewAnn`
- imports of `IntDate`
- type hints and local variables using those types

Replace them with:

- `Chii`
- `Annotation`
- `Date`

This is the mechanical part.

### 2. Re-check all parser/FSM intermediate types

Inspect `FSM_data_classes.py` and related files to confirm whether:

- `FinalBanzukeEntry` still names the final rank field sensibly
- intermediate rank-bearing structures are typed to `NewFoo`
- any parser-facing output types need renaming or retyping to `Chii`

The parser/FSM boundary must be made consistent before deeper logic changes.

### 3. Review duplicate-key normalization carefully

This is a hotspot.

The FSM duplicate logic appears to normalize ranks using `str(...)` and then use those strings as dictionary keys. That means the migration is only safe if:

- `str(Chii)` matches the old `str(NewFoo)` for all relevant ranks
- empty annotations stringify the same way
- sided/sideless forms stringify the same way
- any annotation-bearing forms (including `YO`) stringify the same way

If not, duplicate handling may silently fail even if the code compiles.

This needs explicit verification, not assumption.

### 4. Review sideless recovery carefully

This is another hotspot.

FSM recovery logic appears to construct and compare sideless variants of rank objects. This relies on the new `Chii` model behaving exactly as the old FSM expects.

Points to verify:

- `Side.NONE` is still the representation for sidelessness
- constructing a sideless `Chii` preserves all other identifying information
- equality and ordering behave as the recovery logic expects
- a sideless `Chii` compares appropriately to the expected margin rank

This is semantic logic, not just typing.

### 5. Review annotation recovery carefully

This is the third hotspot.

FSM logic appears to infer or repair ranks by changing only the annotation component. This relies on:

- `Annotation.EMPTY` meaning exactly “no annotation”
- `Annotation.YO` behaving as before
- changing `.ann` while preserving other fields producing the intended semantic rank
- equality and string behavior staying compatible after annotation changes

This also needs line-by-line review.

### 6. Confirm equality / hashing / ordering assumptions

The old FSM relies on rank objects as:

- comparison values
- dictionary keys or normalized lookup surrogates
- reconstruction targets

So the migration must explicitly confirm that the new `Chii` semantics are compatible in the places FSM uses them.

In particular, check:

- equality
- ordering
- hashing
- ordinal-based identity
- behavior of sided vs sideless forms
- behavior of annotated vs unannotated forms

### 7. Confirm string-form assumptions

Because parts of FSM logic appear to use `str(rank)` operationally rather than only for display, the migration must verify the new canonical string form.

This matters for:

- duplicate pools
- debugging and error messages
- any string-based recovery or comparison logic

### 8. Replace `IntDate` consistently

`IntDate` is trivial and appears to be only a convenience wrapper around `Date`.

Decide one consistent approach for FSM:

- import and use `Date` directly, or
- keep a tiny compatibility wrapper temporarily

Either is fine, but it should be consistent.

### 9. Check date-based hacks or historical special cases

`BaseFSM` itself seems light on date semantics, but other FSM files may contain special-case date logic or historical hacks.

So after replacing `IntDate`, check whether any FSM subclass logic relies on:

- direct construction from ints
- date comparisons
- historical date-specific anomaly handling

### 10. Reconcile final output type with parser assembly

The parser currently expects the FSM output to feed into final assembly and eventually into `Banzuke` / `BashoState` / `History`.

So after migrating the FSM’s internal rank type, verify that:

- `FinalBanzukeEntry` (or its replacement) contains the right canonical rank object
- the parser no longer expects `NewFoo`
- the final output is ready for new-model assembly without a compatibility conversion phase

## Suggested order of work

A sensible order is:

1. inspect `FSM_data_classes.py`
2. inspect the concrete FSM subclasses for rank/date/annotation assumptions
3. do the mechanical substitutions (`NewFoo` -> `Chii`, etc.)
4. review the three semantic hotspots:
   - duplicate-key normalization
   - sideless recovery
   - annotation recovery
5. verify the parser-facing output contract
6. test with the smallest runnable slice (`mu_parser.py` / one-basho reconciliation path)

## What success looks like

FSM migration is “done enough” when:

- the parser can still instantiate and run the FSM layer
- the FSM output uses the new canonical rank model
- duplicate handling still works
- sideless recovery still works
- annotation recovery still works
- the one-basho reconciliation path succeeds without needing `NewFoo`

## Bottom line

The FSM migration is now understood at breadth-first level.

The easy part is the model substitution:

- `NewFoo` -> `Chii`
- `NewAnn` -> `Annotation`
- `IntDate` -> `Date`

The hard part is preserving the technical recovery logic that depends on exact rank behavior.

The next practical step is to inspect the remaining FSM files, especially `FSM_data_classes.py`, and then review the duplicate/sideless/annotation recovery methods line by line.
