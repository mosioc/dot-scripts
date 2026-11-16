# Download Assets

Stream HTTP(S) assets into a local directory. Requires Python 3.9+;
no packages to install.

```bash
download-assets https://example.com/logo.png
download-assets -f urls.txt -d ./public/assets --timeout 15
```

URL lists contain one URL per line; blanks and `#` comments are ignored. URLs
from arguments and the file are combined. Output defaults to `./assets`.
Filenames come from the decoded final path component of the original URL,
ignoring query strings; an empty component becomes `download-N`. Unsafe names
and duplicate filenames in a batch are refused. Existing files are never
overwritten. URLs containing credentials are refused.

Downloads stream into temporary files. A complete file is published using an
exclusive hard link; failed downloads leave no final or temporary file. The
output filesystem must support hard links. Failures are reported per URL and
remaining downloads continue; any failure returns nonzero. `--timeout` is the
socket timeout in seconds, default 30, rather than a total batch deadline.
