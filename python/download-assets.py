#!/usr/bin/env python3
"""Download HTTP(S) URLs to files without overwriting existing assets."""

import argparse
import http.client
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from _common import positive_float, run
from _http import collect_urls, open_url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("-f", "--file", help="URL list, one per line; # comments allowed")
    parser.add_argument("-d", "--dir", default="assets", help="output directory (default: assets)")
    parser.add_argument("--timeout", type=positive_float, default=30, help="socket timeout in seconds (default: 30)")
    args = parser.parse_args()
    urls = collect_urls(args.urls, args.file)
    output = Path(args.dir).expanduser().resolve()
    plan = []
    names = set()
    for index, url in enumerate(urls, 1):
        name = unquote(urlsplit(url).path.rsplit("/", 1)[-1]) or f"download-{index}"
        if name in {".", ".."} or any(char in name for char in "/\\") or any(ord(char) < 32 for char in name):
            raise ValueError(f"URL has an unsafe filename: {url}")
        # casefold also prevents collisions on case-insensitive filesystems.
        if name.casefold() in names:
            raise ValueError(f"Multiple URLs have the same filename: {name}")
        names.add(name.casefold())
        plan.append((url, output / name))
    output.mkdir(parents=True, exist_ok=True)
    failed = False
    for url, destination in plan:
        temporary = None
        try:
            if destination.exists() or destination.is_symlink():
                raise FileExistsError(f"Destination exists: {destination}")
            with open_url(url, args.timeout) as response:
                expected = response.headers.get("Content-Length")
                size = 0
                with tempfile.NamedTemporaryFile(dir=output, prefix=".download-", delete=False) as stream:
                    temporary = Path(stream.name)
                    while True:
                        chunk = response.read(64 * 1024)
                        if not chunk:
                            break
                        stream.write(chunk)
                        size += len(chunk)
                if expected is not None and size != int(expected):
                    raise ValueError(f"Incomplete download: expected {expected} bytes, received {size}")
            os.link(temporary, destination)
            print(f"Downloaded {destination.name} ({size} bytes)")
        except (OSError, ValueError, http.client.HTTPException) as error:
            print(f"Failed {url}: {error}", file=sys.stderr)
            failed = True
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return 1 if failed else 0


if __name__ == "__main__":
    run(main)
