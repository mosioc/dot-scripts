# JSON Pretty

Validate and pretty-print UTF-8 JSON. Requires Python 3.9+; no packages to install.

```bash
printf '{"b":2,"a":1}' | json-pretty --sort-keys
json-pretty data.json --indent 4
json-pretty data.json -o formatted.json
```

Input defaults to stdin and output to stdout (`-` selects either explicitly).
`--indent` accepts 0–8, default 2. Unicode text is preserved. Invalid JSON,
including `NaN` and `Infinity`, returns nonzero. Output files must be new:
existing files, including the input file, are never overwritten. Input is loaded
in memory, and ordinary JSON parser number semantics apply.
