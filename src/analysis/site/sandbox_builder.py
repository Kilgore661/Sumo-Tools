"""
Prototype static site builder for the Sumo Lab public shell.

This is intentionally a sandbox builder.  It assembles existing dark-themed
analysis pages into a single navigable static site without making those tools
depend on a final site architecture.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "src" / "analysis"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "files" / "output" / "site"

COMMON_FILES = ANALYSIS_ROOT / "common" / "files"
STANDINGS_FILES = ANALYSIS_ROOT / "standings" / "files"
STANDINGS_DATA = REPO_ROOT / "files" / "output" / "standings" / "publisher" / "latest_data"
BCR_FILES = ANALYSIS_ROOT / "banzuke_compare" / "files"
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
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sumo Lab Prototype</title>
  <link rel="stylesheet" href="common/files/site-wide.css">
  <link rel="stylesheet" href="site-shell.css">
</head>
<body>
  <div class="lab-shell">
    <aside class="lab-nav" aria-label="Site navigation">
      <header class="lab-brand">
        <div class="lab-name">Sumo Lab</div>
        <div class="lab-status">Prototype shell</div>
      </header>

      <nav>
        <section class="nav-section">
          <h2>Tools</h2>
          <button class="nav-item active" data-page="tools/standings/index.html">
            <span>Standings</span>
            <small>Recent form</small>
          </button>
          <button class="nav-item" data-page="tools/banzuke-compare/index.html">
            <span>Banzuke Compare</span>
            <small>Rank changes</small>
          </button>
        </section>

        <section class="nav-section">
          <h2>Sumo Facts</h2>
          <button class="nav-item" data-page="placeholder-facts">
            <span>Coming Later</span>
            <small>Charts and exhibits</small>
          </button>
        </section>
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

  <script src="site-shell.js"></script>
</body>
</html>
"""


def shell_css() -> str:
    return """:root {
  --shell-nav-width: 260px;
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
  min-height: 100vh;
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
.nav-item small,
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

.nav-item {
  display: block;
  width: 100%;
  margin: 0 0 6px;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: var(--site-text);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.nav-item span,
.nav-item small {
  display: block;
}

.nav-item span {
  font-weight: 700;
}

.nav-item small {
  margin-top: 3px;
  font-size: 12px;
}

.nav-item:hover,
.nav-item.active {
  border-color: var(--site-line-soft);
  background: var(--site-panel);
}

.nav-item.active {
  box-shadow: inset 3px 0 0 var(--site-accent);
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
        description="Build the sandbox Sumo Lab static site."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory to receive the generated static site.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    build_site(args.output_root)
    print(f"Sandbox site built: {args.output_root.resolve()}")


if __name__ == "__main__":
    main()

