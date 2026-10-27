# Proposal: controlled P1 versus P1-WL site-bundle comparison

## 1. Purpose

Test the publication consequences of replacing the fixed Elo-89 entrant
prior. The experiment begins after model selection: P1-WL is a constant input,
not a quantity to be fitted, tuned or defended again.

The comparison must exercise the actual `site89` analytical production path,
not reconstruct a selection of page outputs in validation-only code.

## 2. Production path under test

The relevant path is:

```text
produce_site89_bundle
    -> produce_elo89
        -> load paired prior
        -> replay_elo89
        -> write Elo-89 artifacts
    -> load Elo89Artifacts
    -> rating-dependent site89 producers
    -> site-data bundle manifest
```

`make_site89` subsequently validates and copies that site-data bundle into the
static site. It does not recalculate ratings. The primary experimental
boundary is therefore the complete bundle produced by
`src.analysis.site89.producer.produce_site89_bundle`.

## 3. Controlled inputs

Hold constant between the two builds:

- one post-1988 `History`, beginning at `1989/01`;
- the complete ordered basho and result domain;
- q=400 and `files/input/elo_fide.json`;
- the Elo-89 lifecycle and population-normalisation rules;
- future torikumi input, if present;
- Banzuke Changes structural inputs;
- rikishi bio and shikona sources;
- producer code and runtime environment; and
- every output root except the two experiment directories.

Record absolute paths, SHA-256 values where the input is file-backed, the
selected-History fingerprint, represented date bounds, and the relevant Git
commit or dirty-worktree state.

The sole controlled difference is:

| Run | Prior |
|---|---|
| Baseline | published canonical P1 |
| Candidate | accepted epsilon-10 P1-WL |

Do not overwrite `files/output/analysis/equelo_bkp1` and do not deploy either
bundle.

## 4. Minimal production-code change

`produce_elo89()` already accepts `prior_path`, but
`produce_site89_bundle()` does not expose it and therefore always uses the
canonical default.

Add an explicit `prior_path` parameter to the site-bundle producer and pass it
unchanged to `produce_elo89()`. Supply a validation entry point which requires
explicit baseline, candidate and output paths. Ordinary production must retain
its canonical default; routine site builds must not refit P1 or silently choose
a validation candidate.

Add focused tests proving that:

- an explicit prior reaches `produce_elo89()`;
- the default remains the canonical production prior;
- the selected prior identity is recorded in the Elo-89 manifest; and
- separate output roots cannot overwrite one another or the canonical input.

## 5. Expected dependency classes

### 5.1 Direct prior consumers

These outputs use the copied paired prior itself and should change where the
selected prior values differ:

- `typical_rating_values`;
- the modelled trace in `win_probability_by_standing`; and
- prior fallback values in `banzuke_changes` when no preceding rating exists.

The observed win-probability trace does not depend on the prior and should be
unchanged.

### 5.2 Replay-derived consumers

These consume ratings or probabilities produced by the Elo-89 replay and may
change numerically or in rating-based order:

- `torikumi`;
- `basho_results_browser`;
- `career_comparisons`;
- `rating_changes`;
- `highest_rating`; and
- the ordinary rating fields in `banzuke_changes`.

### 5.3 Model-independent consumers

All other bundle artifacts are expected to be byte-identical, subject only to
any already-known volatile metadata. If timestamps or path identities prevent
byte equality, compare parsed semantic content and document why the bytes
differ.

No artifact may be classified from its name alone. The implementation trace
and the observed comparison must agree.

## 6. Comparison procedure

### Phase A: freeze and identify inputs

1. Load one explicit History source and select the Elo-89 interval.
2. Resolve every ancillary input before either build.
3. Write a run manifest before producing outputs.
4. Refuse to proceed if either output directory already exists.

### Phase B: build both bundles

1. Produce the baseline bundle with published P1.
2. Produce the candidate bundle with accepted P1-WL.
3. Validate both using the normal bundle validator.
4. Confirm identical artifact ids, declared paths and schemas.

The builds may run sequentially to avoid hidden competition for shared inputs.
They must not refresh downloads or mutate common analytical inputs between
runs.

### Phase C: compare the Elo-89 source artifacts

Confirm the already-observed causal path inside the actual production build:

- identical bout identities and order;
- identical raw, rated, fusen and draw counts;
- expected copied-prior differences;
- expected basho-start, day-end and basho-end rating differences;
- expected forecast-probability differences; and
- no change to q, K configuration, date bounds or lifecycle policy.

This is a production-path consistency check, not another predictive contest.

### Phase D: compare every site artifact

For each declared artifact and file, record:

- classification: direct prior, replay-derived or model-independent;
- byte-identical status;
- schema and row-count equality;
- identity-key equality;
- changed field names;
- numerical difference summary for rating/probability fields;
- ordering changes; and
- largest individual differences with enough identity fields to inspect them.

Identity keys should use the artifact's natural domain, for example
date/day/rikishi/bout or rank-pair, rather than row number. A reordered file
must not be mistaken for inserted or deleted evidence.

### Phase E: static-site and visual check

Assemble a candidate static site from the candidate bundle without deployment.
Inspect at least:

- Typical Elo-89 ratings;
- win probability by standing;
- current/future torikumi;
- Banzuke Changes;
- basho results;
- career comparisons;
- rating changes; and
- highest ratings.

Check rendering, labels, rounding, sorting, links, empty values and chart
scales. Record screenshots or a concise inspection log where a numerical diff
is not sufficient.

## 7. Invariants and acceptance criteria

The candidate passes this tranche if:

1. both normal production bundles build and validate successfully;
2. the only changed model input is the prior;
3. bout, basho and rikishi evidence domains are unchanged;
4. model-independent semantic outputs are unchanged;
5. every direct-prior change is explained by the P1-to-P1-WL table change;
6. every other changed rating field is downstream of the Elo-89 replay;
7. no schema, link, missing-value or rendering regression is found;
8. the observed scale and location of rating changes agree with the accepted
   exact-replay evaluation; and
9. the final report lists all files which would be replaced by promotion.

An unexplained change is a failed comparison, even if visually small. A large
but correctly propagated numerical change is evidence to assess, not by
itself a build failure.

## 8. Outputs to retain

Persist within this tranche:

- the experiment manifest;
- baseline and candidate bundle manifests;
- an artifact/file comparison CSV;
- per-artifact numerical summaries;
- selected largest-difference tables;
- automated-test output or an exact test command and result;
- the visual inspection record; and
- final findings and a promotion recommendation.

Large generated bundles need not automatically be committed if repository
size makes that inappropriate, but their identities and reproducible commands
must be retained. Any omission of raw output must be an explicit decision,
not an accidental loss of provenance.

## 9. Non-goals

This tranche will not:

- revisit the derivation, epsilon or predictive merit of P1-WL;
- alter the Elo-89 replay equations;
- decide whether returning rikishi retain or regain ratings;
- decide the treatment of off-banzuke participants;
- regenerate P1 automatically during ordinary site builds;
- overwrite the canonical P1 artifact;
- deploy a public site; or
- revise the expert account before the matter is adopted.

The lifecycle and off-banzuke rules are held fixed so that this comparison
isolates the already accepted kimarite correction.

## 10. Decision after the comparison

If the candidate passes, the next action is a separate, explicit promotion:

1. install P1-WL as the canonical fixed prior with its retained manifest;
2. regenerate Elo-89 and all rating-dependent publication artifacts;
3. run the ordinary site build without deployment;
4. repeat focused checks against the promoted output; and
5. deploy only after explicit approval.

If it fails, retain both bundles and the comparison report, correct the
publication-path defect, and rerun the same controlled experiment. Do not
respond by tuning or refitting P1-WL inside this tranche.
