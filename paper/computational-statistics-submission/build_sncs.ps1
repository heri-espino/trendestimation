<#
.SYNOPSIS
Compile the SHORT SN Computer Science manuscript on Windows, and verify PDF exists.

.DESCRIPTION
Runs ONLY LaTeX/BibTeX. Never calls numerical selection, simulations, or
timing benchmarks. Accepts invocation from ANY working directory:

  powershell -ExecutionPolicy Bypass -File .\paper\computational-statistics-submission\build_sncs.ps1

Required: local MiKTeX/TeX Live with pdflatex + bibtex.
By default, use pdflatex/bibtex directly, bypassing Windows latexmk
shim/launcher issues. Use -UseLatexmk only to opt into latexmk+Perl.
#>
[CmdletBinding()]
param(
    [switch]$UseLatexmk,
    [switch]$NoOpen
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$tex = Join-Path $here "sncs_main.tex"
$pdf = Join-Path $here "sncs_main.pdf"
$log = Join-Path $here "sncs_main.log"

function Assert-File([string]$file, [string]$label) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Missing ${label}: $file"
    }
}

function Find-Executable([string]$name) {
    $all = @(Get-Command $name -All -ErrorAction SilentlyContinue)
    foreach ($cmd in $all) {
        if ($cmd.CommandType -eq "Application" -and $cmd.Source) {
            return $cmd.Source
        }
    }
    return $null
}

function Invoke-Checked([string]$executable, [string[]]$arguments) {
    Write-Host "[sncs] $executable $($arguments -join ' ')" -ForegroundColor Cyan
    # PowerShell 7 may propagate native errors as exceptions; still show log.
    & $executable @arguments
    $exitCode = $LASTEXITCODE
    if ($null -ne $exitCode -and $exitCode -ne 0) {
        throw "External process returned exit code $exitCode : $executable"
    }
}

function Check-PDF() {
    if (-not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
        throw ("Build command ended but did NOT create sncs_main.pdf. " +
               "Check the TeX installation and sncs_main.log (if present).")
    }
    $size = (Get-Item -LiteralPath $pdf).Length
    if ($size -lt 1000) {
        throw "Built PDF is unexpectedly small ($size bytes): $pdf"
    }
}

Assert-File $tex "short manuscript"
Assert-File (Join-Path $here "sn-jnl.cls") "Springer class"
Assert-File (Join-Path $here "sn-mathphys-ay.bst") "Springer BibTeX style"
Assert-File (Join-Path $here "bibliografia.bib") "bibliography database"
Assert-File (Join-Path $here "final_solver_inference_table.tex") "cached solver table"
Assert-File (Join-Path $here "final_inversion_table.tex") "cached inversion table"
Assert-File (Join-Path $here "figures\final_solver_inference.pdf") "cached solver figure"
Assert-File (Join-Path $here "figures\final_inversion_speed.pdf") "cached inversion figure"
Assert-File (Join-Path $here "figures\sncs_compact_dashboard.pdf") "cached short-paper dashboard"

$pdflatex = Find-Executable "pdflatex"
$bibtex = Find-Executable "bibtex"
$latexmk = Find-Executable "latexmk"
$perl = Find-Executable "perl"

if (-not $pdflatex -or -not $bibtex) {
    throw ("pdflatex and bibtex must be installed. " +
           "Install MiKTeX for your Windows USER (no administrator required), " +
           "or use TeX Live. Make sure both executables are on PATH. " +
           "Get-Command pdflatex,bibtex -All")
}

Write-Host "[sncs] TeX folder: $here" -ForegroundColor Cyan
Write-Host "[sncs] pdflatex: $pdflatex"
Write-Host "[sncs] bibtex: $bibtex"
Write-Host "[sncs] latexmk: $latexmk"
Write-Host "[sncs] perl: $perl"
Write-Host "[sncs] No optimization or numerical experiments will run."

Push-Location $here
try {
    if ($UseLatexmk) {
        if (-not $latexmk -or -not $perl) {
            throw "-UseLatexmk requires both latexmk and Perl on PATH. Omit the switch to use direct pdfLaTeX."
        }
        Write-Host "[sncs] Compiling with opt-in latexmk." -ForegroundColor Cyan
        Invoke-Checked -executable $latexmk -arguments @("-pdf", "-gg", "-interaction=nonstopmode",
                                  "-file-line-error", "-halt-on-error",
                                  "sncs_main.tex")
    } else {
        Write-Host "[sncs] Compiling directly with pdflatex + bibtex (no Perl required)." -ForegroundColor Cyan
        Invoke-Checked -executable $pdflatex -arguments @("-interaction=nonstopmode", "-file-line-error",
                                    "-halt-on-error", "sncs_main.tex")
        Invoke-Checked -executable $bibtex -arguments @("sncs_main")
        Invoke-Checked -executable $pdflatex -arguments @("-interaction=nonstopmode", "-file-line-error",
                                    "-halt-on-error", "sncs_main.tex")
        Invoke-Checked -executable $pdflatex -arguments @("-interaction=nonstopmode", "-file-line-error",
                                    "-halt-on-error", "sncs_main.tex")
    }
    Check-PDF
    Write-Host "[sncs] SUCCESS: $pdf ($((Get-Item $pdf).Length) bytes)" -ForegroundColor Green
} catch {
    Write-Host "[sncs] LaTeX compilation FAILED: $_" -ForegroundColor Red
    if (Test-Path -LiteralPath $log) {
        Write-Host "[sncs] Last 55 TeX log lines:" -ForegroundColor Yellow
        Get-Content -LiteralPath $log -Tail 55
    } else {
        Write-Host "[sncs] No sncs_main.log was created: the LaTeX executable may not have started." -ForegroundColor Yellow
    }
    throw
} finally {
    Pop-Location
}
if (-not $NoOpen) {
    Start-Process -FilePath $pdf
}
