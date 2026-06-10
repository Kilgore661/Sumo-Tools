# SDDA Design

## Architectural position

SDDA is a single-root static analyser for the Sumo-Tools website product.

The product root is:

```text
src.products.make_site2.__main__
```

SDDA is not a package-discovery tool. It does not scan the repository looking for every module with a main guard, every command-line utility, or every research workflow.

A module is relevant to SDDA only if it is reachable from the product root through imports, bindings, and calls. Other tools in the repository are treated as research unless and until they become reachable from the website build/deploy path.

The analyser's main product is a set of evidence-backed reports about file-family may-dependencies. Build files such as Makefiles or Ninja files are possible later renderings, not the central output.

## Implementation decomposition decision

SDDA shall be implemented as a package decomposed into logical modules, not as one large analyser script.

The acid test is:

```text
No SDDA Python module should be over 300 lines long.
```

If a module approaches that size, it should be split into a package or refactored into smaller logical units before it becomes difficult to understand and modify.

This is both an ordinary maintainability rule and a practical rule for assisted development: smaller, cohesive files are easier to inspect, reason about, and change safely.

## Separation of graphs

SDDA deliberately keeps several graphs and indexes separate.

### Module index

The module index is a broad lookup table:

```text
module name -> source file path
```

It is built from the import root so that project imports can be resolved.

A module appearing in the index does not mean that the module is relevant to the analysed product. It only means that SDDA knows where the module lives if an import refers to it.

### Module dependency graph

The module dependency graph is rooted at the command-line module.

Its nodes are Python modules and its edges are import relationships.

This graph is discovered by starting with the product root and recursively resolving imports that appear in reachable project modules.

The module dependency graph is an intermediate analysis product. It helps SDDA decide which modules may need import-time analysis and which names may need binding resolution.

A module dependency edge is not itself a data dependency edge.

For example:

```python
from src.infra.parser.parser2 import OUTPUT_DIR
```

may create a module dependency from the importing module to `src.infra.parser.parser2`. It may also mean that import-time effects of `parser2` matter. It does not mean that every file use inside every function in `parser2` belongs to the importing module's data dependency graph.

### Scope graph

Each parsed module is split into scopes:

```text
module import-time scope
function body scope
method body scope
class body scope
unknown / unresolved scope
```

File uses are attached to scopes, not merely to modules.

This prevents unrelated sibling functions in an imported module from being treated as part of the website product merely because they share a file with an imported constant or callable.

### Callable graph

The callable graph approximates which functions and methods may call which other functions and methods.

It is rooted at the product entry path and is intentionally conservative.

The first implementation should handle common direct cases:

```text
local_function(...)
imported_function(...)
module.function(...)
self.method(...) when the receiver class is obvious enough
ClassName.method(...) when resolvable
```

Dynamic or unresolved calls should be reported rather than silently ignored.

### Data dependency graph

The data dependency graph is derived from scope-level file uses after import-time and callable reachability have been considered.

Its nodes are file families, URL families, environment settings, and similar non-code dependency entities.

Its edges represent may-actions such as:

```text
may-read
may-write
may-observe / glob
may-copy
may-delete
may-download
may-existence-check
may-create-directory
```

The data dependency graph is the product-facing graph. It is what supports source-distribution and reproduction decisions.

## Top-level algorithm

### 1. Parse command-line arguments

The primary invocation is:

```powershell
python -m sdda src.products.make_site2.__main__ --import-root .
```

The package-module invocation dispatches through:

```text
sdda/__main__.py
```

The command-line root is a Python module, not a package to be searched for functional units.

### 2. Build the module index

Walk the import root and record project Python modules.

The output of this stage is a map such as:

```text
src.products.make_site2.__main__ -> src/products/make_site2/__main__.py
src.products.make_site2.build    -> src/products/make_site2/build.py
src.infra.live_store.api         -> src/infra/live_store/api.py
```

This is only a lookup catalogue. It does not decide product relevance.

### 3. Build the reachable module dependency graph

Starting from the command-line root, parse reachable modules and resolve their imports against the module index.

For each project import that can be resolved, add a module dependency edge.

Continue until no new reachable project modules are found.

External imports should be recorded where useful but are not recursively analysed in the first version.

The output of this stage should feed reports such as:

```text
module_index.csv
imports.csv
module_graph.csv
```

### 4. Extract AST facts by scope

For each reachable project module, parse the AST and split the module into scopes.

Record:

```text
imports
assignments that may bind constants or paths
function definitions
class definitions
call expressions
file uses
URL literals or templates
environment-variable references
obvious local assumptions such as hard-coded IP addresses or absolute local paths
```

At this stage, records are evidence only. They are not yet classified as distribution inputs, outputs, caches, or state.

### 5. Record import-time file uses

Top-level module code may execute when the module is imported.

Therefore, file uses in a reachable module's import-time scope are relevant to the product if the module must be imported to bind a reachable name or execute reachable code.

For example:

```python
# m.py
state = open("foo.csv").readline()

def g():
    return 123
```

A root that does:

```python
from m import g
```

may depend on `foo.csv`, because importing `m` is required to bind `g`.

The report should make the reason clear: `foo.csv` is an import-time dependency of `m`, not a file read performed by the body of `g`.

### 6. Resolve bindings needed for calls and constants

For imported names, determine what local name is bound and what module or object it comes from when this can be done statically.

This is needed for two reasons:

```text
to resolve constants used in path expressions
to resolve call targets used in the callable graph
```

Resolving a binding does not mean that every callable in the provider module is relevant.

### 7. Build the approximate callable graph

Within reachable modules, identify call expressions and resolve obvious call targets.

The graph is a may-call graph. It does not need to prove that calls occur on every execution path.

Unresolved calls, dynamic dispatch, callbacks, and reflection should be reported in `unresolved.csv`.

### 8. Compute the product execution slice

The product execution slice includes:

```text
import-time effects of modules needed by the reachable import graph
file uses in callable scopes reachable from the product root
unresolved dynamic cases marked for review
```

It excludes:

```text
unrelated sibling functions in imported modules
modules not reachable from src.products.make_site2.__main__
research tools that merely have a main guard
package-level functional units not called by the product root
```

This step is the main guard against the old mistake of treating every file use in every imported module as product dataflow.

### 9. Extract file uses from the execution slice

For included scopes, record file and file-like operations such as:

```text
open(...)
Path(...).read_text()
Path(...).write_text()
Path(...).glob(...)
glob.glob(...)
Path.exists()
Path.mkdir(...)
shutil.copy(...)
shutil.copytree(...)
shutil.rmtree(...)
requests.get(...)
urllib calls
os.environ[...] and os.getenv(...)
```

Each file-use record should include evidence:

```text
module
source file
scope kind
scope name
line number
action
raw expression
partially resolved expression, if available
confidence
reason for inclusion
```

### 10. Normalise file uses into file families

Raw file uses are grouped into file families.

Examples:

```text
singleton file:
  files/input/elo_fide.json

glob-discovered family:
  files/output/infra/get_bios/rikishi/*.html

template-generated family:
  files/output/infra/get_bios/rikishi/{rikid:05d}.html

directory tree:
  src/products/make_site2/runtime/site-refactor/**

URL template:
  https://sumodb.sumogames.de/Rikishi.aspx?r={rikid}
```

A glob is treated as a runtime-discovered family. SDDA records the pattern, not the current members of the family.

Where possible, related families should be unified or cross-referenced. For example:

```text
glob:  files/output/infra/get_bios/rikishi/*.html
write: files/output/infra/get_bios/rikishi/{rikid:05d}.html
```

likely describe the same family.

Unification should be conservative and explainable. If the analyser is unsure, it should record a possible-family-match rather than silently merging unrelated families.

### 11. Classify file families and non-file assumptions

Classification is performed after evidence collection and family normalisation.

Initial classifications include:

```text
required_distribution_input
checked_in_static_asset
config_or_seed_data
internet_source
internet_recreatable_source_capture
generated_output
generated_canonical_file
possible_efficiency_cache
possible_state_or_control_file
runtime_cache
diagnostic_output
legacy_or_exploratory_output
unknown_review_needed
```

Read-or-observe plus write on the same family by the same analysed command or scope should initially be classified as:

```text
possible_efficiency_cache
```

or, where appropriate:

```text
possible_state_or_control_file
```

The analyser should not prematurely collapse such a family into only an input or only an output.

Environment variables should be reported by name only. Values must not be read, stored, or emitted.

Hard-coded IP addresses, hostnames, absolute local paths, and local deployment roots should be reported as local assumptions when statically visible.

### 12. Emit reports

The first report set should include:

```text
module_index.csv
imports.csv
module_graph.csv
scopes.csv
calls.csv
file_uses.csv
file_families.csv
file_family_classification.csv
distribution_candidates.csv
environment_assumptions.csv
unresolved.csv
summary.md
```

Report names and core columns should remain stable once introduced.

The reports should distinguish:

```text
evidence collected from code
normalised file families
classification decisions
unresolved review items
```

## Suggested internal modules

The implementation should use a package of small, cohesive modules. The expected starting decomposition is:

```text
sdda/__main__.py
  CLI entry point.

sdda/module_index.py
  Builds module-name to path catalogue.

sdda/import_graph.py
  Resolves imports and builds the reachable module dependency graph.

sdda/scopes.py
  Splits ASTs into import-time, function, method, class, and unknown scopes.

sdda/bindings.py
  Resolves simple imported names, constants, and local bindings.

sdda/calls.py
  Builds an approximate callable may-call graph.

sdda/file_uses.py
  Extracts raw file, URL, and environment uses from scopes.

sdda/file_families.py
  Normalises raw uses into file families and records possible family matches.

sdda/classification.py
  Applies conservative distribution-oriented roles.

sdda/reports.py
  Writes CSV and Markdown reports.
```

The exact module list may evolve, but any module approaching the 300-line acid test should be split or refactored.

The first implementation may borrow code from `src/introspection` where useful, but it should not import from `src/introspection` and should not inherit the old module-level dataflow assumption.

## Development milestones

### Milestone 1: module and import evidence

Implement:

```text
module_index.csv
imports.csv
module_graph.csv
```

for:

```powershell
python -m sdda src.products.make_site2.__main__ --import-root .
```

### Milestone 2: scope-level file-use evidence

Implement:

```text
scopes.csv
file_uses.csv
unresolved.csv
```

with file uses attached to scopes rather than whole modules.

### Milestone 3: execution slice

Implement enough binding and callable reachability to avoid treating every function body in every imported module as relevant product dataflow.

This milestone should specifically avoid the historical false-positive pattern where importing a constant from a module causes all callable-body file uses in that module to be reported as product dependencies.

### Milestone 4: file families

Implement:

```text
file_families.csv
possible family matching
```

including singleton files, glob-discovered families, template-generated families, directory trees, URL templates, and runtime/virtual families.

### Milestone 5: classification and distribution reports

Implement:

```text
file_family_classification.csv
distribution_candidates.csv
environment_assumptions.csv
summary.md
```

### Milestone 6: regression checks

Compare the `src.products.make_site2.__main__` output with the checked-in snapshot under:

```text
src/products/make_site2/buggy_output/src.products.make_site2.__main/
```

Changes from that snapshot are acceptable, but they should be explainable.

Use `src.infra.get_bios.__main__` as a development regression test for difficult analyser behaviour, not as part of the website distribution unless it becomes reachable from the product root.

## Non-goals

The design does not attempt to solve all of Python.

The first version need not fully support:

```text
dynamic imports
reflection-heavy code
arbitrary callbacks
subprocess file effects
all possible method dispatch
runtime-only path construction
third-party package dependency analysis
```

When such cases are visible, SDDA should record unresolved evidence for human review rather than pretending to know more than it does.
