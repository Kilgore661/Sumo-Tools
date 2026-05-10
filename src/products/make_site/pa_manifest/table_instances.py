"""Concrete table PA manifest instances."""

from __future__ import annotations

from .table_pa import (
    ColumnGroup,
    DataSource,
    GroupVisibilityPreset,
    Note,
    Option,
    OptionValue,
    SortSpec,
    TableColumn,
    TablePA,
    TableSection,
)


typical_equelo_values = TablePA(
    id="typical_equelo_values",
    heading="Typical Equelo Ratings",
    renderer="sectioned_table",
    primary_source="typical_equelo_values",
    data_sources=(
        DataSource(
            id="typical_equelo_values",
            label="Typical Equelo Ratings",
            path="data/typical_equelo_values.csv",
            media_type="text/csv",
        ),
    ),
    sections=(
        TableSection(
            id="sanyaku",
            heading="Sanyaku",
            source_field="table",
            source_value="Sanyaku",
            order_by="row_order",
        ),
        TableSection(
            id="maegashira",
            heading="Maegashira",
            source_field="table",
            source_value="Maegashira",
            order_by="row_order",
        ),
        TableSection(
            id="other",
            heading="Other",
            source_field="table",
            source_value="Other",
            order_by="row_order",
        ),
    ),
    columns=(
        TableColumn(
            id="label",
            heading="Rank",
            source_field="label",
            sortable=False,
        ),
        TableColumn(
            id="rating",
            heading="Equelo",
            source_field="rating",
            sortable=False,
            sort_kind="numeric",
            formatter="integer",
            align="right",
        ),
    ),
    notes=(
        Note(
            id="typical_equelo_values",
            format="html",
            text=(
                "<strong>Equelo Ratings.</strong> These are typical rating "
                "landmarks, not promises about every rikishi at a rank. "
                "Sideless labels such as M3 use the average of the east and "
                "west rank slots. See "
                '<a href="../../equelo-methodology/v5-landmark-policy/index.html">'
                "V5 Landmark Policy</a>."
            ),
        ),
        Note(
            id="jd100",
            format="html",
            text=(
                "<strong>Why stop at Jd100?</strong> Below Jd100 the support "
                "is low and Jonokuchi has too much churn for Elo-like ratings "
                "such as Equelo to produce stable public landmarks. See "
                '<a href="../../equelo-methodology/lower-rank-rating-stability/index.html">'
                "Lower-Rank Rating Stability</a> for details."
            ),
        ),
    ),
)


banzuke_changes = TablePA(
    id="banzuke_changes",
    heading="Banzuke Changes",
    renderer="banzuke_change_table",
    primary_source="banzuke_change_report",
    options=(
        Option(
            id="division",
            label="Division",
            kind="enum",
            control="select",
            default="makuuchi",
            url_key="division",
            values=(
                OptionValue(value="makuuchi", label="Makuuchi"),
                OptionValue(value="juryo", label="Juryo"),
                OptionValue(value="makushita", label="Makushita"),
                OptionValue(value="sandanme", label="Sandanme"),
                OptionValue(value="jonidan", label="Jonidan"),
                OptionValue(value="jonokuchi", label="Jonokuchi"),
            ),
        ),
        Option(
            id="context",
            label="Previous Basho Context",
            kind="boolean",
            control="checkbox",
            default=True,
            url_key="context",
        ),
        Option(
            id="banzuke_style",
            label="Banzuke Style",
            kind="boolean",
            control="checkbox",
            default=True,
            url_key="banzuke_style",
        ),
        Option(
            id="delta",
            label="Show Delta",
            kind="boolean",
            control="checkbox",
            default=False,
            url_key="delta",
        ),
        Option(
            id="equelo",
            label="Equelo Ratings",
            kind="boolean",
            control="checkbox",
            default=False,
            url_key="equelo",
        ),
    ),
    data_sources=(
        DataSource(
            id="banzuke_change_report",
            label="Banzuke Change Report",
            path="data/banzuke_change_report.csv",
            media_type="text/csv",
            metadata_path="site_config.json",
        ),
    ),
    column_groups=(
        ColumnGroup(id="equelo", heading="Equelo", columns=("equelo",)),
        ColumnGroup(
            id="context",
            heading="Previous",
            columns=("old_chii", "result"),
        ),
        ColumnGroup(
            id="delta",
            heading="Change",
            columns=("delta_direction", "delta"),
        ),
        ColumnGroup(
            id="identity",
            heading="Current",
            always_visible=True,
            columns=("shikona", "bz_chii"),
        ),
    ),
    columns=(
        TableColumn(
            id="equelo",
            heading="Equelo",
            source_field="equelo",
            group="equelo",
            sort_kind="numeric",
            formatter="integer",
            align="right",
        ),
        TableColumn(
            id="old_chii",
            heading="Chii",
            source_field="old_chii",
            group="context",
            sort_key="old_chii_ordinal",
            sort_kind="chii_ordinal",
        ),
        TableColumn(
            id="result",
            heading="Result",
            source_field="result",
            group="context",
            sort_kind="record",
            note="note_result",
        ),
        TableColumn(
            id="delta_direction",
            heading="Direction",
            source_field="delta_direction",
            group="delta",
            sort_kind="text",
            note="note_direction",
        ),
        TableColumn(
            id="delta",
            heading="Delta",
            source_field="delta",
            group="delta",
            sort_kind="numeric",
            align="right",
            note="note_delta",
        ),
        TableColumn(
            id="shikona",
            heading="Shikona",
            source_field="shikona",
            group="identity",
            sort_kind="text",
            always_visible=True,
            link="rikishi",
        ),
        TableColumn(
            id="bz_chii",
            heading="Rank",
            source_field="bz_chii",
            group="identity",
            sort_key="bz_chii_ordinal",
            sort_kind="chii_ordinal",
            always_visible=True,
        ),
    ),
    group_visibility_presets=(
        GroupVisibilityPreset(
            id="default",
            label="Default",
            visible_groups=("context", "identity"),
        ),
        GroupVisibilityPreset(
            id="all",
            label="All Columns",
            visible_groups=("equelo", "context", "delta", "identity"),
        ),
    ),
    default_sort=SortSpec(column="bz_chii", descending=False),
    notes=(
        Note(
            id="note_result",
            applies_to=("context",),
            text=(
                "Result gives wins, losses and absences followed by prizes if "
                "any. A trailing up/down marker indicates promotion or demotion "
                "into the current division."
            ),
        ),
        Note(
            id="note_direction",
            applies_to=("all",),
            text="Direction indicates a better or worse position than in the previous basho.",
        ),
        Note(
            id="note_delta",
            applies_to=("delta",),
            text=(
                "Delta indicates the size of movement from the previous basho's "
                "position, measured in banzuke rows."
            ),
        ),
    ),
    consumes_options=("division", "context", "banzuke_style", "delta", "equelo"),
)


standings_by_wins = TablePA(
    id="standings_by_wins",
    heading="Standings by Wins",
    renderer="standings_table",
    options=(
        Option(
            id="metric_group_preset",
            label="View",
            kind="enum",
            control="radio_group",
            default="standard",
            url_key="view",
            values=(
                OptionValue(value="standard", label="Wins per Basho"),
                OptionValue(value="percentages", label="Wins per Bout"),
                OptionValue(value="combined", label="Combined"),
            ),
        ),
        Option(
            id="current_num_basho",
            label="Number of Basho",
            kind="enum",
            control="select",
            default=6,
            url_key="num_basho",
            values=(
                OptionValue(value=1, label="1"),
                OptionValue(value=2, label="2"),
                OptionValue(value=3, label="3"),
                OptionValue(value=4, label="4"),
                OptionValue(value=5, label="5"),
                OptionValue(value=6, label="6"),
                OptionValue(value=12, label="12"),
                OptionValue(value=18, label="18"),
                OptionValue(value=24, label="24"),
                OptionValue(value=36, label="36"),
                OptionValue(value=60, label="60"),
            ),
        ),
        Option(
            id="current_only",
            label="Active Rikishi Only",
            kind="boolean",
            control="checkbox",
            default=True,
            url_key="current_only",
        ),
        Option(
            id="division",
            label="Division",
            kind="enum",
            control="select",
            default="makuuchi",
            url_key="division",
            values=(
                OptionValue(value="all", label="All"),
                OptionValue(value="makuuchi", label="Makuuchi"),
                OptionValue(value="juryo", label="Juryo"),
                OptionValue(value="makushita", label="Makushita"),
                OptionValue(value="sandanme", label="Sandanme"),
                OptionValue(value="jonidan", label="Jonidan"),
                OptionValue(value="jonokuchi", label="Jonokuchi"),
            ),
        ),
    ),
    data_sources=(
        DataSource(
            id="window_1",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 1).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 1).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=1,
        ),
        DataSource(
            id="window_2",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 2).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 2).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=2,
        ),
        DataSource(
            id="window_3",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 3).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 3).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=3,
        ),
        DataSource(
            id="window_4",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 4).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 4).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=4,
        ),
        DataSource(
            id="window_5",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 5).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 5).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=5,
        ),
        DataSource(
            id="window_6",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 6).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 6).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=6,
        ),
        DataSource(
            id="window_12",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 12).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 12).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=12,
        ),
        DataSource(
            id="window_18",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 18).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 18).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=18,
        ),
        DataSource(
            id="window_24",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 24).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 24).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=24,
        ),
        DataSource(
            id="window_36",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 36).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 36).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=36,
        ),
        DataSource(
            id="window_60",
            path="data/multiple basho standings view (2026_03, BACKWARDS, 60).csv",
            metadata_path="data/multiple basho standings view (2026_03, BACKWARDS, 60).json",
            media_type="text/csv",
            option_id="current_num_basho",
            option_value=60,
        ),
    ),
    column_groups=(
        ColumnGroup(
            id="identity",
            heading="",
            always_visible=True,
            columns=("row_number", "shikona", "chii", "credited_wins"),
        ),
        ColumnGroup(
            id="wins_per_basho",
            heading="Wins per Basho",
            columns=("selected_average_credited_wins", "selected_average_rank"),
        ),
        ColumnGroup(
            id="wins_per_bout",
            heading="Wins per Bout",
            columns=("selected_expected_bout_count", "win_percent", "win_percent_rank"),
        ),
    ),
    columns=(
        TableColumn(
            id="row_number",
            heading="Row",
            group="identity",
            sortable=False,
            formatter="row_number",
            always_visible=True,
        ),
        TableColumn(
            id="shikona",
            heading="Shikona",
            source_field="shikona",
            group="identity",
            sortable=True,
            sort_key="shikona",
            sort_kind="text",
            formatter="shikona_link",
            always_visible=True,
            note="note_identity",
            link="rikishi",
        ),
        TableColumn(
            id="chii",
            heading="Chii",
            source_field="chii",
            group="identity",
            sortable=True,
            sort_key="chii_ordinal",
            sort_kind="chii_ordinal",
            always_visible=True,
            note="note_identity",
        ),
        TableColumn(
            id="credited_wins",
            heading="Wins",
            source_field="credited_wins",
            group="identity",
            sortable=True,
            sort_key="credited_wins",
            sort_kind="numeric",
            align="right",
            always_visible=True,
            note="note_wins",
        ),
        TableColumn(
            id="selected_average_credited_wins",
            heading="Average",
            source_field="selected_average_credited_wins",
            group="wins_per_basho",
            sortable=True,
            sort_key="selected_average_credited_wins",
            sort_kind="numeric",
            formatter="decimal_2",
            align="right",
        ),
        TableColumn(
            id="selected_average_rank",
            heading="#",
            source_field="selected_average_credited_wins",
            group="wins_per_basho",
            sortable=True,
            sort_key="selected_average_credited_wins",
            sort_kind="numeric",
            formatter="competition_rank",
            align="right",
        ),
        TableColumn(
            id="selected_expected_bout_count",
            heading="Bouts",
            source_field="selected_expected_bout_count",
            group="wins_per_bout",
            sortable=True,
            sort_key="selected_expected_bout_count",
            sort_kind="numeric",
            align="right",
            note="note_bouts",
        ),
        TableColumn(
            id="win_percent",
            heading="Win %",
            source_field="win_percent",
            group="wins_per_bout",
            sortable=True,
            sort_key="win_percent",
            sort_kind="numeric",
            formatter="percent_1",
            align="right",
        ),
        TableColumn(
            id="win_percent_rank",
            heading="#",
            source_field="win_percent",
            group="wins_per_bout",
            sortable=True,
            sort_key="win_percent",
            sort_kind="numeric",
            formatter="competition_rank",
            align="right",
        ),
    ),
    group_visibility_presets=(
        GroupVisibilityPreset(
            id="standard",
            label="Wins per Basho",
            visible_groups=("identity", "wins_per_basho"),
            default_sort=SortSpec(
                column="selected_average_credited_wins",
                role="value",
                descending=True,
            ),
        ),
        GroupVisibilityPreset(
            id="percentages",
            label="Wins per Bout",
            visible_groups=("identity", "wins_per_bout"),
            default_sort=SortSpec(
                column="win_percent",
                role="value",
                descending=True,
            ),
        ),
        GroupVisibilityPreset(
            id="combined",
            label="Combined",
            visible_groups=("identity", "wins_per_basho", "wins_per_bout"),
            default_sort=SortSpec(
                column="win_percent",
                role="value",
                descending=True,
            ),
        ),
    ),
    default_sort=SortSpec(
        column="selected_average_credited_wins",
        role="value",
        descending=True,
    ),
    notes=(
        Note(
            id="note_identity",
            applies_to=("all",),
            text=(
                "The reported Shikona and Chii are those that pertain to the "
                "rikishi in the latest basho."
            ),
        ),
        Note(
            id="note_wins",
            applies_to=("all",),
            text="Wins include fusensho.",
        ),
        Note(
            id="note_active",
            applies_to=("all",),
            text=(
                "An Active rikishi is one that is listed on the banzuke for "
                "the latest basho."
            ),
        ),
        Note(
            id="note_bouts",
            applies_to=("percentages", "combined"),
            text=(
                "Bouts is the expected number of scheduled bouts in the "
                "selected window."
            ),
        ),
    ),
    consumes_options=(
        "metric_group_preset",
        "current_num_basho",
        "current_only",
        "division",
    ),
)


for table_pa in (typical_equelo_values, banzuke_changes, standings_by_wins):
    table_pa.validate()
