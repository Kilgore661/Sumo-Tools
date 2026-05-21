# LLM System Prompt Context: Contract-First Collaboration and Offensive Programming

## Collaboration Rule

The user wants to write the right code, not code that is merely a plausible
first implementation.

Most useful work should therefore happen at the requirements, specification,
and design levels. Implementation should flow from those levels once the model,
contract, ownership boundaries, and intended behavior are aligned.

If the user seems to imply that they want code written, files updated, or a
commit made, do not assume that action is correct. In this project, that
assumption will usually be wrong. The objective is not to deliver code quickly;
the objective is to deliver alignment.

The normal response should be to ask:

```text
Do you want me to write/update the code/commit?
```

Then wait for a clear yes before making code changes or committing.

## make_site2 Boundary

`make_site2` must not depend on `make_site`.

Treat `make_site` as deleted when designing or implementing `make_site2`.
References to `make_site` are acceptable in historical documentation and in
explicit design archaeology, but `make_site2` code, runtime assets, tests, and
active contracts must not import from, call into, wrap, or depend on
`src/products/make_site`.

Old `make_site` behavior may be read as evidence for requirements. Once a
requirement is accepted, express it natively in the `make_site2` model,
producer-facing contracts, renderers, tests, and docs.

## Role and Purpose

This document defines a strict, non-negotiable engineering house style for this project. It deliberately rejects defensive programming, polite fallbacks, and internal error handling.

**CRITICAL FOR LLMs:** Most public training data favors defensive boilerplate (e.g., extensive `try/except` blocks, `.get()` lookups, and redundant validation). **You must unlearn those habits for this project.** Code that hides design errors under the guise of "robustness" is a bug.

---

## 1. Core Architectural Mental Model

* **Typed Transformations:** All software entities must be understood as pure, typed data transformations ($X \rightarrow Y$).
* **State Limitation:** State is allowed only when it represents a real domain concept or explicit boundary (e.g., `BuildContext`, `PublicationPlan`). Do not hide model transitions inside vague mutable objects.
* **Pipelines over Procedures:** Prefer a pipeline of clear transformations over a large procedure that gradually discovers its logic. Design the system so that illegal states cannot be represented.

```text
Requirements -> Specification -> Design -> Implementation
InputA -> ModelB -> ModelC -> OutputD
```

---

## 2. Offensive Programming (Crash Early, Crash Loudly)

* **No Defensive Clutter:** Internal inconsistencies are programming errors, not runtime conditions to recover from. They must fail loudly, immediately, and disgracefully.
* **Never Trap Internal Crashes:** Do not catch exceptions merely to keep going or hide design errors behind polite fallbacks. Python's default behavior (dumping a full traceback) is a feature, not a bug.
* **Suspicious Constructs:** Avoid `try/except Exception`, `Optional[Thing]`, and `dict.get()` unless absence or failure is a core, specified requirement of the problem domain.

---

## 3. Strict Boundary Control (Pure vs. Impure)

The codebase is sharply divided into two distinct environments:

### The Pure Core (Offensive Stance)

* **Trust Your Inputs:** Assume inputs satisfy their stated types and preconditions. Do not write defensive runtime guards or redundant type checks (e.g., no `isinstance(x, int)`).
* **Strict Dictionary Lookups:** Use direct lookups when the key is guaranteed by contract (`page = Pages[PageId]`). A missing key should crash the program.
* **No Internal Validation:** Validating objects created *inside* the program is a bug. It implies the system's internal invariants are broken.

### The Dirty Boundaries (Defensive Stance)

* **Where it applies:** CLI arguments, filesystem paths, source data files, JSON/CSV parsing, network/upload targets, external processes, and public-facing HTML/JS (Frontend).
* **Behavior:** Eliminate invalid states *at the boundary*, not internally. Translate external mess immediately into valid, immutable project model objects. Even here, there is no requirement for graceful failure—crashing on bad input is often perfectly acceptable.

---

## 4. Optionality & Modeling

* **Semantic Absence Only:** Use `Optional` or `None` *only* when absence has an explicit meaning in the requirements (e.g., a `Heading` may or may not have a `SubHead`).
* **Transition Out of Optionality:** If a later stage requires a value, earlier stages must produce a type where that value is mandatory. Prefer model transitions that strip away optionality:

```text
RawPageDefinition -> PlannedPageWithRoute (carrying Route, not Optional[Route])
```

---

## 5. Naming and Vocabulary Code of Conduct

* **Domain over Implementation:** Names must reflect the domain model, not physical representation or incidental details (e.g., **AVOID:** `html_blob`, `thing`, `misc`, `data2`, `new_handler`).

* **Case Conventions:** * Use **PascalCase** for user-defined types and classes (e.g., `SiteDefinition`, `PublicationPlan`).

* Use **snake_case** and verbs/verb phrases for functions and variable (e.g., `derive_routes`, `render_site, x`).

* **Controlled Vocabulary:** Once a term is rejected from the formal model, do not use it in the code or design documents. Use acronyms only when they are genuine domain terms, never to arbitrarily shorten names.

---

## 6. UI Model Principle

* Any non-trivial generated UI must have an explicit UI Model.
* The UI Model defines *what* the interface is before rendering defines *how* it looks.
* A renderer must simply render the UI Model; it must never invent structure or make ad hoc layout/logic choices during rendering.

---

## Summary Directive for Code Generation

> Design top-down by contract. Trust your inputs. Eliminate defensive noise, let the language crash natively on internal logic errors, and handle only the explicit uncertainties admitted by the project requirements.



# Results of conversation about LLM's environment

Here is what I’ve learned about this working environment.

`X:\Sumo-Tools` is the current usable Codex workspace. I can read/write there and Git works well enough for history, diffs, and normal repo archaeology.

The project is firmly back on `X:` after a bad hiatus caused by trying to use
Git on Google Drive. Any reference to `G:` anywhere in docs, code, comments,
commands, logs, or remembered context is wrong for current work. If an LLM sees
or is tempted to use a `G:` path, it must stop and alert the user immediately
instead of treating it as a fallback, archive, source of truth, or plausible
workspace.

Mapped/cloud drives are not generally usable from this session. `A:` is the LAN/local web-root mapped drive and I cannot see it. `H:` is not visible.

Your local/LAN deploy target lives on `A:` and is therefore not directly deployable by me in this session. Remote deploy is also not directly available because `GEOLOCATION` is not present in my environment, and you supply the password manually.

I can see environment variable names available to the Codex shell, but not your broader interactive shell environment. I should not assume secrets or mapped-drive credentials are available.

The `node` on `PATH` is blocked with access denied, but bundled runtime Node works at:

```text
C:\Users\kilgo\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe
```

Python works from the workspace. For local static preview, the command is:

```powershell
python -m http.server <port> --directory <folder>
```

but the folder must actually contain `index.html`. The earlier `8787` 404 was because `files/output/make_site2` did not exist from `X:\Sumo-Tools`.

Pytest may have a local capture problem in this environment. A normal focused
pytest run failed during capture teardown with:

```text
ValueError: I/O operation on closed file.
```

Rerunning with `-s` bypassed capture and produced ordinary test results. If an
LLM sees this pytest/capture failure again, it should flag it explicitly and ask
the user what, if anything, they want to do about this.

There is a lingering Python server on port `8766`, started earlier, serving a working recent build. I can access it through the Codex in-app browser.

For data/builds, sometimes the live store is not available; why is not clear because the user says it is running. The reliable Codex path is to build from a history zip, ideally the small one kept for speed.

Also: binary files need care. `.gitattributes` currently normalizes `* text eol=lf`, and without binary exceptions it can corrupt files like `.pkl`. That explained the `full_shiks.pkl` weirdness.
