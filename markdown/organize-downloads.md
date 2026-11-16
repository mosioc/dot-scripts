# Organize Downloads

Group top-level files into `images`, `documents`, `archives`, `audio`, `video`,
`installers`, and `other` folders by extension. Requires Python 3.9+;
no packages to install.

```bash
organize-downloads                  # Preview ~/Downloads
organize-downloads /path/to/inbox
organize-downloads /path/to/inbox --apply
```

Defaults to a dry run; `--dry-run` is also accepted. Directories, dotfiles,
symlinks, and files ending in `.part`, `.crdownload`, `.download`, or `.tmp` are
skipped. Existing filenames get numbered suffixes (`photo-1.jpg`); files are
never overwritten. Category symlinks are refused. Root, home, home ancestors,
and symlink roots are refused.

Moves use a hard link followed by unlinking the original, within the same
filesystem. Filesystems must support hard links. Errors return nonzero; earlier
successful moves are retained. Run after downloads have finished.
