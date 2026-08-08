# Incremental Bio Refresh Proposal

## Status

Proposal. No implementation is implied by this document.

## Problem

`src.infra.get_bios` has an incremental raw-page downloader but a full-catalogue
parser.

The downloader compares the RikIds represented in `History` with the cached
`Rikishi.aspx` files and downloads only missing pages. The parser then reads
every cached page, rebuilds every parsed record, and rewrites
`rikishi_bios.json`. There are currently more than 9,000 cached pages.

This was tolerable when bio refresh was treated as an occasional manual build
step. It is not a suitable normal update path now that a published banzuke may
be replaced after its initial capture. A replacement can introduce a RikId
which was absent from the original page. Rebuilding History then makes that
RikId part of the public data domain immediately, but `make_site2` cannot build
until the corresponding bio has been downloaded and parsed.

The July 2026 Sawada case demonstrated the complete failure mode:

1. the corrected banzuke introduced RikId 13011 into History;
2. the Live Store correctly published the rebuilt History;
3. the raw bio cache and `rikishi_bios.json` still lacked 13011;
4. `FullShikonaStore.from_sources()` raised `KeyError: 13011`;
5. the failure occurred only after `make_site2` had requested the SFTP
   password and opened a deployment connection.

If current-banzuke pages are checked or refreshed regularly, most updates will
not introduce a new rikishi. The correct bio work for those updates is zero.
When one new rikishi appears, the correct work is to download and parse one
page, not to parse the entire catalogue.

## Current Data Flow

```text
Live History
    |
    v
src.infra.get_bios
    |  downloads only missing RikIds
    v
files/output/infra/get_bios/rikishi/{rikid:05d}.html
    |
    v
src.infra.get_bios.parser
    |  currently reparses every HTML file
    +--> files/output/infra/get_bios/rikishi_bios.json
    `--> files/output/infra/get_bios/rikishi_bio_missing_fields.csv
```

`FullShikonaStore` consumes `rikishi_bios.json` and requires a parsed bio for
every RikId represented in the selected History.

## Goals

The change should provide the following behaviour:

1. A routine refresh parses only new or changed raw bio pages.
2. A refresh with no new or changed bio pages is a fast no-op.
3. A clean build can still parse the complete raw catalogue.
4. A parser-rule change can explicitly invalidate and rebuild all records.
5. A manually replaced raw bio page can be reparsed deliberately.
6. Failed parsing cannot leave the aggregate JSON partially updated.
7. Pending work survives process failure and can be retried.
8. History, parsed bios, public shikona and site publication form an explicit
   dependency chain with a useful error at the first broken boundary.
9. Network access remains an explicit update operation; invoking a site build
   should not silently download data.

## Non-Goals

This proposal does not redesign the `RikishiBio` model, change public-shikona
resolution policy, or decide how often existing SumoDB bio pages should be
refetched. It supplies the mechanism required to process an existing page
again if a future refresh policy replaces it.

It also does not require splitting `rikishi_bios.json` into thousands of
public files. The aggregate JSON is only several megabytes; rewriting it is
cheap compared with reparsing every career table.

## Proposed Design

### 1. Make one-page parsing a pure operation

Refactor the body of `parser.main()` into a function with no output-file side
effects:

```python
def parse_bio_file(path: Path) -> ParsedBioResult:
    ...
```

`ParsedBioResult` should contain everything currently derived while processing
one page:

```text
rikid
persisted bio record
missing-field row
unexpected headings
diagnostic messages
```

Both incremental and full-catalogue modes must call this same function. There
must not be a separate reduced parser for incremental updates.

### 2. Add persistent parse state

Introduce an internal state file:

```text
files/output/infra/get_bios/rikishi_bio_parse_state.json
```

For each successfully parsed RikId it should record at least:

```json
{
  "13011": {
    "source_size": 12345,
    "source_mtime_ns": 1786190000000000000,
    "source_sha256": "...",
    "parser_version": 1
  }
}
```

Directory enumeration and file metadata checks are acceptable on every run;
parsing 9,000 career tables is not. Size and modification time identify cheap
candidates. A hash may be calculated only for a new or apparently changed
candidate, or while the downloader already has the response bytes.

The parser version is an explicit invalidation boundary. A change which can
alter persisted record semantics must increment `BIO_PARSER_VERSION`.
Incremental mode must not silently produce a JSON file containing records made
under incompatible parser versions. On a version mismatch it should stop with
a message directing the operator to `--full`.

### 3. Keep a durable dirty-RikId ledger

The downloader should atomically maintain:

```text
files/output/infra/get_bios/pending_parse_ids.json
```

Whenever it creates or replaces a valid raw page, it adds that RikId to the
pending set. The id is removed only after the incremental parser has
successfully committed the corresponding aggregate record and parse state.

This ledger provides reliable hand-off between two separate commands and
survives a failed parser run. Incremental discovery should use the union of:

* RikIds in the pending ledger;
* raw HTML RikIds absent from `rikishi_bios.json`;
* raw files whose recorded size or modification time changed;
* RikIds supplied explicitly on the command line.

The parser should report where each selected id came from. A zero-sized union
is a successful no-op.

### 4. Add explicit parser modes

The proposed command contract is:

```powershell
# Normal operation. This should become the default.
py -m src.infra.get_bios.parser
py -m src.infra.get_bios.parser --incremental

# Repair or deliberately refresh particular records.
py -m src.infra.get_bios.parser --rikid 13011
py -m src.infra.get_bios.parser --rikid 13011 --rikid 13012

# Clean build or rebuild after a parser-version change.
py -m src.infra.get_bios.parser --full
```

If neither aggregate output nor parse state exists, incremental mode should
promote itself to a full initial build with a clear message. `--full` should
remain available even when the current aggregate is healthy.

An explicit RikId must fail clearly if its raw HTML file is absent. It must not
silently remove an existing aggregate record.

### 5. Merge results and publish atomically

Incremental mode should:

1. load `rikishi_bios.json` as a mapping keyed by RikId;
2. load the existing missing-fields CSV as a mapping keyed by RikId;
3. parse all selected raw pages into memory;
4. stop without changing published outputs if any selected page fails;
5. replace the selected records in both mappings;
6. write JSON, CSV and parse-state candidates to adjacent temporary files;
7. atomically replace the published files;
8. remove successfully committed RikIds from the dirty ledger.

The monolithic JSON may still be rewritten on each successful incremental
update. The important optimisation is avoiding 9,000 HTML parses.

Deletion must be explicit. A missing raw file should be reported, but should
not automatically delete a parsed record. An optional future `--prune` mode
can define deliberate deletion semantics if they are ever required.

### 6. Make diagnostics incrementally coherent

The existing missing-fields CSV is a catalogue-wide artifact and therefore
must be merged per RikId rather than regenerated only from the selected pages.

Unexpected headings and parser diagnostics are currently console output. The
first implementation may print diagnostics for the pages processed in that
run. A preferable follow-up is a per-RikId diagnostic JSON file so repaired
records can replace their own findings while untouched records retain theirs.
This is useful but should not block the core incremental path.

### 7. Separate update orchestration from site building

The normal update chain should be explicit:

```text
refresh raw banzuke/results
    -> build candidate History
    -> determine bio closure for candidate History
    -> download missing raw bios
    -> incrementally parse new/changed bios
    -> validate FullShikonaStore coverage
    -> publish/refresh the coherent History generation
    -> run downstream producers
    -> build local site
    -> connect and deploy
```

The strongest tracker design is to validate bio closure against the candidate
History before publishing that History to the Live Store. To support this,
the bio downloader should accept a supplied `History` or `--history-zip`
instead of requiring the currently published Live Store. This also resolves
the existing boundary issue recorded in the SDDA review.

If automatic bio download is not initially integrated into the tracker, the
intermediate safe design is:

* tracker publishes the new History;
* `_boot.ps1` runs the missing-page downloader and incremental parser before
  any producer;
* `make_site2` performs a local completeness preflight and gives the exact
  repair commands if a History RikId is absent from BioStore.

`make_site2` must perform local build validation before asking for an SFTP
password or opening a deployment connection. It should never discover a
missing bio only after establishing the remote connection.

### 8. Improve boundary errors

`FullShikonaStore.from_sources()` should calculate missing BioStore RikIds
before indexing individual records. Instead of a raw `KeyError`, it should
raise a domain error such as:

```text
BioStore is missing 1 History RikId: 13011.
Run:
    py -m src.infra.get_bios
    py -m src.infra.get_bios.parser
```

This validation is still required after incremental parsing is implemented;
incrementality must not weaken completeness checks.

## Failure Semantics

| Failure | Required result |
| --- | --- |
| No new or changed pages | Success with no aggregate rewrite |
| Download failure | Raw cache and parsed aggregate remain at their previous coherent state; RikId remains pending or missing |
| One selected page fails to parse | No selected aggregate updates are committed; dirty ids remain pending |
| Aggregate temporary write fails | Existing published aggregate remains intact |
| Parser-version mismatch | Incremental run stops and requests `--full` |
| History requires a bio with no raw page | Coherence validation fails before producer execution or deployment connection |
| Process terminates after raw-page write | Dirty ledger causes the page to be retried on the next parser run |

## Tests

The implementation should include focused tests for the following cases:

1. **No-op:** existing aggregate and unchanged raw cache cause zero pages to be
   parsed and no outputs to be rewritten.
2. **New RikId:** adding `13011.html` parses one page, adds one JSON and CSV
   record, records parse state, and clears the dirty id.
3. **Changed RikId:** replacing one existing raw page reparses and replaces only
   that logical record.
4. **Explicit repair:** `--rikid 13011` reparses that page regardless of state.
5. **Failure atomicity:** one bad selected page leaves JSON, CSV, state and
   pending ids coherent.
6. **Version invalidation:** incremental mode refuses mixed parser versions and
   `--full` successfully establishes the new version.
7. **Equivalence:** a full rebuild and an incremental build from the same raw
   page set produce semantically identical `rikishi_bios.json` and
   missing-fields data.
8. **Completeness:** a History RikId absent from BioStore produces a clear
   preflight error listing the missing id.
9. **Build ordering:** local preflight failure occurs before any SFTP password
   prompt or connection attempt.

Tests should inject temporary input and output roots. They must not read or
rewrite the real 9,000-page cache.

## Rollout

### Phase 1: Parser boundary and manual incremental mode

* Extract `parse_bio_file()` and result types.
* Add `--rikid`, `--incremental` and `--full`.
* Implement merge and atomic aggregate writes.
* Add parse state and tests.

This phase immediately reduces the Sawada repair case from a full parse to one
page.

### Phase 2: Downloader hand-off

* Make raw-page writes atomic.
* Add the durable dirty-RikId ledger.
* Record every created or replaced page as pending.
* Add a supplied-History or `--history-zip` boundary.

### Phase 3: Pipeline coherence

* Put downloader plus incremental parser into the normal update/bootstrap
  chain.
* Add BioStore/FullShikonaStore completeness preflight.
* Move site build and validation ahead of SFTP connection.
* Decide whether the tracker publishes History only after bio closure or uses
  an explicitly reported intermediate state.

### Phase 4: Optional diagnostics and refresh policy

* Persist per-RikId diagnostics if catalogue-wide diagnostic continuity is
  valuable.
* Define when existing raw bio pages should be checked for updates.
* Use the same incremental mechanism for any pages replaced by that policy.

## Acceptance Criteria

The proposal is implemented when all of the following are true:

* adding one new History RikId causes at most one bio HTML page to be parsed;
* an ordinary banzuke/results refresh with no new RikIds performs no bio parse;
* full rebuild remains available and produces the same aggregate contract;
* interrupted updates cannot corrupt the published bio aggregate;
* `make_site2` cannot reach SFTP connection with an incomplete History/BioStore
  domain;
* the normal operational documentation states which command performs an
  incremental refresh and when `--full` is required.

