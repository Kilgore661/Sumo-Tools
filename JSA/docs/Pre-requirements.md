# First-pass report: JSA current banzuke data

## 1. Purpose

This note records a first-pass scrape and inspection of the Japan Sumo Association’s current banzuke data. The work was motivated by two exploratory requirements.

### Requirement 1: JSA rikishi identity mapping

The first objective is to obtain JSA rikishi IDs. These may later provide a bridge between JSA records and the existing `sumodb.de` data used elsewhere in the Sumo-Tools project.

The expected later problem is a database-style join:

```text
JSA rikishi record  <->  Sumodb wrestler record
```

This will not be trivial, because the most obvious join candidate, romanised shikona, is not unique.

### Requirement 2: Romanised/Japanese shikona pairing

The second objective is to obtain reliable pairs of romanised and Japanese shikona.

These pairs may later serve as source material for experiments in translating or approximating shikona meanings in English. For example, the aim might be to turn a Japanese shikona into a rough English gloss such as “Happy Dragon King” or “Rising Dragon”, while recognising that shikona meanings may involve kanji choice, name traditions, ateji, sumo context, and non-obvious personal or cultural references.

## 2. Source and pipeline

A rough two-stage scrape and parse pipeline was used.

### Stage 1: Probe and cache

`probe.py` downloads current banzuke AJAX data from the JSA site in both English and Japanese. The responses are cached locally under paths of this form:

```text
files/banzuke_<language>_division_<division>_page_<page>.json
```

For example:

```text
files/banzuke_en_division_2_page_1.json
files/banzuke_ja_division_2_page_1.json
```

This keeps network use low and allows later analysis to be performed against local files rather than repeatedly querying the JSA site.

### Stage 2: Explore and inspect

A separate explorer script inspects the cached JSON files. The explorer focuses on `BanzukeTable`, which appears to contain the actual banzuke row data. It checks for empty strings and JSON `null` values, filters out apparent layout-placeholder rows, and reports the remaining blank/null behaviour in the rikishi rows.

## 3. Relevant payload

The JSA response contains more than just rikishi data. A typical cached JSON file includes:

```text
BanzukeTable
BashoInfo
top-level page / language / division metadata
locally-added scrape metadata such as _downloaded_from
```

For the purposes of this note, the relevant payload is `BanzukeTable`.

The surrounding metadata appears to describe the current basho, page, division, language, and response context. That information may become useful later, but it is not part of the immediate payload needed for the two current objectives. For now, the full raw structure can be inspected in a typical cached output file if needed.

## 4. BanzukeTable rows

`BanzukeTable` contains rows corresponding to the banzuke display table.

Most rows are actual rikishi rows. A rikishi row appears to be identifiable by non-empty fields such as:

```text
rikishi_id
shikona
```

The scrape also revealed a small number of apparent layout-placeholder rows. These are not rikishi records. They seem to exist to preserve the traditional east/west banzuke table layout.

The observed placeholder pattern is:

```text
ew is present
banzuke_id is 0
other fields are empty strings
```

For example, a placeholder row has the general shape:

```json
{
  "pref_id": "",
  "pref_name": "",
  "heya_id": "",
  "heya_name": "",
  "banzuke_name": "",
  "ew": 2,
  "banzuke_id": 0,
  "kakuzuke_id": "",
  "rikishi_id": "",
  "rikishi_banzuke_id": "",
  "shikona": "",
  "photo": "",
  "rank": "",
  "number": "",
  "seat_order": ""
}
```

After filtering these layout rows, the current scrape produced:

```text
Raw BanzukeTable rows per language: 1294
Layout placeholder rows per language: 3
Analysed rikishi rows per language: 1291
```

## 5. English/Japanese consistency

The English and Japanese JSA responses appear to align cleanly.

After filtering layout rows, both languages produced 1291 rikishi rows. The row ordering appears consistent between the English and Japanese versions.

The probe classified row fields into stable and localised fields.

### Stable fields

These fields appeared to have the same values in English and Japanese rows:

```text
banzuke_id
ew
heya_id
kakuzuke_id
number
photo
pref_id
rank
rank_new
rikishi_banzuke_id
rikishi_id
seat_order
sort
```

### Localised fields

These fields differed between the English and Japanese rows, as expected:

```text
banzuke_name
heya_name
numberKanji
pref_name
shikona
```

No mixed fields were observed in the current scrape.

This supports the important practical conclusion that, for the current data, the English `shikona` can be treated as the romanised counterpart of the Japanese `shikona` at the same filtered row index.

## 6. Fields of immediate interest

The current objectives only require a small subset of the fields.

### `rikishi_id`

This appears to be the JSA’s rikishi identifier.

This is the main field of interest for the future identity-mapping work. It may allow a local table of JSA rikishi records to be joined, cautiously, to Sumodb wrestler records.

### `shikona`

This is the rikishi’s shikona in the response language.

In the English endpoint, this gives a romanised form. In the Japanese endpoint, it gives the Japanese form. Since the rows align between languages, this field directly supports the second requirement: producing romanised/Japanese shikona pairs.

### `heya_id` / `heya_name`

These identify the rikishi’s stable. They are not central to the immediate requirements, but may be useful later as supporting data when attempting to match JSA rikishi to Sumodb wrestlers.

### `pref_id` / `pref_name`

These identify the rikishi’s listed origin or prefecture/country. Like heya information, this may later be useful as supporting evidence for disambiguation.

### `banzuke_name`

This is a localised rank/position label. It is not the main payload, but it may be useful as context or for sanity checks.

## 7. Other row fields

Other row fields were observed but have not yet been investigated semantically:

```text
banzuke_id
ew
kakuzuke_id
number
numberKanji
photo
rank
rank_new
rikishi_banzuke_id
seat_order
sort
```

These appear to relate to banzuke position, ordering, rank/category, photo filename, and row identity within the current banzuke. Their exact meanings have not yet been fully surveyed.

One tentative note: `kakuzuke` likely refers to 格付け, meaning ranking or rank classification. In the observed data, `kakuzuke_id` and `Kakuzuke` appear to refer to the broad banzuke category or division, such as Juryo. This has not yet been mapped exhaustively.

## 8. Empty strings and nulls

The explorer checked for both JSON `null` values and empty strings.

After filtering layout-placeholder rows, no JSON `null` values were observed in the analysed rikishi rows.

The only field still containing empty strings was:

```text
rank_new
```

In the current scrape:

```text
rank_new present: 1291
rank_new empty string: 1281
rank_new null: 0
```

This suggests that `rank_new` is a marker field that is usually blank. In the observed Japanese data, non-empty values included strings such as:

```text
新十両
再十両
```

So the empty string probably means that no special “new” or “returning” marker applies to that rikishi in the current banzuke.

This has not been treated as a data error.

## 9. What we know

At this stage, the JSA current banzuke data appears to contain the fields needed for the two motivating requirements.

Specifically:

```text
It exposes JSA rikishi IDs.
It exposes romanised shikona in the English response.
It exposes Japanese shikona in the Japanese response.
The English and Japanese rikishi rows align by list index.
Stable fields are consistent between the two languages.
Localised fields differ as expected.
```

For the limited purposes of this phase, the data behaves as expected.

## 10. What we do not yet know

This work does not claim to provide a full semantic model of JSA data.

In particular, we have not yet surveyed:

```text
the full range of all possible fields across other endpoints
whether the same fields appear in all timing conditions
whether extra fields appear before, during, or after a basho
the exact meanings of all row fields
the complete mapping of rank/category codes
the relationship between JSA IDs and Sumodb IDs
```

The cached JSA response also contains basho and page metadata that has not been analysed, because it is not currently relevant to the two immediate objectives.

## 11. Provisional conclusion

The scrape and first-pass parser are useful.

The current banzuke AJAX data appears to provide a reliable first stepping stone toward both objectives:

1. building a local table containing JSA rikishi IDs; and
2. producing paired romanised/Japanese shikona values.

The JSA data also contains several additional fields that may later prove useful when compared with Sumodb data. However, those fields have only been itemised at a high level. They have not yet been fully interpreted or validated.

## 12. Next steps

### 1. Revisit Sumo-Tools and Sumodb exposure

Revisit the Sumo-Tools project and identify where Sumodb wrestler records are exposed.

The goal is to understand what fields are available for joining JSA rikishi rows to Sumodb records.

The likely first join candidate is romanised shikona, but this is not unique. Any join strategy will need to handle duplicates and may require additional supporting evidence, such as:

```text
rank history
active period
heya
origin
banzuke position
other comparable fields
```

The first task is not to solve the join completely, but to locate the relevant Sumodb-facing records and see what candidate fields are available.

### 2. Explore shikona translation approaches

Explore online tools, APIs, dictionaries, and LLM-based methods for translating or glossing kanji and kana in shikona.

The aim is not necessarily to produce a single authoritative translation. A more realistic target is to generate plausible English approximations, ideally with some sensitivity to sumo context and Japanese naming conventions.

Outputs should probably be treated as candidate glosses rather than definitive translations.

