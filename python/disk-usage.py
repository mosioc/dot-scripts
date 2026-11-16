#!/usr/bin/env python3
"""Rank folders by logical file size without following symlinks."""

import argparse
import os
import sys
from pathlib import Path

from _common import directory, positive_int, run


def human_size(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--depth", type=positive_int, default=1, help="folder depth to show (default: 1)")
    parser.add_argument("--limit", type=positive_int, default=10, help="number of folders (default: 10)")
    args = parser.parse_args()
    root = directory(args.path)
    totals = {}
    errors = []
    for current, dirs, files in os.walk(root, topdown=False, onerror=errors.append):
        folder = Path(current)
        total = 0
        for name in files:
            path = folder / name
            try:
                if not path.is_symlink():
                    total += path.stat().st_size
            except OSError as error:
                errors.append(error)
        total += sum(totals.get(folder / name, 0) for name in dirs)
        totals[folder] = total
    print(f"{human_size(totals.get(root, 0)):>12}  {root} (total)")
    candidates = [(size, path) for path, size in totals.items()
                  if path != root and len(path.relative_to(root).parts) <= args.depth]
    for size, path in sorted(candidates, key=lambda item: (-item[0], str(item[1])))[:args.limit]:
        print(f"{human_size(size):>12}  {path.relative_to(root)}/")
    for error in errors:
        print(f"Warning: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    run(main)
