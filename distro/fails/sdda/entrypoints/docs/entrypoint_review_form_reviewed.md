# SDDA Entrypoint Review Form — Reviewed

Import root: `sdda\entrypoints`

This file records the human review outcome for machine-identified entrypoint candidates in the current `sdda.entrypoints` self-test.

## Machine-written context

total_modules: 7
library_modules: 4
programs: 3
  probable_entrypoints: 1
  imported_programs_needing_review: 2
    probable_library_modules: 2
    possible_entrypoints: 0

## Overall human conclusion

Conclusion:

> This folder has one true entrypoint: `__main__`. The imported programs `classifier` and `module_index` were reviewed as library-like helper modules, not real entrypoints.

True entrypoints:

- `__main__`

Modules reviewed as library-like:

- `classifier`
- `module_index`

Modules still unclear:

- None

## Probable entrypoints

These are standalone programs. They are probable entrypoints, but still need human confirmation.

### `__main__`

Path: `X:\Sumo-Tools\sdda\entrypoints\__main__.py`
First non-declarative statement: line 1, `__main__.py`
Has main guard: `True`
Is `__main__.py`: `True`

- [x] Reviewed as true entrypoint
- [ ] Reviewed as not a true entrypoint
- [ ] Still unclear

Conclusion / comments:

> This is the command entrypoint for `python -m sdda.entrypoints`. It parses CLI arguments, runs the entrypoint analysis, writes reports, and prints the summary.

## Imported programs needing review

These are programs that are imported by at least one other indexed module.

### `classifier`

Path: `X:\Sumo-Tools\sdda\entrypoints\classifier.py`
Subtype hint: `probable_library`
Imported by: `analysis`
First non-declarative statement: line 9, `Assign`
Has main guard: `False`
Is `__main__.py`: `False`

- [x] Reviewed as library-like module
- [ ] Reviewed as real entrypoint
- [ ] Reviewed as obsolete / ignore
- [ ] Still unclear

Conclusion / comments:

> This is a library-like helper module. It is classified as a program only because the strict rule treats top-level assignments as non-declarative. The assignments define classifier constants; there is no command body or main guard.

### `module_index`

Path: `X:\Sumo-Tools\sdda\entrypoints\module_index.py`
Subtype hint: `probable_library`
Imported by: `analysis`
First non-declarative statement: line 7, `Assign`
Has main guard: `False`
Is `__main__.py`: `False`

- [x] Reviewed as library-like module
- [ ] Reviewed as real entrypoint
- [ ] Reviewed as obsolete / ignore
- [ ] Still unclear

Conclusion / comments:

> This is a library-like helper module. It is classified as a program only because the strict rule treats top-level assignments as non-declarative. The assignment defines skipped-directory configuration used by the module indexer; there is no command body or main guard.
