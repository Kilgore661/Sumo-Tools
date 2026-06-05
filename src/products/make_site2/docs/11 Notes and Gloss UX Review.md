# 11 Notes and Gloss UX Review

## Status

Working research and design note for the `make_site2` Notes and gloss system.

This document records the first review pass over Notes, popovers and explanatory
gloss after the main public-site structure became stable. It is not yet a
normative replacement for `04.3 Public UI Model.md`, `04.4 Published Artifact
Model.md` or `05 Rendering Design.md`. Settled rules should be promoted into
those documents when the design is ready.

## Implementation Checklist

This checklist extracts the agreed visible wording changes from the review.
It is the source for the first implementation pass over Navigation labels,
page headings, option labels, PA captions and chart/table captions.

| Page | Navigation / Page title | Page subtitle | PA heading | PA subheading / axis-caption decision | Option / label changes |
| --- | --- | --- | --- | --- | --- |
| `2.1` | `Most Recent Banzuke` | none for now | `The {Month} {Year} Banzuke` | none | keep `Previous Basho`; keep `Delta`; keep `Equelo Ratings` |
| `2.2` | `Rolling Wins-Based Ranking` | `Rikishi ranked by average wins over a selected number of recent basho.` | `Rolling Wins-Based Ranking for the {Division} Division` | `Over the last {num_basho} basho` | `Combined` -> `Both` |
| `3.3` | `Rikishi History` | `Progress from hatsu dohyo to current date/intai.` | `Career History for {selection}` when selected; otherwise base heading | `({earliest_date} to {last_date})` where available | `Log` -> `Compress`; `Basho from Hatsu` -> `Hatsu` in controls |
| `4.3.1` | `Banzuke Structure by Era` | `How the size and division makeup of the banzuke changed over time.` | `Average Banzuke Composition by Era` | `Average rikishi per basho, grouped by division.` | none |
| `4.3.2` | `Makuuchi Structure by Era` | `How the lower edge of the top division changed over time.` | `Makuuchi Rank Appearances by Era` | `Count of banzuke appearances at each Makuuchi rank.` | none |
| `4.4` | `Division Persistence` | `How consistently each basho's division members stayed in the same division across that basho and the previous 10.` | `Division Persistence` | duplicate page subtitle | none |
| `4.5` | `First Chii Appearance` | existing framing is acceptable for now | `First Chii Appearance` | no immediate change | none |
| `5.1` | `Wins: Finish Chances` / `Finish Chances by Wins` | `How often rikishi at a selected chii finished near the top or bottom of their division by wins.` | `{Division} {Chii}: {Top|Bottom} Finish Chances` | `Historical probability of finishing at position N = 1,...,10 by wins; sample size n = {n}.` | x-axis uses `Finish Position N, no worse than` or `Finish Position N, no better than` |
| `6.2.1` | `Typical Equelo Ratings` | existing framing is acceptable | `Typical Equelo Ratings` | no caption change | columns should not be sortable in a later behaviour pass |
| `6.3.1` | `Win Probability by Ranks` | `How likely is one rikishi to beat another based on rank?` | `Win Probability ({Observed|Predicted})` | no subheading; axes carry selected/opponent roles | `Equelo` source label -> `Predicted`; x-axis `Opponent Rank`; y-axis `P(selected rikishi wins)`; legend `Selected Rank` |
| `7.1` | `Basho Results` | existing framing acceptable | existing dynamic results heading | delete `Final` PA subheading | `Changes` -> `Next Basho`; `Analysis` -> `Ratings Fit`; leave `nuChii` in place for now |

---

## 1. Purpose

The Notes and gloss system should help readers understand visible analytical
material without turning the site into a manual.

The target reader can follow a simply designed UI:

```text
site title
NavigationBar
ContentPanel
  Heading
  optional Filters
  PAPanel
    PA
    Notes
```

The reader is expected to learn by exploring. They will often click first and
only later notice how the Navigation tree, Heading, Filters, PA, popovers and
Notes relate.

Gloss should support that discovery path. It should not compensate for weak
navigation labels, unclear page titles or poor option labels.

---

## 2. Reader Context Ladder

A typical reader parses the page progressively:

1. Navigation item `X`: there is information on this subject.
2. Page title `P`: the content panel refines what the selected page shows.
3. Optional subtitle `Q`: the page gives additional public framing where useful.
4. Together, `X`, `P` and `Q` tell the reader where they are.
5. Filters then ask what data set, representation or visible features the
   reader wants.
6. The selected Filter state `R` changes the visible PA state.
7. The PA details are read in the context of `X`, `P`, `Q` and `R`.

Gloss belongs late in this ladder. A column heading or option label should not
have to restate the whole page context. It should clarify a local point that is
easy to misread after the surrounding context is understood.

---

## 3. Navigation and Discovery Findings

Quick Links may be less useful than first assumed. If Quick Links point at pages
whose importance is seasonal, such as a new-banzuke page immediately after a
banzuke release, they may teach the wrong mental model about the site's main
structure.

The current Navigation tree is not yet product truth. It is partly a prototype
scaffold that proved a nested subject-led list could work. Historically, many
implemented PAs were research results used to drive UI-methodology work, and
many additional Navigation items came from a later menu brain dump. Therefore
the current tree mixes:

- implemented public or candidate PAs;
- research/prototype artifacts;
- plausible future product ideas;
- placeholders that may never appear in the finished product;
- navigation-shape experiments.

The tree can still be used as the traversal list for review, but it should not
over-authorize page placement, section structure or gloss decisions.

The preferred discovery direction is:

```text
Landing
  -> collapsed subject-led Navigation tree
  -> expand/explore a subject
  -> active Navigation item
  -> page Heading
  -> Filters
  -> PA gloss and Notes
```

Implications:

- Quick Links may be removed or deferred.
- The Navigation tree should be a collapsible nested list.
- The initial Navigation view should show main section headings.
- The active Navigation item should be visually obvious.
- When a page is selected, the Navigation tree should scroll the active item
  into view if necessary.
- Public pages intended for discovery should appear in the Navigation tree.
  `GOATs` is currently missing from the tree if it is intended as public
  surface.

Seasonal prominence should not be confused with navigation structure. A page
may remain in its subject position while a future landing panel or date-aware
feature promotes it when timely.

Before glossifying a Navigation item, classify the item itself:

```text
public deliverable
research/prototype deliverable
future product idea
placeholder
navigation experiment
```

Only public deliverables and research/prototype deliverables should normally
receive a full gloss review. Placeholder or brainstorm nodes should be marked
as such rather than polished.

---

## 4. Gloss Types

Gloss should be short. When the explanation is long, the popover should point
to Notes or to another explanatory page.

Useful gloss types:

| Type | Purpose | Example shape |
| --- | --- | --- |
| Definition gloss | Define a simple unfamiliar term locally. | `Rikishi fighting name.` |
| Note pointer gloss | Signal that a visible feature has a caveat or convention. | `Size of movement. See Notes.` |
| Hybrid gloss | Give a tiny disambiguation and point to a fuller Note. | `Result arrows mean rank-group movement. See Notes.` |
| External guide gloss | Point to a wider explanatory area when a concept is bigger than the current PA. | `Model rating. See Ratings & Models.` |

`See Notes` should open the Notes panel if it is closed. Ideally it should also
focus or briefly highlight the relevant Note.

Implementation contract for the first runtime pass:

- declarative model fields carry local gloss as `help`;
- Filters and Filter values may declare `help`;
- Table columns and table column groups may declare `help`;
- renderers display `help` as hover popovers attached to the existing label or
  heading; the popover itself is rendered in a top-level overlay so scrollable
  PA/table containers cannot clip it;
- the existence of gloss is signalled by a small inert token next to the label;
  the token is not itself the popover target;
- dropdown controls can show Filter-level help, but not value-level help,
  because native `option` elements cannot contain popover markup;
- chart axis, trace and legend gloss remain a later extension.

---

## 5. Filters, Notes and Ownership

Filters do not own Notes.

A Filter may reveal, hide or change a visible PA feature. If that visible PA
feature has an explanatory Note, the Note becomes relevant because the PA state
changed, not because the Filter owns explanatory material.

This preserves the existing page grammar:

```text
Contents -> FilterSection? . PAPanel
PAPanel -> PA . Notes
```

Option gloss is still allowed. It should usually be a short local explanation
of what the option changes. If an option reveals a semantically loaded PA
feature, the option popover may use the same note-pointer gloss as the
corresponding PA heading.

Example:

```text
Delta option gloss
  Size of movement. See Notes.

Delta column gloss
  Size of movement. See Notes.
```

If an option needs a full Note while the corresponding PA feature is not
visible, that is evidence that the label or product model needs review. An
option-specific caveat should normally be handled by a short option popover. If
the necessary caveat is too long for a popover, treat that as evidence of a bad
or overloaded option until the page review proves otherwise.

Example:

```text
Active Rikishi Only option gloss
  When off, longer windows may include retired rikishi.
```

This does not create an `Active Rikishi Only` Note. It explains the option
locally.

---

## 6. Depth and Wording Policy

The wording depth should follow the page or view depth.

Each page review should classify at least:

- depth;
- primary user type;
- optional secondary user types or specialist edges.

The current depth vocabulary is:

```text
Basic
Advanced
Research
```

`Basic+` may be used as a working review label for a page whose default
experience is Basic but whose optional controls or Notes provide limited
Advanced depth. It is not yet a formal replacement for the existing vocabulary.

The current user-type vocabulary is:

```text
Type A  Casual / Mainstream Fan
Type B  Enthusiast
Type C  Analyst / Specialist
```

Basic/current pages should prefer concrete examples over technical terms.
Advanced pages may use terms, but should define them locally when they first
matter. Research pages may rely on heavier terminology, but Notes and gloss
should still expose assumptions and caveats rather than project-private
language.

For basic pages, a good Note often answers:

```text
What does this visible thing count, show or qualify?
```

not:

```text
What is the full internal model?
```

---

## 7. 2.1 New Banzuke Review

The first microscope pass considered the page currently known as Banzuke
Changes. The product direction is to frame it as a new-banzuke page under
Current Sumo, especially in the period after a new banzuke is released and
before or shortly after the basho begins.

Working classification:

```text
Depth
  Basic+

Primary user type
  Type A - Casual / Mainstream Fan

Secondary affordance
  Type B exploration through optional Previous Basho, Delta and Equelo controls

Specialist/research leakage risk
  Equelo and expert movement semantics, if not clearly framed
```

The default experience should therefore remain strongly Type A: familiar
banzuke shape, minimal required explanation, concrete Notes and short popovers.
Optional controls may serve deeper readers, but should not make the page feel
like an analyst tool on first contact.

### 7.1 Navigation and Heading

Candidate Navigation wording:

```text
Current Sumo
  Most Recent Banzuke
```

Alternative shorter Navigation wording:

```text
New Banzuke
```

The ContentPanel title may repeat the Navigation item by default, but it should
not be forced to do so. A short Navigation label can expand into a fuller page
title after selection.

Candidate expanded title shape:

```text
How the {date} banzuke changed from the previous banzuke
```

This wording needs refinement, but the design principle is settled: the
Navigation label can be compact while the page title supplies more context.

A subtitle may not be necessary if the page title already states the comparison
clearly. Freshness or provenance text may later belong in a Note, data-as-of
treatment or seasonal landing treatment rather than a permanent subtitle.

### 7.2 PA Heading and Self-Contained Artifact Caption

A PA may need its own heading and optional subheading distinct from the
Navigation item and page Heading. This is especially important for tables and
charts because readers may visually jump straight to the artifact, share it, or
say "look at this table" without re-reading the whole page.

The PA heading/subheading should say exactly what the artifact presents under
the current option state. Some redundancy with the page Heading is acceptable.

For the new-banzuke page, the date is central to the reader's likely question.
During June, readers may be asking whether the June banzuke is out. The PA
heading should therefore foreground the dated banzuke itself.

Likely PA heading:

```text
The {Month} {Year} Banzuke
```

No PA subheading is needed by default. The Navigation context can carry that
this is the most recent banzuke; the PA heading identifies the object readers
want to see.

### 7.3 Default Table

The default table should read as a basic two-column east/west banzuke with a
movement column.

Likely default gloss:

| Feature | Gloss |
| --- | --- |
| `Shikona` | `Rikishi fighting name.` |
| `⇅` | `Banzuke movement. See Notes.` |

The existing disambiguation note for shikona with bracketed values is pertinent
and correctly not tied to a single column heading. The bracketed value currently
uses a SumoDB id to disambiguate rikishi with the same shikona. A future public
version may use a more meaningful disambiguator, such as a surname.

### 7.4 Previous Basho Context

`Previous Basho` is understandable as an option label.

When enabled, the `Result` column contains compact strings representing:

- win/loss/absence score;
- prizes, where present;
- movement into or out of a broad rank group, where present.

The trailing arrows in `Result` do not mean the same thing as the default
movement column.

`⇅` column:

```text
movement up or down in banzuke slot order
```

`Result` trailing arrow:

```text
movement between broad rank groups
```

The phrase `rank group` is preferred over `division` here because Yokozuna,
Ozeki, Sekiwake, Komusubi and Maegashira are not normally called divisions, even
though the display needs a shared term for `Y`, `O`, `S`, `K`, `M`, `J`, and the
lower divisions.

Likely gloss:

```text
Result arrows mean rank-group movement. See Notes.
```

Likely Note direction:

```text
In Result, arrows show movement between broad rank groups such as Maegashira,
Komusubi, Sekiwake, Ozeki, Yokozuna or the lower divisions. This differs from
the movement column, which shows movement up or down in the banzuke slot order.
```

The compact 2.1 `Result` string is a pragmatic presentation, not the preferred
general result model. The 7.1 table separates result into subcolumns, which is
currently preferred where the table structure can support it.

2.1 follow-up:

```text
Make the 2.1 `Result` presentation follow the 7.1 pattern where possible:
separate wins, losses, absences and prizes into compact terminal columns rather
than presenting a single compact result string.
```

The same rule should be applied to any other table PA that exposes a `Result`
column: prefer the 7.1 decomposed result shape unless the specific table has a
strong reason to stay compact.

### 7.5 Delta

`Delta` is probably not an ideal option label, but no very short replacement is
currently better. It can stay if supported by gloss.

Likely option and column gloss:

```text
Size of movement. See Notes.
```

Current preferred Note wording:

```text
Delta measures how many east/west banzuke slots a rikishi moved. A full
numbered rank change, such as M2e to M3e, counts as two slots.
```

This is intentionally less technical than `half-rank` language because the
readers most likely to need the Note are likely to be the least technical.

Advanced wrinkle:

Banzuke structure is not fixed. For example, a move from `S2e` to `S1e` can
look different depending on whether the previous or current banzuke includes an
`S2e` slot. The movement size is measured relative to the previous banzuke.

This should not be pushed into the basic Note. A future expert-facing link may
be added at the end of the Note:

```text
Advanced
```

where the target is a future `For Experts` or methodology page.

### 7.6 Equelo Ratings

`Equelo Ratings` introduces a model concept that new readers will not already
understand. Its explanation is bigger than the current PA.

Likely option and column gloss:

```text
Model rating. See Ratings & Models.
```

Local Note direction:

```text
Equelo is an experimental rating model used by Sumo Lab. Treat it as analytical
context, not as an official rank.
```

The deeper target should be a future `Ratings & Models` introduction or quick
guide. `Typical Equelo Ratings` under `6.1 Rating Overview` is likely relevant
supporting material.

---

## 8. 2.2 Rolling Wins-Based Ranking Review

The second microscope pass considered the page currently known as Standings by
Wins.

This page is not a normal Current Sumo standings page. It is a research view
over a transparent wins-based ranking idea. Many ordinary sumo readers may
reasonably object that sumo does not work this way. That objection is correct:
the page is a research lens, not an account of ordinary banzuke-making.

Working classification:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B only when already curious about chii/rating semantics

Default reader expectation
  Not Type A
```

The table itself is simple. The complexity is interpretive, not mechanical.
The page should therefore be framed clearly as research, but the immediate
caption and controls should still be straightforward where the ideas are
straightforward.

### 8.1 Navigation, Page Heading and Subtitle

`Standings by Wins` is an odd title in the current site because `standings` is
not a settled site-wide word. `Ranking` is likely clearer.

Settled working wording:

```text
Title
  Rolling Wins-Based Ranking

Subtitle
  Rikishi ranked by average wins over a selected number of recent basho.
```

The title is deliberately straightforward even though the page belongs in a
research section. The table's basic idea is simple; the research status comes
from the interpretation and context.

### 8.2 PA Heading and Option-Aware Caption

Tables and charts should be self-contained as artifacts. The PA heading and
optional subheading should say exactly what is being presented under the
current option state.

For this page, likely PA caption shape:

```text
PA heading
  Rolling Wins-Based Ranking for the {Division} Division

PA subheading
  Over the last {num_basho} basho
```

This creates some redundancy with the page Heading, but that is acceptable
because readers may focus directly on the PA.

### 8.3 Filters

`Combined` should probably become `Both`.

The other current filter labels are broadly clear enough for now:

- View;
- Number of Basho;
- Active Rikishi Only;
- Division.

`Active Rikishi Only` should not have a PA Note merely because the option needs
a caveat. It can have an option popover instead.

Likely option gloss:

```text
When off, longer windows may include retired rikishi.
```

This is a local option explanation, not a PA Note.

### 8.4 Table Notes

The current first Note is legacy. It should no longer explain that reported
Shikona and Chii pertain to the latest basho. The useful current issue is
disambiguation where a shikona is followed by a number.

Likely replacement Note:

```text
`Shikona` values followed by a number identify rikishi who have shared the same
fighting name.
```

`Active Rikishi Only` no longer needs a PA Note because activity is not a
visible table column. Its caveat belongs in the option popover above.

The remaining Notes are broadly right for now, with wording polish:

```text
`Wins` include fusensho.

`Bouts` means the expected number of scheduled bouts in the selected window.
```

The existing `Bouts is ...` wording is clumsy and should be replaced.

### 8.5 Special Text Treatment for UI Tokens

Where Notes refer to exact column headings, option labels or other visible UI
tokens, those labels should receive a special text treatment. In this document,
backticks such as `` `Bouts` `` mean "the chosen special UI-token treatment",
not necessarily final literal monospace styling.

Such token references are singular. For example, write about `` `Bouts` `` as
the column heading token even though the ordinary English word is plural.

## 9. 3.3 Rikishi History Review

The third microscope pass began with the page currently known as Career
Comparisons.

Working Navigation-item classification:

```text
public deliverable
```

This page is definitely intended as a deliverable. Unlike many current
Navigation-tree entries, it is not merely a placeholder or navigation-shape
experiment.

The current name, `Career Comparisons`, is correct but clunky. The first thing
readers likely want is to see one rikishi's history or trajectory. As soon as
they see one trace, they naturally want to compare it with another rikishi, but
comparison is the next use case rather than the base concept.

Candidate naming direction:

```text
Rikishi History
Rikishi Trajectory
```

The current preference is to call the page something beginning with `Rikishi`,
then let the page subtitle and PA caption clarify the exact scope.

Working classification:

```text
Depth
  Basic+ or Advanced, pending final framing

Primary user type
  Type B - Enthusiast

Secondary user type
  Type C when Equelo or compressed chii/rating comparisons are used
```

The base chart should be understandable to an interested sumo fan looking up a
rikishi. The comparison and rating options add depth.

### 9.1 Navigation, Page Heading and Subtitle

Working title:

```text
Rikishi History
```

Working subtitle:

```text
Progress from hatsu dohyo to current date/intai.
```

This needs wording polish, but records the intended meaning: the page shows a
rikishi's career progress from first appearance to the latest available date or
retirement.

### 9.2 Empty Selection State

When no rikishi are selected, the current page says:

```text
Select one or more rikishi.
```

This is blunt, but acceptable as a first empty-state instruction because it
tells the reader both what to do and that multiple rikishi can be selected.

### 9.3 PA Heading and Option-Aware Caption

The PA heading should not remain `Career Comparisons` once the page is renamed.
It should state the selected subject in a self-contained way.

For one selected rikishi:

```text
{shikona} History
```

or:

```text
Career History for {shikona}
```

The second form extends naturally to multiple rikishi:

```text
Career History for {list}
```

where `{list}` might be `X, Y and Z`.

Likely PA subheading:

```text
({earliest_date} to {last_date})
```

This makes the chart self-contained when the reader focuses directly on the PA.

### 9.4 Options Gloss

The chart options need compact gloss because the controls are terse and the
two-dimensional option table is not self-explanatory on first contact.

Candidate option gloss:

| Option token | Gloss |
| --- | --- |
| `Date` | `Use calendar date on the x-axis.` |
| `Hatsu` | `Use basho since first appearance on the x-axis.` |
| `Chii` | `Show chii achieved.` |
| `Equelo` | `Show rating achieved.` |
| `Both` | `Show chii and rating together.` |
| `Compress` | `Compress lower banzuke divisions.` |

`Log` should probably be renamed to `Compress`. Its current meaning is too
technical for the visible option label. The popover can explain what is being
compressed without exposing the implementation detail first.

### 9.5 Notes

The existing Career Comparisons Note is necessary, but too long in its current
form for the current Notes treatment.

Current meaning to preserve:

```text
Some obscure pre-1989 lower-division chii are outside the Equelo bout-data
rating domain; Equelo traces omit points without a rating.
```

This is a PA-level remark because it explains the plotted artifact and missing
points in one of its supported representations. It is not an Options Note.

The stronger ownership rule is:

```text
The Notes panel is for remarks pertaining to the PA artifact, not the
ContentPanel as a whole.
```

This reinforces the existing rule that Options do not get Notes. Options may
have compact popover gloss. If selecting an option changes the PA in a way that
requires a PA-level caveat, the resulting visible PA state may make a PA Note
relevant.

### 9.6 Chart PA Detail Review

This is the first chart reviewed under the Notes/gloss procedure. The procedure
therefore needs to include chart-internal labels and layout details, not only
popover gloss and Notes.

For charts, review:

- PA heading and subheading;
- empty state;
- option labels and option gloss;
- x-axis title;
- y-axis title;
- tick label wording, density and formatting;
- legend title and legend entries;
- hover text;
- whether traces obscure labels or other explanatory text.

These are chart equivalents of table headings and table-cell conventions. They
are part of PA comprehension.

#### Chii by Date

Current y-axis title is wrong because `position` is redundant. The title should
probably be:

```text
Chii
```

or, when compressed:

```text
Chii (Compressed)
```

The y-axis layout needs real work. Compression should be smooth, with a
deliberate density of labels per pixel, and traces should not be plotted over
axis labels.

The x-axis title `Date` is acceptable. X-axis tick-label density still needs a
general chart treatment.

#### Chii by Hatsu

The same y-axis comments apply.

The x-axis title should be:

```text
Number of Basho since Hatsu Dohyo
```

or a shorter equivalent if space requires it. The current label should not
remain `Basho from hatsu` in public UI.

#### Equelo

The y-axis title `Equelo` is acceptable.

The x-axis title follows the same Date/Hatsu rules as the Chii charts. X-axis
tick-label density needs the same general treatment.

#### Both

The preceding Chii and Equelo comments apply. Dual-axis presentation needs the
same title, tick-label density and label-overlap review as the single-axis
charts.

The right y-axis title orientation should be reviewed. It may be easier to read
if rotated 180 degrees from the current orientation so it reads from top to
bottom, but this should be checked visually rather than decided abstractly.

#### General Chart Review Items

Axis titles are titles. Review whether they should consistently use title case,
for example:

```text
Chii (Compressed)
Number of Basho since Hatsu Dohyo
```

This is a general rendering/style question, not only a Career History question.

Chart tick-label density is also a general issue. The chart renderer should
avoid overcrowded date or ordinal labels and should choose a readable density
based on available pixel space.

Legend placement should be reviewed per chart PA rather than settled as a
single site-wide rule.

## 10. 7.1 Basho Results Review

The fourth microscope pass began with Basho Results, referred to as `7.1` in
the current Navigation numbering.

Working Navigation-item classification:

```text
public deliverable
```

Basho Results is a deliverable, but its ultimate table appearance has not yet
stabilised. It is a special recursive table, effectively a table of tables. The
recent design work explored how layout should flow from this structure and
raised a broader question: are ordinary tables also instances of a general
meta-table model?

Current design stance:

```text
Keep simple tables simple until the table-of-tables model and presentation are
fully nailed down.
```

The 7.1 recursive table model should not force ordinary flat tables into a more
complex representation before the specialised case is understood.

### 10.1 Navigation, Page Heading and Subtitle

The current Navigation entry, title and subtitle are broadly acceptable. They
feel somewhat clunky, but there is not yet a clear replacement wording.

No immediate gloss decision follows from the clunkiness. Leave wording open
until a better phrase emerges.

The PA/table heading itself is fine and needs no subheading. Delete the current
`Final` subheading.

### 10.2 Filters

`Basho` and `Division` need no gloss.

`Previous Basho` is acceptable as a label.

`Changes` should become:

```text
Next Basho
```

`Equelo Ratings` is obvious enough as an option label.

`nuChii` is legacy, but should be left in place for now.

`Analysis` was a placeholder and should not remain as public wording. The
feature is research-level, but valuable and fun for readers who know what it is
about. It opens the door to deeper questions such as:

```text
What is a chii?
Why not use a transparent wins/rating-based system?
```

The data behind `Analysis` is derived from comparing chii with rating in a
particular way. There is no simple option-level explanation. Since Options do
not get Notes, the option should use an external-guide popover rather than a PA
Note.

Likely popover shape:

```text
See <research section/page>.
```

The target should be a research/methodology section that explains the
calculation and interpretation. A full description such as `Reconciliation of
Banzuke with Ratings` is too long for an option label, but captures the
direction of meaning.

Settled public label for the option and table heading:

```text
Ratings Fit
```

Settled gloss:

```text
See TBD
```

The underlying idea is already documented in the Basho Results specification
and model docs as rating-order analysis, `BZ Error` / `DeltaBZ`, and `RBBP`.
The reader-facing intuition is:

```text
Take a banzuke at the start or end of a basho.
Rub out all the shikona.
Rank the rikishi by Equelo rating.
Fill the same banzuke slots greedily using that rating order.
Compare the resulting rating-order placement with the official banzuke
placement.
```

This is not how real banzuke movement works and is not a recommendation that
the JSA should build banzuke this way. It is a research comparison between two
orderings:

- official banzuke/chii order;
- Equelo rating order.

The useful question is:

```text
If Equelo is a reasonable measure of recent performance relative to opposition,
where does the official banzuke order differ from the rating order?
```

`DeltaBZ` is the size and direction of that difference. It can be read as the
number of banzuke slots the rikishi would move if the selected population kept
the same slots but were rearranged by rating.

`Eq Chii` / `RBBP` is the banzuke slot the rikishi would occupy under that
rating-order rearrangement.

Examples of reader interpretation:

- an underperforming Ozeki whose `Eq Chii` is around `M3e` can be read as
  performing more like an M3 in the rating order;
- a Maegashira whose `Eq Chii` is `Y1e` can be read as showing stellar
  rating-order performance, even if real banzuke rules would not move them
  there.

This analysis deliberately relaxes real banzuke-making constraints such as rank
structure, promotion rules, rank-holding conventions, vacancies and committee
judgement. The feature should point to a research guide rather than trying to
explain all of this in an option popover.

Superseded candidate labels:

```text
Rating Order
Rating Reorder
Banzuke vs Rating
```

### 10.3 Table Structure and Captions

The caption `Reference` should be deleted, while leaving the corresponding
cells/columns present. The reference cell remains structurally useful, but the
visible group caption adds clutter or misleading emphasis.

Unlike the compact result string used in 2.1, the 7.1 `Result` presentation has
separate subcolumns. This is currently preferred where the structure is
available.

The extant Basho Results Notes are legacy and should be deleted/replaced.

Candidate table gloss and Notes:

| Feature | Gloss |
| --- | --- |
| `Result` group or compact result headings | `See Notes.` |
| `Eq` | `Equelo rating.` |
| `DeltaEq` | `Difference in rating.` |
| up/down movement heading | `See Notes.` |

`nuChii` is left in place for now, despite being legacy.

The `Result` subheadings can remain supercompact:

```text
W
L
A
<Prize emoji>
```

Likely `Result` Note:

```text
`Result` shows the number of wins, losses, absences and prizes.
```

Movement gloss should attach to the up/down heading, not separately to `Chii`
and `Div`.

Likely movement Note direction:

```text
`Chii` movement follows banzuke slot order. `Div` movement shows significant
movement: transitions between sanyaku levels and between banzuke divisions.
```

This needs wording polish, but preserves the 2.1 distinction between ordinary
banzuke movement and broad rank-group movement.

### 10.4 PA Rendering Findings

These findings are rendering-detail issues discovered while applying the
gloss/PA review procedure. They should not be confused with the framework
itself.

Specific 7.1 finding:

```text
Put the legend back on the right.
```

This is a PA-specific rendering issue, not a site-wide legend-placement rule.

## 11. 4.3 Banzuke Structure Facts Review

The next microscope pass began with `4.3.1` and `4.3.2`, currently Banzuke
Division by Era and Makuuchi Rank by Era.

Working category:

```text
Vaguely interesting facts you may not know
```

These are research-oriented historical structure exhibits. They are not
front-door current-sumo tools, but they are useful context for understanding the
shape of the banzuke. Examples of the intended reader payoff:

```text
There was a time when the lowest Maegashira rank was M13.
There was a time when there were more than 200 Jonokuchi rikishi.
```

They are also practically important when doing deeper research, for example
when asking what the structure of a next banzuke might be.

Working classification for both:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B when interested in historical banzuke facts
```

### 11.1 4.3.1 Banzuke Division by Era

The current title is wrong or at least unsatisfactory.

Recommended wording:

```text
Nav text
  Banzuke Structure by Era

Page title
  Banzuke Structure by Era

Page subtitle
  How the size and division makeup of the banzuke changed over time.

PA heading
  Average Banzuke Composition by Era

PA subheading
  Average rikishi per basho, grouped by division.
```

`Structure` is preferred for the Navigation and Page title because it names the
reader-facing subject: how the banzuke's broad shape changed over time.
`Composition` is better in the PA heading because the chart specifically shows
stacked division composition averaged by era.

The chart is simple, almost a noddy chart, but the fact it shows is important
background for research into banzuke structure and likely next-banzuke shape.

### 11.2 4.3.2 Makuuchi Rank by Era

Recommended wording:

```text
Nav text
  Makuuchi Structure by Era

Page title
  Makuuchi Structure by Era

Page subtitle
  How the lower edge of the top division changed over time.

PA heading
  Makuuchi Rank Appearances by Era

PA subheading
  Count of banzuke appearances at each Makuuchi rank.
```

`Makuuchi Structure by Era` matches the 4.3.1 structure wording while making the
scope clear. The PA heading is more exact because the chart appears to count how
often each Makuuchi rank appears across eras.

Alternative subtitle if plainer wording is wanted:

```text
How deep the Makuuchi ranks went in different eras.
```

## 12. 4.4 Division Persistence Review

The `4.4` item is currently called Division Stability.

Working Navigation-item classification:

```text
research/prototype deliverable
```

Working classification:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B if interested in banzuke movement and division churn
```

The current implementation is not quite "probability that a rikishi in a given
division stays in that division after a basho." It is retrospective division
persistence. For each anchor basho and division, it looks at the rikishi who
are currently in that division and asks how consistently they have been in the
same division over the current basho plus a previous lookback window.

Absence from the banzuke is excluded from a rikishi's denominator. Being on the
banzuke in another division counts against persistence in the anchor division.

### 12.1 Navigation, Page Heading and Subtitle

Recommended wording:

```text
Nav text
  Division Persistence

Page title
  Division Persistence

Page subtitle
  How consistently each basho's division members stayed in the same division across that basho and the previous 10.
```

`Persistence` is more exact than `Stability` because the chart is not measuring
whether the division as a whole is structurally stable. It measures how
persistent each anchor basho's division members have been over a retrospective
window.

### 12.2 PA Heading and Subheading

This page has only one chart, so the Page title/subtitle and PA
heading/subheading may feel redundant. However, the working policy is that PAs
should be standalone artifacts together with their Notes. For now, duplicate the
Page title/subtitle into the PA caption and accept the redundancy.

Recommended wording:

```text
PA heading
  Division Persistence

PA subheading
  How consistently each basho's division members stayed in the same division across that basho and the previous 10.
```

The explicit `10` should appear because the active site bundle is built with
`num_basho = 10`, meaning each point uses the anchor basho plus the previous 10
basho.

---

## 13. 4.5 First Chii Appearance Review

The `4.5` item is currently called First Chii Appearance.

Working Navigation-item classification:

```text
research/prototype deliverable
```

Working classification:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B if interested in historical data coverage and banzuke structure
```

The intention is to illustrate the 1989 data cliff in the available SumoDB-derived
bout data, especially for lower banzuke positions. The current chart does not
make that cliff especially clear, but the item is pure research and can remain
as-is for now.

No immediate gloss changes are proposed. If this page becomes a polished
research exhibit later, the review should focus less on local popovers and more
on whether the chart design actually exposes the intended data-coverage break.

---

## 14. 5.1 Finish Chances by Wins Review

The `5.1` item is currently called Finish by Chii.

Working Navigation-item classification:

```text
research/prototype deliverable
```

Working classification:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B if interested in transparent wins-based outcomes
```

This page is strongly tied to `2.2` and `6.3.1`. Together they form a research
cluster around the question "what if you only counted wins?" The shared key term
is `Wins`.

The chart answers threshold questions for a selected division and starting
`Chii`:

- in the `Top` view, how often rikishi at that `Chii` finished no worse than
  1st, 2nd, 3rd and so on by wins;
- in the `Bottom` view, how often rikishi at that `Chii` finished no better
  than worst, 2nd-worst, 3rd-worst and so on by wins.

The probabilities are empirical, based on historical appearances at the selected
`Chii`. The sample size should be referred to as `n`.

### 14.1 Navigation, Page Heading and Subtitle

If this item later sits under a `By Wins` heading in the Research section, the
Navigation label can be shorter:

```text
Research section heading
  By Wins

Nav text
  Finish Chances
```

While it stands alone outside a `By Wins` heading, use the shared keyword in the
Navigation label:

```text
Nav text
  Wins: Finish Chances

Page title
  Finish Chances by Wins

Page subtitle
  How often rikishi at a selected chii finished near the top or bottom of their division by wins.
```

`Finish Chances` is preferred to `Likely Outcome` because it describes the bars
without sounding too much like a prediction or a win/loss result.

### 14.2 PA Heading, Subheading and Axes

Recommended PA caption:

```text
PA heading
  {Division} {Chii}: {Top|Bottom} Finish Chances

PA subheading
  Historical probability of finishing at position N = 1,...,10 by wins; sample size n = {n}.
```

Use `N` for the finishing-position threshold shown on the x-axis. Reserve `n`
for the sample size. This avoids the current ambiguity where "n" can mean both
the threshold and the number of observations.

Recommended axis captions:

```text
Top x-axis
  Finish Position N, no worse than

Bottom x-axis
  Finish Position N, no better than

Y-axis
  Probability
```

Alternative shorter x-axis captions if the PA subheading carries the full
threshold explanation:

```text
Top x-axis
  Finish Position N

Bottom x-axis
  Finish Position N
```

The shorter version is cleaner, but only works if the `Top`/`Bottom` context and
PA subheading are visible and unambiguous.

---

## 15. 6.2.1 Typical Equelo Ratings Review

The `6.2.1` item is currently called Typical Equelo Ratings.

Working Navigation-item classification:

```text
public/research bridge deliverable
```

Working classification:

```text
Depth
  Advanced

Primary user type
  Type B - Enthusiast

Secondary user type
  Type C - Analyst / Specialist
```

The item is fine as currently framed. It is a landmark/reference table rather
than a table for exploratory sorting.

Columns should not be sortable. The section order and row order carry the
meaning: they present typical Equelo rating landmarks by rank area, not an
ordinary data set where reordering would help the reader.

---

## 16. 6.3.1 Win Probability by Ranks Review

The `6.3.1` item is currently called Win Probability by Standing.

Working Navigation-item classification:

```text
research/prototype deliverable
```

Working classification:

```text
Depth
  Research

Primary user type
  Type C - Analyst / Specialist

Secondary user type
  Type B if interested in what rank says about bout outcomes
```

This page belongs with `2.2` and `5.1` in the research cluster around wins.
It is not the same view as `5.1` with different axes: `5.1` asks where rikishi
at a starting `Chii` finished within a whole division by wins, while `6.3.1`
asks how often a selected rank beat an opponent rank in actual or predicted
bouts.

The key presentation problem is that the chart has two rank roles:

```text
selected rank
  the rank represented by the visible trace / legend item

opponent rank
  the rank on the x-axis
```

The word `Standing` should be replaced by `Rank` for public wording unless a
more precise term emerges. The underlying model may still use `selected_chii`
and `opponent_chii`, but the public page should speak in terms of ranks.

### 16.1 Navigation, Page Heading and Subtitle

Recommended wording:

```text
Nav text
  Win Probability by Ranks

Page title
  Win Probability by Ranks

Page subtitle
  How likely is one rikishi to beat another based on rank?
```

This is slightly blunt, but it keeps the visible title short and lets the chart
caption and axes carry the selected/opponent distinction.

### 16.2 Options

Recommended source option labels:

```text
Observed
Predicted
```

`Equelo` should become `Predicted`.

Likely popover for `Predicted`:

```text
Prediction based on Equelo rating.
```

`Division` is clear enough. `Error bars` applies naturally to `Observed` data
and may need either source-specific availability or a short popover if the
control remains visible for `Predicted`.

### 16.3 PA Heading and Axes

Recommended PA caption:

```text
PA heading
  Win Probability ({Observed|Predicted})

PA subheading
  none
```

The PA heading should switch with the selected source. No subheading is needed
if the axis titles and legend establish the two rank roles.

Recommended chart labels:

```text
Legend title
  Selected Rank

X-axis
  Opponent Rank

Y-axis
  P(selected rikishi wins)
```

This lets the chart read as:

```text
For each Selected Rank trace, show the probability that a rikishi at that rank
beats a rikishi at the Opponent Rank on the x-axis.
```

The current `P(selected standing wins)` is too opaque. `P(selected rikishi wins)`
is still compact, but makes the selected/opponent role structure visible.

---

## 17. Process for the Next Page Review

Use the same microscope process for the next Navigation item.

For each page:

1. Classify the Navigation item itself: public deliverable,
   research/prototype deliverable, future product idea, placeholder or
   navigation experiment.
2. Stop or defer if the item is not a current deliverable worth glossifying.
3. Identify the expected reader moment and likely entry route.
4. Classify the page or view by depth.
5. Classify the primary user type and any secondary/specialist edge.
6. Review the Navigation label in context.
7. Review whether the ContentPanel title should repeat or expand the Navigation
   label.
8. Decide whether a subtitle is necessary.
9. Review each Filter label under the assumption the reader understands the
   Navigation label and Heading.
10. Identify which Filters reveal semantically loaded PA features.
11. Review PA-internal labels under the full context of Navigation, Heading and
   selected Filters: table headings, chart axes, tick labels, legends, hover
   text, captions and empty states.
12. Decide whether each confusing feature needs better primary wording, short
   gloss, a local Note, an external guide link, or no explanation.
13. Keep popovers short; move long explanations into Notes or guide pages.

This process should reveal both page-specific wording decisions and general
rules worth promoting into the normative design documents.
