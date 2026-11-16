# Clean Build

Find generated `build`, `dist`, `out`, and `coverage` directories recursively.
Requires Python 3.9+; no packages to install.

```bash
clean-build                         # Preview within the current project
clean-build /path/to/project
clean-build /path/to/project --apply
```

Defaults to a dry run; `--dry-run` is also accepted. Matching folders and their
contents are deleted with `--apply`, including matches in nested projects.
Selection is by folder name; review the preview if you use these names for source.
Symlinks, VCS metadata, `node_modules`, `.venv`, and `venv` are not traversed.
Root, home, home ancestors, and symlink roots are refused. Errors return nonzero.
