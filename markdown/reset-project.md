# Reset Project

Remove `node_modules`, `.cache`, `.parcel-cache`, `.next`, `.nuxt`, and `.turbo`
directories recursively, leaving source and lockfiles in place.
Requires Python 3.9+; no packages to install.

```bash
reset-project                       # Preview within the current project
reset-project /path/to/project --apply
```

Defaults to a dry run; `--dry-run` is also accepted. Review the preview before
applying: matching folder names identify disposable dependencies and caches.
Symlinks, VCS metadata, `.venv`, and `venv` are not traversed. Once a matching
folder is selected, it is removed as a whole. Root, home, home ancestors, and
symlink roots are refused. This does not reinstall dependencies. Errors return nonzero.
