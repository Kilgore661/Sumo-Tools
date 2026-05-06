"""
Prototype static site builder for the Sumo Lab public shell.

This is intentionally a sandbox builder.  It assembles existing dark-themed
analysis pages into a single navigable static site without making those tools
depend on a final site architecture.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import json
import os
import posixpath
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "src" / "analysis"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "site"
SHELL_ASSET_VERSION = "20260506-nav-tree"
HOST = "www.661.org.uk"
USER = "root"
LOCAL_ROOT = Path("A:/local/html/site")
REMOTE_ROOT = "/var/www/html/site"

COMMON_FILES = ANALYSIS_ROOT / "common" / "files"
STANDINGS_FILES = ANALYSIS_ROOT / "standings" / "files"
STANDINGS_DATA = REPO_ROOT / "files" / "output" / "standings" / "publisher" / "latest_data"
BCR_FILES = ANALYSIS_ROOT / "banzuke_compare" / "files"
FINISH_BY_CHII_SOURCE = REPO_ROOT / "files" / "output" / "misc" / (
    "finish_by_chii_1958_2026.html"
)
BANZUKE_DIVISION_ERA_SOURCE = (
    REPO_ROOT / "files" / "output" / "banzuke_division_era_chart.html"
)
RANK_ERA_SOURCE = REPO_ROOT / "files" / "output" / "rank_era_chart.html"
DIVISION_STABILITY_SOURCE = REPO_ROOT / "files" / "output" / "persistence" / (
    "division_persistence (1958-2026, num_basho=10).html"
)
OBSERVED_STANDING_WIN_PROBABILITY_SOURCE = (
    REPO_ROOT / "files" / "output" / "probability" / "matchups" / (
        "observed_sideless_matchup_traces.html"
    )
)
EQUELO_STANDING_WIN_PROBABILITY_SOURCE = (
    REPO_ROOT / "files" / "output" / "probability" / "matchups" / (
        "equelo_sideless_matchup_traces.html"
    )
)
BCR_GENERATED_DATA_CANDIDATES = (
    REPO_ROOT / "files" / "output" / "bcr",
    Path("A:/local/html/bcr"),
)


@dataclass(frozen=True)
class ToolSpec:
    key: str
    label: str
    description: str
    source_static: Path
    output_dir: Path
    static_files: tuple[str, ...]


def build_site(output_root: Path) -> None:
    """
    Contract:
        output_root is a writable directory under the repository.

        Rebuilds a prototype static site containing a shell index, shared CSS,
        standings, and banzuke-change tool pages.
    """

    output_root = output_root.resolve()
    require_inside_repo(output_root)
    reset_output_root(output_root)

    write_shell(output_root)
    copy_common_files(output_root)
    publish_standings(output_root)
    publish_banzuke_compare(output_root)
    publish_finish_by_chii(output_root)
    publish_banzuke_division_era(output_root)
    publish_rank_era(output_root)
    publish_division_stability(output_root)
    publish_standing_win_probability(output_root)


def require_inside_repo(path: Path) -> None:
    if not path.is_relative_to(REPO_ROOT):
        raise ValueError(f"Refusing to write outside repository: {path}")


def reset_output_root(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)

    for item in output_root.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def clear_local_dir(path: Path) -> None:
    if path.drive and not Path(path.drive + "\\").exists():
        raise FileNotFoundError(
            f"Local deployment drive is not available: {path.drive}\\"
        )

    path.mkdir(parents=True, exist_ok=True)

    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def copy_deploy_tree(source_root: Path, target_root: Path) -> None:
    if not source_root.is_dir():
        raise FileNotFoundError(f"Build output does not exist: {source_root}")

    clear_local_dir(target_root)

    for source in source_root.rglob("*"):
        if not source.is_file():
            continue

        target = target_root / source.relative_to(source_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def ensure_remote_dir(sftp, remote_dir: str) -> None:
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)
        print(f"Created: {remote_dir}")


def ensure_remote_tree(sftp, remote_dir: str) -> None:
    parts = [part for part in remote_dir.split("/") if part]
    current = ""

    for part in parts:
        current = f"{current}/{part}"
        ensure_remote_dir(sftp, current)


def upload_tree(sftp, local_root: Path, remote_root: str) -> int:
    ensure_remote_tree(sftp, remote_root)
    count = 0

    for local_file in local_root.rglob("*"):
        if not local_file.is_file():
            continue

        relative = local_file.relative_to(local_root)
        remote_file = posixpath.join(remote_root, *relative.parts)
        ensure_remote_tree(sftp, posixpath.dirname(remote_file))
        sftp.put(str(local_file), remote_file)
        count += 1

    return count


def get_password() -> str:
    password = os.environ.get("MY_SFTP_PASS")
    if password:
        print("Using MY_SFTP_PASS for remote deployment.")
        return password

    print("MY_SFTP_PASS is not set; prompting for remote deployment password.")
    password = getpass.getpass("SFTP password: ")

    if not password:
        raise ValueError("No SFTP password supplied.")

    return password


def deploy_remote(local_root: Path, remote_root: str) -> int:
    import paramiko

    if not local_root.is_dir():
        raise FileNotFoundError(f"Local deployment tree does not exist: {local_root}")

    password = get_password()
    transport = paramiko.Transport((HOST, 22))
    transport.connect(username=USER, password=password)

    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        count = upload_tree(sftp, local_root, remote_root)
        sftp.stat(posixpath.join(remote_root, "index.html"))
        return count
    finally:
        transport.close()


def copy_common_files(output_root: Path) -> None:
    target = output_root / "common" / "files"
    target.mkdir(parents=True, exist_ok=True)

    for name in ("site-wide.css", "tool-layout.css"):
        shutil.copy2(COMMON_FILES / name, target / name)


def publish_standings(output_root: Path) -> None:
    tool = ToolSpec(
        key="standings",
        label="Standings",
        description="Rolling recent-performance table.",
        source_static=STANDINGS_FILES,
        output_dir=output_root / "tools" / "standings",
        static_files=("index.html", "standings.css", "standings.js.txt"),
    )
    copy_tool_static(tool)
    copy_data_tree(STANDINGS_DATA, tool.output_dir / "data")


def publish_banzuke_compare(output_root: Path) -> None:
    tool = ToolSpec(
        key="banzuke-compare",
        label="Banzuke Compare",
        description="New-banzuke change report.",
        source_static=BCR_FILES,
        output_dir=output_root / "tools" / "banzuke-compare",
        static_files=(
            "index.html",
            "banzuke_change_report.css",
            "banzuke_change_report.js.txt",
        ),
    )
    copy_tool_static(tool)

    generated_source = first_existing_bcr_publication()
    if generated_source is None:
        write_sample_bcr_data(tool.output_dir)
    else:
        copy_bcr_publication_data(generated_source, tool.output_dir)


def publish_finish_by_chii(output_root: Path) -> None:
    if not FINISH_BY_CHII_SOURCE.is_file():
        return

    target_dir = output_root / "tools" / "finish-by-chii"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FINISH_BY_CHII_SOURCE, target_dir / "index.html")


def publish_banzuke_division_era(output_root: Path) -> None:
    if not BANZUKE_DIVISION_ERA_SOURCE.is_file():
        return

    target_dir = output_root / "tools" / "banzuke-division-era"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BANZUKE_DIVISION_ERA_SOURCE, target_dir / "index.html")


def publish_rank_era(output_root: Path) -> None:
    if not RANK_ERA_SOURCE.is_file():
        return

    target_dir = output_root / "tools" / "rank-era"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RANK_ERA_SOURCE, target_dir / "index.html")


def publish_division_stability(output_root: Path) -> None:
    if not DIVISION_STABILITY_SOURCE.is_file():
        return

    target_dir = output_root / "tools" / "division-stability"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DIVISION_STABILITY_SOURCE, target_dir / "index.html")


def publish_standing_win_probability(output_root: Path) -> None:
    targets = (
        (
            OBSERVED_STANDING_WIN_PROBABILITY_SOURCE,
            output_root / "tools" / "win-probability-by-standing" / "observed",
        ),
        (
            EQUELO_STANDING_WIN_PROBABILITY_SOURCE,
            output_root / "tools" / "win-probability-by-standing" / "equelo",
        ),
    )

    for source, target_dir in targets:
        if not source.is_file():
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_dir / "index.html")


def copy_tool_static(tool: ToolSpec) -> None:
    tool.output_dir.mkdir(parents=True, exist_ok=True)

    for name in tool.static_files:
        shutil.copy2(tool.source_static / name, tool.output_dir / name)


def copy_data_tree(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    for source in source_dir.iterdir():
        if source.is_file() and source.suffix.lower() in {".csv", ".json"}:
            shutil.copy2(source, target_dir / source.name)


def first_existing_bcr_publication() -> Path | None:
    for candidate in BCR_GENERATED_DATA_CANDIDATES:
        if (candidate / "site_config.json").is_file() and (candidate / "data").is_dir():
            return candidate
    return None


def copy_bcr_publication_data(source_root: Path, target_root: Path) -> None:
    shutil.copy2(source_root / "site_config.json", target_root / "site_config.json")
    copy_data_tree(source_root / "data", target_root / "data")


def write_sample_bcr_data(target_root: Path) -> None:
    """
    Write enough BCR data for the browser app to render in the prototype shell.
    """

    data_dir = target_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "title": "Prototype Banzuke Change Report",
        "current_date": "2026/11",
        "previous_date": "2026/09",
        "default_division": "makuuchi",
        "data_file": "data/banzuke_change_report.csv",
        "divisions": [
            {"id": "makuuchi", "label": "Makuuchi"},
            {"id": "juryo", "label": "Juryo"},
        ],
    }
    (target_root / "site_config.json").write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )

    rows = [
        {
            "division_id": "makuuchi",
            "division_label": "Makuuchi",
            "bz_chii": "Y1",
            "east_rikishi_id": "1",
            "east_chii": "Y1e",
            "east_shikona": "Onosato",
            "east_graph_shikona": "Onosato",
            "east_old_chii": "Y1e",
            "east_result": "12-3 Y",
            "east_delta": "0",
            "east_delta_class": "neutral",
            "east_equelo": "2519",
            "west_rikishi_id": "2",
            "west_chii": "Y1w",
            "west_shikona": "Hoshoryu",
            "west_graph_shikona": "Hoshoryu",
            "west_old_chii": "Y1w",
            "west_result": "11-4 J",
            "west_delta": "0",
            "west_delta_class": "neutral",
            "west_equelo": "2538",
        },
        {
            "division_id": "makuuchi",
            "division_label": "Makuuchi",
            "bz_chii": "O1",
            "east_rikishi_id": "3",
            "east_chii": "O1e",
            "east_shikona": "Kotozakura",
            "east_graph_shikona": "Kotozakura",
            "east_old_chii": "O1e",
            "east_result": "8-7",
            "east_delta": "0",
            "east_delta_class": "neutral",
            "east_equelo": "2360",
            "west_rikishi_id": "4",
            "west_chii": "O1w",
            "west_shikona": "Aonishiki",
            "west_graph_shikona": "Aonishiki",
            "west_old_chii": "S1w",
            "west_result": "12-3 K",
            "west_delta": "0.5",
            "west_delta_class": "up low",
            "west_equelo": "2294",
        },
        {
            "division_id": "juryo",
            "division_label": "Juryo",
            "bz_chii": "J1",
            "east_rikishi_id": "5",
            "east_chii": "J1e",
            "east_shikona": "Prototype East",
            "east_graph_shikona": "Prototype East",
            "east_old_chii": "J3w",
            "east_result": "10-5",
            "east_delta": "2.5",
            "east_delta_class": "up mid",
            "east_equelo": "1980",
            "west_rikishi_id": "6",
            "west_chii": "J1w",
            "west_shikona": "Prototype West",
            "west_graph_shikona": "Prototype West",
            "west_old_chii": "M17e",
            "west_result": "5-10",
            "west_delta": "1.5",
            "west_delta_class": "down mid",
            "west_equelo": "2010",
        },
    ]

    fieldnames = tuple(rows[0].keys())
    with (data_dir / "banzuke_change_report.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_shell(output_root: Path) -> None:
    (output_root / "index.html").write_text(shell_html(), encoding="utf-8")
    (output_root / "site-shell.css").write_text(shell_css(), encoding="utf-8")
    (output_root / "site-shell.js").write_text(shell_js(), encoding="utf-8")


def shell_html() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sumo Lab Prototype</title>
  <link rel="icon" type="image/x-icon" href="../Sumo/meep.png">
  <link rel="stylesheet" href="common/files/site-wide.css">
  <link rel="stylesheet" href="site-shell.css?v={SHELL_ASSET_VERSION}">
</head>
<body>
  <div class="lab-shell">
    <aside class="lab-nav" aria-label="Site navigation">
      <header class="lab-brand">
        <div class="lab-name">Sumo Lab</div>
        <div class="lab-status">Prototype shell</div>
      </header>

      <nav>
        {nav_tree_html()}
      </nav>
    </aside>

    <main class="lab-main">
      <header class="lab-title-bar">
        <div>
          <h1 id="active-title">Standings</h1>
          <p id="active-summary">Recent rolling standings inside the lab shell.</p>
        </div>
        <a class="open-link" id="open-link" href="tools/standings/index.html">Open page</a>
      </header>

      <section class="frame-panel" id="frame-panel">
        <iframe
          id="tool-frame"
          title="Selected Sumo Lab page"
          src="tools/standings/index.html"
        ></iframe>
      </section>

      <section class="placeholder-panel" id="placeholder-panel" hidden>
        <h2>Sumo Facts</h2>
        <p>
          This area is reserved for descriptive exhibits such as finish by Chii,
          banzuke structure over time, and observed matchup distributions.
        </p>
      </section>
    </main>
  </div>

  <script src="site-shell.js?v={SHELL_ASSET_VERSION}"></script>
</body>
</html>
"""


def nav_tree_html() -> str:
    return """<ol class="nav-tree">
  <li>
    <span>Home</span>
    <ol>
      <li>
        <span>Welcome / site orientation</span>
        <ol>
          <li><span>What this site is</span></li>
          <li><span>What is new / latest updates</span></li>
          <li><span>Featured current pages</span></li>
          <li><span>Known caveats and interpretation warnings</span></li>
        </ol>
      </li>
      <li>
        <span>Quick entry points</span>
        <ol>
          <li><span>Latest standings</span></li>
          <li><span>Banzuke changes</span></li>
          <li><span>Rikishi lookup</span></li>
          <li><span>Rank outcomes</span></li>
          <li><span>Ratings and models</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Current Sumo</span>
    <ol>
      <li>
        <span>Latest Tables</span>
        <ol>
          <li><span>Current rating / standings table</span></li>
          <li><span>Date navigation</span></li>
          <li><span>Division filters</span></li>
          <li><span>Sortable columns</span></li>
          <li><span>Shikona click-through to rikishi pages</span></li>
          <li><span>Table notes / column definitions</span></li>
          <li>
            <span>Analyst columns</span>
            <ol>
              <li><span>Elo / Equelo</span></li>
              <li><span>Expected wins</span></li>
              <li><span>Probability-derived values</span></li>
              <li><span>Current score</span></li>
              <li><span>Latest rating</span></li>
              <li><span>New / projected chii</span></li>
              <li><span>Delta Elo</span></li>
              <li><span>Delta banzuke</span></li>
              <li><span>Delta chii, only if audited</span></li>
              <li><span>Rank-relative values such as vChii</span></li>
            </ol>
          </li>
        </ol>
      </li>
      <li>
        <button class="nav-item" data-page="tools/banzuke-compare/index.html">
          <span>Banzuke Changes</span>
        </button>
        <ol>
          <li><span>Mechanical changes</span></li>
          <li><span>Promotions</span></li>
          <li><span>Demotions</span></li>
          <li><span>Notable changes / headlines</span></li>
          <li><span>Detailed filtered report</span></li>
        </ol>
      </li>
      <li>
        <span>Current Basho</span>
        <ol>
          <li><span>Latest results</span></li>
          <li><span>Day view</span></li>
          <li><span>Basho view</span></li>
          <li><span>Rikishi result links</span></li>
        </ol>
      </li>
      <li>
        <span>Current Banzuke</span>
        <ol>
          <li><span>Current banzuke browser</span></li>
          <li><span>Division view</span></li>
          <li><span>Rank slot view</span></li>
          <li><span>Rikishi links</span></li>
        </ol>
      </li>
      <li>
        <button class="nav-item active" data-page="tools/standings/index.html">
          <span>Standings by Wins</span>
        </button>
        <ol>
          <li><span>Window selector</span></li>
          <li><span>Division selector</span></li>
          <li><span>Combined / separated views</span></li>
        </ol>
      </li>
      <li>
        <span>Current Leaders</span>
        <ol>
          <li><span>Max average wins</span></li>
          <li><span>Max rating probability</span></li>
          <li><span>Highest-rated rikishi</span></li>
          <li><span>Biggest rating movers</span></li>
          <li><span>Biggest banzuke movers</span></li>
          <li><span>Unusual current rikishi by expected wins / probability</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Rikishi</span>
    <ol>
      <li>
        <span>Rikishi Lookup</span>
        <ol>
          <li><span>Search by shikona</span></li>
          <li><span>Current rank / division</span></li>
          <li><span>Profile link</span></li>
          <li><span>Shikona history, if available</span></li>
        </ol>
      </li>
      <li>
        <span>Rikishi Profile</span>
        <ol>
          <li>
            <span>Summary</span>
            <ol>
              <li><span>Current chii</span></li>
              <li><span>Current rating</span></li>
              <li><span>Career high</span></li>
              <li><span>Recent record</span></li>
              <li><span>Current trend</span></li>
            </ol>
          </li>
          <li>
            <span>Career Timeline</span>
            <ol>
              <li><span>Rank / chii over calendar time</span></li>
              <li><span>Rank / chii by basho count</span></li>
              <li><span>Division history</span></li>
              <li><span>Career high markers</span></li>
            </ol>
          </li>
          <li>
            <span>Rating Timeline</span>
            <ol>
              <li><span>Elo / Equelo over calendar time</span></li>
              <li><span>Daily rating movement</span></li>
              <li><span>Bout-level rating movement</span></li>
              <li><span>Rating deltas</span></li>
            </ol>
          </li>
          <li>
            <span>Combined Career View</span>
            <ol>
              <li><span>Chii + rating on dual y-axes</span></li>
              <li><span>Rank movement and rating movement together</span></li>
              <li><span>Calendar-time mode</span></li>
              <li><span>Basho-count mode</span></li>
            </ol>
          </li>
          <li>
            <span>Performance Context</span>
            <ol>
              <li><span>Recent form</span></li>
              <li><span>Rank trend</span></li>
              <li><span>Rating trend</span></li>
              <li><span>Expected wins</span></li>
              <li><span>Observed outcomes from similar chii</span></li>
            </ol>
          </li>
        </ol>
      </li>
      <li>
        <span>Career Comparisons</span>
        <ol>
          <li><span>Comparable careers</span></li>
          <li><span>Fast-rising prospects</span></li>
          <li><span>Journeymen</span></li>
          <li><span>Newcomer context</span></li>
        </ol>
      </li>
      <li>
        <span>Career Facts</span>
        <ol>
          <li><span>Career high table</span></li>
          <li><span>First appearance / debut context</span></li>
          <li><span>Rank at retirement</span></li>
          <li><span>Career length</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Banzuke &amp; Rank</span>
    <ol>
      <li>
        <span>Chii Explained</span>
        <ol>
          <li><span>What M3e means</span></li>
          <li><span>Division, number, side, annotation</span></li>
          <li><span>Sideless chii</span></li>
          <li><span>Chii ordering</span></li>
          <li><span>Rank movement glossary</span></li>
          <li><span>Promotion / demotion basics</span></li>
        </ol>
      </li>
      <li>
        <span>Current Banzuke</span>
        <ol>
          <li><span>Official-looking banzuke browser</span></li>
          <li><span>Division filters</span></li>
          <li><span>Rank slots</span></li>
          <li><span>East / west layout</span></li>
        </ol>
      </li>
      <li>
        <span>Banzuke Changes</span>
        <ol>
          <li><span>Current banzuke change report</span></li>
          <li><span>New banzuke headlines</span></li>
          <li><span>Promotions and demotions</span></li>
          <li><span>Mechanical fact view</span></li>
          <li><span>Editorial / interpretation view</span></li>
        </ol>
      </li>
      <li>
        <span>Banzuke Structure Over Time</span>
        <ol>
          <li>
            <button class="nav-item" data-page="tools/banzuke-division-era/index.html">
              <span>Banzuke Division by Era</span>
            </button>
          </li>
          <li><span>Banzuke population history</span></li>
          <li><span>Changes to sizes of divisions</span></li>
          <li><span>Division sizes over time</span></li>
        </ol>
      </li>
      <li>
        <span>Makuuchi Structure</span>
        <ol>
          <li>
            <button class="nav-item" data-page="tools/rank-era/index.html">
              <span>Makuuchi Rank by Era</span>
            </button>
          </li>
          <li><span>Rank structure changes</span></li>
          <li><span>Sanyaku / maegashira population history</span></li>
        </ol>
      </li>
      <li>
        <span>Rank Slot History</span>
        <ol>
          <li><span>First chii appearance</span></li>
          <li><span>Y1e history</span></li>
          <li><span>Historical / rare ranks</span></li>
          <li><span>Curated-rank explanation</span></li>
        </ol>
      </li>
      <li>
        <span>Division Movement</span>
        <ol>
          <li>
            <button class="nav-item" data-page="tools/division-stability/index.html">
              <span>Division Stability</span>
            </button>
          </li>
          <li><span>Promotion / demotion frequency</span></li>
          <li><span>Movement between divisions</span></li>
        </ol>
      </li>
      <li>
        <span>Retirement and Rank</span>
        <ol>
          <li><span>Rank at retirement</span></li>
          <li><span>Retirement-rank distribution</span></li>
          <li><span>Bg / intai ambiguity caveats</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Performance</span>
    <ol>
      <li>
        <span>Rank Outcomes</span>
        <ol>
          <li>
            <button class="nav-item" data-page="tools/finish-by-chii/index.html">
              <span>Finish by Chii</span>
            </button>
          </li>
          <li><span>Average finish by chii</span></li>
          <li><span>Threshold views</span></li>
          <li><span>Top records from a rank</span></li>
          <li><span>Bottom records from a rank</span></li>
          <li><span>Expected record from rank context</span></li>
          <li><span>Division filters</span></li>
          <li><span>Sample-size display</span></li>
        </ol>
      </li>
      <li>
        <span>Matchups</span>
        <ol>
          <li><span>Observed matchup probabilities</span></li>
          <li><span>Sideless chii matchup traces</span></li>
          <li><span>Pair support / sample size</span></li>
          <li><span>Confidence intervals</span></li>
          <li><span>Curated rank domain</span></li>
          <li><span>Division filters</span></li>
        </ol>
      </li>
      <li>
        <span>Observed Expectations</span>
        <ol>
          <li><span>What usually happens from this rank?</span></li>
          <li><span>What usually happens against this opponent rank?</span></li>
          <li><span>Rank outcome explorer</span></li>
          <li><span>Support-aware interpretation</span></li>
        </ol>
      </li>
      <li>
        <span>Performance Patterns</span>
        <ol>
          <li><span>Current form versus historical expectation</span></li>
          <li><span>Rank trend</span></li>
          <li><span>Overperformance / underperformance, if method is defined</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Ratings &amp; Models</span>
    <ol>
      <li>
        <span>Rating Overview</span>
        <ol>
          <li><span>Why ratings?</span></li>
          <li><span>What rating is trying to measure</span></li>
          <li><span>Rating versus banzuke rank</span></li>
          <li><span>What ratings do not prove</span></li>
        </ol>
      </li>
      <li>
        <span>Current Ratings</span>
        <ol>
          <li><span>Current Elo / Equelo table</span></li>
          <li><span>Rating leaders</span></li>
          <li><span>Rating probability leaders</span></li>
          <li><span>Rating changes</span></li>
          <li><span>Date navigation</span></li>
        </ol>
      </li>
      <li>
        <span>Rating and Rank</span>
        <ol>
          <li><span>Elo / Equelo vs chii</span></li>
          <li><span>Rating-vs-rank validation</span></li>
          <li><span>Mean rating by chii</span></li>
          <li><span>Mean expected wins by chii</span></li>
          <li><span>Mean probability-derived value by chii</span></li>
          <li><span>Normalised probability-derived value by chii</span></li>
          <li><span>Intro rating table / chart</span></li>
        </ol>
      </li>
      <li>
        <span>Observed vs Modelled</span>
        <ol>
          <li>
            <span>Win Probability by Standing</span>
            <ol>
              <li>
                <button class="nav-item" data-page="tools/win-probability-by-standing/observed/index.html">
                  <span>Observed</span>
                </button>
              </li>
              <li>
                <button class="nav-item" data-page="tools/win-probability-by-standing/equelo/index.html">
                  <span>Equelo</span>
                </button>
              </li>
            </ol>
          </li>
          <li><span>Difference / residual chart, later</span></li>
          <li><span>Support-aware comparison</span></li>
          <li><span>Consistency checks</span></li>
        </ol>
      </li>
      <li>
        <span>Model Diagnostics</span>
        <ol>
          <li><span>Inflation by rank / chii</span></li>
          <li><span>Rating spread variants</span></li>
          <li><span>Rating distribution</span></li>
          <li><span>Estimators</span></li>
          <li><span>Mean rating vs banzuke size</span></li>
          <li><span>Calibration reports</span></li>
          <li><span>Probability calibration</span></li>
          <li><span>Drift over time</span></li>
        </ol>
      </li>
      <li>
        <span>Methodology</span>
        <ol>
          <li><span>Elo explanation</span></li>
          <li><span>Equelo explanation</span></li>
          <li><span>BKQ / legacy model explanation</span></li>
          <li><span>Formulae</span></li>
          <li><span>Parameters</span></li>
          <li><span>Assumptions</span></li>
          <li><span>Teleological-risk caveats</span></li>
          <li><span>Why some outputs are research only</span></li>
        </ol>
      </li>
      <li>
        <span>Research Archive</span>
        <ol>
          <li><span>Fixed-v1 rating curve charts</span></li>
          <li><span>One-shot simulation charts</span></li>
          <li><span>Expt3 predicted probability distribution</span></li>
          <li><span>Calibration experiments</span></li>
          <li><span>Model failures and dead ends</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Sumo History</span>
    <ol>
      <li>
        <span>Population History</span>
        <ol>
          <li><span>Division sizes over time</span></li>
          <li><span>Changes to sizes of divisions</span></li>
          <li><span>Banzuke population</span></li>
          <li><span>Mean rating vs banzuke size</span></li>
        </ol>
      </li>
      <li>
        <span>Career Lifecycle</span>
        <ol>
          <li><span>Career length count</span></li>
          <li><span>Career length probability</span></li>
          <li><span>Cumulative career length probability</span></li>
          <li><span>Retirement-rank distribution</span></li>
        </ol>
      </li>
      <li>
        <span>Rank History</span>
        <ol>
          <li><span>First chii appearance</span></li>
          <li><span>Y1e history</span></li>
          <li><span>Historical rank slots</span></li>
          <li><span>Makuuchi rank structure over time</span></li>
        </ol>
      </li>
      <li>
        <span>Recruitment and Retirement</span>
        <ol>
          <li><span>Recruitment patterns, future</span></li>
          <li><span>Retirement patterns</span></li>
          <li><span>Division entry / exit patterns</span></li>
        </ol>
      </li>
      <li>
        <span>Historical Exhibits</span>
        <ol>
          <li><span>Banzuke division by era</span></li>
          <li><span>Makuuchi by era</span></li>
          <li><span>Long-term rank population charts</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Data &amp; Methods</span>
    <ol>
      <li>
        <span>Data Source</span>
        <ol>
          <li><span>Where the data comes from</span></li>
          <li><span>Update policy</span></li>
          <li><span>Currentness policy</span></li>
          <li><span>Parsed history</span></li>
          <li><span>Known source limitations</span></li>
        </ol>
      </li>
      <li>
        <span>Glossary</span>
        <ol>
          <li><span>Basho</span></li>
          <li><span>Banzuke</span></li>
          <li><span>Chii</span></li>
          <li><span>Rikishi</span></li>
          <li><span>Shikona</span></li>
          <li><span>Division</span></li>
          <li><span>Record</span></li>
          <li><span>Fusen / non-fought outcomes</span></li>
          <li><span>East / west</span></li>
          <li><span>Sideless chii</span></li>
        </ol>
      </li>
      <li>
        <span>Known Limitations</span>
        <ol>
          <li><span>Missing or ambiguous data</span></li>
          <li><span>Historical rank quirks</span></li>
          <li><span>Retirement ambiguity</span></li>
          <li><span>Parser limitations</span></li>
          <li><span>Model limitations</span></li>
          <li><span>What not to infer</span></li>
        </ol>
      </li>
      <li>
        <span>Method Notes</span>
        <ol>
          <li><span>How historical data is parsed</span></li>
          <li><span>How outputs are generated</span></li>
          <li><span>How confidence intervals are computed</span></li>
          <li><span>How curated domains are chosen</span></li>
          <li><span>Difference between observed data and model projections</span></li>
        </ol>
      </li>
      <li>
        <span>Technical Appendix</span>
        <ol>
          <li><span>Parser and validation notes</span></li>
          <li><span>Warning logs summary, not raw logs</span></li>
          <li><span>Persistence reports if promoted</span></li>
          <li><span>Data-quality notes</span></li>
        </ol>
      </li>
    </ol>
  </li>

  <li>
    <span>Lab / Archive</span>
    <ol>
      <li>
        <span>Experimental Charts</span>
        <ol>
          <li><span>Miscellaneous legacy charts that do not yet have public framing</span></li>
          <li><span>Old model diagnostics</span></li>
          <li><span>Prototype charts</span></li>
        </ol>
      </li>
      <li>
        <span>Internal Diagnostics</span>
        <ol>
          <li><span>Parser warning summaries</span></li>
          <li><span>Weirdness reports, if ever exposed</span></li>
          <li><span>Raw downloaded HTML should not be public navigation</span></li>
        </ol>
      </li>
      <li>
        <span>Deprecated / Superseded</span>
        <ol>
          <li><span>Broken or unaudited columns</span></li>
          <li><span>Delta chii, until fixed</span></li>
          <li><span>Old ranking/index behavior caveats</span></li>
          <li><span>Research outputs retained for provenance</span></li>
        </ol>
      </li>
    </ol>
  </li>
</ol>"""


def shell_css() -> str:
    return """:root {
  --shell-nav-width: 312px;
}

body {
  overflow: hidden;
}

.lab-shell {
  display: grid;
  grid-template-columns: var(--shell-nav-width) minmax(0, 1fr);
  min-height: 100vh;
}

.lab-nav {
  height: 100vh;
  min-height: 100vh;
  overflow: auto;
  border-right: 1px solid var(--site-line);
  background: var(--site-panel-subtle);
}

.lab-brand {
  padding: 20px 18px;
  border-bottom: 1px solid var(--site-line);
  background: var(--site-panel);
}

.lab-name {
  font-size: 24px;
  font-weight: 700;
}

.lab-status,
.lab-title-bar p {
  color: var(--site-muted);
}

.lab-status {
  margin-top: 4px;
  font-size: 13px;
}

.nav-section {
  padding: 16px 12px 4px;
}

.nav-section h2 {
  margin: 0 0 8px;
  padding: 0 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--site-accent);
  text-transform: uppercase;
}

.nav-tree {
  counter-reset: nav-level;
  list-style: none;
  margin: 0;
  padding: 10px 14px 28px 30px;
  font-size: 13px;
  line-height: 1.35;
}

.nav-tree ol {
  counter-reset: nav-level;
  list-style: none;
  margin: 4px 0 6px;
  padding-left: 20px;
}

.nav-tree li {
  counter-increment: nav-level;
  margin: 3px 0;
}

.nav-tree li::before {
  content: counters(nav-level, ".") ". ";
  color: var(--site-muted);
  font-variant-numeric: tabular-nums;
}

.nav-tree li:has(> .nav-item)::before {
  color: #ff3030;
}

.nav-tree > li {
  margin-bottom: 12px;
}

.nav-tree > li > span {
  font-weight: 700;
  color: var(--site-accent);
  text-transform: uppercase;
}

.nav-tree li li > span {
  color: var(--site-text);
}

.nav-item {
  display: inline;
  width: auto;
  margin: 2px 0 4px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: 0;
  background: transparent;
  color: var(--site-text);
  font: inherit;
  cursor: pointer;
}

.nav-item span {
  font-weight: 700;
  color: #ff3030;
}

.nav-item:hover,
.nav-item.active {
  border-color: transparent;
  background: transparent;
}

.nav-item.active {
  box-shadow: none;
}

.lab-main {
  min-width: 0;
  height: 100vh;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.lab-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--site-line);
  background: var(--site-panel);
}

.lab-title-bar h1 {
  font-size: 24px;
}

.lab-title-bar p {
  margin: 4px 0 0;
}

.open-link {
  flex: 0 0 auto;
  padding: 8px 10px;
  border: 1px solid var(--site-line-soft);
  border-radius: 6px;
  background: var(--site-panel-strong);
  text-decoration: none;
  font-weight: 700;
}

.frame-panel {
  min-width: 0;
  min-height: 0;
  overflow: auto;
  background: var(--site-bg);
}

#tool-frame {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}

.placeholder-panel {
  margin: 18px;
  padding: 20px;
  border: 1px solid var(--site-line);
  background: var(--site-panel);
}

.placeholder-panel h2 {
  margin-bottom: 10px;
}

.placeholder-panel p {
  max-width: 720px;
  margin: 0;
  color: var(--site-muted);
  line-height: 1.5;
}

@media (max-width: 760px) {
  body {
    overflow: auto;
  }

  .lab-shell {
    grid-template-columns: 1fr;
  }

  .lab-nav {
    height: auto;
    max-height: 42vh;
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--site-line);
  }

  .lab-main {
    height: 78vh;
  }
}
"""


def shell_js() -> str:
    return """const pages = {
  "tools/standings/index.html": {
    title: "Standings",
    summary: "Recent rolling standings inside the lab shell.",
  },
  "tools/banzuke-compare/index.html": {
    title: "Banzuke Compare",
    summary: "New-banzuke change report inside the lab shell.",
  },
  "tools/finish-by-chii/index.html": {
    title: "Finish by Chii",
    summary: "Historical finishing outcomes grouped by chii.",
  },
  "tools/banzuke-division-era/index.html": {
    title: "Banzuke Division by Era",
    summary: "Historical banzuke division structure by era.",
  },
  "tools/rank-era/index.html": {
    title: "Makuuchi Rank by Era",
    summary: "Historical Makuuchi rank structure by era.",
  },
  "tools/division-stability/index.html": {
    title: "Division Stability",
    summary: "Historical continuity within divisions.",
  },
  "tools/win-probability-by-standing/observed/index.html": {
    title: "Win Probability by Standing: Observed",
    summary: "Historical win proportions by standing.",
  },
  "tools/win-probability-by-standing/equelo/index.html": {
    title: "Win Probability by Standing: Equelo",
    summary: "Equelo-implied win probabilities by standing.",
  },
  "placeholder-facts": {
    title: "Sumo Facts",
    summary: "Reserved space for stable charts and exhibits.",
  },
};

const frame = document.getElementById("tool-frame");
const framePanel = document.getElementById("frame-panel");
const placeholderPanel = document.getElementById("placeholder-panel");
const activeTitle = document.getElementById("active-title");
const activeSummary = document.getElementById("active-summary");
const openLink = document.getElementById("open-link");
const navItems = document.querySelectorAll(".nav-item");

for (const item of navItems) {
  item.addEventListener("click", () => selectPage(item.dataset.page));
}

function selectPage(page) {
  const meta = pages[page];
  if (!meta) {
    return;
  }

  for (const item of navItems) {
    item.classList.toggle("active", item.dataset.page === page);
  }

  activeTitle.textContent = meta.title;
  activeSummary.textContent = meta.summary;

  if (page === "placeholder-facts") {
    framePanel.hidden = true;
    placeholderPanel.hidden = false;
    openLink.hidden = true;
    return;
  }

  frame.src = page;
  framePanel.hidden = false;
  placeholderPanel.hidden = true;
  openLink.hidden = false;
  openLink.href = page;
}
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, locally deploy, and remotely deploy the sandbox site."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Persisted site output directory to build and deploy from.",
    )
    parser.add_argument(
        "--local-root",
        type=Path,
        default=LOCAL_ROOT,
        help="Local web directory to receive the deployable site.",
    )
    parser.add_argument(
        "--remote-root",
        default=REMOTE_ROOT,
        help="Remote web root to receive the deployable site.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Build and copy to A:, but do not upload remotely.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    output_root = args.output_root.resolve()
    local_root = args.local_root.resolve()

    build_site(output_root)
    copy_deploy_tree(output_root, local_root)

    print(f"Sandbox site built: {output_root}")
    print(f"Sandbox site locally deployed: {local_root}")

    if args.local_only:
        return

    remote_count = deploy_remote(local_root, args.remote_root)
    print(
        f"Sandbox site remotely deployed: {remote_count} files "
        f"to {HOST}:{args.remote_root}"
    )
    print(f"https://www.661.org.uk{args.remote_root.removeprefix('/var/www/html')}/")


if __name__ == "__main__":
    main()
