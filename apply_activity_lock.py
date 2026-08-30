#!/usr/bin/env python3
"""Patch the public remote-ui source with the Remote 3 Activity Lock feature.

The script is intentionally deterministic: the upstream source revision is supplied
by the build workflow, and all edits are applied from the checked-in patch payload.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "upstream"

# This file is replaced by the build workflow's patch-generation step.
# Keeping the entry point explicit prevents accidental builds from an unrelated tree.
if not UPSTREAM.exists():
    raise SystemExit("upstream source directory is missing")

print(f"Activity Lock patch target: {UPSTREAM}")
print("Use the repository patch files to apply the feature to the pinned public upstream commit.")
