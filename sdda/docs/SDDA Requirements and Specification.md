# SDDA Requirements and Specification

## Requirements

The Static Data-Dependency Analyser, `sdda.py`, is required to determine what non-code file families may be needed, produced, or observed by a Sumo-Tools Python entry point, package, or command.

The purpose is to support distribution and reproduction decisions for the repository.

In particular, the analyser should help answer:

```text
What non-code files need to be included in a distribution of the repo?
What non-code files can be regenerated from code, internet sources, or other generated file families?
What file dependencies are currently implicit in the code?
```

The analyser is not primarily required to generate a Makefile. A Makefile, Ninja file, `doit` task file, or other build recipe may be a later output, but build-file generation is only a test of whether the extracted dependency information is sufficiently complete and precise.

The analyser should be conservative. It should report file families that may be used, not only file families that must be used on every execution path.

## Specification

### Scope

`sdda.py` shall live under:

```text
sdda/sdda.py
```

It is part of the repository audit and distribution-analysis tooling, not part of the application runtime under `src`.

Given a Python root module or entry point, it shall statically analyse the reachable code and produce an evidence-backed over-approximation of file-family use.

Generated reports shall be written by default under:

```text
files/output/sdda/{root-module}/
```

### Definitions

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

### Core semantics

The analyser shall report **may-dependencies**.

If a statically visible import-time effect or execution path may read, write, observe, copy, delete, download, create, or check a file family, that file family should be included in the output.

The analyser is not required to prove that a file family is used on every possible execution path.

### Scope model

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

### Import and callable handling

The analyser shall keep import analysis, but import reachability alone shall not imply dataflow reachability for all function bodies in the imported module.

For an imported module or imported name, the analyser shall include:

```text
import-time file uses of the imported module
file uses of callables that are actually reachable from the analysed entry point
unresolved dynamic cases marked for review
```

It shall not include file uses from unrelated sibling functions merely because those functions live in an imported module.

### File family classification

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

### Required reports

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
unresolved.csv
summary.md
```

A later version may emit downstream renderings such as:

```text
Makefile.candidate
build.ninja
doit tasks
custom build plan
```

Those renderings are projections of the richer file-family model and are not the primary product.

### Command-line interface

The analyser should be invokable with a root module and import root, for example:

```powershell
python sdda/sdda.py src.infra.get_bios.__main__ --import-root .
python sdda/sdda.py src.infra.get_bios.parser --import-root .
python sdda/sdda.py src.products.make_site2.__main__ --import-root .
```

### Acceptance tests

The first adequacy test shall be `src.infra.get_bios.__main__`.

A satisfactory first result should report that:

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

The second adequacy test shall be `src.products.make_site2.__main__`.

The generated output should be compared with the checked-in snapshot under:

```text
src/products/make_site2/buggy_output/src.products.make_site2.__main/
```

Changes from that snapshot need not be avoided, but they should be visible and explainable.

### Non-goals and limits

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
