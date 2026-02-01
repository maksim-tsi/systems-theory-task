#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IN_MD="$ROOT/docs/Theory of Systems - Ilin.md"
OUT_PDF="$ROOT/docs/reports/Systems_Theory_Ilin.pdf"

cd "$ROOT"

pandoc "$IN_MD" \
  --from markdown+yaml_metadata_block+tex_math_dollars+tex_math_single_backslash \
  --to pdf \
  --pdf-engine=xelatex \
  --toc \
  --number-sections \
  -V geometry:margin=25mm \
  -V fontsize=12pt \
  -V mainfont="Times New Roman" \
  -V monofont="Menlo" \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -V toccolor=black \
  -V documentclass=article \
  -V papersize=a4 \
  -o "$OUT_PDF"

echo "Built: $OUT_PDF"
