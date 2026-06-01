# LLM System Prompt Context: Contract-First Collaboration and Offensive Programming

Read this file together with `docs/House Style.md`. The House Style document
contains project-wide documentation, coding and git workflow rules, including
the commit message policy and required `Next:` section.

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

## Filename Convention

The human uses spaces in non-code filenames, especially documentation
filenames.

When referring to or operating on such files, quote the filename or use
literal-path forms. Do not assume project filenames are shell-token friendly
just because code module filenames are.

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

## 5.1 Module Documentation

* Every new Python or JavaScript module must have a top-level orientation
  docstring/comment.
* Add short docstrings/comments to major constructs: public entry points,
  model transformations, renderers, state transitions, sort/value derivations
  and other functions a maintainer would naturally look for first.
* Keep these comments semantic and architectural. Do not add line-by-line
  narration or comments that merely restate the code.

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



Mapped/cloud drives are not generally usable from this session. `A:` is the LAN/local web-root mapped drive and I cannot see it. `H:` is not visible.

Your local/LAN deploy target lives on `A:` and is therefore not directly deployable by me in this session. Remote deploy is also not directly available because `GEOLOCATION` is not present in my environment, and you supply the password manually.

Because the user's local web server serves files from mapped drive `A:`, an LLM
should normally run `make_site2` with `--build-only` rather than `--local-only`.

Functional browser behaviour is distinct from syntax checks and pytest checks.
Python/JavaScript syntax checks can show that files parse; pytest can check
model/build/runtime contracts covered by tests; but browser behaviour needs a
shared preview page that both the user and LLM can inspect. The agreed standard
preview URL is:

```text
http://localhost:8766/
```

To create or refresh that shared preview, build output first, then serve the
output directory on port `8766`:

```powershell
py -m src.products.make_site2 --build-only --history-zip ".\files\output\Historys\1978_01 to 1980_11.zip"
py -m http.server 8766 --directory ".\files\output\make_site2"
```

The serving PowerShell process must keep running. If a server is already running
on `8766`, rebuild the output and refresh the browser rather than starting a
second server on an ad hoc port. Use another port only after telling the user and
recording why `8766` is unavailable.

Browser inspection is not guaranteed in every ChatGPT/GitHub-only environment.
If the active environment can only read/write GitHub files, it can inspect code
and docs but cannot prove localhost browser behaviour. In that case, state
plainly that the behaviour needs Codex/local-preview access or human browser
inspection rather than pretending that source review or pytest proves it.

I can see environment variable names available to the Codex shell, but not your broader interactive shell environment. I should not assume secrets or mapped-drive credentials are available.

Node.js LTS is installed normally at:

```text
C:\Program Files\nodejs\node.exe
```

Plain `node` should resolve to this normal install and currently reports
`v24.16.0`. The Codex app also ships its own bundled Node, and it may still
appear later in `Get-Command node -All`, but project checks should use the
normal Node install when available.

PowerShell may choose `npm.ps1` / `npx.ps1` and block them under the execution
policy. Use the `.cmd` shims instead:

```powershell
npm.cmd --version
npx.cmd playwright --version
```

Playwright is installed as a project-local dependency under:

```text
X:\Sumo-Tools\node_modules\playwright
```

Use normal Node for JavaScript checks:

```powershell
node --check ".\src\products\make_site2\runtime\site-refactor\ui\charts.js"
```

Use project-local Playwright for browser smoke checks against the shared preview.
For example:

```powershell
node -e "const { chromium } = require('playwright'); (async () => { const browser = await chromium.launch(); const page = await browser.newPage(); const errors = []; page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); }); page.on('pageerror', error => errors.push(error.message)); await page.goto('http://localhost:8766/', { waitUntil: 'networkidle' }); console.log(await page.title()); console.log('errors=' + errors.length); if (errors.length) console.log(errors.join('\n')); await browser.close(); })().catch(error => { console.error(error); process.exit(1); });"
```

Python works from the workspace. For local static preview, the command is:

```powershell
python -m http.server 8766 --directory <folder>
```

but the folder must actually contain `index.html`. The earlier `8787` 404 was because `files/output/make_site2` did not exist from `X:\Sumo-Tools`.

The make_site2 tests live under the repository-root `tests` directory, for
example:

```text
tests\test_make_site2_basho_results_redesign.py
tests\test_make_site2_table_sorting.py
tests\test_make_site2_build.py
```

Do not rely on the GitHub connector to discover unknown test files. In this
environment it can usually read files by exact known path, but file/directory
discovery and broad code search may miss existing files. Use local Git/shell
discovery from the repo root instead:

```powershell
git ls-files "tests/*"
git ls-files "tests/test_make_site2*.py"
git ls-files "*pytest*"
```

Use the repo-local virtual environment for tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -s <test paths>
```

For focused make_site2 checks, start with known root tests such as:

```powershell
.\.venv\Scripts\python.exe -m pytest -s tests\test_make_site2_basho_results_redesign.py tests\test_make_site2_table_sorting.py
```

Then broaden only when the focused checks are understood:

```powershell
.\.venv\Scripts\python.exe -m pytest -s tests
```

Testing policy is pragmatic. This is not a professional safety-critical build
where every historical test must be maintained forever. Tests may be current,
stale, or legacy/redundant. Current useful tests should be kept; stale tests may
be rewritten when they protect the current model; legacy tests that assert
abandoned structure may be deleted. A failing test is evidence to classify, not
automatic proof that product code is wrong.

Use tests to support the work just done or about to be done. Do not preserve
broad tests merely because they exist. It is acceptable to keep only a lightweight
baseline plus focused regression checks for recent changes.

For `make_site2`, useful recurring checks are:

```text
syntax/import checks
  Python compile/import where relevant; JavaScript `node --check` on edited
  runtime files.

focused pytest checks
  Model, manifest, build, CLI, data-output or renderer contracts directly
  affected by the change.

build/preview checks
  Build the site, serve it on localhost:8766, and inspect the relevant browser
  behaviour when the environment supports it.
```

Pytest is not a substitute for browser inspection. It cannot by itself prove
click behaviour, DOM event wiring, CSS layout, heading alignment, Plotly
visibility or other functional browser behaviour. When those are the material
risk, use the shared preview or ask for human browser inspection.

The user is not personally invested in maintaining test internals. If a change
under `tests/*` is needed to delete legacy tests, update stale tests, or add a
focused check for the current work, do it and explain the classification.

The user-site pytest install may be visible to the human's interactive shell
but not to Codex. If `py -m pytest` or `python -m pytest` fails from Codex,
do not chase the global Python environment first; use the repo-local `.venv`.

Pytest may also have a local capture problem in this environment. A normal
focused pytest run failed during capture teardown with:

```text
ValueError: I/O operation on closed file.
```

Rerunning with `-s` bypassed capture and produced ordinary test results. If an
LLM sees this pytest/capture failure again, it should switch to the `.venv`
command above with `-s`, then report any remaining real test failures.

There may be a lingering Python server on port `8766`, started earlier, serving
a recent build. Treat `8766` as the shared preview port and check with the user
before killing or replacing that process.

For data/builds, sometimes the live store is not available; why is not clear because the user says it is running. The reliable Codex path is to build from a history zip, ideally the small one kept for speed.

Also: binary files need care. `.gitattributes` currently normalizes `* text eol=lf`, and without binary exceptions it can corrupt files like `.pkl`. That explained the `full_shiks.pkl` weirdness.
