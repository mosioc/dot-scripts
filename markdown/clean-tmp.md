# Clean Tmp

Remove old regular files from a temp/cache directory you explicitly select.
Requires Python 3.9+; no packages to install.

```bash
clean-tmp ./scratch                  # Preview files last modified over 7 days ago
clean-tmp ./scratch --days 30
clean-tmp ./scratch --days 30 --apply
```

Defaults to a dry run; `--dry-run` is also accepted. Age uses modification time;
`--days 0` selects all existing regular files. Directories, symlinks, and `.git`
subtrees are kept. Root, home, home ancestors, and symlink roots are refused.
Choose a directory containing disposable files; this does not detect files that
other processes are currently using. No privilege escalation is attempted.
Errors return a nonzero exit status.
