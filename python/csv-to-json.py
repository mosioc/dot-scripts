#!/usr/bin/env python3
"""Convert a CSV header and rows to a JSON array of objects with string values."""

import argparse
import csv
import json
import sys
from pathlib import Path

from _common import run, write_text


def convert(stream, delimiter):
    reader = csv.DictReader(stream, delimiter=delimiter, strict=True)
    headers = reader.fieldnames
    if not headers or any(not header.strip() for header in headers):
        raise ValueError("CSV requires nonempty column headers")
    if len(set(headers)) != len(headers):
        raise ValueError("CSV column headers must be unique")
    rows = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV row near line {reader.line_num} has the wrong number of columns")
        rows.append(row)
    return json.dumps(rows, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="CSV file, or - for stdin (default)")
    parser.add_argument("-o", "--output", default="-", help="new output file, or - for stdout (default)")
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()
    if len(args.delimiter) != 1 or args.delimiter in "\r\n\0":
        raise ValueError("Delimiter must be a single character other than newline or NUL")
    try:
        if args.input == "-":
            result = convert(sys.stdin, args.delimiter)
        else:
            with Path(args.input).expanduser().open(encoding="utf-8-sig", newline="") as stream:
                result = convert(stream, args.delimiter)
    except csv.Error as error:
        raise ValueError(f"Invalid CSV: {error}") from error
    write_text(result, args.output)


if __name__ == "__main__":
    run(main)
