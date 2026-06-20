# Deployment Issues

## Legacy `files/input/bios.json` dependency

During the clean-room `make_site2` bootstrap, the Equelo refresh path
failed because it reads:

```text
files/input/bios.json
```

This remains a true current input dependency for the fixed-supported Equelo
pipeline, not a generated `files/output` artifact in the path tested so far.

However, `bios.json` is legacy data. It should eventually be replaced by a
current artifact produced by the `src.infra.get_bios` pipeline. That pipeline
currently downloads raw SumoDB rikishi pages and parses them to:

```text
files/output/infra/get_bios/rikishi_bios.json
```

The clean-room deployment work should not pause to solve this migration. For
now, record that `files/input/bios.json` must be included in the distribution or
the Equelo code must be changed to consume a generated `get_bios` artifact.

## Probable Overengineering Ideas

### Per-stage file manifests

It may eventually be useful to know, for each pipeline stage, exactly which
files it creates or updates.

Possible approaches:

- declared contracts in documentation or code;
- static scanning using the abandoned/parked `sdda2` ideas;
- empirical before/after filesystem snapshots around each stage.

The empirical approach is probably the most useful for the current brute-force
deployment work: run one command in a clean tree, snapshot `files/output` before
and after, and record the observed file delta.

This should not become the next project yet. The immediate goal remains to
discover the actual missing inputs and stage order needed to build
`make_site2` from a clean checkout. If the stage order stabilises, per-stage
manifests may become a lightweight way to distinguish:

```text
source inputs
source-cache snapshots
generated intermediates
final static-site artifacts
deployment targets
```

## Extended Distribution Candidates

### Raw internet source-cache bundles

The clean-room run showed that some stages are technically capable of fetching
their raw internet inputs, but doing so from an empty tree is slow and noisy.

Candidate source-cache bundles:

```text
files/output/current standings/
files/output/HTML results/
files/output/infra/get_bios/rikishi/
```

These are raw SumoDB HTML caches rather than derived analytical results. An
extended distribution can include them to avoid thousands of repeated network
requests, then run the relevant downloader/bootstrap step to repair any missing
or stale files.

## Observed Pipeline Usability Issues

### `src.infra.get_bios.parser` has no progress indicator

During the clean-room run, `py -m src.infra.get_bios.parser` parsed 9064 cached
rikishi bio HTML files and eventually completed successfully, writing:

```text
files/output/infra/get_bios/rikishi_bio_missing_fields.csv
files/output/infra/get_bios/rikishi_bios.json
```

The command appeared silent while it worked. It should probably print progress,
or at least periodic counts, because this stage can take long enough that a
user may think it is hung.

## Deferred Design Issues

### Shared constant discoverability

The Sumo-Tools codebase has constants in many local modules, including
analysis producers, product builders, deployment packaging and runtime-support
code. Some are deliberately local, but some appear to be cross-cutting public or
operational policy values.

Open question: are all project-wide or distro-relevant constants gathered in
one easy-to-find place, or at least organised under obvious domain-level
constant/config modules?

If not, consider introducing or documenting a clearer constants policy. The
goal is not to centralise every local magic value, but to make shared policy
values, output roots, distro paths, limits and operational defaults easy to
discover and hard to accidentally duplicate.

### Shared banzuke calendar/source-availability model

During the clean-room run, `src.analysis.banzuke_compare.publisher` defaulted
to the next two-month basho date after the latest completed History key and
therefore tried to load:

```text
files/output/current standings/2026 07.html
```

on 2026-06-12, before that banzuke was expected to exist.

The immediate code fix makes Banzuke Compare select the latest available
`files/output/current standings/*.html` source file when no explicit date is
requested. This is a practical deployment fix because Banzuke Compare publishes
the latest banzuke source it actually has.

This is not the ideal model boundary. The same abstract calendar entities also
exist in tracker scheduling: basho window, pre-basho period, banzuke
availability, current banzuke date, and previous completed basho. Long term,
that logic should be isolated in a shared calendar/source-availability model
instead of being inferred from file existence in one place and calendar state in
another.
