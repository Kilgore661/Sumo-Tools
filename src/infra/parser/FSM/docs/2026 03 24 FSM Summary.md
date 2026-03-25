## FSM module: what the parser depends on

The parser does **not** appear to depend on the FSM internals directly. From the parser’s point of view, the FSM layer is used as a **black-box validation/orchestration step** inside `parser2_body.py`, and the top-level parser only touches a small public surface.  

### Public API the parser uses

`parser2_body.py` imports these names from `.FSM`: `GruntFSM`, `OSK_FSM`, `YokozunaFSM`, and `FinalBanzukeEntry`. 

`parser2.py` imports `FinalBanzukeEntry` from `.FSM`, but in the file you shared it is only used in a type hint for `tidy_up(...)`. I do not see any direct construction of FSM objects in `parser2.py`; all FSM execution happens lower down in `parser2_body.py`. 

### Where FSM execution happens

The only place shown that actually instantiates and runs FSMs is `parse_and_validate_body(...)` in `parser2_body.py`. It builds an FSM class from `FSM_CONFIG`, constructs it with `date`, `sorted_margin_data`, and `dups` plus optional rank args, then calls `.run(fsm_body_stream)`. After that it reads results from `fsm.output` and, for Makuuchi only, advances `body_cursor` using `fsm.rows_processed`. 

So the parser-facing contract is not just `.run()`. The caller also expects these instance attributes to exist after running:

* `output`
* `rows_processed` (used for sequential Makuuchi slicing only) 

### Input shape expected by the FSM layer

`parse_and_validate_body(...)` feeds the FSM layer **adapted body rows**, not raw HTML and not raw `parse_body(...)` output. It first calls `parse_body(...)`, then `_extract_performance(...)`, then `adapt_body_data_for_fsm(...)`; the adapted result is what becomes `fsm_body_stream`. 

The FSM `run()` method expects a `List[BanzukeRow]`. `BanzukeRow` contains `east`, `west`, and `rank_string`; `east` and `west` are optional `RikishiData` objects with `id` and `shikona`.  

The constructor also expects a margin slice shaped as `List[Tuple[RikId, NewFoo]]` plus a duplicates dict. That data comes from `get_margin_data(date)` in the top-level parser flow.  

### Output shape expected by the parser

The FSM layer produces a mapping from `RikId` to `FinalBanzukeEntry`. `FinalBanzukeEntry` has exactly two fields:

* `chii: NewFoo`
* `shikona: Shikona` 

`parser2.py` then converts that validated mapping into the final basho state in `tidy_up(...)` by pulling `entry.chii` and `entry.shikona` from each `FinalBanzukeEntry`. It explicitly expects `entry.chii` to still be a `NewFoo`, not a downgraded legacy type. 

### Return value of `.run()`

`BaseFSM.run()` returns `self.output`, i.e. `Dict[RikId, FinalBanzukeEntry]`, but `parser2_body.py` does not use the return value. It relies on the side effect of `fsm.output` being populated.  

### Class split the parser assumes

`FSM_CONFIG` in `parser2_body.py` hardcodes the parser’s routing logic:

* `Y` → `YokozunaFSM`
* `O`, `S`, `K` → `OSK_FSM` with the rank letter passed as an extra positional arg
* `M`, `J`, `Ms`, `Sd`, `Jd`, `Jk` → `GruntFSM` 

So if you remove FSM, anything replacing it must preserve this routing behavior or `parse_and_validate_body(...)` will need to be rewritten.

### Behavioral assumptions baked into the parser

For Makuuchi, the parser processes one shared stream in rank-group order `['Y', 'O', 'S', 'K', 'M']`, and it expects each FSM to consume only the rows belonging to its rank group, exposing how many rows it consumed through `rows_processed`. 

For lower divisions, the parser passes the whole division stream to a single FSM and does not use `rows_processed`. 

Errors during FSM processing are caught broadly in `parser2_body.py`; on failure it prints an error and returns `None`. Then `parse_bashostate(...)` in `parser2.py` treats falsy validated data as failure and returns `'error'`.  

### Minimal replacement surface, if you need a stub

If your goal is just to upload or preserve the parser code without the FSM implementation, the minimum parser-visible surface appears to be:

* classes or placeholders named `GruntFSM`, `OSK_FSM`, `YokozunaFSM`

* a dataclass `FinalBanzukeEntry(chii, shikona)`

* each FSM class must be constructible with the same arguments used in `parser2_body.py`

* each instance must support:
  
  * `.run(fsm_body_stream)`
  * `.output`
  * `.rows_processed`  

Anything beyond that is internal to the FSM package as far as the parser files you shared are concerned.

### Most important parser-level dependency summary

`parser2.py` depends on `parser2_body.parse_and_validate_body(...)`; `parser2_body.py` is the only shown file that directly depends on the FSM package; and the final parser output only needs the validated `Dict[RikId, FinalBanzukeEntry]` that comes back out of that stage.  
