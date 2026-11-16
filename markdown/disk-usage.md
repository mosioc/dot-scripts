# Disk Usage

Show the largest folders by logical file size. Requires Python 3.9+; no packages to install.

```bash
disk-usage                          # Current directory, largest 10 children
disk-usage ~/Downloads --limit 20
disk-usage . --depth 2 --limit 15
```

The total includes files at the root. Folder sizes include all their descendants;
`--depth` controls which folders are displayed. Parent and child totals overlap.
Sizes count file bytes, not allocated disk blocks; hard links count per path.
Symlinks are skipped. Unreadable paths produce warnings and exit status 1, with
partial totals still displayed. No files are changed.
