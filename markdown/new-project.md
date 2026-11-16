# New Project

Create a minimal Python or Node.js project. Requires Python 3.9+ to scaffold;
the Node template requires Node.js/npm to run.

```bash
new-project my-tool                  # Python template
new-project my-app --template node
new-project my-app --template node --dry-run
```

Creates a README, `.gitignore`, and runnable hello-world entry point. Python
projects include `requirements.txt`; Node projects include `package.json` with
an `npm start` script. No installs, Git initialization, or network calls run.
Existing destinations are refused, even if empty. The parent directory must
exist. Names use letters, digits, hyphens, and underscores and start with a
letter or digit. Errors return nonzero.
