# Full Shikona Rollout Plan

## Status

Requirements and design plan.

This document records the agreed plan for moving public shikona
disambiguation from investigation into production use. It is not an
implementation record.

The immediate focus is the `3.3 Rikishi History` dropdown in `make_site2`.
The wider requirement is that any public-facing web page that names a rikishi
by shikona should be able to use a disambiguated public label when the context
requires it.

## Vocabulary

### History shikona

The canonical one-word shikona stored in `History`.

This is the public "surname" shikona. When a rikishi has a two-word recorded
name, the second word behaves like a given name.

History shikona owns the public handle. The latest holder of History shikona
`X` gets to be public `X`, even when `get_bios` knows a longer maximal shikona
for that rikishi.

### Maximal shikona

The one- or two-word latest shikona parsed by `get_bios` / `BioStore`.

This is used as a preferred disambiguating candidate for earlier holders of a
non-unique History shikona. It is not the default public label for every
rikishi.

### Full shikona

The catalogue-derived, public, disambiguated label for a rikishi.

The full shikona rule is:

```text
Group by History shikona H.

If the rikishi is the latest holder of H:
    full shikona = H

If the rikishi is an earlier holder of H and has maximal shikona M != H:
    candidate full shikona = M

If the rikishi is an earlier holder of H and has no distinct maximal shikona:
    candidate full shikona = H

If an earlier-holder candidate is H, collides with another candidate, or
collides with any latest-holder bare History shikona:
    append Intai year: candidate (YYYY)

If candidate (YYYY) is still not unique:
    append Intai year/month: candidate (YYYY/MM)
```

`YYYY` and `YYYY/MM` are derived from the rikishi's `Intai` value.

The latest-holder rule is settled: the most recent holder of `X` gets to be
public `X`; earlier `X` holders carry the disambiguation burden.

### Identity

Rikishi identity is `RikId`.

Shikona text is display and search text only. Public UI selection, plotting,
linking and state restoration must not identify rikishi by shikona.

## Non-Goals

This rollout does not:

1. Move disambiguated shikona into `History`.
2. Use `rikid` as public disambiguation text.
3. Make maximal shikona the default public label for every rikishi.
4. Re-open the general choice of owner label.
5. Treat the old probe implementation as production design.

The probe is evidence. The production implementation should express the
settled contract directly.

## Phase 1: Current Dropdown Contract

Find exactly where the `3.3 Rikishi History` dropdown options are populated.

Trace the label source backwards:

```text
runtime dropdown
  -> generated Career Comparisons data
  -> producer transformation
  -> public shikona resolver or History shikona source
```

Determine whether the current list is:

1. A straight lookup from `History` shikona.
2. A consumer of `make_public_shikona(...)`.
3. A consumer of `trajectory_master.json`.
4. A failed local disambiguation attempt in the runtime.
5. Some combination of the above.

Confirm the identity contract:

```text
selected rikishi id      RikId
URL selected state       RikId
chart trace data         RikId
display/search labels    shikona text
```

Any use of shikona text as identity is a model bug.

Describe the current failure precisely:

1. Repeated indistinguishable dropdown labels such as multiple `Abe` entries.
2. Any label-keyed maps that collapse duplicate labels.
3. Which public UI surfaces consume the same label:
   dropdown candidates, selected chips, chart legend, caption, hover text and
   URL restoration.

## Phase 2: Production Full-Shikona Resolver

Promote the decided Intai-based rule into a production resolver.

The core transformation is:

```text
History + BioStore + Rikishi.aspx shikona-search rows -> FullShikonaStore
```

`FullShikonaStore` is a deliberate publication-time entity parallel to
`History`. It is a hack in the useful sense: it isolates public identity data
that arguably belongs in the History-building pipeline, without changing
`History` during this rollout.

The resolver owns only the computation of full shikona. It does not decide
whether a public context displays History shikona or full shikona.

Required resolver behaviour:

1. Use `History` to find each represented rikishi's History shikona.
2. Group represented rikishi by History shikona.
3. Use `History` to choose the latest holder of each non-unique History
   shikona.
4. Give the latest holder the bare History shikona.
5. For earlier holders, use distinct maximal shikona from `BioStore` where
   that produces an unambiguous public label.
6. Add `Intai` year to earlier-holder candidates that are still ambiguous, that
   collapse to the bare History shikona, or that collide with another
   latest-holder bare History shikona.
7. Add `Intai` month when year is not enough.
8. Fail loudly if an earlier holder needs an `Intai` suffix and no usable
   `Intai` value exists.
9. Fail loudly if the produced full shikona labels are not unique where the
   calling contract requires uniqueness.

This keeps the offensive-programming stance: missing or contradictory catalogue
data is not papered over with a public `rikid` fallback.

## Phase 3: Rikishi History Dropdown

Replace the dropdown's current public label source with full shikona labels.

The first implementation point is the Career Comparisons producer:

```text
src/products/make_site2/perf_chart/build.py
```

It writes full shikona labels into the existing `trajectory_master.json`
structure, so the JavaScript dropdown can keep its current data flow.

The dropdown should:

1. Search and display full shikona labels.
2. Keep `RikId` as the selected value.
3. Preserve URL state as rikishi ids.
4. Avoid label-keyed selection maps where duplicate labels can overwrite each
   other.
5. Show distinct labels when a user types a broad prefix such as `a`, including
   multiple different `Abe` entries.

Expected result:

```text
typing "a" in 3.3 Rikishi History shows distinct Abe labels
selecting one Abe selects the intended RikId
selected chips, chart traces and URL state agree
```

The most recent holder of a reused History shikona may still appear as the bare
name. Disambiguation is for earlier holders.

## Phase 4: Public-Facing Shikona Audit

After the dropdown works, audit every public-facing web page occurrence of
rikishi shikona.

The audit should include:

1. Generated JSON fields.
2. Generated CSV fields.
3. Table columns.
4. Chart legends.
5. Chart captions.
6. Hover text.
7. Selected chips and controls.
8. Public links.
9. Notes and gloss text where a shikona appears as a rikishi label.

Classify each occurrence:

```text
must use full shikona
may use History shikona
should expose full shikona as optional/search/help text
should remain unchanged because it is source text, diagnostic text or internal output
```

The desired product shape is that all public shikona displays can opt into full
shikona without each page inventing its own rule.

## Phase 5: Shared Public Label Contract

Introduce a shared producer-facing label contract if the audit shows repeated
needs.

The likely model is:

```text
rikishi_id
history_shikona
full_shikona
graph_shikona, if needed for legacy graph links
search aliases, if needed by selectors
```

Contexts choose which public label to display:

```text
selection/search context       full shikona
compact table context          History shikona or full shikona by page contract
legend/caption context         page-specific, but should be able to choose full shikona
hover/help context             often full shikona
legacy graph-link context      graph shikona if required
```

The context choice is not the responsibility of the full-shikona resolver.

## Phase 6: Freshness and Maintenance

Define how full-shikona labels stay current.

The freshness requirement has two parts:

1. Latest-holder freshness.
2. Intai-suffix/catalogue freshness.

Latest-holder freshness is active now. When new History or bio data changes
which rikishi is the latest holder of `X`, the bare `X` label must move to that
rikishi and earlier holders must be recomputed.

Intai-suffix freshness follows from the production rule. If new or repaired
`get_bios` data changes an earlier holder's `Intai`, the full shikona label may
change.

The likely maintenance design is to hook the disambiguation inputs into the
tracker or publication refresh path:

```text
tracker/history refresh
  -> get_bios cache refresh where needed
  -> parsed BioStore refresh
  -> full-shikona resolver
  -> collision check
  -> publication
```

Publication should fail loudly if the resolver cannot produce the labels
required by public selectors or other full-shikona contexts.

Fresh raw source files matter. A stale or corrupt `current standings` cache can
poison History shikona and therefore the owner calculation. This was observed
with a bad `1964/01`-era source cache that incorrectly made `RikId(11446)` look
like the latest History holder of `Tonegamine`. Rebuilding `History` from fresh
source files restored agreement:

```text
11184 -> Tonegamine
11446 -> Sadonohana
```

The rollout should therefore treat source-cache freshness as part of the
full-shikona maintenance story, not merely as a tracker concern.

## Verified Dropdown Check

On a fresh source-cache rebuild in `C:\Users\kilgo\Sumo-Tools`, the corrected
`FullShikonaStore` policy produced unique labels for the Career Comparisons
artifact:

```text
labels 9064
unique 9064
duplicates 0
```

Selected known cases:

```text
11184 Tonegamine
11446 Sadonohana
1123 Hakuho
8206 Hakuho (1975)
9048 Abe (1973)
9111 Abe
2103 Takahashi Hirokazu
7237 Takahashi Shinichi
```

## Documentation and Commit Plan

The work should be committed at conceptual boundaries:

1. Dropdown contract investigation and production resolver specification.
2. Full-shikona resolver implementation and tests.
3. Rikishi History dropdown integration and browser verification.
4. Public-facing shikona audit and follow-up page integrations.
5. Freshness/tracker design and implementation.

Relevant documentation should distinguish:

1. History shikona.
2. Full shikona.
3. Latest-holder rule.
4. Intai suffix rule.
5. Resolver ownership.
6. Page/context choice of which label to display.
7. Freshness requirements.
