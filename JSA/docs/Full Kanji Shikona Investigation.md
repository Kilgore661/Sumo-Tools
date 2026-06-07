# Full Kanji Shikona Investigation

## Purpose

This note records a separate investigation from the earlier JSA
pre-requirements work. It pertains to work done in get_bios and the module stkp (was: sumodb_title_kanji_probe) in infra/parser. The resolution-by-kanji approach has been abandoned since it seems the JSA pages only have info re the current basho/banzuke.

The earlier note was concerned with JSA current-banzuke data as source material
for JSA rikishi IDs and romanised/Japanese shikona pairs, partly for possible
translation or glossing experiments.

This note is concerned with a different product problem:

```text
Can full kanji shikona help Sumo-Tools disambiguate public rikishi labels?
```

The immediate trigger is the failure of the current romanised full-shikona
policy. Hakuho Sho, `RikId(1123)`, remains public `Hakuho` as the latest holder
of that History shikona. The earlier Hakuho, `RikId(8206)`, also has full
romanised shikona `Hakuho`. Therefore romanised full shikona does not always
disambiguate.

## Current theory

The promising theory is that the ambiguity is at least partly caused by
romanisation.

If a shikona is understood as the Japanese string used to write it, then:

1. The first romanised shikona word represented as kanji may be unique within a
   single basho.
2. The full shikona represented as kanji may be unique across the publication
   catalogue.
3. Where first-word kanji is not enough across basho, second-word kanji may be
   the natural public disambiguator.

This would be preferable to exposing internal `rikid` values in public labels.

## What the SumoDB banzuke HTML gives us

SumoDB banzuke rows include rikishi links with `title` attributes. For example:

```html
<a title='大皇翔, Oitekaze, Kagawa, 21.02.2002, 2024.03, , 189 cm 166 kg, Jd55'
   href='Rikishi.aspx?r=12858'>Daikosho</a>
```

The visible link text is the romanised shikona, here `Daikosho`.

The `title` attribute is ordinary HTML advisory text. Browsers commonly display
it as a tooltip. SumoDB uses it to pack a comma-separated mini bio into the
link.

The first comma-separated field appears to be Japanese shikona headword data:

```text
大皇翔
```

The remaining fields appear to be metadata such as heya, origin, birth date,
hatsu dohyo, intai or blank lifecycle field, height/weight, and rank.

This is useful, but it is not full kanji shikona. For `Daikosho`, outside
evidence from the JSA site gives the full kanji shikona as:

```text
大皇翔 大陽
```

The SumoDB title field therefore appears to give only the kanji form of the
visible headword, not the full kanji shikona needed for the stronger
disambiguation theory.

## What the JSA current-banzuke JSON gives us

The `JSA` folder already contains a probe of current JSA banzuke AJAX data.

The current cached files include paired English and Japanese banzuke rows. The
English row gives a romanised `shikona`; the Japanese row gives a Japanese
`shikona`. Rows appear to align between the English and Japanese endpoints after
layout placeholders are filtered.

Examples from the current cache:

```text
Hoshoryu  -> 豊昇龍　智勝
Daikosho  -> 大皇翔(だいこうしょう)
Karino    -> 狩野(かりの)
```

This is an important lead, but it is not yet the target data.

The Japanese banzuke field can contain:

1. What looks like a full kanji shikona, such as `豊昇龍　智勝`.
2. What looks like kanji headword plus reading, such as
   `大皇翔(だいこうしょう)`.
3. What looks like kanji headword plus reading for a one-word shikona, such as
   `狩野(かりの)`.

Therefore the banzuke JSON is not currently proven to contain full kanji
shikona for every rikishi.

## What we may have found

Although the JSA current-banzuke JSON may not contain full kanji shikona, it may
contain exactly the lookup material needed to find full kanji shikona elsewhere
on the Japanese JSA site:

```text
JSA rikishi_id
Japanese banzuke shikona field
English banzuke shikona field
heya_id / heya_name
pref_id / pref_name
rank and banzuke position context
```

The key field is `rikishi_id`. If the Japanese JSA site has a rikishi profile
or home-page endpoint keyed by JSA rikishi ID, then the current-banzuke JSON may
provide the bridge from a banzuke row to a full Japanese profile record.

There is now a concrete example of the target endpoint shape:

```text
https://sumo.or.jp/ResultRikishiData/profile/4249/
```

For Daikosho, this profile page reportedly displays the full registered kanji
shikona:

```text
大皇翔 大陽
```

This suggests a possible path from SumoDB to full kanji shikona:

```text
SumoDB rikid
  -> SumoDB title first field / Japanese headword kanji
  -> JSA search or profile lookup
  -> JSA profile full kanji shikona
```

The profile number in this example, `4249`, appears to be a JSA-side rikishi
identifier, not a SumoDB rikid.

## What we still need

The next requirement is to investigate the Japanese JSA site outside the
current-banzuke AJAX response.

Specifically, determine whether there is a Japanese profile or home-page record
that provides:

```text
JSA rikishi_id -> full kanji shikona
```

If such a record exists, test whether it is reachable from:

1. The JSA `rikishi_id` in the current-banzuke JSON.
2. A Japanese or romanised shikona search.
3. A profile link or photo link encoded in the current-banzuke response.

## Identity problem

The Sumo-Tools public identity key is the SumoDB rikishi ID.

The JSA data uses a different `rikishi_id`.

The real bridge needed for production use is therefore:

```text
SumoDB rikid -> JSA rikishi_id -> full kanji shikona
```

The `JSA` folder contains WIP work toward understanding JSA IDs and current
banzuke rows, but it does not yet solve the SumoDB-to-JSA crosswalk.

Possible join evidence includes:

1. Romanised shikona.
2. Japanese shikona headword.
3. Heya.
4. Origin / prefecture.
5. Current rank and banzuke position.
6. Birth date, if available from both sources.
7. Hatsu dohyo or active-period overlap.

Romanised shikona alone is not enough because shikona are not unique.

## Historical coverage risk

Even if the Japanese JSA site provides full kanji shikona for current rikishi,
it may not provide an archive back to the 1958 Sumo-Tools epoch.

This matters because the current counterexample includes an old rikishi:

```text
RikId(8206): earlier Hakuho, retired in 1975
```

So the JSA route may produce a useful modern resolver without being a complete
historical resolver.

The investigation should explicitly distinguish:

1. Current rikishi coverage.
2. Recently retired rikishi coverage.
3. Historically retired rikishi coverage.
4. Whether old records can be searched even if they are not present on current
   banzuke pages.

There is a second coverage risk: SumoDB may not have always included Japanese
headword kanji in rikishi-link `title` attributes. If this was added only in a
recent era, then the route from SumoDB HTML to JSA profile search will only work
for rikishi whose cached SumoDB pages contain that kanji.

This means the probe must measure both:

```text
SumoDB title-kanji coverage by basho/date
JSA full-profile coverage by rikishi cohort
```

## Next probe

The next probe should start from a current rikishi whose full kanji shikona is
known from the JSA site, for example:

```text
Daikosho
JSA current-banzuke Japanese field: 大皇翔(だいこうしょう)
known full kanji shikona from JSA site: 大皇翔 大陽
JSA profile URL reported for this record:
https://sumo.or.jp/ResultRikishiData/profile/4249/
```

Questions:

1. Which Japanese JSA URL or endpoint contains `大皇翔 大陽`?
2. Is that URL keyed by the JSA `rikishi_id` from the current-banzuke JSON?
3. Can the same endpoint be reached for other current rikishi?
4. Does it expose full kanji shikona in a stable field?
5. Does an equivalent English page exist, and if so does it omit the kanji?

If the endpoint is stable, the next additive implementation probe is:

1. Extend the SumoDB parser just enough to persist the first comma-separated
   field from rikishi-link `title` metadata as Japanese headword kanji.
2. Use that headword kanji to search or look up the rikishi on the Japanese JSA
   site.
3. Parse the JSA profile page for full kanji shikona.

Only after those questions are answered should the SumoDB-to-JSA crosswalk or
production public-shikona policy be designed.

## Additive SumoDB title probe

The first implementation probe is intentionally separate from the production
parser model:

```text
src/infra/parser/sumodb_title_kanji_probe.py
```

It scans cached SumoDB daily-results HTML, extracts `Rikishi.aspx` anchors, and
writes a CSV with one row per SumoDB rikishi id. Repeated observations for the
same rikishi may differ because the SumoDB title field is basho-local observed
metadata, not a canonical one-record-per-rikishi fact. Those differences are
therefore written as variants rather than treated as errors.

The important output columns are:

```text
rikid
romanised_shikona
title_headword
has_cjk_headword
has_japanese_headword
title_identity
observation_count
first_romanised_text
first_title
first_source_path
first_line
```

The uniqueness check is intentionally over identity-like values only:

1. `romanised_shikona` strips a leading chii/rank token from the visible anchor
   text, so `Jk22e Chiyoshinzan` and `Chiyoshinzan` compare equal.
2. `title_identity` uses the comma-separated SumoDB title fields through the
   blank lifecycle slot, e.g. `headword, heya, origin, birth, hatsu, `. The
   height/weight and final rank fields after that point are retained in
   `first_title`, but are not used for the variant check because they may vary
   over time.

The default scan is deliberately limited to:

```text
files/output/HTML results/{year} {month}/{day}.html
```

Those are the files where the first useful SumoDB `title` evidence was found.
Do not mix in current-standings files until the daily-results evidence has been
inspected for repeated-row stability.

For careful first-pass inspection, run it on a single cached daily-results file:

```powershell
python -m src.infra.parser.sumodb_title_kanji_probe --source-file "files\output\HTML results\2026 05\01.html" --output-csv "files\output\infra\parser\sumodb_title_headwords_2026_05_day_01.csv"
```

Run the default daily-results-only corpus probe with:

```powershell
python -m src.infra.parser.sumodb_title_kanji_probe
```

The default output is:

```text
files/output/infra/parser/sumodb_title_headwords_daily_results.csv
```

Current-standings files can be included later, explicitly, with:

```powershell
python -m src.infra.parser.sumodb_title_kanji_probe --include-current-standings
```

The earlier sample over `current standings/2026 05.html` produced:

```text
observations: 1265
observations with CJK headword: 1261
observations with Japanese headword: 1265
```

The difference between CJK and Japanese counts matters. Some headwords may be
written in kana rather than kanji, for example foreign names represented in
katakana. These are still Japanese-script search terms even though they are not
kanji.

The first flat-dump run showed that the daily-results corpus is too large for a
spreadsheet-scale inspection: more than five million observed links produced a
CSV of roughly one gigabyte. The probe therefore moved to a one-row-per-rikishi
shape with separate variant output.

The first one-day variant found was context-dependent visible text:

```text
rikid: 12978
romanised_text: Jk22e Chiyoshinzan != Chiyoshinzan
```

The title metadata itself matched in that case. This needs a policy decision:
visible anchor text with a leading chii is not part of the uniqueness contract.
The probe now separates raw `first_romanised_text` from normalised
`romanised_shikona`.

The next full-corpus attempt found genuine metadata variation, beginning with:

```text
rikid: 3913
title_headword: Kitanonada written with two different Japanese headwords
```

The probe now writes three CSVs:

```text
files/output/infra/parser/sumodb_title_headwords_daily_results.csv
files/output/infra/parser/sumodb_title_headword_variants_daily_results.csv
files/output/infra/parser/sumodb_title_headword_duplicates_daily_results.csv
```

It keeps only one canonical row per rikishi in the main output, writes one row
per unique differing field in the variant output, and writes same-source
Japanese headword duplicates to a separate CSV. Variants are not errors; they
are evidence about the shape of incidental SumoDB title metadata.

The first variant sample also showed that disagreement is not limited to
`kanji versus kana` spelling variation. Some records differ by romanised
shikona, Japanese headword, or heya-like identity fields across basho. That may
be historically meaningful rather than bad data, so this probe records those
differences without normalising or collapsing them.

The duplicate-headword output tests the current, weaker hypothesis available
from SumoDB alone:

```text
Within one cached daily-results source, no two rikids should share the same
Japanese title headword.
```

This is not a test of full kanji shikona uniqueness, because SumoDB title
headwords are not full kanji shikona. It is nevertheless useful evidence about
whether the title headword can act as a JSA search term in a single basho/day
context.

---

Current version: src/infra/parser/stkp.py
Live hypotheses:
Current live hypotheses, as I understand them:

1. **Romanised shikona are not enough**
   Single-word romanised shikona are reused, and romanisation is lossy. So romanised `Hakuho` does not tell us whether the underlying Japanese written names are the same.

2. **SumoDB title headword is useful but not canonical**
   The first field in SumoDB link titles, e.g. `北ノ洋`, appears to be a Japanese headword for the visible shikona at that observed basho. It is not full kanji shikona and not one stable value per rikid.

3. **Title metadata variants are expected**
   For one rikid, title fields can vary across time because of genuine shikona changes, spelling/orthography variants, heya changes, and possibly sparse older formats. These are observations, not errors.

4. **Within one source/basho, Japanese headwords may be distinguishable**
   The testable SumoDB-only hypothesis is: within a single cached daily-results file, no two rikids share the same Japanese title headword. The new duplicate CSV tests this.

5. **The stronger target is full kanji shikona**
   The real disambiguation candidate is full kanji shikona, not SumoDB’s headword. We suspect active rikishi names must be distinguishable by Japanese written name, perhaps full kanji shikona.

6. **Historical reuse remains unknown**
   Even if full kanji shikona are unique at approval time or within a basho, we do not yet know whether the same full kanji shikona can be reused historically after retirement/name change.

7. **JSA may provide full kanji shikona**
   The JSA Japanese profile pages may expose full registered kanji shikona, e.g. the reported Daikosho page. But we still need to establish a reliable bridge:
   `SumoDB rikid -> JSA rikishi_id -> full kanji shikona`.

8. **SumoDB headword may help build that bridge**
   The title headword may be a useful Japanese search term for finding the JSA profile, especially when combined with heya, origin, birth date, hatsu dohyo, and rank context.

9. **The local epoch is enough for now**
   We care about the Sumo-Tools cached epoch, not all SumoDB history back to c.1750. The probe should measure what our local files can support.

---

Follow-on remarks after the `stkp.py` switch

The live hypotheses above need one immediate correction. The SumoDB-only
short-headword uniqueness hypothesis has failed on local evidence.

The basho-level duplicate-headword output from `src/infra/parser/stkp.py`
showed that the Japanese title headword `小林` was shared within a basho:

```text
2016/03: rikids 12276 and 12287
2017/01: rikids 12276 and 12361
```

This means SumoDB title headwords are not unique even within a single basho.
They remain useful Japanese-script search/context terms, but they cannot be the
public disambiguator.

The current local SumoDB evidence appears to split the needed information in
two:

```text
Daily results / current standings anchors:
  short Japanese title headword, e.g. 小林 or 大皇翔

SumoDB Rikishi.aspx bio pages parsed by get_bios:
  full romanised shikona, e.g. Kobayashi Rintaro or Daikosho Taiyo
```

For example, `RikId(12858)` has SumoDB title headword `大皇翔` and get_bios full
romanised shikona `Daikosho Taiyo`; the desired full kanji shikona is reported
from the JSA profile as `大皇翔 大陽`. In the sampled local SumoDB sources, that
full kanji form is not present.

Therefore the current state of play is:

1. Romanised full shikona is better than simple History shikona, but has known
   failures such as the Hakuho case.
2. SumoDB short Japanese title headword is not enough, because it can collide
   within a basho.
3. Local SumoDB bio pages give full romanised shikona, not full kanji shikona,
   in the sampled evidence.
4. If full kanji shikona remains the preferred disambiguator, the next serious
   route is probably the JSA Japanese profile data, using SumoDB rikid,
   headword, heya, origin, birth date, hatsu dohyo, and other context fields to
   build or test a SumoDB-to-JSA bridge.

This is not yet an exhaustive proof that no SumoDB endpoint exposes full kanji
shikona. It is the working conclusion from the cached daily-results/current
standings anchors, the get_bios `Rikishi.aspx` cache, and targeted examples
around Hakuho, Daikosho, and the three Kobayashi rikishi.

---

Suggested next step

The next session should start by treating the JSA route as the main candidate,
while keeping one small SumoDB escape hatch open.

The immediate question is:

```text
Can we reliably get from a SumoDB rikid to the JSA Japanese profile page that
contains full kanji shikona?
```

A good first probe would use a deliberately small hand-picked test set:

```text
12858  Daikosho Taiyo      known target: 大皇翔 大陽
12276  Kobayashi Rintaro   collides on SumoDB headword 小林
12287  Kobayashi Riku      collides on SumoDB headword 小林
12361  Kobayashi Mineo     collides on SumoDB headword 小林
1123   Hakuho Sho          romanised full-shikona policy failure case
8206   Hakuho              romanised full-shikona policy failure case
```

For each rikid, collect the SumoDB-side join evidence already available:

```text
rikid
latest/full romanised shikona from get_bios
observed SumoDB Japanese title headwords
heya history
shusshin / origin
birth date
hatsu dohyo
intai
height/weight if useful
```

Then test JSA lookup strategies in increasing order of explicitness:

1. Search the Japanese JSA site for the SumoDB Japanese headword plus sumo
   context, as in the Daikosho example.
2. If a JSA profile page is found, record the JSA profile id and parse the full
   kanji shikona field.
3. Compare the JSA profile metadata against the SumoDB evidence: romanised
   shikona, heya, origin, birth date, and debut date.
4. Decide whether the match is deterministic enough to support a crosswalk.

The first output should be a small CSV, not production code:

```text
sumodb_rikid
sumodb_latest_romanised_shikona
sumodb_title_headwords
sumodb_heya
sumodb_shusshin
sumodb_birth_date
sumodb_hatsu_dohyo
jsa_profile_id
jsa_full_kanji_shikona
jsa_match_status
jsa_match_notes
```

The probe should be offensive about contradictions once a candidate JSA match is
chosen: if birth date or other strong identity fields disagree, treat that as a
bad match rather than silently accepting it.

The small SumoDB escape hatch is to inspect whether another SumoDB endpoint,
not currently cached by `get_bios`, exposes full Japanese shikona. Do not spend
long on this before trying JSA. The sampled local evidence already says the
current daily-results/current-standings anchors and `Rikishi.aspx` bio pages do
not provide the target field.

If the hand-picked JSA probe works, broaden in stages:

1. Current active rikishi, where JSA coverage should be strongest.
2. Recently retired rikishi.
3. Known collision sets from `stkp.py`, especially basho-level duplicate
   headwords.
4. Historical policy-failure cases such as Hakuho.

At each stage, report coverage and ambiguity separately:

```text
rikids tested
JSA profile found
full kanji shikona parsed
unique match
ambiguous match
metadata contradiction
no JSA coverage
```

Only after those measurements should make_site2 policy change again. The next
production decision is not "use kanji" in the abstract, but whether there is a
maintainable cache of:

```text
SumoDB rikid -> full kanji shikona
```

with clear freshness rules and known failure modes.
