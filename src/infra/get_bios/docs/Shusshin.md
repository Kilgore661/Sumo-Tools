# Japanese `Shusshin` entries from SumoDB

A `Shusshin` value appears to represent one or more hierarchical Japanese geographical location paths.

The entries are not free-form prose. They appear to follow a mostly machine-generated or at least strongly standardized structure.

Examples:

```text
Aichi-ken
Aichi-ken, Aisai-shi
Aichi-ken, Ama-gun, Saya-cho
Akita-ken, Senboku-gun, Sennan-mura - Akita-ken, Senboku-gun, Misato-cho
```

---

# Proposed Grammar

## High-level grammar

```text
Shusshin ::= Place (" - " Place)*
```

Meaning:

* a `Shusshin` entry consists of one or more `Place` values
* multiple places are separated by a hyphen-like delimiter surrounded by spaces

The interpretation of multiple `Place` entries is believed to be:

```text
historical municipality -> newer/current municipality
```

rather than alternative birthplace descriptions.

---

## Place grammar

```text
Place ::= Component (", " Component)*
```

Meaning:

* a `Place` is an ordered list of geographical components
* components proceed from coarse geography to fine geography

Examples:

```text
Aichi-ken
Aichi-ken, Aisai-shi
Aichi-ken, Ama-gun, Saya-cho
```

---

# Administrative Components

The following suffixes are commonly observed.

| Suffix            | Meaning          |
| ----------------- | ---------------- |
| `-to`             | Tokyo metropolis |
| `-do`             | Hokkaido         |
| `-fu`             | urban prefecture |
| `-ken`            | prefecture       |
| `-gun`            | district/county  |
| `-shi`            | city             |
| `-ku`             | ward             |
| `-cho` / `-machi` | town             |
| `-mura` / `-son`  | village          |

Not all entries contain all levels.

Examples:

```text
Aichi-ken
```

prefecture only.

```text
Aichi-ken, Aisai-shi
```

prefecture + city.

```text
Aichi-ken, Ama-gun, Saya-cho
```

prefecture + district + town.

---

# Ordering Constraint

Within a `Place`, components are believed to proceed from larger administrative unit to smaller administrative unit.

Typical progression:

```text
prefecture
→ district
→ city/town/village
```

though not all levels are always present.

This ordering should be treated as a validation heuristic rather than a strict parser requirement.

---

# Interpretation of Hyphen-Separated Places

Examples:

```text
Aichi-ken, Atsumi-gun, Atsumi-cho - Aichi-ken, Tahara-shi
```

```text
Akita-ken, Senboku-gun, Sennan-mura - Akita-ken, Senboku-gun, Misato-cho
```

These are believed to represent municipality mergers or administrative renaming.

Interpretation:

```text
OLD MUNICIPALITY -> CURRENT MUNICIPALITY
```

For example:

```text
Akita-ken, Senboku-gun, Sennan-mura
```

was likely merged into:

```text
Akita-ken, Senboku-gun, Misato-cho
```

during Japanese municipal reorganizations.

Thus:

```text
Place1 - Place2
```

should be interpreted as:

* historical designation
* followed by modern/current designation

rather than:

* ambiguous alternatives
* or a single longer hierarchy

---

# Parsing Strategy

Recommended parser strategy:

1. Split `Shusshin` on spaced hyphen separators:

```regex
\s+[-‐-‒–—―]\s+
```

2. Treat each resulting part as a `Place`

3. Split each `Place` on:

```text
", "
```

4. Preserve original strings exactly

5. Optionally classify components by suffix

6. Optionally validate ordering heuristically

---

# Important Caveats

The above model is believed to describe mainland Japanese entries reasonably well, but exceptions likely exist.

Potential complications include:

* foreign birthplaces
* historical geopolitical entities
* islands/subregions
* military bases
* informal/localized naming
* inconsistent historical data entry
* municipality mergers and dissolutions

Therefore:

* the grammar should be permissive
* validations should produce diagnostics rather than hard failures
* original strings should always be preserved losslessly.

