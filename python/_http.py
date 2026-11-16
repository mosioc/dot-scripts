"""HTTP-only URL handling for the network helpers."""

from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class HTTPOnlyRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        if urlsplit(new_url).scheme not in {"http", "https"}:
            raise ValueError("Redirect must use HTTP(S)")
        return super().redirect_request(request, response, code, message, headers, new_url)


def collect_urls(positional, filename):
    urls = list(positional)
    if filename:
        urls.extend(line.strip() for line in Path(filename).expanduser().read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.lstrip().startswith("#"))
    if not urls:
        raise ValueError("Supply at least one URL or --file")
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(f"Expected an HTTP(S) URL: {url}")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("Credentials in URLs are not supported")
        # Validate ports before starting any requests.
        parsed.port
    return urls


def open_url(url, timeout):
    request = Request(url, headers={"User-Agent": "dot-scripts/1.0"})
    return build_opener(HTTPOnlyRedirectHandler()).open(request, timeout=timeout)
