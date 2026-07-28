#!/bin/bash
set -e

TARGETS="reprobench ReproducibilityChecklist appendix_standalone"

for target in $TARGETS; do
    echo "========== Compiling $target =========="
    pdflatex -interaction=nonstopmode $target.tex > /dev/null 2>&1 || true
    bibtex $target > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode $target.tex > /dev/null 2>&1 || true
    pdflatex -interaction=nonstopmode $target.tex > /dev/null 2>&1 || true
    if [ -f $target.pdf ]; then
        echo "  ✓ $target.pdf ($(du -h $target.pdf | cut -f1))"
    else
        echo "  ✗ $target.pdf FAILED"
    fi
done

echo "========== Done =========="
