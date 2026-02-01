#!/usr/bin/env python3
"""Check repository for files larger than the allowed limit (100 MB).

Usage:
    python scripts/check_large_files.py

Exits with non-zero status if any files exceed the limit.
"""
from pathlib import Path
import sys

MAX_BYTES = 100 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[1]

ignore = {".git", "venv", "env", "__pycache__", "data"}

if __name__ == "__main__":
    big_files = []
    for p in ROOT.rglob("*"):
        try:
            if p.is_file():
                # skip files under ignored top-level dirs
                if any(part in ignore for part in p.relative_to(ROOT).parts):
                    continue
                size = p.stat().st_size
                if size > MAX_BYTES:
                    big_files.append((p, size))
        except Exception:
            continue

    if big_files:
        print("Found files exceeding 100 MB:")
        for p, s in big_files:
            print(f" - {p} ({s / (1024*1024):.2f} MB)")
        sys.exit(2)
    print("No files >100 MB found.")
    sys.exit(0)
