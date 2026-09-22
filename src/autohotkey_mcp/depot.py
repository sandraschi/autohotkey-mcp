"""Resolve the scriptlet depot directory without a hardcoded absolute path.

A fresh `git clone` of this repo on any machine, drive, or username needs the depot to
resolve correctly. AUTOHOTKEY_SCRIPT_DEPOT always wins when set; otherwise we look for a
sibling "autohotkey-tools" checkout next to this repo, which is the fleet's own layout
(both repos cloned under the same parent directory) and also the natural result of
following the autohotkey-tools README's own clone instructions next to this one.
"""

from __future__ import annotations

import os
from pathlib import Path


def resolve_depot_path() -> Path:
    env = os.getenv("AUTOHOTKEY_SCRIPT_DEPOT")
    if env:
        return Path(env)

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() and parent.name == "autohotkey-mcp":
            sibling = parent.parent / "autohotkey-tools"
            if sibling.exists():
                return sibling
            break

    return Path.home() / "autohotkey-tools"
