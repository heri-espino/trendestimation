<#
Build all research-lecture figures and export Marp HTML/PDF.
powershell -ExecutionPolicy Bypass -File slides/professor_lecture/build.ps1
Options: -HtmlOnly, -SkipFigures. Heavy benchmarks never run by default.
#>
param([switch]$HtmlOnly,[switch]$SkipFigures)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepositoryRoot=(Resolve-Path (Join-Path $Root "../..")).Path
# Use the repository's src-layout package without requiring an editable pip
# installation. Preserve an existing PYTHONPATH and restore it on exit.
$SourceDirectory=Join-Path $RepositoryRoot "src"
$PreviousPythonPath=[Environment]::GetEnvironmentVariable("PYTHONPATH", "Process")
Push-Location $RepositoryRoot
try {
    if ([string]::IsNullOrEmpty($PreviousPythonPath)) {
        $env:PYTHONPATH=$SourceDirectory
    }
    else {
        $env:PYTHONPATH="$SourceDirectory$([IO.Path]::PathSeparator)$PreviousPythonPath"
    }
    & python -c "import trendestimation; print('[lecture] Using:', trendestimation.__file__)"
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot import local trendestimation source. Run: python -m pip install -e '.[plot]'"
    }
    if (-not $SkipFigures) {
        Write-Host "[lecture] Generating reproducible SVG figures..."
        & python (Join-Path $Root "make_figures.py")
        if ($LASTEXITCODE -ne 0) { throw "Figure generator failed: $LASTEXITCODE" }
    }
    $md=Join-Path $Root "main.md"
    $css=Join-Path $Root "theme.css"
    $html=Join-Path $Root "main.html"
    $pdf=Join-Path $Root "main.pdf"
    Write-Host "[lecture] Exporting offline HTML..."
    & npx --yes "@marp-team/marp-cli" $md --theme $css --html --allow-local-files --output $html
    if ($LASTEXITCODE -ne 0) { throw "Marp HTML failed: $LASTEXITCODE" }
    if (-not $HtmlOnly) {
        Write-Host "[lecture] Exporting PDF (needs Chromium)..."
        & npx --yes "@marp-team/marp-cli" $md --theme $css --html --allow-local-files --pdf --output $pdf
        if ($LASTEXITCODE -ne 0) { throw "Marp PDF failed: $LASTEXITCODE" }
    }
    Write-Host "[lecture] HTML: $html"
    if (-not $HtmlOnly) { Write-Host "[lecture] PDF: $pdf" }
    Write-Host "[lecture] SVG provenance: $(Join-Path $Root 'figures/manifest.json')"
}
finally {
    if ($null -eq $PreviousPythonPath) {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONPATH=$PreviousPythonPath
    }
    Pop-Location
}
