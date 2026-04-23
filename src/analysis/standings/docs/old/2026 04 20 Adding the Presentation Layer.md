# Project Position Statement

## 1. Current State of the Project

The project has progressed successfully through the development of a **standings engine** for sumo analysis.

That engine now provides a coherent computational capability operating over canonical historical data (`History`) and is able to generate ranked standings based on recorded bout outcomes.

The implemented capability includes:

* single-basho standings
* multi-basho standings over contiguous rolling windows
* selectable win definitions (`real` / `all`)
* structured ranked outputs
* derived comparative metrics for multi-basho analysis
* CSV reporting outputs
* command-line entry points
* separation between calculation logic and reporting/persistence

In architectural terms, this part of the project is in a relatively healthy state. It reflects a sensible progression from:

* requirements
* specification
* design
* implementation

The engine is reusable, reasonably well-factored, and not tightly coupled to any presentation layer.

---

## 2. What Has Been Learned Since Then

During later reflection, it became clear that the standings engine is **not itself the final product**.

The intended end-user outcome is not “a command-line standings generator” but a **published standings application** that ordinary users can consult easily.

By considering the problem from the perspective of a user, a clearer picture of the real application has emerged.

The desired product is now understood to be:

* a browser-based standings page
* showing current rolling standings
* backed by precomputed data
* hosted statically on a legacy web host
* simple to navigate
* honest about what data is available
* constrained to a fixed set of supported windows
* not a general-purpose historical query tool

This clarification did not invalidate the engine work. Rather, it revealed that the engine is one component within a larger application.

---

## 3. Where the Project Now Stands

The project is therefore at a **transition point**.

The computational subsystem exists and is substantially ahead of the original minimum requirements.

However, the overall application requirements were only partially understood when the engine was first specified.

As a result:

* engine requirements are comparatively mature
* presentation/publication requirements were discovered later
* some existing documents understate the role of the user-facing product
* some implementation outputs may be broader than what the final application needs
* some presentation semantics remain to be clarified

This is a normal and healthy stage in product evolution.

---

## 4. What Needs to Be Done Next

The next task is **not** to make ad hoc changes to code or HTML.

The next task is to re-state the project properly from the top down, incorporating what is now understood about the actual product.

That means revisiting each layer in order.

---

## 5. Required Next Steps

## 5.1 Rewrite Requirements

Produce a fresh requirements statement for the **whole application**, not merely the standings engine.

This should define:

* the intended users
* the purpose of the site
* the current rolling standings model
* supported controls (window size, division)
* unsupported controls (arbitrary anchor dates, arbitrary ranges)
* static publication constraints
* clarity, trustworthiness, and maintainability goals

---

## 5.2 Revise Specification

From those requirements, derive an updated specification describing:

* data publication model
* supported rolling windows
* page behaviour
* control semantics
* title/range display
* refresh/update workflow
* relationship between engine outputs and page inputs

---

## 5.3 Revise Design

Then restate the design as a system comprising:

* standings engine
* publication/build process
* static web assets
* browser-side interaction layer

This stage should confirm boundaries and responsibilities.

---

## 5.4 Reconcile Implementation

Only after the above should implementation changes be made.

Likely implementation tasks include:

* tailoring outputs to page needs
* simplifying exported metrics if appropriate
* generating standard datasets only
* finalising HTML/CSS/JS assets
* automating publication
* resolving any remaining display-policy questions

---

## 6. What Should Not Be Done

The project should avoid:

* patching implementation first
* allowing current code shape to dictate requirements
* exposing engine internals unnecessarily in the UI
* adding controls users do not need
* overengineering a simple published product

---

## 7. Expected Outcome

If the existing engine architecture is sound, this top-down revision should mainly produce:

* clearer positioning
* cleaner product scope
* improved presentation
* better alignment between outputs and user needs
* limited downstream code disruption

The aim is refinement rather than rework.

---

## 8. Final Summary

The project has successfully built a standings engine.

It has subsequently learned what the actual product should be.

The immediate task is now to reconcile the whole project around that fuller understanding, proceeding from requirements downward so that each lower layer reflects the layer above it.
