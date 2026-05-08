# make_site Docs

This directory records the public-site design, producer contracts, site-builder
notes, and open work for `src.products.make_site`.

The docs are split into:

* `current/` - live policy, requirements, implementation notes, and open work;
* `archive/` - preserved design notes and exploratory material that helped get
  the site to its current shape but should not be treated as the first place to
  look for current policy.

This reorganisation is intentionally preservation-first. The archived notes
have not been aggressively summarised or deleted. They remain useful for
understanding why the current decisions were made.

## Start Here

Read the current docs in this order when trying to understand the public site:

1. `current/Public Site Requirements.md`
2. `current/Public Site Specification.md`
3. `current/Public Site Design.md`
4. `current/Producer Writers and Prototype Embeds.md`
5. `current/Equelo Version Naming.md`
6. `current/TBD Register.md`

For implementation details, also read:

* `current/Make Site Builder Notes.md`
* `current/Site Definition Handoff Memo.md`

## Current Equelo Position

The current public Equelo rating-landmark curve is named:

```text
Mark 3.2.1(2000)
```

The page `Typical Equelo Ratings` uses that curve.

Names such as `v0`, `v1`, ..., `v5` refer only to diagnostic chart stages in
the fixed-v1 audit trail. They are not public model names. See
`current/Equelo Version Naming.md` for the canonical naming policy.

## Documentation Policy

Completeness is preferred over lossy tidying.

When a note is still useful but no longer represents current policy, move it to
`archive/` and point to the current replacement. Do not delete or compress it
merely because it overlaps with newer notes.

