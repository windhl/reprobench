# compile.ps1 - LaTeX Compilation Script for HexBench
# Usage:
#   .\compile.ps1            # compile main.pdf (and figures)
#   .\compile.ps1 -Figures   # (re)compile standalone figures first
#   .\compile.ps1 -Clean     # remove auxiliary files
#   .\compile.ps1 -Open      # open the PDF when done

param(
    [switch]$Clean,
    [switch]$Open,
    [switch]$Figures
)

# Native tools (Tectonic) emit harmless messages on stderr; do not treat as fatal.
$ErrorActionPreference = "Continue"
$MainFile = "main"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== HexBench LaTeX Compiler ===" -ForegroundColor Cyan

# Clean mode
if ($Clean) {
    Write-Host "Cleaning auxiliary files..." -ForegroundColor Yellow
    $auxExtensions = @("aux", "bbl", "blg", "log", "out", "toc", "lof", "lot", "fls", "fdb_latexmk", "synctex.gz", "xdv")
    foreach ($ext in $auxExtensions) {
        Remove-Item -Path "*.$ext" -ErrorAction SilentlyContinue
        Remove-Item -Path "figures\*.$ext" -ErrorAction SilentlyContinue
    }
    Write-Host "Clean complete." -ForegroundColor Green
    exit 0
}

# Locate a TeX engine. Prefer Tectonic (handles bibtex + multi-pass automatically).
$tectonicLocal = Join-Path $ScriptDir "..\..\tools\tectonic\extracted\tectonic.exe"
$tectonic = $null
if (Test-Path $tectonicLocal) { $tectonic = (Resolve-Path $tectonicLocal).Path }
elseif (Get-Command tectonic -ErrorAction SilentlyContinue) { $tectonic = "tectonic" }

if ($tectonic) {
    # Compile standalone figures first if requested or if PDFs are missing.
    $figs = @("pipeline", "case_study", "roadblock_heatmap")
    foreach ($f in $figs) {
        $tex = "figures\$f.tex"
        $pdf = "figures\$f.pdf"
        if ((Test-Path $tex) -and ($Figures -or -not (Test-Path $pdf))) {
            Write-Host "Compiling figure: $f ..." -ForegroundColor Yellow -NoNewline
            & $tectonic -X compile $tex --outdir figures *> $null
            if (Test-Path $pdf) { Write-Host " OK" -ForegroundColor Green }
            else { Write-Host " FAILED" -ForegroundColor Red; exit 1 }
        }
    }

    Write-Host "Compiling $MainFile.tex with Tectonic ..." -ForegroundColor Yellow -NoNewline
    & $tectonic -X compile "$MainFile.tex" --outdir . *> $null
    if (Test-Path "$MainFile.pdf") {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "Re-run with: $tectonic -X compile $MainFile.tex --keep-logs" -ForegroundColor White
        exit 1
    }
}
elseif (Get-Command pdflatex -ErrorAction SilentlyContinue) {
    Write-Host "Tectonic not found; using pdflatex." -ForegroundColor Yellow
    $steps = @(
        "pdflatex -interaction=nonstopmode $MainFile.tex",
        "bibtex $MainFile",
        "pdflatex -interaction=nonstopmode $MainFile.tex",
        "pdflatex -interaction=nonstopmode $MainFile.tex"
    )
    foreach ($cmd in $steps) {
        Invoke-Expression $cmd 2>&1 | Out-Null
    }
    if (-not (Test-Path "$MainFile.pdf")) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }
}
else {
    Write-Host "Error: no TeX engine found (tectonic or pdflatex)." -ForegroundColor Red
    Write-Host "Tectonic was installed at tools\tectonic\extracted\tectonic.exe" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Compilation successful! Output: $MainFile.pdf" -ForegroundColor Green

if ($Open -and (Test-Path "$MainFile.pdf")) {
    Start-Process "$MainFile.pdf"
}
