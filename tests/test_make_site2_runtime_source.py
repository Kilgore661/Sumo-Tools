from pathlib import Path


RUNTIME_SOURCE = Path("src/products/make_site2/runtime/site.js")


def test_banzuke_changes_renderer_marks_shikona_cells_for_shared_alignment() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert 'data-column-id="shikona"' in source
    assert "function banzukeCellAttributes(columnId)" in source


def test_banzuke_changes_renderer_does_not_emit_selected_division_as_title() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")
    start = source.index("function renderBanzukeChangesTable")
    end = source.index("function renderBanzukeStyleTable")
    function_body = source[start:end]

    assert "divisionLabel" not in function_body
    assert "state.division" not in function_body


def test_standings_renderer_selects_source_from_window_filter() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert "function selectedStandingsSource(artifact, state)" in source
    assert "artifact.selector_filter_id" in source
    assert "String(source.option_value)" in source


def test_stacked_bar_chart_renderer_uses_model_trace_fields() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert "function renderStackedBarChartContentPanel(panel, artifact)" in source
    assert "function stackedBarTraceSpec(artifact)" in source
    assert "trace.group_by" in source
    assert "trace.x" in source
    assert "trace.y" in source
    assert "artifact.provenance.stack_order" in source


def test_grouped_line_chart_renderer_uses_model_trace_fields() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert "function renderGroupedLineChartContentPanel(panel, artifact)" in source
    assert "function groupedLineTraceSpec(artifact)" in source
    assert "candidate.kind === \"scatter\"" in source
    assert "trace.group_by" in source
    assert "trace.x" in source
    assert "trace.y" in source
    assert "artifact.provenance.default_visible" in source


def test_ordered_bar_chart_renderer_uses_model_trace_fields() -> None:
    source = RUNTIME_SOURCE.read_text(encoding="utf-8")

    assert "function renderOrderedBarChartContentPanel(panel, artifact)" in source
    assert "function orderedBarTraceSpec(artifact)" in source
    assert "candidate.kind === \"bar\"" in source
    assert "trace.x" in source
    assert "trace.y" in source
    assert "artifact.provenance.order_field" in source
    assert "artifact.provenance.base_year" in source
