Here is a clean **mini-spec for `update_cycle`**, written as design rather than code, and aligned with the proposal in *Adding Analysis* 

## `update_cycle` mini-spec

### Purpose

`update_cycle` is the orchestration step that turns the tracker’s high-level policy into one concrete maintenance attempt.

It is responsible for taking the required source-record set for the current moment, executing the required maintenance stages in the correct order, and returning a single cycle verdict to the outer tracker loop.

It does not decide *when* to run. It decides only *what this cycle achieved*.

### Role in the system

The outer tracker loop is responsible for:

* deciding when a cycle should run
* computing the required source-record set
* passing that set into `update_cycle`
* interpreting the returned verdict

`update_cycle` is responsible for:

* retrieval
* conditional canonical-history rebuild
* conditional canonical publication
* conditional cache refresh
* conditional analysis
* verification of required derived artifacts
* returning one overall outcome

So the outer tracker remains policy-oriented, while `update_cycle` remains pipeline-oriented.

---

## Inputs

`update_cycle` requires:

### 1. Required source-record set

A complete description of the source records that must exist locally for the current cycle.

This comes from the planner.

### 2. Required derived-artifact set

A complete description of the derived analysis artifacts that are mandatory for tracker success in the current cycle.

This may be fixed configuration or a computed set, but for `update_cycle` it should appear simply as an input requirement.

### 3. Access to the maintenance stages

`update_cycle` depends on the following stage interfaces existing conceptually:

* retrieval
* canonical-history rebuild
* canonical publication
* cache lifecycle control
* analysis execution
* derived-artifact verification

It does not need to know their internals.

---

## Outputs

`update_cycle` returns exactly one overall cycle result.

At minimum, the result space should distinguish:

* **SUCCESS**
* **FAILURE**
* **NO_NEW_DATA**

If you later want richer internal failure categories such as retrieval failure, publication failure, cache failure, or analysis failure, those can exist too, but the essential contract is that `update_cycle` returns one verdict that the tracker can interpret.

---

## Retrieval contract

The first stage is retrieval.

Retrieval must return one of three outcomes:

### Retrieval failure

Not all required source files are present locally after the retrieval attempt.

### Retrieval success unchanged

All required source files are present locally, and no new files were downloaded during the retrieval attempt.

### Retrieval success changed

All required source files are present locally, and one or more files were downloaded during the retrieval attempt.

This retrieval outcome is the main control signal for the rest of the cycle.

---

## Cache precondition

Analysis depends on a running cache.

Therefore, before any analysis stage runs, `update_cycle` must ensure:

> there is a running cache corresponding to the current canonical history.

How this is achieved depends on the retrieval outcome.

---

## Branching rules

### Case 1: retrieval failure

If retrieval fails, the cycle fails immediately.

Reason:

* source completeness has not been achieved
* no downstream published artifact can be trusted as current for this cycle

So in this branch:

* do not rebuild canonical history
* do not publish canonical zip
* do not refresh cache
* do not run analysis
* return **FAILURE**

---

### Case 2: retrieval success unchanged

If retrieval succeeds unchanged, then the managed source dataset is treated as unchanged.

This implies:

* canonical-history rebuild is not required
* canonical publication is not required
* cache restart is not required

However, required downstream artifacts must still be satisfied.

So this branch works as follows:

#### Step 1: ensure cache is running

If no cache is running, start it from the current canonical history.

If a cache is already running, leave it alone.

#### Step 2: inspect required derived artifacts

Check whether all required derived artifacts already exist and are usable.

#### Step 3: conditional analysis

* If all required derived artifacts already exist and are usable, no analysis run is required.
* If one or more required derived artifacts are missing or unusable, run analysis to generate them.

#### Step 4: verify derived artifacts

After any analysis run, verify that all required derived artifacts now exist and are usable.

#### Outcome

* If cache start fails, return **FAILURE**
* If analysis was required and fails, return **FAILURE**
* If derived-artifact verification fails, return **FAILURE**
* If no downstream action was required because cache and artifacts were already satisfactory, return **NO_NEW_DATA**
* If downstream action was required and completed successfully, return **SUCCESS** or **NO_NEW_DATA**, depending on how you want to classify “unchanged inputs but regenerated missing outputs”

My recommendation is:

* use **NO_NEW_DATA** only when nothing needed doing downstream
* use **SUCCESS** when the cycle had to repair or create required downstream artifacts even though source data was unchanged

That preserves the meaning of `NO_NEW_DATA` as a true no-op success.

---

### Case 3: retrieval success changed

If retrieval succeeds changed, then the managed source dataset has changed this cycle.

This implies that downstream published artifacts must be refreshed.

This branch works as follows:

#### Step 1: rebuild canonical history

Rebuild canonical history from the current managed source files.

If rebuild fails, return **FAILURE**.

#### Step 2: publish canonical history

Publish the rebuilt canonical history as the canonical serialized artifact.

If publication fails, return **FAILURE**.

#### Step 3: refresh cache

If a cache is already running, stop it.

Then start a new cache from the newly published canonical history.

If cache refresh fails, return **FAILURE**.

#### Step 4: run analysis

Run the required analysis jobs against the refreshed cache.

If analysis fails, return **FAILURE**.

#### Step 5: verify derived artifacts

Verify that all required derived artifacts now exist and are usable.

If verification fails, return **FAILURE**.

#### Outcome

If all these stages succeed, return **SUCCESS**.

---

## Derived-artifact verification

This is a mandatory final step whenever required derived artifacts are expected to exist after the cycle.

Verification should answer only the question:

> do all required derived artifacts now exist and are they usable?

This should remain separate from the analysis step itself.

That separation is useful because:

* analysis may claim success but fail to emit all required outputs
* the tracker’s contract is about artifacts, not merely process exit status

So analysis success alone is not enough; artifact verification is still required.

---

## `NO_NEW_DATA` semantics

`NO_NEW_DATA` should be used narrowly.

It should mean:

* retrieval succeeded unchanged
* cache was already satisfactory or did not need repair beyond being present
* all required derived artifacts already existed and were usable
* no rebuild, refresh, or analysis work was needed

That makes `NO_NEW_DATA` a very clean result:

> nothing upstream changed, and nothing downstream needed repair

---

## `SUCCESS` semantics

`SUCCESS` should mean:

* after this cycle, all required maintained artifacts are now current and usable
* and some real maintenance or repair work may have been performed to make that true

This includes both:

* changed-source cycles that rebuilt and republished everything
* unchanged-source cycles that had to restore missing downstream artifacts

---

## `FAILURE` semantics

`FAILURE` should mean:

* after this cycle, at least one required maintained artifact remains absent, stale, or unusable

This includes failure at any mandatory stage.

---

## Invariants

After a **successful** cycle, the following must hold:

1. all required source files exist locally
2. canonical history is available for the current source dataset
3. cache is running against that canonical history
4. all required derived artifacts exist and are usable

After a **NO_NEW_DATA** cycle, the same invariants hold, with the extra fact that no maintenance work was required.

---

## Non-responsibilities

`update_cycle` does not:

* decide when a cycle should run
* decide what the current active-window policy is
* define parser internals
* define zip internals
* define cache implementation internals
* define analysis internals

It only coordinates them.

---

## Recommended shape of the result space

Even if the outer tracker only needs broad verdicts, internally I think the cleanest result model is:

* `SUCCESS`
* `NO_NEW_DATA`
* `RETRIEVAL_FAILED`
* `REBUILD_FAILED`
* `PUBLISH_FAILED`
* `CACHE_FAILED`
* `ANALYSIS_FAILED`
* `DERIVED_ARTIFACTS_MISSING`

Then `tracker.py` can collapse these into broader policy reactions if it wants.

That keeps the implementation debuggable without weakening the high-level model.

---

## Short operational summary

`update_cycle` should behave like this:

* retrieve required source files
* if retrieval failed: fail
* if retrieval changed source data:

  * rebuild canonical history
  * publish canonical artifact
  * refresh cache
  * run analysis
  * verify derived artifacts
* if retrieval left source data unchanged:

  * ensure cache exists
  * run analysis only if required derived artifacts are missing
  * verify derived artifacts if analysis ran
* return one overall cycle result

That is the design point where the code really does become almost mechanical.
