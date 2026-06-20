# Fixed Supported Regression Test Design

## Status

Regression test design.

The tests should prove that `fixed_supported` satisfies the requirements before
the production app path is switched over.

## Test Order

Run tests in this order:

1. policy and completion tests;
2. artifact contract tests;
3. known-failure regression tests;
4. downstream data-artifact tests;
5. app-plumbing regression tests.

This order keeps failures local. If the new model fails, find that before
changing `make_site2`.

## Policy And Completion Tests

Use small artificial chii sets where the expected answer is obvious.

Test the support collapse policy:

- annotations are removed;
- numbered sanyaku overflow maps to the canonical first-pair west chii;
- ordinary numbered ranks remain distinct east/west chii.

Test nearest-supported completion:

- direct chii keep their own rating;
- unsupported chii choose the nearest supported chii by ordinal;
- equal-distance ties choose the stronger, lower-ordinal chii;
- completion fails loudly if there are no supported chii.

These tests should not need live history data.

## Artifact Contract Tests

Build or load a master chii initial-rating map and assert:

- every simulation-required chii is present;
- every row has a valid chii and ordinal;
- every row has an initial rating;
- every row has `source_kind`;
- `direct` rows use themselves as source chii;
- `nearest_supported` rows identify a different supported source chii unless
  the same-chii case is explicitly allowed by the policy;
- no row has an unknown source kind;
- metadata records support rule, completion rule, base convention, and input
  history.

These checks should run against a small fixture if possible, and against the
real generated artifact when doing release validation.

## Known-Failure Regression Tests

The old failure mode was low-support lower-division chii acquiring
Yokozuna-level initial ratings.

Regression checks should assert:

- no unsupported lower-division chii has a near-3000 initial rating;
- the formerly suspicious tail chii are completed from supported sources;
- `Jk73w`-like chii do not receive independent direct estimates when below the
  support threshold;
- the resulting Highest Equelo table does not contain short-career
  lower-division artifacts near the top.

Where exact historical examples are used, prefer checks against generated
artifacts rather than slow end-to-end recomputation.

## Downstream Data-Artifact Tests

After the new model artifacts exist, test downstream producers without the
browser UI.

Checks:

- Highest Equelo has Hakuho first;
- only Hakuho is above 3000;
- known bad examples such as Kotonakamura and Mitsueumi are not top-table
  artifacts;
- Typical Equelo Values have the Yokozuna landmark approximately 2500 under the
  accepted base convention;
- downstream producers load production artifacts or APIs, not experiment
  paths.

These are regression tests for the data path. They are not meant to prove the
whole statistical model from first principles.

## App-Plumbing Regression Tests

Before final wiring, remove temporary `make_site2` experiment plumbing and run
the old app path. This establishes that removing temporary hooks did not damage
the existing app.

After final wiring, run the app data build again and confirm:

- Equelo-consuming pages use the production fixed-supported artifacts;
- no public producer refers to experiment run folders;
- table data still has the expected shape;
- no UI model changes were required solely to consume the new ratings.

Full site build/deploy may be slow and can remain a manual release-validation
step when necessary.

## Slow Tests

The fixed-point solver is slow. Routine tests should avoid rerunning the full
solver unless the solver or policy implementation changed.

Prefer:

- small artificial fixtures for policy logic;
- generated artifact contract checks;
- release-validation commands for full-history solver runs.

When a slow full-history run is required, record the exact command and output
location in the release notes or handoff log.
