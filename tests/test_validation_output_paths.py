from pathlib import Path

from src.validation.kimarite.audit import DEFAULT_OUTPUT_DIR
from src.validation.kimarite.p1_wl import DEFAULT_OUTPUT_PARENT as P1_WL_OUTPUT
from src.validation.kimarite.p1_wl_evaluation import (
    DEFAULT_OUTPUT_PARENT as EVALUATION_OUTPUT,
)
from src.validation.kimarite.p1_wl_website.runner import (
    DEFAULT_CANDIDATE_BUNDLE,
    DEFAULT_OUTPUT_PARENT as WEBSITE_OUTPUT,
)
from src.validation.p1_epsilon_sweep.runner import (
    DEFAULT_OUTPUT_PARENT as SWEEP_OUTPUT,
)
from src.validation.p1_trajectory.runner import (
    DEFAULT_OUTPUT_PARENT as TRAJECTORY_OUTPUT,
)
from src.validation.p1_wl_site_bundle.runner import (
    DEFAULT_CANDIDATE_PRIOR,
    DEFAULT_OUTPUT_PARENT as SITE_BUNDLE_OUTPUT,
)
from src.validation.paths import VALIDATION_OUTPUT_ROOT


def test_validation_generated_outputs_live_under_ignored_output_root():
    expected = Path("files/output/validation")
    assert VALIDATION_OUTPUT_ROOT == expected

    output_locations = (
        DEFAULT_OUTPUT_DIR,
        P1_WL_OUTPUT,
        EVALUATION_OUTPUT,
        WEBSITE_OUTPUT,
        SWEEP_OUTPUT,
        TRAJECTORY_OUTPUT,
        SITE_BUNDLE_OUTPUT,
    )
    assert all(path.is_relative_to(expected) for path in output_locations)


def test_validation_downstream_defaults_use_validation_output_root():
    assert DEFAULT_CANDIDATE_PRIOR.is_relative_to(VALIDATION_OUTPUT_ROOT)
    assert DEFAULT_CANDIDATE_BUNDLE.is_relative_to(VALIDATION_OUTPUT_ROOT)
