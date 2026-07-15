"""FastMCP 3.2 providers for autohotkey-mcp.

Registers a SkillsDirectoryProvider pointing at the .cursor/skills directory
so agents using CodeMode can discover AHK v2 authoring skills without knowing
the exact tool names upfront.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers import SkillsDirectoryProvider

logger = logging.getLogger(__name__)

# Skills dir: .cursor/skills in the autohotkey-mcp repo root
_REPO_ROOT = Path(__file__).parent.parent.parent  # src/autohotkey_mcp/providers.py -> repo root
_DEFAULT_SKILLS_DIR = _REPO_ROOT / ".cursor" / "skills"


def register_providers(mcp: FastMCP) -> None:
    """Register FastMCP 3.2 providers: SkillsDirectoryProvider for AHK skills."""
    skills_dir = Path(os.getenv("AUTOHOTKEY_SKILLS_DIR", str(_DEFAULT_SKILLS_DIR)))

    if not skills_dir.exists():
        logger.info(
            "Skills directory not found at %s — skipping SkillsDirectoryProvider. "
            "Set AUTOHOTKEY_SKILLS_DIR or create .cursor/skills/ in the repo root.",
            skills_dir,
        )
        return

    try:
        provider = SkillsDirectoryProvider(roots=skills_dir, reload=False)
        mcp.add_provider(provider)
        logger.info("Registered SkillsDirectoryProvider from %s", skills_dir)
    except Exception as e:
        logger.warning("Failed to register SkillsDirectoryProvider: %s", e)
