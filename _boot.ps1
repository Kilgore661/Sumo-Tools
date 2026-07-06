# _boot.ps1
#
# Empirical bootstrap/build sequence for make_site2 from a clean checkout.
# Run from the repository root, for example:
#
#   C:\Users\me\Sumo-Tools> .\_boot.ps1
#
# Slow internet refresh stages and the fixed-supported Equelo refresh are left commented.
# Use the commented stages when rebuilding the corresponding cached artifacts
# rather than consuming an extended distro/cache.

$ErrorActionPreference = "Stop"

$BuildStart = Get-Date
$LogDirectory = Join-Path -Path (Get-Location) -ChildPath "files\output\logs"
$LogFileName = "{0}.log" -f $BuildStart.ToString("yyyy-MM-dd HH-mm-ss")
$LogPath = Join-Path -Path $LogDirectory -ChildPath $LogFileName

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null
Start-Transcript -Path $LogPath -Force | Out-Null

$BuildSucceeded = $false

function Run {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Command
    )

    Write-Host ""
    Write-Host "> $Command"

    $global:LASTEXITCODE = 0
    Invoke-Expression $Command

    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Command"
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($env:GEOLOCATION)) {
        Write-Host "env:GEOLOCATION is not set. Build cannot continue."
        exit 1
    }

    # True input dependencies observed so far:
    #   files/input/bios.json
    #   files/input/elo_fide.json
    #
    # Extended distro/cache candidates observed so far:
    #   files/output/current standings/
    #   files/output/HTML results/
    #   files/output/infra/get_bios/rikishi/
    #   files/output/Equelo/fixed_supported/

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

    # Fixed-supported Equelo refresh: slow. Regenerates the master chii
    # initial-rating map and process/day-end ratings consumed by Equelo-based
    # downstream producers such as Highest Equelo, Typical Equelo, and Rating Changes.
    # Run "py -m src.analysis.equelo.fixed_supported"

    # Downloader: refresh missing raw rikishi bio HTML from SumoDB.
    # Run this only when files/output/infra/get_bios/rikishi/ is absent or stale.
    # Run "py -m src.infra.get_bios"

    # Parse raw rikishi bio HTML into the typed bio JSON consumed by make_site2.
    Run "py -m src.infra.get_bios.parser"

    # Producer bundles consumed directly by make_site2.
    Run "py -m src.infra.new_banzuke"
    Run "py -m src.analysis.banzuke_compare.publisher"
    Run "py -m src.analysis.standings.publisher"
    Run "py -m src.misc.finish_by_chii"
    Run "py -m src.misc.banzuke_by_era"
    Run "py -m src.misc.makuuchi_by_era"
    Run "py -m src.analysis.persistence --num-basho 10"
    Run "py -m src.misc.first_appearance"
    Run "py -m src.analysis.sumo_history.career_lifecycle.rank_at_retirement"
    Run "py -m src.analysis.sumo_history.career_lifecycle.career_length"
    Run "py -m src.analysis.sumo_history.records.consecutive_bouts"
    Run "py -m src.analysis.sumo_history.records.career_wins"
    Run "py -m src.analysis.sumo_history.records.career_losses"
    Run "py -m src.analysis.sumo_history.records.highest_equelo"
    Run "py -m src.analysis.equelo.rating_change_tables"

    # Win-probability-by-standing producer. trace_main depends on the empirical
    # matchup output and fixed-supported chii initial ratings.
    Run "py -m src.analysis.probability.matchups"
    Run "py -m src.analysis.probability.matchups.trace_main"

    # Build and deploy the make_site2 static output tree.
    Run "py -m src.products.make_site2"

    $BuildSucceeded = $true
}
finally {
    $BuildEnd = Get-Date
    $Elapsed = $BuildEnd - $BuildStart

    if ($BuildSucceeded) {
        Write-Host ""
        Write-Host ("Build completed successfully in {0:hh\:mm\:ss} ({1:N1} seconds)." -f $Elapsed, $Elapsed.TotalSeconds)
    }

    Write-Host ""
    Write-Host "Log file: $LogPath"

    Stop-Transcript | Out-Null
}
