Add this section to the proposal:

---

# 14. Why This Should Work

The proposed `variant_publisher.py` works because each run of the standings calculation can be understood as producing one complete metric regime.

The same table structure can therefore be reused across regimes.

## 14.1 Parameter Choices Change the Numbers

Changing `WinsPolicy` changes what counts as a win.

For example:

* with fusensho included, fusensho contribute to Wins
* with fusensho excluded, fusensho do not contribute to Wins

Changing `BoutBasis` changes what counts as a bout.

For example:

* with expected bouts, Bouts reflect expected opportunity
* with available bouts, Bouts reflect actual available contest opportunities

Because derived metrics are computed from these regime-specific values, changing the parameters also changes downstream values such as:

* Average
* Bouts
* Win %

Each generated CSV therefore contains values that are already correct for its own regime.

## 14.2 Stable Column Headings Still Make Sense

The column headings do not need to encode every selected policy.

The headings name the metric family:

* Wins
* Average
* Bouts
* Win %

The selected expert options define the exact meaning of those metric families.

So **Wins** means “wins under the currently selected WinsPolicy”.

**Bouts** means “bouts under the currently selected BoutBasis”.

**Win %** means “Wins divided by Bouts under the current regime”.

This avoids cluttered headings such as:

```text
Wins excluding fusensho
Bouts available excluding fusenpai
Win % under selected policy combination
```

## 14.3 The Dataset Is Internally Coherent

The key requirement is that every file-set is generated consistently.

A dataset generated for:

```text
WinsPolicy = exclude fusensho
BoutBasis = available
```

must compute all displayed values under exactly that interpretation.

The browser then only needs to load the correct dataset. It does not need to repair or reinterpret mixed metrics.

## 14.4 Expert Options Provide the Context

Because these settings belong in an advanced/expert area, the user can be expected to understand that changing options changes the meaning of the numbers.

The UI should still provide notes or gloss, but the table itself can remain clean.

## 14.5 Practical Consequence

The browser can keep using the same column layout across all variants.

Only the loaded file-set changes.

That is the central reason the approach is attractive: different regimes produce different numbers, while the table grammar remains stable.

