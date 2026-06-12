# Entrypoints Review

## Status

This document records the current requirements-level review of `sdda.entrypoints`.

The review treats the existing code as evidence, not authority. The question is whether the package delivers something that fits the top-level SDDA requirements, rather than whether it can perfectly infer Python author intent.

## Assessment

`sdda.entrypoints` is a good fit for SDDA's tool-identification requirement, with one missing downstream hand-off piece.

The package does not deliver perfect entrypoint detection. It delivers a conservative, Sumo-Tools-style program classification and review queue:

```text
indexed Python modules
  -> declarative library modules
  -> program-like modules
       -> standalone command-like candidates
       -> standalone weak candidates
       -> imported probable-library modules
       -> imported possible-entrypoint review items
```

This is useful for SDDA because SDDA needs to know which programs are worth running dataflow over, and which modules are probably support code.

## Classification Model

The classifier treats `__main__.py` and non-declarative top-level statements as program evidence.

This rule is deliberately conservative. For example, a module containing a top-level assignment may have program evidence even if human review later treats it as library-like support code.

The important second stage combines that program evidence with import topology:

```text
program-like module with inbound indexed imports
  -> imported_program

program-like module with no inbound indexed imports
  -> standalone_program
```

Imported program-shaped modules are then classified as either:

```text
probable_library
review / possible entrypoint
```

Standalone program-shaped modules are classified as either:

```text
command_like
weak_entrypoint_signal
```

Labels such as `probable_library` are not incidental. They are central output. They express the practical local judgement that a module has executable Python evidence, but in Sumo-Tools-style code its shape probably belongs to support or library code.

## Fit For SDDA

The package fits the SDDA requirement once program classification under local conventions is understood as the point.

SDDA is not trying to solve entrypoint detection for all possible Python packages. It is analysing Sumo-Tools and adjacent code written in the same style.

Under that local contract, static syntactic and topological signals are meaningful:

```text
__main__.py usually means runnable package or program
main guard usually means runnable script or program
unimported executable module often means standalone tool
imported executable module with mostly definitions/constants often means support module
ordinary imports usually express meaningful code dependency
```

The package's explicit assumptions are therefore appropriate rather than embarrassing. The import root is treated as the closed universe for reference analysis. Dynamic imports, subprocess execution, shell scripts, task runners, config-driven plugin loading, and external users invoking modules directly are outside the current static evidence model.

## Gap

The main gap is pipeline hand-off.

`sdda.entrypoints` currently produces machine classifications and a Markdown human review form. It does not yet produce a durable, machine-readable reviewed program catalogue for a future SDDA integration layer.

That gap does not invalidate the package. It identifies the next contract that must be specified before `sdda.dataflow` and the future repository-level SDDA layer can consume reviewed entrypoint results.

## Conclusion

`sdda.entrypoints` should be kept.

It should not be treated as a throwaway prototype.

Its classification scheme should be treated as part of the emerging SDDA model, provided the human-review step remains explicit and a reviewed-output contract is added later.

The existing code does not force a change to the top-level SDDA requirements.
