# Requires PowerShell 5.1+ (Windows 11) and the existing 'trendestimation' Conda env.
# From the repo root:
#   .\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small
#   .\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small -Execute -Archive
#   .\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase medium -Execute -Archive
#   .\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase large -Execute -Archive
#   .\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small -ResumeTag TAG -Execute -Archive
[CmdletBinding()]
param(
  [ValidateSet('small','medium','large','all')][string]$Phase = 'small',
  [ValidateRange(1,100)][int]$Seeds = 100,
  [ValidateSet(1,10,100,1000,10000)][int]$MaxCandidates = 10000,
  [ValidateRange(1,1000000000)][int]$MaxWork = 50000000,
  [ValidateSet(32,64,128,256,512,1024,2048)][int]$DenseLimitN = 512,
  [ValidatePattern('^[A-Za-z0-9_-]{4,70}$')][string]$ResumeTag,
  [string]$CondaExe,
  [switch]$Execute,
  [switch]$Archive
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$entered = $false

function Assert-GitSuccess([string]$purpose) {
  if ($LASTEXITCODE -ne 0) { throw "Git failed during $purpose (exit $LASTEXITCODE)" }
}

try {
  Push-Location $repo
  $entered = $true
  $branchName = (git branch --show-current).Trim()
  Assert-GitSuccess 'checking source branch'
  if ($branchName -ne 'main') {
    throw "This measurement must start on a synchronized main checkout (current: $branchName). Do not overwrite another agent's branch."
  }
  git diff --quiet
  Assert-GitSuccess 'checking clean tracked working tree'
  git diff --cached --quiet
  Assert-GitSuccess 'checking clean staged index'
  git fetch origin main
  Assert-GitSuccess 'fetching source ref'
  $localSha=(git rev-parse HEAD).Trim()
  Assert-GitSuccess 'resolving local source SHA'
  $remoteSha=(git rev-parse origin/main).Trim()
  Assert-GitSuccess 'resolving remote source SHA'
  if ($localSha -ne $remoteSha) {
    throw "main and origin/main differ. Review and run 'git pull --ff-only origin main' before measuring."
  }
  if ($Archive -and -not $Execute) {
    throw 'Use -Execute -Archive to measure and archive; plain invocation is dry-run.'
  }
  if ($Archive) {
    $authorName = git config user.name
    Assert-GitSuccess 'checking Git author identity'
    $authorEmail = git config user.email
    Assert-GitSuccess 'checking Git author email'
    if ([string]::IsNullOrWhiteSpace($authorName) -or [string]::IsNullOrWhiteSpace($authorEmail)) {
      throw 'Configure Git user.name and user.email before starting a multi-hour run.'
    }
  }
  $env:OPENBLAS_NUM_THREADS='1'
  $env:MKL_NUM_THREADS='1'
  $env:OMP_NUM_THREADS='1'
  $env:NUMEXPR_NUM_THREADS='1'
  $env:VECLIB_MAXIMUM_THREADS='1'
  $env:PYTHONHASHSEED='0'

  if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    $candidate='C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe'
    if (Test-Path -LiteralPath $candidate) {
      $CondaExe=$candidate
    } else {
      $command=Get-Command conda.exe -ErrorAction Stop
      $CondaExe=$command.Source
    }
  }
  if (!(Test-Path -LiteralPath $CondaExe)) {
    throw "Conda executable does not exist: $CondaExe"
  }
  if ($ResumeTag) {
    $runTag=$ResumeTag
  } else {
    $runTag='experiment013_{0}_{1}_{2}' -f $Phase,(Get-Date -Format 'yyyyMMdd_HHmmss'),$PID
  }
  $relative="paper/benchmarks/experiment013/runs/$runTag"
  $runFolder=Join-Path $repo ($relative.Replace('/','\'))
  if ($Execute -and !$ResumeTag -and (Test-Path -LiteralPath $runFolder)) {
    throw "Run directory already exists: $runFolder"
  }
  $py='paper/benchmarks/experiment013/run.py'
  $argsList=@('run','--no-capture-output','-n','trendestimation','python',
              $py,'--phase',$Phase,'--seeds',"$Seeds",
              '--max-candidates',"$MaxCandidates",'--max-work',"$MaxWork",
              '--dense-limit-n',"$DenseLimitN")
  if ($Execute) {
    $argsList += @('--execute','--out',$relative)
  }
  if ($ResumeTag) {
    $argsList += '--resume'
  }
  Write-Host "Source commit $localSha"
  Write-Host "Phase $Phase; seeds $Seeds; maximum candidates $MaxCandidates; difference orders 1,2,3"
  if (!$Execute) {
    Write-Host 'PLAN ONLY. No numerical work; -Execute is required.'
    & $CondaExe @argsList
    if ($LASTEXITCODE -ne 0) { throw "Experiment plan failed ($LASTEXITCODE)" }
    return
  }

  $runFailed=$false
  try {
    & $CondaExe @argsList
    if ($LASTEXITCODE -ne 0) { $runFailed=$true; Write-Warning "Numerical run exit code $LASTEXITCODE" }
    if (!$runFailed) {
      & $CondaExe run --no-capture-output -n trendestimation python paper/benchmarks/experiment013/analyze.py --input $relative
      if ($LASTEXITCODE -ne 0) { $runFailed=$true; Write-Warning "Evidence audit failed ($LASTEXITCODE)" }
    }
  } catch {
    $runFailed=$true
    Write-Warning "Run or analysis interrupted: $($_.Exception.Message)"
  }

  if ($Archive) {
    if (!(Test-Path -LiteralPath $runFolder)) {
      throw 'Cannot archive: output directory was never created.'
    }
    $manifest=Join-Path $runFolder 'file_inventory.csv'
    Get-ChildItem -LiteralPath $runFolder -File -Recurse |
      Where-Object { $_.FullName -ne $manifest } |
      Sort-Object FullName |
      ForEach-Object {
        [PSCustomObject]@{
          path=$_.FullName.Substring($runFolder.Length+1).Replace('\','/')
          bytes=$_.Length
          sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
      } | Export-Csv -LiteralPath $manifest -NoTypeInformation -Encoding UTF8

    $resultBranch="results/experiment013-$runTag"
    $archiveDir=Join-Path (Split-Path $repo -Parent) "experiment013-archive-$runTag"
    if (Test-Path -LiteralPath $archiveDir) {
      throw "Archive worktree location already exists: $archiveDir"
    }
    git worktree add -b $resultBranch $archiveDir $localSha
    Assert-GitSuccess 'creating independent archive worktree'
    $destination=Join-Path $archiveDir 'paper/benchmarks/experiment013/runs'
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Copy-Item -LiteralPath $runFolder -Destination $destination -Recurse -Force
    Push-Location $archiveDir
    try {
      $identityName=(git config user.name).Trim()
      Assert-GitSuccess 'checking Git author name'
      $identityEmail=(git config user.email).Trim()
      Assert-GitSuccess 'checking Git author email'
      if (!$identityName -or !$identityEmail) {
        throw 'Configure Git user.name and user.email in this VM checkout before archiving.'
      }
      git add -f -- $relative
      Assert-GitSuccess 'staging only new results'
      git diff --cached --quiet
      if ($LASTEXITCODE -eq 0) { throw 'Archive contained no new tracked evidence' }
      git commit -m "experiment013: preserve Windows $Phase raw evidence ($runTag)"
      Assert-GitSuccess 'committing archived evidence'
      git push -u origin "HEAD:refs/heads/$resultBranch"
      Assert-GitSuccess 'pushing immutable archive'
      Write-Host "PUSHED: https://github.com/heri-espino/trendestimation/tree/$resultBranch"
    } finally {
      Pop-Location
    }
    Write-Host "Unmodified original evidence remains: $runFolder"
    Write-Host "A separate archive worktree remains at: $archiveDir"
  }
  if ($runFailed) {
    throw 'Some runs/analysis failed. Partial evidence was preserved; inspect it before -ResumeTag.'
  }
  Write-Host "Finished Experiment013 $Phase ($Seeds scheduled seeds per case)."
} finally {
  if ($entered) { Pop-Location }
}
