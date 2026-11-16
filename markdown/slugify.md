# Slugify

Convert text to lowercase words separated by single hyphens.
Requires Python 3.9+; no packages to install.

```bash
slugify 'Hello, World!'              # hello-world
slugify 'Café déjà vu' --ascii       # cafe-deja-vu
printf 'سلام دنیا' | slugify         # سلام-دنیا
```

Arguments are joined with spaces; with no arguments, text is read from stdin.
Unicode letters and numbers are preserved by default. Spaces, underscores, and
punctuation become hyphens, with leading/trailing hyphens removed. `--ascii`
removes accents where normalization permits and drops other non-ASCII characters;
it does not transliterate Persian or other scripts. Empty results return nonzero.
