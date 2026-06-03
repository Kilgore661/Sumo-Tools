# `src.infra.get_bios`

`src.infra.get_bios` is a small enrichment package for rikishi biographical data.

It supplements the parsed tournament `History` with data downloaded from SumoDB `Rikishi.aspx` pages.

## Modules

### `__main__.py`

Run as:

```bash
py -m src.infra.get_bios
```

This module connects to the live `History` store, discovers all rikishi IDs present in the parsed tournament history, and downloads the corresponding SumoDB `Rikishi.aspx` pages.

Downloaded pages are stored as:

```text
files/output/infra/get_bios/rikishi/{rikid}.html
```

The downloader skips files that already exist, treats failed or very small downloads as glitches, and stops after repeated consecutive glitches to avoid continuing when the network or SumoDB is likely unavailable.

---

### `parser.py`

Run as:

```bash
py -m src.infra.get_bios.parser
```

This module reads the downloaded `Rikishi.aspx` HTML files and extracts headline biographical details from the top rikishi information table.

It currently persists:

```text
Birth Date
Shusshin
Heya
Shikona
Hatsu Dohyo
Intai
Height
Weight
Height_by_Date
Weight_by_Date
```

The main output is written to:

```text
files/output/infra/get_bios/rikishi_bios.json
```

The parser also writes a missing-field diagnostic table:

```text
files/output/infra/get_bios/rikishi_bio_missing_fields.csv
```

`Shikona` is reconstructed from the career table, using each shikona heading and the first following basho date to infer the first use of that name.

`Height_by_Date` and `Weight_by_Date` are extracted from date-stamped entries in the career table. The top-level `Height` and `Weight` values are taken from the headline bio table.

The parser performs rudimentary validation, including:

* unexpected headline bio fields
* discrepancies between headline shikona history and career-table shikona history
* unusual characters in shikona
* shikona with more than two words
* malformed or partial height/weight values
* whether height and weight are either both present or both absent

At present, observed height and weight data appears to be paired: height and weight are either both present or both absent.

---

### `bmi.py`

Run as:

```bash
py -m src.infra.get_bios.bmi
```

This module reads `rikishi_bios.json` and computes BMI values from the persisted headline `Height` and `Weight` fields.

It reports:

* count
* minimum BMI
* maximum BMI
* mean BMI
* standard deviation
* a 20-bin BMI distribution

This is mainly a probe/validation module to check that the JSON output is usable for downstream analysis.

---

### `probe.py`

Run as:

```bash
py -m src.infra.get_bios.probe
```

This module reads `rikishi_bios.json` and creates frequency distributions for selected fields. Its first use was to inspect `Shusshin` values and understand how much duplication or standardization exists in the birthplace/location strings.

It writes outputs such as:

```text
files/output/infra/get_bios/shusshin_bins.csv
```

This is exploratory rather than core persistence logic.

## Current Model

`src.infra.get_bios` enriches the parsed sumo `History` with biographical data from SumoDB `Rikishi.aspx` pages.

The package downloads individual rikishi pages, parses headline biographical details plus dated shikona/height/weight changes, performs lightweight validation, writes the result to JSON, and includes probe scripts for BMI, `Shusshin` frequency, and data-shape exploration.

## Open Questions / Next Steps

### 1. Relationship Between Headline Values and Career-Table Values

Sometimes the headline bio table reports a shikona, height, or weight that is not the last value found in the career table.

Question:

> Should the headline value be treated as the latest recorded value?

If yes, then:

* the headline table is authoritative for current/latest values
* the career table provides dated historical observations
* a mismatch is not necessarily an error

This gives a two-layer model:

```text
Height              latest headline height
Weight              latest headline weight
Height_by_Date      dated historical height observations
Weight_by_Date      dated historical weight observations
Shikona             dated shikona history inferred from career table
latest Shikona?     possibly headline title or final headline shikona item
```

If no, then:

* the headline and career table are two inconsistent sources
* mismatches should be treated as data-quality issues
* both may need to be preserved explicitly, or one source chosen per downstream task

### 2. Pattern of Size Reporting

Height and weight appear together, but they are not present for every career row.

Questions:

* Is size reporting mostly a recent-era phenomenon?
* Is there a date before which size reports are rare or absent?
* Are size reports tied to particular divisions, promotions, or sekitori status?
* For an individual rikishi, is the number of size reports related to career length?
* Are longer careers simply more likely to accumulate more dated size observations?

Possible probes:

* distribution of `Height_by_Date` / `Weight_by_Date` support counts
* first and last date of size observation per rikishi
* count of size observations by basho date
* count of size observations by rikishi career length
* comparison of headline `Height` / `Weight` coverage vs dated table coverage

### 3. `Shusshin` Parsing

Japanese `Shusshin` entries appear to be structured as one or more ordered geographical paths:

```text
Shusshin ::= Place (" - " Place)*
Place    ::= Component (", " Component)*
```

Within each `Place`, components appear to be ordered from coarse to fine geography.

For mainland Japanese entries, a hyphen-separated chain probably represents historical-to-current municipality changes, for example:

```text
Akita-ken, Senboku-gun, Sennan-mura - Akita-ken, Senboku-gun, Misato-cho
```

meaning roughly:

```text
former Sennan-mura, now Misato-cho
```

This needs more probing before normalization.
