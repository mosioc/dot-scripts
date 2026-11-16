#!/usr/bin/env python3
"""Group top-level downloaded files into categories without overwriting files."""

import argparse
import os
from pathlib import Path

from _common import add_apply, check_target, mutation_root, run


CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic", ".avif"},
    "documents": {".pdf", ".txt", ".md", ".doc", ".docx", ".odt", ".csv", ".xls", ".xlsx", ".ppt", ".pptx"},
    "archives": {".zip", ".gz", ".bz2", ".xz", ".tar", ".7z", ".rar"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"},
    "video": {".mp4", ".mov", ".mkv", ".webm", ".avi"},
    "installers": {".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm", ".appimage"},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=str(Path.home() / "Downloads"))
    add_apply(parser)
    args = parser.parse_args()
    root = mutation_root(args.path)
    plan = []
    reserved = set()
    for path in sorted(root.iterdir()):
        if path.name.startswith(".") or path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() in {".part", ".crdownload", ".download", ".tmp"}:
            continue
        category = next((name for name, extensions in CATEGORIES.items()
                         if path.suffix.lower() in extensions), "other")
        folder = root / category
        check_target(root, folder)
        if folder.exists() and not folder.is_dir():
            raise ValueError(f"Category is not a directory: {folder}")
        destination = folder / path.name
        index = 1
        while destination.exists() or destination.is_symlink() or destination in reserved:
            destination = folder / f"{path.stem}-{index}{path.suffix}"
            index += 1
        reserved.add(destination)
        plan.append((path, destination))
    for source, destination in plan:
        print(f"{'Move' if args.apply else 'Would move'} {source.name} -> {destination.relative_to(root)}")
        if args.apply:
            check_target(root, source)
            check_target(root, destination)
            destination.parent.mkdir(exist_ok=True)
            # Both paths are on the same filesystem. A hard link gives exclusive
            # destination creation, so even a late collision cannot overwrite data.
            os.link(source, destination, follow_symlinks=False)
            source.unlink()
    print(f"{len(plan)} file(s) {'moved' if args.apply else 'selected; use --apply to move'}.")


if __name__ == "__main__":
    run(main)
