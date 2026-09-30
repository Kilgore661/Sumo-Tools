# _boot89.ps1
#
# Produce the Sumo '89 site from the live store, assemble it, and deploy it to
# the configured local server. The make_site89 command-line flags are forwarded
# unchanged, for example:
#
#   .\_boot89.ps1
#   .\_boot89.ps1 --build-only
#   .\_boot89.ps1 --no-build
#   .\_boot89.ps1 --prod

$ErrorActionPreference = "Stop"

$BuildStart = Get-Date
$LogDirectory = Join-Path -Path (Get-Location) -ChildPath "files\output\logs"
$LogFileName = "{0} site89.log" -f $BuildStart.ToString("yyyy-MM-dd HH-mm-ss")
$LogPath = Join-Path -Path $LogDirectory -ChildPath $LogFileName

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null
Start-Transcript -Path $LogPath -Force | Out-Null

$BuildSucceeded = $false

function Run-PythonModule {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Module,

        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]] $ModuleArguments
    )

    $display = @("py", "-m", $Module) + $ModuleArguments
    Write-Host ""
    Write-Host ("> " + ($display -join " "))

    & py -m $Module @ModuleArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $($display -join ' ')"
    }
}

try {
    $NoBuild = $args -contains "--no-build"

    if (-not $NoBuild) {
        # Refresh the Torikumi snapshot from the live History before producing
        # the site-data bundle.
        Run-PythonModule "src.infra.torikumi"

        # Refresh the structural Banzuke Changes input consumed by site89.
        Run-PythonModule "src.infra.new_banzuke"
        Run-PythonModule "src.analysis.banzuke_compare.publisher"
    }

    Run-PythonModule "src.products.build_site89" @args
    $BuildSucceeded = $true
}
finally {
    $BuildEnd = Get-Date
    $Elapsed = $BuildEnd - $BuildStart

    if ($BuildSucceeded) {
        Write-Host ""
        Write-Host ("Sumo '89 build completed successfully in {0:hh\:mm\:ss} ({1:N1} seconds)." -f $Elapsed, $Elapsed.TotalSeconds)
    }

    Write-Host ""
    Write-Host "Log file: $LogPath"
    Stop-Transcript | Out-Null
}
