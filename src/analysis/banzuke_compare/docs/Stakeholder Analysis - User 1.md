# Stakeholder Analysis: User 1

## Status

Requirements-capture note from an early stakeholder conversation.

This document records one strong stakeholder viewpoint. It should not be read as
the complete product scope for `news`. It captures one user's preferred way of
seeing "the new banzuke" when a fresh banzuke is published.

The wider scoping exercise remains open. Other users may prefer headline
summaries, individual rikishi lookup, division churn reports, promotion stories,
CSV exports, or other views.

## 1. Stakeholder Profile

User 1 is interested in understanding a newly published banzuke through a dense,
traditional banzuke-shaped table.

The stakeholder is comfortable with sumo-specific notation and does not need
the display to explain basic terms such as `Y1`, `O1`, `M3`, or east/west
placement. They prefer the display to preserve the feel of a banzuke rather than
turning the data into a generic dashboard.

This user values:

- compactness
- direct comparison with the previous basho
- a traditional east/west layout
- visibility of previous rank and result
- a local movement signal
- editable HTML/CSS assets that can be refined outside the generator

## 2. Core User Need

When the new banzuke comes out, User 1 wants to see the new banzuke and the
previous-basho context in one place.

The central question is:

```text
What does the new banzuke look like, and how did each rikishi get there?
```

This differs from a pure news-headline view. The stakeholder is not asking only
for "who got promoted?" or "what are the biggest stories?" They want a full
table that allows the reader to scan and infer stories directly.

## 3. Preferred Display Concept

The preferred display is a divisional, traditional east/west banzuke table.

The current concept is documented in:

```text
src/analysis/news/docs/Banzuke Display Specification.md
```

The editable mock assets are currently:

```text
src/analysis/news/files/banzuke_news_mock.html
src/analysis/news/files/banzuke_news_mock.css
```

The rough visual structure is:

```text
East: old rank | previous result | delta | shikona
Rank
West: shikona | delta | previous result | old rank
```

The centre `Rank` column contains `bz_chii` values such as:

```text
Y1
O1
S1
M3HD
```

`bz_chii` is a display row heading, not a core-model `Chii`.

## 4. Captured Requirements

### Traditional Banzuke Shape

The table should retain the familiar east/rank/west layout. This is important
because the stakeholder expects readers to understand banzuke structure by eye.

### Division-Based Rendering

The display should be organised by division. The first mock focuses on
Makuuchi, but the concept should extend to other divisions.

### Dense Layout

Rows should be vertically compact. The final table may contain many more than
five rows, so generous dashboard spacing is not appropriate.

### Dark Theme

The stakeholder favours a dark theme for this output. Body text should be plain
white, with headings bold but not otherwise typographically exotic.

### Previous Rank

For each current rikishi, show the previous full `Chii`, e.g. `Y1w` or `M7w`.

### Previous Result

Show the previous basho result, including absences where they occur:

```text
8-7
8-6-1
11-4 J
10-5 JS
```

Multiple prizes should be concatenated, not comma-separated.

### Local Movement Delta

Show a movement column headed with capital Greek delta:

```text
Δ
```

The delta is pair-local and computed over observed `Chii` slots in the compared
banzuke pair. It is useful for the display, but not a universal rank-distance
metric.

### Colour Encoding

Delta should be colour-coded:

- green for upward movement
- red for downward movement
- neutral for unchanged/unavailable
- saturation based on `abs(delta)`

Initial saturation bands:

```text
low:  abs(delta) 0.5 to 1.5
mid:  abs(delta) 2.0 to 3.0
high: abs(delta) 3.5 and above
```

### Annotated Rows

Annotated chii should be treated as normal display row headings with the side
removed and annotation preserved:

```text
M3eHD -> M3HD
M3wHD -> M3HD
```

Annotated rows may have only one side populated.

### Editable Static Assets

The HTML/CSS mock lives under `src/analysis/news/files` because it is intended
to become an input to a publishing/deployment app.

The stakeholder wants to be able to edit fixed structure and styling in a
WYSIWYG or normal HTML/CSS editor, and have those changes picked up by the
generator later.

## 5. Things Deferred For This Stakeholder View

The first table concept deliberately defers:

- entrants section
- exits section
- career-high stories
- returns after absence
- "hot prospect or journeyman" classification
- promotion/demotion narrative text
- performance-consistency judgement
- historical comparison of movement magnitude
- individual rikishi search
- CSV or data export

These may still be in scope for the broader `news` package. They are just not
part of this first captured table concept.

## 6. Product Scope Caution

This stakeholder view is strong but narrow.

It should inform a "new banzuke" option, but it should not be allowed to define
the entire `news` product. The scoping exercise should still consider other
stakeholders and other ways of consuming banzuke news.

Possible additional product modes include:

- headline summary
- division movement report
- promotion/demotion report
- individual rikishi lookup
- career milestone report
- performance-surprise report
- machine-readable export

The current mock is best treated as a concept prototype produced during
requirements capture, not as final proof that all users want this exact page.

## 7. Implementation Implications

The captured concept suggests a future split between:

- fixed HTML/CSS assets
- dynamic basho title/date
- dynamic division sections
- dynamic banzuke rows
- dynamic movement classes

The generator will eventually need a clear boundary between the editable static
parts and the injected data.

Likely dynamic row fields:

- current `bz_chii`
- east/west shikona
- east/west old chii
- east/west previous result
- east/west delta
- east/west delta colour class

The mock should remain a design aid until the data model and renderer are ready.
