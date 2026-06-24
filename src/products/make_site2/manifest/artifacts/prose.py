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

EQUELO_EXPLANATION_ARTIFACT = ProseArtifact(
    id="equelo_explanation",
    heading="Equelo Ratings",
    kind="prose",
    renderer="prose",
    path="prose/Equelo Ratings.html",
)
