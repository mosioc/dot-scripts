"""Small helpers shared by the Python command-line scripts."""

import argparse
import math
import sys
from pathlib import Path


def run(main):
    try:
        sys.exit(main() or 0)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Aborted.", file=sys.stderr)
        sys.exit(130)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than 0")
    return number


def nonnegative_float(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite number of at least 0")
    return number


def directory(value):
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    return path


def mutation_root(value):
    path = Path(value).expanduser().absolute()
    if path.is_symlink():
        raise ValueError(f"Refusing a symlink root: {path}")
    root = directory(path)
    home = Path.home().resolve()
    if root == home or root in home.parents or root == Path(root.anchor):
        raise ValueError(f"Choose a specific subdirectory, not {root}")
    return root


def check_target(root, target):
    """Recheck containment and symlinks immediately before a mutation."""
    relative = target.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Refusing a symlink: {current}")
    target.resolve().relative_to(root)


def add_apply(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="perform the changes")
    group.add_argument("-n", "--dry-run", action="store_true", help="preview only (default)")


def write_text(text, output):
    if output == "-":
        sys.stdout.write(text)
    else:
        # Exclusive creation prevents accidentally overwriting the input or other files.
        with Path(output).expanduser().open("x", encoding="utf-8", newline="") as stream:
            stream.write(text)


def strict_json_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")
