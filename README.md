# Dot Scripts

Store scripts repository.

## System & OS scripts

* `system-update` -> update OS & packages (todo)
* [`disk-usage`](./markdown/disk-usage.md) -> show largest folders
* [`clean-tmp`](./markdown/clean-tmp.md) -> clear old temp/cache files
* `backup-home` -> backup important dirs (todo)
* [`free-memory`](./markdown/free-memory.md) -> free RAM / show memory

## Workflow scripts

* [`clean-build`](./markdown/clean-build.md) -> delete build/dist folders
* [`reset-project`](./markdown/reset-project.md) -> remove node\_modules, caches
* `run-tests-all` -> run tests across projects (todo)
* `format-all` -> run formatter everywhere (todo)
* `git-wip` -> save WIP commit (todo)

## CLI utility scripts

* `mkcd` -> create + cd into directory (todo)
* `extract` -> extract any archive (todo)
* [`serve-here`](./markdown/serve-here.md) -> local static server
* [`json-pretty`](./markdown/json-pretty.md) -> format JSON
* [`slugify`](./markdown/slugify.md) -> convert text to URL slug

## Automation & batch scripts

* `setup-dev-env` -> install tools, configs (todo)
* [`new-project`](./markdown/new-project.md) -> scaffold project
* `deploy-preview` -> build + upload (todo)
* `sync-dotfiles` -> sync configs (todo)
* [`daily-routine`](./markdown/daily-routine.md) -> run many scripts

## Data & file manipulation scripts

* [`rename-files`](./markdown/rename-files.md) -> batch rename
* [`md-headings`](./bash/md-headings.sh) -> extract headings from markdown files
* `resize-images` -> image processing (todo)
* [`csv-to-json`](./markdown/csv-to-json.md) -> convert CSV rows to JSON
* `json-to-yaml` (todo)
* [`organize-downloads`](./markdown/organize-downloads.md) -> group files by category

## Networking & API helpers scripts

* [`ping-hosts`](./markdown/ping-hosts.md) -> check availability
* [`download-assets`](./markdown/download-assets.md) -> download HTTP(S) assets
* [`api-health-check`](./markdown/api-health-check.md) -> check HTTP endpoint status
* `fetch-weather` (todo)
* `github-backup` (todo)

## Scraping

* [`web-to-markdown`](./markdown/web-to-markdown.md) -> fetch webpages and convert to markdown

## Folder Tree

```txt
dot-scripts/
├── bash/ -> `.sh`
├── node/ -> `.js`
├── python/ -> `.py`
├── bin/ -> exec
├── markdown/ -> documentation
├── README.md
```

## Usage

The twelve commands added above require Python 3.9+ and use only its standard
library. Each includes `--help` and an executable launcher in `bin/`. Keep the
`python/` folder next to `bin/`, including its shared helper modules.

`clean-tmp`, `clean-build`, `reset-project`, `organize-downloads`, and
`daily-routine` preview their actions by default; pass `--apply` to execute.

   1. Scripts (in bash, node or python folders)
      Something like this:

      ```txt
      node/clean-build.js
      ```

   2. Launcher (in bin)
      Probably:

      ```txt
      bin/clean-build
      ```

      bin/clean-build:

      ```sh
      #!/bin/sh
      node ../node/clean-build.js "$@"
      ```

      make it executable:

      ```bash
      chmod +x bin/clean-build
      ```

   3. Using bin:
      Add this to `.bashrc` or `.zshrc`:

      ```bash
      export PATH="$HOME/dot-scripts/bin:$PATH"
      ```

      You can now run:

      ```bash
      clean-build
      ```

      No `node`, no path, no extension.\
      That’s the whole philosophy of dot-scripts.

## Verification

Run the integration tests for the twelve Python commands from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Tests use temporary directories and a local HTTP server. They do not contact
external services or modify your projects or Downloads folder.
