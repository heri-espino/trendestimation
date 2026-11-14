# Run only after the benchmark has stopped. Makes a verified local copy;
# never changes the source checkout, Git index, or remote repository.
param(
    [string]$Repo = 'C:\Users\175199\trendestimation-PC08_add97svd_20261105_025108',
    [string]$BackupRoot = 'C:\Users\175199\experiment011-backups'
)
$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path -LiteralPath $Repo).Path
$active = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -like '*experiment011*'
}
if ($active) { throw 'Stop/wait for Experiment011 processes before taking a consistent backup.' }
$relativeReport = 'paper\benchmarks\experiment011\campaigns\PC08_resume12_20261108_200034\report.json'
$reportPath = Join-Path $Repo $relativeReport
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if ($report.planned_jobs -ne 2813 -or @($report.results).Count -ne 2813) {
    throw 'Expected the author-reported 2813/2813 final checkpoint; inspect before backing up.'
}
$duplicates = @($report.results | Group-Object -Property seed_index,case | Where-Object Count -gt 1)
if ($duplicates.Count -gt 0) { throw 'Duplicate seed/case records in final report.' }
$destination = Join-Path $BackupRoot ('experiment011_' + (Get-Date -Format 'yyyyMMdd_HHmmssfff'))
if (Test-Path -LiteralPath $destination) { throw 'Backup destination already exists.' }
New-Item -ItemType Directory -Path $destination | Out-Null
$relativeRoots = @('paper\benchmarks\experiment011', 'paper\benchmarks\experiment006', 'src')
foreach ($relative in $relativeRoots) {
    $source = Join-Path $Repo $relative
    $target = Join-Path $destination $relative
    if (-not (Test-Path -LiteralPath $source)) { throw "Missing source: $source" }
    Write-Host "Copying $relative"
    robocopy $source $target /E /COPY:DAT /DCOPY:T /R:1 /W:1 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) { throw "Copy failed: $relative. Keep source and partial backup." }
}
$metadata = Join-Path $destination 'metadata'
New-Item -ItemType Directory -Path $metadata | Out-Null
Copy-Item -LiteralPath $reportPath -Destination (Join-Path $metadata 'report.json')
$head = git -C $Repo rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Could not record Git HEAD.' }
$branch = git -C $Repo branch --show-current
if ($LASTEXITCODE -ne 0) { throw 'Could not record Git branch.' }
[PSCustomObject]@{
    source_checkout = $Repo
    git_head = "$head"
    git_branch = "$branch"
    source_report = $reportPath
    report_sha256 = (Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash
    completed_jobs = @($report.results).Count
    planned_jobs = $report.planned_jobs
    backup_path = $destination
    captured_utc = (Get-Date).ToUniversalTime().ToString('o')
    independent_disk_backup = $false
} | ConvertTo-Json | Set-Content (Join-Path $metadata 'provenance.json') -Encoding UTF8
# Every copied file must match the source byte for byte. This takes time.
$inventory = @(
    foreach ($relative in $relativeRoots) {
        Get-ChildItem -LiteralPath (Join-Path $Repo $relative) -File -Recurse | ForEach-Object {
            $relativeFile = $_.FullName.Substring($Repo.Length).TrimStart('\')
            $copy = Join-Path $destination $relativeFile
            $sourceHash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            $copyHash = (Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash
            if ($sourceHash -ne $copyHash) { throw "Backup mismatch: $relativeFile" }
            [PSCustomObject]@{ path=$relativeFile; bytes=$_.Length; sha256=$sourceHash }
        }
    }
)
$inventory | Export-Csv (Join-Path $metadata 'files_sha256.csv') -NoTypeInformation -Encoding UTF8
Write-Host "VERIFIED COPY: $destination"
Write-Host "FINAL REPORT: $(Join-Path $metadata 'report.json')"
Write-Host "PROVENANCE: $(Join-Path $metadata 'provenance.json')"
Write-Host "FILE INVENTORY: $(Join-Path $metadata 'files_sha256.csv')"
Write-Host 'No uploads performed. A same-disk copy does not protect against disk/VM loss.'
