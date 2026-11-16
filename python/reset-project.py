#!/usr/bin/env python3
"""Remove node_modules and common tool caches; keep source files and lockfiles."""

from _common import run
from _project_cleanup import clean


if __name__ == "__main__":
    run(lambda: clean(__doc__, {"node_modules", ".cache", ".parcel-cache", ".next", ".nuxt", ".turbo"}))
