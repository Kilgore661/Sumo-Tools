# House Style

## Status

Draft engineering house style for this and related projects.

This document records preferred ways of thinking, naming, designing, and writing
code. It is not a universal software-engineering doctrine. It is a project-local
style guide intended to keep work rigorous, comprehensible, and resistant to
prototype drift.

---

# 1. General Philosophy

Software entities should be understood as typed transformations.

The preferred mental model is:

```python
def f(x: Xtype) -> Ytype:
    ...
```

Even where implementation requires state, I still prefer to understand the
operation as a function with explicit inputs and outputs:

```python
def f(x: Xtype) -> Ytype:
    # also uses package state z: Ztype
    ...
```

Classes are useful when they name real concepts, preserve invariants, or bundle
state that genuinely belongs together. They should not be used merely to imitate
framework patterns.

Top-down design should proceed by contract:

```text
requirements
  -> specification
  -> design
  -> implementation
```

The goal is to avoid wandering implementation-first into accidental structures.

---

# 2. Contract-First Design

Each important function, class, module, or package should have a clear contract.

A contract should answer:

```text
What does this thing consume?
What does it produce?
What assumptions does it make?
What invariants does it preserve?
What is outside its responsibility?
```

Prefer a pipeline of clear transformations:

```text
InputA
  -> ModelB
  -> ModelC
  -> OutputD
```

over a large procedure that gradually discovers what it is doing.

Where possible, design so that illegal states cannot be represented.

---

# 3. Offensive Programming

This house style favors offensive programming.

Internal inconsistencies are programming errors.

They should fail loudly, immediately, and disgracefully.

The program should not defensively recover from impossible internal states.

Do not hide design errors behind polite fallbacks.

Do not guess.

Do not silently continue with partial or contradictory state.

Examples of suspect constructs:

```python
try:
    ...
except Exception:
    ...

value = mapping.get(key)

Optional[Thing]
```

These are not banned from Python, but they are suspect. Their presence usually
means that something is under-specified.

Use them only when absence or failure is genuinely part of the model.

---

# 4. Validation

Validation is suspect when applied to objects created inside the program.

If the program creates an invalid internal object, that is a bug in the program,
not a runtime condition to recover from.

Validation may be appropriate at dirty boundaries:

```text
CLI arguments
filesystem paths
source data files
JSON/CSV/text parsing
deployment configuration
network or upload targets
external process boundaries
```

Even at dirty boundaries, failure may be blunt.

There is no general requirement for graceful failure.

If the input is wrong, crashing is often acceptable. Fix the input or fix the
program.

---

# 5. Optionality

Use optionality only when absence is semantic.

Good optionality:

```text
A Heading may or may not have a SubHead.
A Note may or may not have a target feature.
A deployment command may or may not have a remote target.
```

Suspicious optionality:

```text
A promoted page may or may not have a route.
A rendered page may or may not have contents.
A table column may or may not have an id.
A page reference may or may not resolve.
```

If a later stage requires a value, earlier stages should produce a type where
that value is mandatory.

Prefer model transitions that remove optionality:

```text
RawPageDefinition
  -> PlannedPageWithRoute
```

rather than carrying `Optional[Route]` everywhere.

---

# 6. Dictionaries and Lookups

Use dictionary lookups when the key is guaranteed by contract.

Prefer:

```python
page = Pages[PageId]
```

over:

```python
page = Pages.get(PageId)
```

A missing key should crash if the contract says the key exists.

Use `.get()` only when the absence of the key is part of the model and has a
specified meaning.

---

# 7. Exceptions

Exceptions are for exceptional or external failures.

They should not be used as normal control flow in core model code.

Avoid broad exception handlers.

Avoid catching exceptions merely to keep going.

If an exception is caught, the design should say why that failure belongs to the
contract of the current boundary.

Examples where exception handling may be reasonable:

```text
reading a missing external file
parsing malformed external JSON
uploading to a remote host
invoking an external process
```

Examples where exception handling is usually wrong:

```text
missing internal page id
unsupported promoted artifact kind
unknown branch in a closed grammar
missing required field in an internally created object
```

---

# 8. Naming

Use names that reflect the model, not incidental implementation detail.

Names should answer:

```text
What is this thing?
What role does it play?
Who owns it?
What boundary does it belong to?
```

Avoid names that preserve obsolete prototype concepts.

Avoid names that merely describe physical representation:

```text
html_blob
thing
misc
custom
data2
new_handler
```

unless the concept really is physical or temporary.

## Type and Class Names

Use Pascal-case for user-defined types and classes.

Examples:

```python
class SiteDefinition:
    ...

class PublicationPlan:
    ...

class FilterSection:
    ...
```

## Function Names

Use lower-case function names with underscores.

Function names should usually be verbs or verb phrases:

```python
derive_routes(...)
resolve_ui_model(...)
render_site(...)
write_output(...)
```

## Acronyms

Use project acronyms when they are genuine domain terms.

Examples:

```text
PA
BRB
BCR
```

Do not invent acronyms merely to shorten names.

---

# 9. Model Vocabulary

Choose model vocabulary deliberately.

Once a term is rejected, do not keep using it in requirements, specification,
design, or implementation-facing model names.

Ordinary conversation may still use ordinary English words casually, but formal
project vocabulary should be controlled.

Example from `make_site2`:

```text
Use:
  Filter

Do not use as a model term:
  Option
```

This does not mean the English word "option" is forbidden in conversation. It
means it is not part of the formal model.

---

# 10. Requirements, Specification, Design, Implementation

Keep the four levels distinct.

## Requirements

Requirements say what must be true from the product, project, or user point of
view.

They should not prescribe implementation unless the implementation constraint is
itself a requirement.

## Specification

Specification says what the system does.

It should describe behavior, contracts, inputs, outputs, ownership, and
invariants.

A good spec is precise enough that more than one implementation could satisfy
it.

## Design

Design says how this implementation will satisfy the specification.

It names layers, modules, transformations, data structures, and ownership
boundaries.

## Implementation

Implementation is code.

It should follow from the design rather than replace it.

---

# 11. Documentation Style

Documents should be written to preserve thinking, not merely to satisfy process.

Prefer:

```text
short purpose statement
clear status
explicit scope
precise vocabulary
small sections
examples where useful
```

Avoid:

```text
giant unstructured design notebooks
unlabelled historical sediment
mixing requirements, spec, design, and implementation in one paragraph
unexplained jargon
```

When a document is superseded, say so.

When a decision is provisional, say so.

When a document is evidence rather than authority, say so.

---

# 12. Prototype Discipline

A prototype is evidence, not authority.

A prototype may reveal:

```text
real requirements
useful model concepts
bad assumptions
visual needs
data needs
migration risks
```

But prototype implementation details should not automatically become design.

Before copying prototype code, ask:

```text
What responsibility does this code implement?
Does that responsibility still exist in the new design?
Is the copied code implementing a real model concept or preserving an accident?
What implications come with copying it?
```

Copy/paste is allowed when the implications have been considered.

Copying without conceptual review is not.

---

# 13. State

State is allowed when it represents a real concept or boundary.

Examples:

```text
BuildContext
SiteDefinition
PublicationPlan
UIModel
DeploymentConfig
```

State should not become a dumping ground.

Prefer immutable or mostly immutable model objects where practical.

If something changes over time, say what transition is happening:

```text
RawDefinition -> PlannedPublication -> UIModel -> RenderedSite
```

Do not hide model transitions inside vague mutable objects.

---

# 14. Boundaries

Make dirty boundaries explicit.

Typical dirty boundaries:

```text
file system
CLI
external data
deployment
network
browser runtime
legacy generated outputs
```

Inside the pure core, assume valid model objects and clear contracts.

At boundaries, translate external mess into project model objects.

Do not let external mess leak everywhere.

---

# 15. Testing and Debugging

Testing should focus on contracts and transformations.

Useful tests include:

```text
given this input model, derive these routes
given this page definition, resolve this UI model
given this UI model, render this structural output
given this producer manifest, construct this artifact model
```

Debugging with `pdb` is acceptable.

Simple command-line workflows are acceptable.

Tooling should support thinking, not obscure it.

---

# 16. Git and Workflow

Git is useful but should not dominate the working method.

Prefer small, meaningful commits at conceptual boundaries:

```text
add requirements doc
add specification doc
add design overview
introduce core model skeleton
add first G1 page slice
```

Git enforces some commit message shape and encourages a short first line. That
is fine.

A normal commit message should also explain the work in this order:

```text
Short imperative-ish subject

Purpose: ...

What changed: ...

Verification: ...

Next: ...
```

The exact amount of detail may vary with the size of the change, but the
message should usually record why the change exists, what changed, how it was
checked, and what the next intended step is.

It is easy for the human to forget the `Next:` section. When an LLM is helping
and the human says or implies that a commit should be made, it is the LLM's
responsibility to make sure the next step is known and included in the commit
message.

Before a risky change, make a branch.

Before moving many files, commit the clean state or branch first.

Use Git to preserve recoverability, not to impose ceremony.

---

# 17. User-Facing Public Systems

For public analytical sites, distinguish:

```text
public facts
interpretation
model output
research
diagnostic material
legacy material
internal artefacts
```

Do not publish something merely because it exists.

Do not expose internal implementation vocabulary as public explanation unless it
has been deliberately promoted.

Public defaults should be clear and low-friction.

Deeper controls and caveats should be available without overwhelming the first
view.

---

# 18. UI Model Principle

Any non-trivial generated UI should have an explicit UI Model.

The UI Model defines what the interface is before rendering defines how it looks.

Without a UI Model, structural decisions escape into ad hoc HTML, CSS,
JavaScript, and custom handlers.

A renderer should render the UI Model.

It should not invent the model while rendering.

---

# 19. Rendering Principle

Rendering should preserve semantic structure.

Before adding visual grouping, ask:

```text
What semantic boundary does this represent?
```

Before adding a custom renderer, ask:

```text
Is this custom behavior page structure or artifact internals?
```

Custom renderers are acceptable for real local artifact needs.

They should not redefine the surrounding page or shell unless the design says
they may.

---

# 20. Final Rule of Thumb

When in doubt, ask:

```text
What is the model?
What is the contract?
Where is the boundary?
Who owns this?
What type should this be?
Why is absence possible?
Why is failure possible?
Is this a real concept or a prototype accident?
```

If those questions cannot be answered, do not hide the uncertainty in defensive
code. Step back and fix the requirements, specification, or design.
