#!/usr/bin/env python3
"""Scaffold a small Python or Node.js project in a new directory."""

import argparse
import json
import re
from pathlib import Path

from _common import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="new project directory (parent must already exist)")
    parser.add_argument("--template", choices=("python", "node"), default="python")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(args.path).expanduser().absolute()
    name = root.name
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", name):
        raise ValueError("Project name must contain only letters, digits, hyphens, or underscores")
    if root.exists() or root.is_symlink():
        raise ValueError(f"Destination already exists: {root}")
    if not root.parent.is_dir():
        raise ValueError(f"Parent directory does not exist: {root.parent}")
    if args.template == "python":
        files = {
            "README.md": f"# {name}\n\nRun with `python3 main.py`.\n",
            ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\n.env\n",
            "main.py": 'def main():\n    print("Hello, world!")\n\n\nif __name__ == "__main__":\n    main()\n',
            "requirements.txt": "# Add project dependencies here.\n",
        }
    else:
        files = {
            "README.md": f"# {name}\n\nRun with `npm start`.\n",
            ".gitignore": "node_modules/\ndist/\n.env\n",
            "index.js": 'console.log("Hello, world!");\n',
            "package.json": json.dumps({"name": name.lower().replace("_", "-"), "version": "0.1.0",
                                        "private": True, "scripts": {"start": "node index.js"}}, indent=2) + "\n",
        }
    if not args.dry_run:
        root.mkdir()
    for filename, content in files.items():
        print(f"{'Would create' if args.dry_run else 'Create'} {root / filename}")
        if not args.dry_run:
            (root / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    run(main)
