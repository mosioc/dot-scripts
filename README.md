# Dot Scripts

Store scripts repository.

## System & OS scripts

* `system-update` -> update OS & packages (todo)
* `disk-usage` -> show largest folders (todo)
* `clean-tmp` -> clear temp/cache files (todo)
* `backup-home` -> backup important dirs (todo)
* `free-memory` -> free RAM / show memory (todo)

## Workflow scripts

* `clean-build` -> delete build/dist folders (todo)
* `reset-project` -> remove node\_modules, caches (todo)
* `run-tests-all` -> run tests across projects (todo)
* `format-all` -> run formatter everywhere (todo)
* `git-wip` -> save WIP commit (todo)

## CLI utility scripts

* `mkcd` -> create + cd into directory (todo)
* `extract` -> extract any archive (todo)
* `serve-here` -> local static server (todo)
* `json-pretty` -> format JSON (todo)
* `slugify` -> convert text to URL slug (todo)

## Automation & batch scripts

* `setup-dev-env` -> install tools, configs (todo)
* `new-project` -> scaffold project (todo)
* `deploy-preview` -> build + upload (todo)
* `sync-dotfiles` -> sync configs (todo)
* `daily-routine` -> run many scripts (todo)

## Data & file manipulation scripts

* `rename-files` -> batch rename (todo)
* `resize-images` -> image processing (todo)
* `csv-to-json` (todo)
* `json-to-yaml` (todo)
* `organize-downloads` (todo)

## Networking & API helpers scripts

* [`ping-hosts`](./node/ping-hosts.js) -> check availability 
* `download-assets` (todo)
* `api-health-check` (todo)
* `fetch-weather` (todo)
* `github-backup` (todo)

## Folder Tree

```txt
dot-scripts/
├── bash/ -> `.sh`
├── node/ -> `.js`
├── python/ -> `.py`
├── bin/
├── README.md
```

## Usage

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
