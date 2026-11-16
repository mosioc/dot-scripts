#!/usr/bin/env python3
"""Check HTTP endpoints concurrently; fail if any status is unexpected."""

import argparse
import http.client
import json
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError

from _common import positive_float, positive_int, run
from _http import collect_urls, open_url


def check(url, timeout, expected):
    start = time.monotonic()
    status = None
    error = None
    try:
        with open_url(url, timeout) as response:
            status = response.status
    except HTTPError as failure:
        status = failure.code
        failure.close()
    except (OSError, ValueError, http.client.HTTPException) as failure:
        error = str(failure)
    ok = status == expected if expected is not None else status is not None and 200 <= status < 300
    return {"url": url, "status": status, "ok": ok,
            "elapsed_ms": round((time.monotonic() - start) * 1000, 1), "error": error}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("-f", "--file", help="URL list, one per line; # comments allowed")
    parser.add_argument("--timeout", type=positive_float, default=5, help="socket timeout in seconds (default: 5)")
    parser.add_argument("--workers", type=positive_int, default=4)
    parser.add_argument("--expect", type=int, choices=range(100, 600), metavar="STATUS", help="require this status instead of any 2xx")
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    args = parser.parse_args()
    urls = collect_urls(args.urls, args.file)
    with ThreadPoolExecutor(max_workers=min(args.workers, len(urls))) as pool:
        results = list(pool.map(lambda url: check(url, args.timeout, args.expect), urls))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            detail = result["error"] or f"HTTP {result['status']}"
            print(f"{'OK' if result['ok'] else 'FAIL'} {result['url']} {detail} ({result['elapsed_ms']} ms)")
    return 0 if all(result["ok"] for result in results) else 1


if __name__ == "__main__":
    run(main)
