# Elo-89 normalisation diagnostics

This package will quantify the contribution of population normalisation to
published Elo-89 rating changes. Its purpose is to give the author numbers,
distributions and concrete examples with which to judge practical importance.
It is not a model-selection gate, and an appreciable effect does not by itself
require changing the accepted model.

**Status: proposal only.** The package contains no executable analysis yet.

Read [the implementation proposal](docs/Proposal.md) for the questions, input
contract, accounting definitions, proposed outputs and verification requirements.
The motivating appraisal is
[Elo-89 Rating System Appraisal](../docs/story/22%20Elo-89%20Rating%20System%20Appraisal.md).

The proposed analysis reads existing production Elo-89 artifacts and matching
History metadata. It writes only to its own output directory. It does not
modify the rating calculation, recompute P1, regenerate the website or deploy
anything. The initial experiment concerns observed rating-change accounting;
a replay without normalisation would answer a different question and is not
part of this proposal.
