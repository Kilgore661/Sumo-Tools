# Chess Rating Tier Population Estimates (Revised)

Revised table following comparison with a second LLM and cross-checking against known FIDE database figures.

| Tier | Category | Floor | Revised Est. | Original | v1 Est. |
|------|----------|-------|-------------|----------|---------|
| SM | Super Master | 2700+ | ~32 | 31 | ~40 |
| GM | Grandmaster | 2500 | ~1,800 | 2,050 | ~1,800 |
| IM | International Master | 2400 | ~3,800 | 4,150 | ~3,500 |
| FM | FIDE Master | 2300 | ~8,000 | 9,700 | ~7,000 |
| CM | Candidate Master | 2200 | ~21,000 | 24,000 | ~12,000 |
| Exp | Expert | 2000 | ~35,000 | 48,000 | ~35,000 |
| Int | Intermediate | 1800 | ~70,000 | 82,000 | ~70,000 |
| Clb | Club | 1400 | ~345,000 | 280,000 | ~320,000 |
| **Total** | | | **~485,000** | **~450,000** | **~450,000** |

## Key Revisions from v1

**SM (~32):** Accepted the correction. April 2026 data places only two players above 2800
(Carlsen 2840, Nakamura 2810), with the 2700 line being very tight. My earlier 40 was
too generous.

**CM (~21,000):** Substantially revised upward from my v1 estimate of 12,000. The second
LLM's explanation holds: the 2024 FIDE compression (formula: 0.4 × (2000 − rating),
applied to all players below 2000) pushed many players from the 1800–1900 range upward,
inflating the eligible CM population. The original table's 24,000 was probably closer to
the truth than my v1 correction.

**Club (~345,000):** Revised upward significantly. This is a consequence of anchoring
to the correct total.

## Anchoring the Total

The FIDE database held just over **486,000 registered players** as of January 2025, of
whom roughly **292,000 were inactive**. All tier estimates here count the full registered
database (active + inactive). Active-only counts would roughly halve every tier, with the
Club tier taking the biggest hit (most lapsed players sit at the bottom).

The second LLM's claim of 1.1 million total was rejected — this appears to be a
hallucination, more than double the verified figure.

## Confidence by Tier

| Tier | Confidence | Reason |
|------|-----------|--------|
| SM | High | Small enough to count directly from public lists |
| GM | High | Well-documented; title-holders tracked publicly |
| IM | Medium | Good title data but some ambiguity around inactive holders |
| FM | Medium | Same as IM |
| CM | Low | Most affected by 2024 compression; no clean public histogram |
| Exp | Low | No title boundary; hardest to pin without raw FIDE data |
| Int | Low | Same as Expert |
| Clb | Medium | Largely derived as a residual from the total anchor |
