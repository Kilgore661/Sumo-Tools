# Equelo Fixed v1 Requirements

## Status

Initial requirements statement.

This package defines the first fixed project-level Equelo rating series.  It is
not specific to any downstream report or application.  The Banzuke Change
Report may consume it, but it does not define it.

## Purpose

The project needs an efficient way to know the Equelo rating of any represented
rikishi at any represented point in time from January 1958 onward.

The rating series is derived data.  It is computed from the canonical sumo
`History` plus a documented Equelo model specification.  It is not an observed
historical fact and is not currently part of `History`.

## Core Requirement

For a fixed model version, the Equelo layer shall provide ratings for rikishi
through time without requiring callers to rerun the full rating computation.

At minimum, callers shall be able to obtain:

- basho-start ratings for all active rikishi on a basho banzuke;
- day-end ratings for all active rikishi after each represented competition
  day;
- the rating for a specified `RikId` at a specified represented point;
- enough model metadata to know exactly which rating definition produced the
  numbers.

## Persistence Requirement

The generated rating series shall be persisted as project data under
`files/output/Equelo`.

JSON is preferred for the first implementation because the rating series is
naturally sparse and nested by basho date, day, and rikishi id.

The persisted data shall include:

- date;
- day or phase;
- rikishi id;
- rating;
- model version metadata, either in a separate metadata file or repeated in a
  controlled way.

The persisted rating data should not duplicate chii, shikona, or banzuke
membership because those are derivable from `History`.

## Model Definition Requirement

`fixed_v1` shall define a single project-level meaning for "Equelo rating".
The definition must name all parameters and source artefacts needed to reproduce
the series.

The intended first model definition is:

- source history: cleaned history from January 1958 onward;
- simulator: the existing Expt1 Elo-like simulator;
- interpretation: Expt3c-style sequential bout processing;
- mode: closed;
- entrant policy: scaled fixed-point initialisation;
- fixed-point source: Expt2 combined final chii ratings;
- alpha: approximately `0.55`;
- logistic scale `q`: `900`;
- K policy: divisional;
- K config: `files/input/elo_fide.json`;
- chii collapse mode: annotation-only.

The implementation may refine path names and exact metadata fields, but any
change to the model definition must be explicit.

## Justification Requirement

The package documentation shall explain why this model version was chosen.

The explanation should be honest and practical:

- the project needs stable rating numbers for downstream tools;
- constant entrant initialisation is a useful baseline but creates a long
  settling period;
- fixed-point chii ratings provide plausible rank-aware initial values;
- scaling the fixed-point values avoids over-dispersed priors;
- retained experiments show reasonable calibration, Brier performance, and
  robustness under parameter sweeps;
- the model is not claimed to be final, causal, or uniquely correct.

The documentation should not undersell the work.  These ratings are
experimental, but they are the result of a coherent series of tests rather than
arbitrary decoration.

## Update Requirement

The rating series shall be regenerated when its inputs change.

For the first implementation, a batch command that regenerates the full
`fixed_v1` rating series is sufficient.  Later work may integrate this command
with the tracker so ratings are refreshed automatically when `History` changes.

Tracker integration is allowed to remain separate from the live store decision.
The live store may continue to publish only canonical `History`, while ratings
remain a derived persisted artefact.

## Non-Goals

This package does not:

- make Equelo ratings part of the canonical observed `History`;
- define every future Equelo model;
- prove that `fixed_v1` is the best possible rating system;
- replace the banzuke or other institutional rankings;
- require downstream tools to recompute ratings.

## First Consumers

The Banzuke Change Report is expected to be the first consumer of `fixed_v1`.
That use case should help validate the API and output format, but the package
contract remains project-level rather than report-specific.
