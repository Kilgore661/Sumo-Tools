Yes — by “display identity” I meant exactly **shikona** and **chii**.

Here is a proposal text you can paste into your notes.

# Presentation Layer Proposal

## 1. Purpose

The standings capability shall support a presentation-oriented layer whose initial form is an HTML page showing **multiple-basho standings** for a selected basho-window length.

This layer is intended to present a simple, accessible view of the standings for users who want the obvious headline numbers rather than the fuller analytical output.

The page is conceptually driven by the output of the multiple-basho standings process, currently exposed through the `multiple_basho_main` entrypoint and its derived multiple-basho view output.  

---

## 2. Scope

The initial presentation layer concerns the case:

```text
py -m src.analysis.standings.multiple_basho_main --num-basho N
```

with backwards-looking semantics relative to the current default anchor date unless another anchor date is explicitly selected upstream.

The presentation layer is not responsible for running the standings computation on demand. Instead, standings data shall be computed in advance and made available to the page as pre-generated artefacts.

This keeps the presentation layer separate from standings calculation, which is already structured as a calculation/view/reporting pipeline.   

---

## 3. User Controls

The page shall provide a **num-basho** selector.

Initial supported values shall be:

* 1
* 2
* 3
* 4
* 5
* 6 (default)
* 12
* 18
* 24
* 36
* 60

The page shall also provide a **division** selector.

Initial supported values shall be:

* All
* Makuuchi (default)
* Juryo
* Makushita
* Sandanme
* Jonidan
* Jonokuchi

Division filtering shall be based on **chii ordinal**, not on chii string display.

---

## 4. Table Columns

The initial visible columns shall be:

* **Row Number**
* **Shikona**
* **Chii**
* **Wins**
* **Count**
* **Mean**

These columns shall have the following meanings:

* **Row Number**: display row index in the currently displayed table, always shown as `1, 2, 3, ...`
* **Shikona**: shikona at the anchor basho
* **Chii**: chii string at the anchor basho
* **Wins**: `all_wins`
* **Count**: `bout_count`
* **Mean**: `window_average_all_wins`

The current multiple-basho view already contains `shikona`, `chii`, `chii_ordinal`, `all_wins`, `bout_count`, and `window_average_all_wins`, so these columns are compatible with the existing derived view shape. 

---

## 5. Sorting Behaviour

The default table ordering shall be by **Mean descending**.

All column headings except **Row Number** shall be clickable.

Clicking a heading shall toggle the sort order for that column.

### Column-specific sort semantics

* **Shikona**: sort on displayed shikona text
* **Chii**: display chii string, but sort using `chii_ordinal`
* **Wins**: sort on `all_wins`
* **Count**: sort on `bout_count`
* **Mean**: sort on `window_average_all_wins`

For **Chii**, the default sort direction shall be **ascending**, since lower ordinal corresponds to higher rank.

For **Wins**, **Count**, and **Mean**, the default sort direction shall be **descending**.

Secondary sort keys are not yet specified.

---

## 6. Division Semantics

Division filtering shall be derived from **chii ordinal**.

The intended grouping rule is:

* `ordinal // 100000 = 0..4` → **Makuuchi**
* `ordinal // 100000 = 5` → **Juryo**
* `ordinal // 100000 = 6` → **Makushita**
* `ordinal // 100000 = 7` → **Sandanme**
* `ordinal // 100000 = 8` → **Jonidan**
* `ordinal // 100000 = 9` → **Jonokuchi**

The presentation layer may use these ordinal bands directly for filtering.

---

## 7. Identity Semantics

Where shikona and chii are shown, they shall be interpreted as the values applying at the **anchor basho**.

They shall not be interpreted as timeless identity fields.

They shall not be taken from whichever selected basho in the window happens to be latest for that rikishi.

This matters because the current multiple-basho view logic presently sources display identity from the **most recent selected basho in which the rikishi was present**, rather than explicitly from the anchor basho. 

---

## 8. Data Supply Model

The page shall consume **precomputed standings data**.

The server shall not invoke Python standings computation interactively in response to page actions.

A separate script or scheduled process shall generate the standings artefacts for the supported `num-basho` values and publish them for the page to load.

The precise transport/storage format for those artefacts remains undecided.

---

## 9. Relationship to Existing Outputs

This presentation layer is intentionally narrower than the full current multiple-basho analytical output.

The existing multiple-basho CSV/reporting output includes many additional fields, including exposure counts, presence averages, standard deviations, SEM values, and CI95 half-widths.  

The initial HTML view does **not** attempt to expose all of these.

Instead it presents a reduced, simpler surface oriented around:

* obvious total wins
* obvious participation count
* obvious window-average wins
* familiar identity fields for display

This is a deliberate simplification for first presentation use.

---

## 10. TBD

The following items remain open:

### 10.1 Identity Fix

The standings data supplied to the presentation layer should be corrected so that displayed **shikona** and **chii** are taken from the **anchor basho**, not from the latest selected basho in which the rikishi was present. The current multiple-basho view does not yet implement this semantics. 

### 10.2 Data Format

Whether the page should consume **JSON**, **CSV**, or some other static artefact format remains undecided.

### 10.3 Delivery Architecture

Whether the page is served locally or remotely, and what web-serving arrangement is most appropriate, remains undecided.

### 10.4 Secondary Sort Keys

No secondary or tertiary sort-key policy has yet been fixed.

### 10.5 Broader Analytical Features

The initial page does not expose richer measures such as presence averages, variability measures, or confidence-style metrics, though these already exist in the current multiple-basho derived output. Whether and how such features should later be surfaced remains open. 

If you want, I can also turn this into a more formal spec-style section matching the tone of your revised standings document.
