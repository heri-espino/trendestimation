# Import and verify Experiment005 GitHub-hosted simulation outputs on Windows.
# This copies existing results, not a new independent simulation run.
param(
    [string]$ArchiveBranch = 'results/paper-c-exp005-cloud-42547883064-a1',
    [string]$CloudRunDir = 'cloud-42547883064-a1',
    [string]$Destination = "$env:USERPROFILE\Documents\TrendEstimation-PaperC\experiment005\import-cloud-42547883064-a1"
)
$ErrorActionPreference = 'Stop'
$repo = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or !(Test-Path -LiteralPath $repo)) {
    throw 'Run from inside an existing trendestimation Git clone.'
}
if (Test-Path -LiteralPath $Destination) {
    throw "Refusing overwrite: $Destination"
}
$relative = "paper/ngsim-jerk-case-study/experiments/experiment005/runs/$CloudRunDir"
$temp = Join-Path $env:TEMP ("trendestimation-exp005-import-" + $PID)
if (Test-Path -LiteralPath $temp) {
    throw "Temporary worktree already exists: $temp"
}
$added = $false
try {
    $fetchSpec = ("refs/heads/{0}:refs/remotes/origin/{0}" -f $ArchiveBranch)
    & git fetch origin $fetchSpec
    if ($LASTEXITCODE -ne 0) { throw 'Could not fetch complete cloud results' }
    & git worktree add --detach $temp "refs/remotes/origin/$ArchiveBranch"
    if ($LASTEXITCODE -ne 0) { throw 'Could not open isolated results worktree' }
    $added = $true
    $source = Join-Path $temp $relative
    $inventoryPath = Join-Path $source 'metadata\file_inventory.json'
    if (!(Test-Path -LiteralPath $inventoryPath)) {
        throw 'Cloud result inventory was not found'
    }
    $inventory = Get-Content -LiteralPath $inventoryPath -Raw | ConvertFrom-Json
    if ($inventory.run_status -ne 'pilot_and_confirm_complete') {
        throw "Source run incomplete: $($inventory.run_status)"
    }
    New-Item -Path (Split-Path -Parent $Destination) -ItemType Directory -Force | Out-Null
    New-Item -Path $Destination -ItemType Directory | Out-Null
    Get-ChildItem -LiteralPath $source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }
    $checked = 0
    foreach ($entry in $inventory.files) {
        $relativePath = $entry.relative_path -replace '/', [IO.Path]::DirectorySeparatorChar
        $candidate = Join-Path $Destination $relativePath
        if (!(Test-Path -LiteralPath $candidate)) {
            throw "Missing copied file: $candidate"
        }
        $length = (Get-Item -LiteralPath $candidate).Length
        $hash = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($length -ne [int64]$entry.bytes -or $hash -ne $entry.sha256.ToLowerInvariant()) {
            throw "Size/SHA mismatch: $candidate"
        }
        $checked += 1
    }
    if ($checked -ne $inventory.total_files_excluding_this_inventory) {
        throw 'Manifest file count mismatch'
    }
    $import = [ordered]@{
        source_archive_branch = $ArchiveBranch
        source_cloud_run_directory = $relative
        provenance = 'GitHub-hosted simulation COPIED to VM; not independently rerun'
        source_inventory_sha256 = (Get-FileHash -LiteralPath (Join-Path $Destination 'metadata\file_inventory.json') -Algorithm SHA256).Hash.ToLowerInvariant()
        imported_utc = [DateTime]::UtcNow.ToString('o')
        destination = $Destination
        verified_files = $checked
        source_commit = (Get-Content -LiteralPath (Join-Path $Destination 'metadata\source_commit.txt') -Raw).Trim()
    }
    $import | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Destination 'metadata\vm_import_manifest.json') -Encoding UTF8
    Write-Host "Verified all $checked cloud-generated files at $Destination"
}
finally {
    if ($added) {
        & git worktree remove --force $temp | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Check temporary worktree manually: $temp"
        }
    }
}
