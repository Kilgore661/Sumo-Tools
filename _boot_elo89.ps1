# _boot_elo89.ps1
#
# Refresh the accepted Elo-89 inputs, produce its independent bundle, assemble
# files/output/make_elo89, and deploy to the configured sumo-elo89 targets.
# Pass --local-only to skip the remote SFTP target.

$ErrorActionPreference = "Stop"

$BuildStart = Get-Date
$LogDirectory = Join-Path -Path (Get-Location) -ChildPath "files\output\logs"
$LogFileName = "{0} elo89.log" -f $BuildStart.ToString("yyyy-MM-dd HH-mm-ss")
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
        Run-PythonModule "src.infra.new_banzuke"
        Run-PythonModule "src.infra.torikumi"
        Run-PythonModule "src.analysis.banzuke_compare.publisher"
    }

    Run-PythonModule "src.products.build_elo89" @args
    $BuildSucceeded = $true
}
finally {
    $BuildEnd = Get-Date
    $Elapsed = $BuildEnd - $BuildStart

    if ($BuildSucceeded) {
        Write-Host ""
        Write-Host ("Elo-89 build completed successfully in {0:hh\:mm\:ss} ({1:N1} seconds)." -f $Elapsed, $Elapsed.TotalSeconds)
    }

    Write-Host ""
    Write-Host "Log file: $LogPath"
    Stop-Transcript | Out-Null
}
