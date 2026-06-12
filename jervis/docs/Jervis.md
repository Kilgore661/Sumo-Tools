# Summary of Discussion: Semantics of a Toy Imperative Language

This document summarizes our discussion on defining a formal semantics for a restricted imperative programming language and its properties.

## 1. Language Definition
The language is a toy imperative language with the following constructs:
* **Assignment (`x := e`)**
* **Sequential Composition (`S;S`)**
* **Conditionals (`if b then S else S fi`)**
* **Bounded Iteration (`do n times S`)**

Notably, this language excludes `while` loops, ensuring it remains **total** (all programs terminate).

## 2. Formal Analysis: `init(S)` and `free(S)`
We defined the static analysis of variables:
* **`init(S)`**: The set of variables guaranteed to be initialized before use in $S$.
    * `init(x := e) = {x} \ var(e)`
    * `init(S1; S2) = init(S1) \cup (init(S2) \setminus var(S1))`
    * `init(if b then S1 else S2 fi) = (init(S1) \cap init(S2)) \setminus var(b)`
    * `init(do n times S) = \emptyset` (due to the possibility that $n=0$).
* **`free(S)`**: The set of variables required to be defined in the initial state $\sigma$ for $S$ to execute safely. Defined as `free(S) = var(S) \setminus init(S)`.

**Safety Property**: If $\sigma(x)$ is defined for all $x \in free(S)$, then $M(S)(\sigma)$ is well-defined.

## 3. Extensions and Modularity
* **User-defined Functions**: The language supports `def f(args) -> type: S`, where `var(args) \supseteq free(S)`.
* **Imports**: Static imports (`from m import f`) are treated as a pre-processing step. By excluding runtime/conditional imports, the global environment of functions remains statically determinable.
* **Algebraic Foundation**: The system operates over an $S$-sorted algebra with a fixed signature $\Sigma$. Imports are treated as adding total functions to $\Sigma$ without introducing new sorts (**Fixed Sort Integrity**).

## 4. Build Systems (Makefiles)
When variables of sort `file` are considered, `free(S)` and `init(S)` provide a direct mapping to dependency management:
* **Targets**: Variables in `init(S)` (outputs).
* **Prerequisites**: Variables in `free(S)` (inputs).

## 5. Current Assessment For `Sumo-Tools`

The original Jervis idea remains attractive as a formal model, but applying it directly to ordinary Python modules now looks unlikely to be the right first approach for this project.

The motivating practical question is not "can every Python file be run from a cold checkout?" The better question is "what product or artifact family is promised, and what files or external resources are required to produce it?"

For example, `src.products.make_site2` is machinery. The true targets are the generated website files and the copied/deployed server file sets. Similarly, a module such as `foo.py` may be less important than a product such as `foo-outputs`.

This suggests a product-oriented distribution contract:

* **Builder**: Python code used to create artifacts.
* **Product**: named artifact collection or target state.
* **Inputs**: local files or external resources required to build the product.
* **Outputs**: files or target states produced by the builder.

## 6. Why Direct `free(P)` For Python Looks Too Ambitious

An AST census of `src` is feasible and useful, but it exposes the gap between the toy language and real project Python. The source uses ordinary constructs such as `for`, `if`, function definitions, imports, class definitions, file operations, exceptions, context managers, `break`, and `continue`.

Some of these are not fatal for a conservative analysis. For example, if loops are assigned:

```text
init(for ...: S) = empty
```

then `break` and `continue` do not make the post-loop initialization result much worse. The loop already guarantees no initialization, because it might run zero times.

However, that conservative rule also makes the analysis much less useful. Many real outputs are naturally produced inside loops:

```python
for basho in bashos:
    write_html(output_dir / f"{basho}.html")
```

A useful build analysis would want to recognize an output family. But once guards are added:

```python
for basho in bashos:
    if basho[0] == "x":
        write_html(output_dir / f"{basho}.html")
```

the output is conditional on an arbitrary Python expression. Fully analyzing this pushes the project toward a Python abstract interpreter or symbolic execution engine. That is probably over-engineering for the actual goal of building and distributing a website.

Likewise, a formal treatment of bounded loops with `break` and `continue` could be imagined by expanding `do n times S od` into `S; ...; S` and treating `break` and `continue` as structured jumps. This may be mathematically plausible, but it is more machinery than the current problem warrants.

## 7. Ideas Worth Taking Forward

The AST-based work is still valuable if it is treated as reconnaissance and classification rather than as a complete proof system.

Promising next steps:

* Keep the raw AST scan as a project census.
* Add a file-effect scan for calls such as `open`, `Path.read_text`, `Path.write_text`, `json.load`, `json.dump`, `pickle.load`, `pickle.dump`, `shutil.copy`, and related APIs.
* Classify discovered paths by obviousness:
    * concrete literal path;
    * `Path(...) / "literal"` style path;
    * f-string or template path;
    * variable-derived path;
    * opaque path.
* Record the enclosing context of each file effect:
    * module/function;
    * inside loop;
    * inside `if`;
    * inside `try`;
    * guarded or unconditional where obvious.
* Report certainty levels rather than pretending to have exact makefile targets:
    * concrete file;
    * parametric file family;
    * conditional file family;
    * opaque file effect.
* Compare discovered file effects against declared products and distribution contracts.

The goal should therefore shift from "derive a complete makefile from arbitrary Python" to "extract candidate file effects, classify their certainty, and use that evidence to define or validate product-oriented distribution contracts."
