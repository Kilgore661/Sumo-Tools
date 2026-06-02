# Shikona Normalisation Proposal

## Status

Proposal note.

This document records a proposed policy for public shikona display and
disambiguation. It is not an implementation plan. It belongs in
`src/products/docs` while the issue is still being shaped. Once the policy is
settled, the relevant contract should be integrated into
`src/products/make_site2/docs`.

---

## 1. Problem

Shikona are not unique.

This affects public display, search, selectors, links, persisted site-facing
artifacts and integrity checking. A public product cannot safely treat a
shikona string as rikishi identity.

The immediate trigger is rikishi selection for the Rikishi Skill Trajectory
chart, but the issue is broader than that chart.

---

## 2. Identity

The underlying identity is rikishi id.

Normalised shikona are display and search values. They are not identity values.

Any selector, link, chart trace or table row that needs a stable rikishi
identity should carry rikishi id, even when it displays a normalised shikona.

---

## 3. Last-Known Shikona Policy

The public display policy is to use the rikishi's last-known shikona.

This name is applied retroactively in public display. If rikishi `1234` joined
in March 1980 as `Fred`, then changed shikona to `Jim` in January 1985, public
display may refer to him as `Jim` even for basho before January 1985.

The rationale is public lookup and recognition. Readers will usually search for
and recognise rikishi by the latest name known to the site, not necessarily by
the period-accurate shikona used on an earlier banzuke.

This is a deliberate tradeoff. A reader who knows that `Jim` was called `Fred`
before 1985 may be surprised, but that surprise is accepted by the policy.

The policy is historical and data-instance-relative: "last-known" means
last-known in the selected History or data instance used to produce the product.

---

## 4. Disambiguation

When the last-known shikona is unique across the selected History, display it
without a suffix.

When the last-known shikona is not unique, disambiguate every rikishi using that
last-known shikona. The first rikishi using the shikona is not exempt.

The proposed disambiguator is the rikishi's hatsu date, not:

- rikishi id;
- the date when the shikona was first used;
- the date when the rikishi changed into the shikona.

Example:

```text
rikishi 1234:
  hatsu: March 1980
  first shikona: Fred
  changed to: Jim in January 1985

normalised display: Jim (1980)
```

If there was an earlier rikishi known as `Jim` whose hatsu was in 1960, that
rikishi is also disambiguated:

```text
Jim (1960)
Jim (1980)
```

The display format for the hatsu suffix is still open. The examples use year
only.

---

## 5. Recalculation

Normalisation must be recalculated when the selected History changes in a way
that can affect last-known shikona or shikona uniqueness.

Examples:

- a new rikishi joins;
- an existing rikishi changes shikona;
- a different History/data instance is selected for a product build.

This matters because a once-unique shikona can become non-unique. When that
happens, all affected display names must change together.

---

## 6. Persistence and Integrity

Normalised shikona are likely to be persisted in some site-facing artifacts.

If persisted, they create an integrity duty. The site integrity checker should
verify that persisted normalised shikona remain coherent with the selected
History or data instance.

At minimum, integrity checking should detect:

- persisted normalised shikona derived from stale last-known shikona;
- missing disambiguation after a shikona becomes non-unique;
- unnecessary disambiguation after uniqueness changes, if that state can occur;
- suffixes that do not match the rikishi's hatsu value under the adopted
  display format.

---

## 7. Same-Time Duplicate Assumption

The proposal assumes that two active rikishi have never had the same shikona at
the same time.

This should be checked against History. It should not be treated as permanent
folklore.

If the assumption is false, the normalisation policy needs further design.

---

## 8. Open Questions

- Should the disambiguating hatsu suffix use year only, basho date, or another
  compact date format?
- Which producer or product layer owns deriving normalised shikona?
- Which artifacts should persist normalised shikona, and which should derive
  them at build/render time?
- What exact integrity-checker command should audit persisted normalised
  shikona?
- Has any pair of active rikishi ever shared the same shikona at the same time?

