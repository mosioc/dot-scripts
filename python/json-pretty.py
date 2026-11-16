#!/usr/bin/env python3
"""Validate and format JSON from a UTF-8 file or standard input."""

import argparse
import json
import sys
from pathlib import Path

from _common import run, strict_json_constant, write_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="input file, or - for stdin (default)")
    parser.add_argument("-o", "--output", default="-", help="new output file, or - for stdout (default)")
    parser.add_argument("--indent", type=int, choices=range(0, 9), default=2)
    parser.add_argument("--sort-keys", action="store_true")
    args = parser.parse_args()
    text = sys.stdin.read() if args.input == "-" else Path(args.input).expanduser().read_text(encoding="utf-8-sig")
    value = json.loads(text, parse_constant=strict_json_constant)
    result = json.dumps(value, indent=args.indent, sort_keys=args.sort_keys, ensure_ascii=False, allow_nan=False)
    write_text(result + "\n", args.output)


if __name__ == "__main__":
    run(main)
