"""Shared preview-first cleanup for generated project directories."""

import argparse
import os
import shutil
from pathlib import Path

from _common import add_apply, check_target, mutation_root


def clean(description, names):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("path", nargs="?", default=".", help="project root (default: current directory)")
    add_apply(parser)
    args = parser.parse_args()
    root = mutation_root(args.path)
    count = 0

    def walk_error(error):
        raise error

    for current, dirs, _ in os.walk(root, onerror=walk_error):
        folder = Path(current)
        descend = []
        for name in sorted(dirs):
            path = folder / name
            if path.is_symlink() or name in {".git", ".hg", ".svn"}:
                continue
            if name in names:
                print(f"{'Remove' if args.apply else 'Would remove'} {path.relative_to(root)}/")
                if args.apply:
                    check_target(root, path)
                    shutil.rmtree(path)
                count += 1
            elif name not in {"node_modules", ".venv", "venv"}:
                descend.append(name)
        dirs[:] = descend
    print(f"{count} directory(s) {'removed' if args.apply else 'selected; use --apply to remove'}.")
