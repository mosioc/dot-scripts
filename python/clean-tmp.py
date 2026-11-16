#!/usr/bin/env python3
"""Remove old regular files from an explicitly chosen temp/cache directory."""

import argparse
import os
import stat
import time
from pathlib import Path

from _common import add_apply, check_target, mutation_root, nonnegative_float, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="temp/cache directory to clean")
    parser.add_argument("--days", type=nonnegative_float, default=7, help="minimum age in days (default: 7)")
    add_apply(parser)
    args = parser.parse_args()
    root = mutation_root(args.path)
    cutoff = time.time() - args.days * 86400
    count = 0

    def walk_error(error):
        raise error

    for current, dirs, files in os.walk(root, onerror=walk_error):
        folder = Path(current)
        dirs[:] = sorted(name for name in dirs if name != ".git" and not (folder / name).is_symlink())
        for name in sorted(files):
            path = folder / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_mtime > cutoff:
                continue
            print(f"{'Remove' if args.apply else 'Would remove'} {path.relative_to(root)}")
            if args.apply:
                check_target(root, path)
                # A file refreshed during the scan should be retained.
                if path.stat().st_mtime > cutoff:
                    continue
                path.unlink()
            count += 1
    print(f"{count} file(s) {'removed' if args.apply else 'selected; use --apply to remove'}.")


if __name__ == "__main__":
    run(main)
