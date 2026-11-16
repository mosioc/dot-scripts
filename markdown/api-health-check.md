# API Health Check

Check HTTP(S) endpoints with concurrent GET requests. Requires Python 3.9+;
no packages to install.

```bash
api-health-check https://example.com/health https://example.com/api
api-health-check -f endpoints.txt --timeout 3 --workers 8
api-health-check https://example.com/health --expect 204 --json
```

URL lists contain one URL per line; blanks and `#` comments are ignored. URLs
from arguments and the file are combined. Redirects are followed. Any final
2xx status is healthy by default; `--expect` requires exactly one status
(including an expected 4xx/5xx). URLs containing credentials are refused.

Output includes the URL, final status or connection error, and elapsed time.
`--json` produces an array with `url`, `status`, `ok`, `elapsed_ms`, and `error`.
The default socket timeout is 5 seconds and the default worker count is 4.
Response bodies are not validated. Exit status is 0 only when every endpoint
matches; otherwise it is nonzero.
