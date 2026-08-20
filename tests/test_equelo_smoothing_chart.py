import csv
from pathlib import Path

from src.analysis.equelo.smoothing.chart import (
    load_chii_support,
    load_supported_estimates,
    write_chii_support_csv,
    write_supported_fixed_point_chart,
)
from src.sumo_core.Chii import Chii


FIELDS = (
    "chii",
    "ordinal",
    "rating",
    "observations",
    "distinct_rikishi",
    "strictly_less_than_preceding",
    "violation",
    "n_basho_start",
    "mean_basho_start",
    "stdev_basho_start",
    "se_basho_start",
    "ci95_lower",
    "ci95_upper",
)


def test_smoothing_input_chart_loads_ordinal_order_and_writes_responsive_page(
    tmp_path: Path,
) -> None:
    source = tmp_path / "combined_final_with_stats.csv"
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(_row("J1e", 500100, 1900.0, 120, 8, 2.5))
        writer.writerow(_row("M1e", 400100, 2000.0, 240, 12, 1.5))

    estimates = load_supported_estimates(source)
    support_path = write_chii_support_csv(
        tmp_path / "all_chii_support.csv",
        {
            Chii.from_str("M1e"): 240,
            Chii.from_str("J1e"): 120,
            Chii.from_str("Ms1e"): 12,
        },
    )
    support = load_chii_support(support_path)
    output = write_supported_fixed_point_chart(source, support_csv=support_path)
    html = output.read_text(encoding="utf-8")

    assert [row.chii for row in estimates] == ["M1e", "J1e"]
    assert [row.chii for row in support] == ["M1e", "J1e", "Ms1e"]
    assert output.name == "supported_fixed_point_estimates.html"
    assert "plotly.js-dist-min@2.35.2" in html
    assert "width: 100vw" in html
    assert '"responsive":true' in html
    assert html.index("M1e") < html.index("J1e")
    assert "basho starts=%{customdata[0]}" in html
    assert "Excluded (n < 60)" not in html
    assert '"x":["M1e","J1e","Ms1e"]' in html
    assert '"y":[2000.0,1900.0,null]' in html
    assert '"mode":"markers"' in html
    assert "lines+markers" not in html
    assert "Ms1e" in html


def _row(
    chii: str,
    ordinal: int,
    rating: float,
    n_basho_start: int,
    distinct_rikishi: int,
    se_basho_start: float,
) -> dict[str, object]:
    return {
        "chii": chii,
        "ordinal": ordinal,
        "rating": rating,
        "observations": n_basho_start * 15,
        "distinct_rikishi": distinct_rikishi,
        "strictly_less_than_preceding": "",
        "violation": "False",
        "n_basho_start": n_basho_start,
        "mean_basho_start": rating,
        "stdev_basho_start": 10.0,
        "se_basho_start": se_basho_start,
        "ci95_lower": rating - 5,
        "ci95_upper": rating + 5,
    }
