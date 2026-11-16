#!/usr/bin/env python3
"""Run an ordered list of commands from a JSON configuration, without a shell."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

from _common import add_apply, directory, positive_float, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", default="routine.json")
    parser.add_argument("--keep-going", action="store_true", help="continue after a failed step")
    parser.add_argument("--timeout", type=positive_float, default=300, help="seconds per step (default: 300)")
    add_apply(parser)
    args = parser.parse_args()
    config_path = Path(args.config).expanduser().resolve(strict=True)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("steps"), list) or not config["steps"]:
        raise ValueError('Configuration must contain a nonempty "steps" array')
    steps = []
    # Validate the entire plan before running even its first command.
    for index, step in enumerate(config["steps"], 1):
        if not isinstance(step, dict):
            raise ValueError(f"Step {index} must be an object")
        command = step.get("command")
        if (not isinstance(command, list) or not command
                or not all(isinstance(arg, str) and "\0" not in arg for arg in command)
                or not command[0]):
            raise ValueError(f"Step {index}: command must be a nonempty array of string arguments")
        name = step.get("name", f"Step {index}")
        cwd = step.get("cwd", ".")
        if not isinstance(name, str) or not isinstance(cwd, str):
            raise ValueError(f"Step {index}: name and cwd must be strings")
        workdir = directory(config_path.parent / Path(cwd).expanduser())
        steps.append((name, command, workdir))
    failed = False
    for name, command, workdir in steps:
        print(f"{name}: {shlex.join(command)} (cwd: {workdir})", flush=True)
        if not args.apply:
            continue
        try:
            result = subprocess.run(command, cwd=workdir, timeout=args.timeout, check=False)
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"{name}: {error}", file=sys.stderr)
            code = 1
        if code:
            print(f"{name}: failed (exit {code})", file=sys.stderr)
            failed = True
            if not args.keep_going:
                break
    if not args.apply:
        print("Preview only; use --apply to run these commands.")
    return 1 if failed else 0


if __name__ == "__main__":
    run(main)
