# SDDA2 Design Notes

## Product-First Framing

The old question was often phrased as:

```text
What does the `make_site2` module need?
```

The better question is:

```text
What does the local website product need, and what artifacts does it promise?
```

This distinction matters because code is machinery. The distribution target is the artifact set or target state delivered by that machinery.

## Why This Is Not Jervis

The Jervis line of thought asks whether a formal `free(S)` / `init(S)` analysis can be applied to Python-like programs.

That remains intellectually useful, but direct application to ordinary Python quickly becomes too expensive:

* loops may execute zero times;
* guarded loop outputs become conditional file families;
* `break` and `continue` require control-flow-sensitive treatment;
* useful precision tends toward abstract interpretation or symbolic execution.

SDDA2 should avoid that path.

The SDDA2 question is not:

```text
Can we prove the exact free set of this Python program?
```

It is:

```text
What file effects can we observe statically, how certain are they,
and how do they relate to a declared product?
```

## Useful Ideas To Keep

From the original SDDA work:

* scan file effects such as reads, writes, globs, copies, deletes, downloads, and environment reads;
* normalize file effects into file families;
* keep raw evidence separate from interpretation;
* classify evidence into reviewable policy buckets;
* report unresolved cases rather than hiding them;
* use execution slices as builder evidence where helpful.

From the Jervis discussion:

* be explicit about what can be known statically;
* distinguish guaranteed facts from possible or conditional facts;
* avoid pretending that arbitrary Python has a simple makefile semantics.

## New Center Of Gravity

SDDA2 should introduce product records before it introduces module analysis.

Candidate concepts:

```text
Product
Builder
Artifact family
Input family
External resource
Generated intermediate
Deployment target
Packaging policy
Evidence row
Review item
```

The report should answer product questions:

```text
For product P:
  what artifacts are promised?
  what source files/assets are required?
  what precomputed artifacts must be included or regenerated?
  what external resources are assumed?
  what generated intermediates are observed?
  what remains unresolved?
```

## Immediate Non-Goals

SDDA2 should not initially:

* infer every product from the repository;
* treat every module with a main guard as a product;
* derive a complete makefile;
* implement full Python control-flow semantics;
* prove exact file dependencies.

## Known Join Problem

The first SDDA2 action layer exposes an important problem from the earlier SDDA work: consumers and producers often name the same file family at different levels of resolution.

For example, a consumer may read:

```text
files/output/bcr/data/banzuke_change_report.csv
```

while a possible producer is only seen statically as writing:

```text
output_file
request.output_root/name
```

or another local parameter/field expression.

Humans can often see that the producer is nearby, but the analyser cannot safely join those rows unless it resolves enough parameter, local alias, return-value, and field provenance to put both sides into the same file-family vocabulary.

This is why SDDA2 currently separates:

* `input_worklist.csv`: inputs needing action;
* `producer_search.csv`: automatic candidate evidence;
* `input_resolution.csv`: current resolution status.

Low-confidence textual candidates are useful hints, not proof that a producer product has been found.

## Static Path Normalisation Experiment

The `sdda2.file_roots` experiment tried a narrower version of the same problem:

```text
Can we accumulate a normalised catalogue of file path expressions used by `src`?
```

The intended normal form was a literal-ish file path or file template:

```text
(<folder>/)*<file>.<ext>
```

Examples that worked well:

```text
files/output/HTML results/{year} {month:02d}/{day:02d}.html
files/output/current standings/{date.year} {date.month:02d}.html
files/output/fide_stdevs.json
files/input/elo_fide.json
```

The useful part of the experiment was bounded partial evaluation of common path-building idioms:

* imported path constants;
* `Path(...) / "literal"` expressions;
* f-strings and simple format specs;
* `os.path.join(...)`;
* simple helper-function returns;
* some local variable aliases;
* simple `self.field` values derived from constructor parameters.

The current report separates:

* `path_pattern`: populated only when the analyser has a normal-form file path/template;
* `normalisation_status`: the explicit answer to whether the expression was normalised;
* `symbolic_source`: provenance for unresolved legacy expressions such as `module:scope:name`.

The summary currently gives a useful bottom line: how many path expressions were normalised, and how many remain unresolved.

## Where The Static Approach Stops

Further progress now looks feasible only by making the partial evaluator much less partial.

For example, the analyser would need to understand cases such as:

* dataclass fields passed between modules;
* object properties such as `request.data_dir`;
* loop variables ranging over tuples of filenames;
* directory iteration such as `LOCAL_DATA.iterdir()`;
* suffix guards such as `local_file.suffix.lower() in {".csv", ".json"}`;
* deployment helpers that pass local and remote paths through wrapper functions.

Each individual case is tempting and many are tractable in isolation. The problem is cumulative: the work starts to resemble a small Python abstract interpreter, which is not proportionate to the practical goal of producing and deploying the website.

The conclusion of this experiment is therefore:

```text
Static scanning is useful reconnaissance, but it should not be the primary
mechanism for proving the deployment contract.
```

The next approach should be direct and empirical: run the relevant build/deploy code in a clean deployment environment and observe what is missing, created, read, and copied.

Candidate next project:

```text
src/deploy_test
```

That project should treat the deployment as the thing under test, rather than trying to infer the whole contract from source code alone.
