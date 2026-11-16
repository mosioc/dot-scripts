# CSV to JSON

Convert CSV with a header row to a JSON array of objects.
Requires Python 3.9+; no packages to install.

```bash
csv-to-json people.csv
csv-to-json people.csv -o people.json
csv-to-json data.tsv --delimiter $'\t'
printf 'name,age\nMehdi,30\n' | csv-to-json
```

Input defaults to stdin and output to stdout (`-` selects either explicitly).
Input is UTF-8; files may include a BOM. Quoted delimiters and multiline fields
are supported. Values stay strings, including numbers and empty cells. Empty or
duplicate headers, malformed quoting, and rows with extra/missing columns fail
with a nonzero exit status. Output files must be new and are only created after
successful conversion. The JSON result is assembled in memory.
