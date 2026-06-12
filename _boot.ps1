# _boot.ps1
#
# Empirical bootstrap/build sequence for make_site2 from a clean checkout.
# Run from the repository root, for example:
#
#   C:\Users\kilgo\Sumo-Tools> .\_boot.ps1
#
# Slow internet refresh stages and the fixed-point solver are left commented.
# Use the commented stages when rebuilding the corresponding cached artifacts
# rather than consuming an extended distro/cache.

$ErrorActionPreference = "Stop"

function Run {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Command
    )

    Write-Host ""
    Write-Host "> $Command"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Command"
    }
}

# True input dependencies observed so far:
#   files/input/bios.json
#   files/input/elo_fide.json
#
# Extended distro/cache candidates observed so far:
#   files/output/current standings/
#   files/output/HTML results/
#   files/output/infra/get_bios/rikishi/

# Downloader: refresh raw banzuke and daily-result HTML from SumoDB.
# Run this only when the raw source cache is absent or intentionally refreshed.
# Run "py -m src.infra.bootstrap_sources --help" for date-free and as-of modes.
# Run "py -m src.infra.bootstrap_sources"

# Parse downloaded raw banzuke/results HTML into the canonical History zip.
Run "py -m src.infra.parser.parser2"

# Start the live store before producer stages that call get_history()/connect().
# This process is long-running; start it in a separate terminal and leave it open:
#
#   py -m src.infra.tracker.tracker
#
# Once it reports DORMANT, continue this script in the original terminal.

# Fixed-point solver: slow. Required to regenerate
# files/output/Equelo/expt2_combined_final.csv, consumed by fixed_v2.
# Run "py -m src.analysis.equelo.expt2.run_all --start 1958 --end 2026 --modern-end-year 2026 --k-policy divisional --collapse annotation-only"

# Current Equelo process-rating outputs.
Run "py -m src.analysis.equelo.fixed_v2"

# Public Equelo landmark bundle consumed by make_site2.
Run "py -m src.analysis.equelo.fixed_v2.v5_landmarks"

# Downloader: refresh missing raw rikishi bio HTML from SumoDB.
# Run this only when files/output/infra/get_bios/rikishi/ is absent or stale.
# Run "py -m src.infra.get_bios"

# Parse raw rikishi bio HTML into the typed bio JSON consumed by make_site2.
Run "py -m src.infra.get_bios.parser"

# Producer bundles consumed directly by make_site2.
Run "py -m src.analysis.banzuke_compare.publisher"
Run "py -m src.analysis.standings.publisher"
Run "py -m src.misc.finish_by_chii"
Run "py -m src.misc.banzuke_by_era"
Run "py -m src.misc.makuuchi_by_era"
Run "py -m src.analysis.persistence --num-basho 10"
Run "py -m src.misc.first_appearance"
Run "py -m src.analysis.sumo_history.career_lifecycle.rank_at_retirement"
Run "py -m src.analysis.sumo_history.career_lifecycle.career_length"

# Win-probability-by-standing producer. trace_main depends on the empirical
# matchup output and fixed_v2 entrant initial ratings.
Run "py -m src.analysis.probability.matchups"
Run "py -m src.analysis.probability.matchups.trace_main"

# Build the make_site2 static output tree. Add --short only for a smoke test.
Run "py -m src.products.make_site2 --build-only"
