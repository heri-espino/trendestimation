# Run from repository root in a dedicated worktree on Windows PCAG103A-08.
# Each finished/failed batch is committed to an immutable GitHub results branch.
param(
    [ValidateRange(0,999)][int]$ShardIndex = 0,
    [ValidateRange(1,1000)][int]$ShardCount = 16,
    [ValidateRange(0,1000000)][int]$StartAttempt = 0,
    [ValidateRange(1,1000)][int]$MethodAttempts = 10,
    [ValidateRange(1,32)][int]$Workers = 8,
    [ValidateRange(1,100)][int]$Repeats = 2,
    [ValidateRange(2,100)][int]$SeriesCount = 2,
    [ValidateRange(1,68719476736)][long]$MaxDenseBytes = 2147483648,
    [ValidateRange(1,137438953472)][long]$TotalParallelDenseBytes = 17179869184,
    [string]$CondaExe = 'C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe'
)
$ErrorActionPreference = 'Stop'
if ($ShardIndex -ge $ShardCount) { throw 'ShardIndex must be smaller than ShardCount.' }
if ($Workers * $MaxDenseBytes -gt $TotalParallelDenseBytes) {
    throw 'Reserved worker memory exceeds TotalParallelDenseBytes; reduce Workers or memory per worker.'
}
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Push-Location $repo
try {
    if (-not (Test-Path -LiteralPath $CondaExe)) {
        throw "Conda executable not found: $CondaExe"
    }
    $status = @(& git status --porcelain)
    if ($LASTEXITCODE -ne 0 -or $status.Count -gt 0) {
        throw 'Use a clean dedicated Git worktree before running benchmarks.'
    }
    $sourceSha = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read source commit.' }
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
    $machine = if ($env:COMPUTERNAME) { $env:COMPUTERNAME } else { 'windows' }
    $slug = "experiment010-uncapped-$machine-$stamp-shard$ShardIndex-offset$StartAttempt"
    $relative = "paper/benchmarks/experiment010/runs/$slug"
    $archive = "results/$slug"
    $env:PYTHONPATH = (Join-Path $repo 'src')
    $env:OPENBLAS_NUM_THREADS = '1'
    $env:MKL_NUM_THREADS = '1'
    $env:OMP_NUM_THREADS = '1'
    $env:NUMEXPR_NUM_THREADS = '1'
    $env:PYTHONHASHSEED = '0'

    Write-Host "Source: $sourceSha ; shard $ShardIndex/$ShardCount ; start $StartAttempt"
    Write-Host "Independent worker processes: $Workers; one BLAS thread each."
    Write-Host 'No per-method, estimated-work, or whole-batch time cutoff; parallel worker pool enabled.'
    $runError = $null
    try {
        $testArgs = @('run','--no-capture-output','-n','trendestimation',
          'python','-m','pytest','-q','tests/test_experiment010_runner.py',
          'tests/test_experiment010_mle_normalization.py',
          'tests/test_experiment006_selected_inverse.py',
          'tests/test_experiment006_hybrid_criteria.py')
        & $CondaExe @testArgs
        if ($LASTEXITCODE -ne 0) { throw "Preflight tests failed: $LASTEXITCODE" }

        $runArgs = @('run','--no-capture-output','-n','trendestimation',
          'python','paper/benchmarks/experiment010/run_parallel.py',
          '--shard-index',"$ShardIndex",
          '--shard-count',"$ShardCount",'--start-attempt',"$StartAttempt",
          '--max-method-attempts',"$MethodAttempts",
          '--workers',"$Workers",
          '--repeats',"$Repeats",'--series-count',"$SeriesCount",
          '--max-dense-bytes',"$MaxDenseBytes",
          '--total-parallel-dense-bytes',"$TotalParallelDenseBytes",
          '--output',$relative)
        & $CondaExe @runArgs
        if ($LASTEXITCODE -ne 0) { throw "Benchmark exited with code $LASTEXITCODE" }
    }
    catch {
        $runError = $_
        Write-Warning "Batch incomplete; preserving available evidence: $($_.Exception.Message)"
    }

    # Archive all completed rows, numerical errors and even partial logs.
    $dir = Join-Path $repo $relative
    if (Test-Path -LiteralPath $dir) {
        $summaryFile = Join-Path $dir 'batch_summary.json'
        if (Test-Path -LiteralPath $summaryFile) {
            $summary = Get-Content -Raw -LiteralPath $summaryFile | ConvertFrom-Json
            Write-Host "Next attempt within same shard: $($summary.next_attempt_offset)"
        }
        $freezeFile = Join-Path $dir 'requirements-resolved.txt'
        & $CondaExe run --no-capture-output -n trendestimation python -m pip freeze |
          Out-File -FilePath $freezeFile -Encoding utf8
        & git switch -c $archive
        if ($LASTEXITCODE -ne 0) { throw "Cannot create results branch $archive" }
        & git add -f -- $relative
        if ($LASTEXITCODE -ne 0) { throw 'Cannot stage outputs.' }
        & git commit -m "experiment010: uncapped numerical outcomes $slug"
        if ($LASTEXITCODE -ne 0) { throw 'Cannot commit outputs.' }
        & git push origin "HEAD:refs/heads/$archive"
        if ($LASTEXITCODE -ne 0) {
            throw "Git push failed; evidence remains locally on branch $archive"
        }
        Write-Host "Archived: https://github.com/heri-espino/trendestimation/tree/$archive"
        & git switch --detach $sourceSha
        if ($LASTEXITCODE -ne 0) { throw 'Results pushed, but cannot reset detached source.' }
    }
    if ($null -ne $runError) {
        throw "Archived partial results. Cause: $($runError.Exception.Message)"
    }
    Write-Host 'Finished. Use next_attempt_offset for the following batch.'
}
finally {
    Pop-Location
}
