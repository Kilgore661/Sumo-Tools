# SDDA Specification

## Scope

The command-line entry point shall be:

```text
sdda/__main__.py
```

It is part of the repository audit and distribution-analysis tooling, not part of the application runtime under `src`.

The analyser targets the Sumo-Tools website product. Its primary analysed root is:

```text
src.products.make_site2.__main__
```

Given that Python module entry point, it shall statically analyse the code that may be reached through imports, bindings, and calls from that entry point, and produce an evidence-backed over-approximation of file-family use.

Code not reachable from the website build/deploy entry point is out of distribution scope, even if it defines a command-line tool, a main guard, or a useful research/probe workflow.

Such code is treated as research unless and until it becomes reachable from the website build/deploy path.

The analyser is not required to discover every functional unit in a package or every module with a main guard.

The target distribution mode is:

```text
source distribution with internet access
```

Generated reports shall be written by default under:

```text
files/output/sdda/{root-module}/
```

## Definitions

A **file use** is one observed operation in code involving a file, directory, URL, or file-like family. Examples include:

```text
read
write
glob / observe
copy
delete
download
existence check
mkdir / directory creation
```

A **file family** is the inferred file or set of files described by one or more file uses.

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

runtime / virtual family:
  live-store shared-memory segment history{VERSION}
```

A concrete file is a singleton file family.

A glob-discovered family is a runtime-discovered set. The analyser may know the path pattern, but it must not assume that it knows the actual members of the family.

A URL or URL template shall be recorded as an external source family when observed. The analyser shall record URLs as given; it shall not attempt to validate whether they are stable, authoritative, complete, or semantically correct.

## Core semantics

The analyser shall report **may-dependencies**.

If a statically visible import-time effect or execution path reachable from the website build/deploy entry point may read, write, observe, copy, delete, download, create, or check a file family, that file family should be included in the output.

The analyser is not required to prove that a file family is used on every possible execution path.

## Distribution interpretation

The analyser targets a source distribution with internet access for building and deploying the website locally and remotely.

Under this distribution mode, files that can be regenerated from code plus internet access are normally not required distribution inputs.

The analyser shall still report such files as file families, together with their observed producers, consumers, and classifications, because they may be useful for reproducibility, auditing, cache decisions, or later build-recipe generation.

The analyser shall report candidate required distribution inputs where a file family appears to be needed by the website build/deploy path and no regeneration path is evident from the analysed code.

## Scope model

The analyser shall distinguish file uses by lexical/runtime scope.

At minimum, it shall distinguish:

```text
module import-time scope
function body scope
method body scope
class body scope
unknown / unresolved scope
```

This distinction is required because importing a module executes its top-level code.

For example:

```python
# m.py
state = open("foo.csv").readline()

def g():
    return 123
```

The statement:

```python
from m import g
```

may depend on `foo.csv`, because binding `g` requires importing `m`, and importing `m` executes the top-level read.

The analyser should therefore distinguish:

```text
import-time effects needed to bind a name
callable-body effects of the bound callable
callable-body effects of callees reachable from that callable
```

## Import and callable handling

The analyser shall keep import analysis, but import reachability alone shall not imply dataflow reachability for all function bodies in the imported module.

For an imported module or imported name, the analyser shall include:

```text
import-time file uses of the imported module
file uses of callables that are actually reachable from the analysed entry point
unresolved dynamic cases marked for review
```

It shall not include file uses from unrelated sibling functions merely because those functions live in an imported module.

It shall not scan packages for unrelated command-line tools or main-guard modules unless those modules are reachable from the website build/deploy entry point.

## Environment and local assumptions

The analyser shall report obvious non-file distribution assumptions when they are statically visible.

These include:

```text
environment variables
hard-coded IP addresses
hard-coded hostnames
absolute local paths
hard-coded local deployment roots
```

Environment variables shall be reported by name only. Their values shall not be read, stored, or emitted.

If an environment variable is used as a password, token, or deployment secret, the analyser should classify it as a deployment setting or deployment secret, but it must not attempt to obtain or display the value.

Deployment performed by `make_site2` is in scope. If deployment code depends on an environment variable, that setting shall be reported as part of the project's source-distribution responsibilities, even though the value is repo-deployer-specific and should not be committed.

The analyser is not required to solve Python package availability, virtual environments, or third-party installation requirements in its first version.

## File family classification

Raw file-use evidence shall be kept separate from interpretation.

The analyser shall classify file families into reviewable roles where possible.

Initial role names may include:

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

A file family that is both read or observed and written by the same analysed command or scope shall initially be classified conservatively as:

```text
possible_efficiency_cache
```

or, where appropriate:

```text
possible_state_or_control_file
```

The analyser shall not prematurely collapse such a file family into only an input or only an output. Later policy may decide how to treat it.

## Required reports

The primary outputs shall be neutral audit reports, not build files.

The first report set should include files such as:

```text
file_uses.csv
file_families.csv
file_family_classification.csv
distribution_candidates.csv
imports.csv
scopes.csv
calls.csv
environment_assumptions.csv
unresolved.csv
summary.md
```

Report names and core columns are part of the analyser interface and should remain stable once introduced.

Classification labels are provisional during early development and may evolve, but changes should be visible and explained.

A later version may emit downstream renderings such as:

```text
Makefile.candidate
build.ninja
doit tasks
custom build plan
```

Those renderings are projections of the richer file-family model and are not the primary product.

## Command-line interface

The analyser should be invokable as a package module with a root module and import root.

The primary invocation is:

```powershell
python -m sdda src.products.make_site2.__main__ --import-root .
```

The package-module invocation shall dispatch through `sdda/__main__.py`.

Other module roots may be analysed as development tests of the analyser, but package-wide discovery of unrelated tools is not a distribution requirement.

## Acceptance tests

The primary adequacy test shall be `src.products.make_site2.__main__`.

The generated output should be compared with the checked-in snapshot under:

```text
src/products/make_site2/buggy_output/src.products.make_site2.__main/
```

Changes from that snapshot need not be avoided, but they should be visible and explainable.

The `make_site2` test should exercise:

```text
singleton config or input-like files, if present, such as files/input/elo_fide.json
deployment environment variables, if present
hard-coded local host or IP assumptions, if present
```

`src.infra.get_bios.__main__` may be used as a development regression test for analyser behaviour because it exposes useful edge cases. A satisfactory development result should report that:

```text
src.infra.get_bios.__main__ may obtain live History via live_store
files/output/store_name.txt is a possible runtime state/control dependency
files/output/infra/get_bios/rikishi/*.html is observed by glob
files/output/infra/get_bios/rikishi/{rikid:05d}.html is written
those two rikishi HTML shapes likely describe the same file family
that family is a possible efficiency cache / self-observed output family
parser2 callable-body file effects are not included merely because OUTPUT_DIR was imported
SumoDB Rikishi.aspx URLs are internet sources
```

This `get_bios` test does not make `get_bios.__main__` part of the website distribution unless it is reachable from `src.products.make_site2.__main__`.

## Non-goals and limits

`sdda.py` shall not promise perfect static knowledge of Python behaviour.

The analyser may encounter:

```text
dynamic imports
reflection
callbacks
subprocesses
environment-dependent paths
data-dependent filenames
runtime-only file families
```

These cases should be reported as unresolved or review-needed where practical, rather than silently ignored.

The intended contract is:

```text
sdda.py produces an evidence-backed, conservative over-approximation of file-family may-dependencies for human review and distribution planning.
```
