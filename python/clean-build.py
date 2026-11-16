#!/usr/bin/env python3
"""Delete generated build, dist, out, and coverage folders within a project."""

from _common import run
from _project_cleanup import clean


if __name__ == "__main__":
    run(lambda: clean(__doc__, {"build", "dist", "out", "coverage"}))
