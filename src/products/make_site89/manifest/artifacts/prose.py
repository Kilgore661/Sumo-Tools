"""Prose published artifacts."""

from __future__ import annotations

from ...artifact_model import ProseArtifact


WHAT_THIS_SITE_IS_ARTIFACT = ProseArtifact(
    id="what_this_site_is",
    heading="What this site is",
    kind="prose",
    renderer="prose",
    path="prose/What this site is.html",
)

WHY_RATINGS_ARTIFACT = ProseArtifact(
    id="why_ratings",
    heading="Why ratings?",
    kind="prose",
    renderer="prose",
    path="prose/Why ratings.html",
)

ELO_EXPLANATION_ARTIFACT = ProseArtifact(
    id="elo_explanation",
    heading="Elo Ratings",
    kind="prose",
    renderer="prose",
    path="prose/Elo Ratings.html",
)

ELO89_EXPLANATION_ARTIFACT = ProseArtifact(
    id="elo89_explanation",
    heading="Elo-89 Ratings",
    kind="prose",
    renderer="prose",
    path="prose/Elo-89 Ratings.html",
)

ELO89_ASSUMPTIONS_ARTIFACT = ProseArtifact(
    id="elo89_assumptions",
    heading="Assumptions",
    kind="prose",
    renderer="prose",
    path="prose/Elo-89 Assumptions.html",
)

ELO89_VS_CHII_ARTIFACT = ProseArtifact(
    id="elo89_vs_chii",
    heading="Elo-89 vs Chii",
    kind="prose",
    renderer="prose",
    path="prose/Elo-89 vs Chii.html",
)
