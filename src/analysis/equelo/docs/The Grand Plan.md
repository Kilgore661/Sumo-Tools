Here’s a revised draft that incorporates your key correction about **torikumi**, keeps the tone neutral, and frames the proposal as an optional analytical tool rather than a reform agenda.

---

# Proposal: An Elo-like Rating System for Professional Sumo

## Status

Historical / deletion candidate.

This draft is early proposal material, not current Equelo implementation
guidance. Preserve only if needed for archive archaeology.

---

## 1. Purpose

This document outlines a proposal for implementing an Elo-like rating system for professional sumo as a supplementary tool for analysing relative competitive strength.

The aim is not to replace existing structures—particularly the Banzuke—but to provide an explicit, transparent method for deriving a global ordering from observed bout results.

---

## 2. Structural Observations

Professional sumo has several defining features:

- Wrestlers compete in discrete tournaments (basho), not a continuous league season

- Within a basho, each wrestler faces a limited number of opponents

- Match pairings (the Torikumi) are not fixed in advance but depend on:
  
  - current rank (banzuke position)
  
  - ongoing performance within the tournament

As a result:

> The set of observed comparisons is not predetermined, but is itself shaped by institutional decisions.

This has two consequences:

1. Wrestlers do not face a common set of opponents

2. The mapping from results to a global ordering is not uniquely determined by results alone

At present, this underdetermination is resolved through established practices governing both torikumi and banzuke construction.

---

## 3. Motivation

If one wishes to obtain a ranking that:

- reflects **current relative competitive strength**

- is **consistent across divisions** (e.g. Makuuchi and lower tiers)

- is **explicit and reproducible**

then an additional formal mechanism is required to resolve the ambiguity inherent in the results.

An Elo-like rating system provides one such mechanism.

---

## 4. Conceptual Framework

The proposed system follows the general principles of the Elo rating system:

- Each wrestler is assigned a numerical rating

- Each bout is treated as evidence about relative strength

- Ratings are updated after each bout based on:
  
  - expected outcome (from rating difference)
  
  - actual outcome (win/loss)

Thus:

> Ratings represent an inferred ordering over the population, derived from the network of observed bouts.

---

## 5. Key Properties

An Elo-like system would have the following characteristics:

### 5.1 Global Comparability

- Ratings allow comparison between wrestlers who have not directly faced each other

- Information propagates through chains of opponents

### 5.2 Responsiveness

- Ratings evolve continuously as new bouts are observed

- Recent performance can be weighted more strongly if desired

### 5.3 Consistency

- Identical results lead to identical updates

- The system is fully specified in advance

### 5.4 Independence from Scheduling

- The system accepts torikumi as given

- It does not require a round-robin structure

---

## 6. Relationship to Existing Structures

This system is intended to be **complementary**.

### Banzuke

- Remains the official ranking for organisational and ceremonial purposes

- Ratings provide an alternative, explicitly defined ordering

### Torikumi

- Remains unchanged

- The rating system treats pairings as input data

### Basho Results

- Tournament outcomes (e.g. yūshō winners) are unaffected

- Ratings provide additional context for interpreting those results

---

## 7. Interpretation

It is important to distinguish between:

- **Institutional rank** (banzuke position)

- **Inferred competitive strength** (rating)

The proposal concerns only the latter.

It does not assert that one should replace the other, but that:

> Where a global, model-based notion of relative strength is desired, an explicit rating system provides a transparent way to obtain it.

---

## 8. Implementation Outline

1. **Data Collection**
   
   - Historical bout results (ideally multiple years)

2. **Initial Ratings**
   
   - Assign baseline ratings by division or entry point

3. **Update Rule**
   
   - Standard Elo update after each bout
   
   - Optional tuning parameters (e.g. K-factor)

4. **Validation**
   
   - Compare predictive accuracy against observed outcomes
   
   - Examine consistency with banzuke movements

5. **Publication (Optional)**
   
   - Ratings released alongside or independently of official rankings

---

## 9. Limitations

- Ratings depend on modelling assumptions (e.g. transitivity of strength)

- Scheduling effects (torikumi) remain embedded in the data

- Numerical ratings may be less intuitive than rank titles

---

## 10. Conclusion

Professional sumo combines:

- selectively generated comparisons (via torikumi)

- periodic global ordering (via banzuke)

In such a system:

> Results alone do not uniquely determine a global ranking.

Any ranking therefore depends on an additional rule.

At present, this rule is implicit in established practice. An Elo-like system offers an alternative:

> an explicit, consistent, and analytically tractable method for deriving a global ordering from the same underlying data.

This proposal is intended as an optional framework for those interested in such an approach.
