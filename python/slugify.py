#!/usr/bin/env python3
"""Convert text to a lowercase URL slug, preserving Unicode letters by default."""

import argparse
import re
import sys
import unicodedata

from _common import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="text to convert (default: stdin)")
    parser.add_argument("--ascii", action="store_true", help="strip characters without an ASCII representation")
    args = parser.parse_args()
    text = " ".join(args.text) if args.text else sys.stdin.read()
    if args.ascii:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    else:
        text = unicodedata.normalize("NFKC", text)
    slug = re.sub(r"[\W_]+", "-", text.lower(), flags=re.UNICODE).strip("-")
    if not slug:
        raise ValueError("Text contains no usable letters or numbers")
    print(slug)


if __name__ == "__main__":
    run(main)
