# Daily Routine

Preview or run commands in order from a JSON configuration.
Requires Python 3.9+; no packages to install.

Create `routine.json`:

```json
{
  "steps": [
    {"name": "Disk report", "command": ["disk-usage", "."]},
    {"name": "Tests", "command": ["npm", "test"], "cwd": "./my-app"}
  ]
}
```

```bash
daily-routine                       # Preview routine.json
daily-routine routine.json --apply
daily-routine routine.json --apply --keep-going --timeout 120
```

Each command is an array of arguments, executed directly without shell parsing;
pipes, variable expansion, and redirections are not interpreted. Commands must
be installed/on `PATH`, or use absolute executable paths. Relative `cwd` values
resolve against the config's folder; by default commands run in that folder.
The whole configuration is validated first. Only run configurations you trust.

`--apply` executes; `--dry-run` explicitly previews. The runner stops at the
first failure unless `--keep-going` is set, and returns nonzero if any step
fails. Each step has a default 300-second timeout. The timeout kills the direct
command process; it does not manage grandchildren started by that command.
