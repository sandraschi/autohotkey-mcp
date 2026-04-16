"""MCP resources: prompt catalog exposed under ``ahk://prompts/...`` for agents."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from autohotkey_mcp import prompt_catalog


def register_prompt_resources(mcp: FastMCP) -> None:
    """Register static + template resources for the preset AHK generation prompt library."""

    @mcp.resource(
        "ahk://prompts/catalog",
        mime_type="application/json",
        description="Full preset prompt library (id, title, category, tags, prompt).",
    )
    def resource_prompt_catalog() -> str:
        return json.dumps(prompt_catalog.list_prompts_for_api(), indent=2)

    @mcp.resource(
        "ahk://prompts/categories",
        mime_type="application/json",
        description="Sorted list of prompt categories.",
    )
    def resource_prompt_categories() -> str:
        return json.dumps(prompt_catalog.categories(), indent=2)

    @mcp.resource(
        "ahk://prompts/{prompt_id}",
        mime_type="application/json",
        description="Single preset prompt by id (e.g. hk_toggle_mute). JSON error if unknown.",
    )
    def resource_prompt_by_id(prompt_id: str) -> str:
        p = prompt_catalog.get_prompt_by_id(prompt_id)
        if not p:
            return json.dumps(
                {
                    "error": "unknown_prompt_id",
                    "prompt_id": prompt_id,
                    "hint": "Read ahk://prompts/catalog for valid ids.",
                },
                indent=2,
            )
        return json.dumps(
            {
                "id": p["id"],
                "title": p.get("title"),
                "category": p.get("category"),
                "tags": p.get("tags") or [],
                "prompt": p.get("prompt"),
            },
            indent=2,
        )
