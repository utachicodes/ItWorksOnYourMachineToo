# -*- coding: utf-8 -*-
"""Homebrew Brewfile export artifact generator."""

from pathlib import Path
from typing import Any, Dict


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `Brewfile` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    lines = []
    if runtime in ("nodejs", "bun"):
        lines.append('brew "node"')
    if runtime in ("python", "django"):
        lines.append('brew "python"')
    if runtime == "rust":
        lines.append('brew "rust"')
    if runtime == "go":
        lines.append('brew "go"')
    if runtime in ("php", "laravel"):
        lines.append('brew "php"')
        lines.append('brew "composer"')
    if runtime in ("java", "kotlin"):
        lines.append('brew "openjdk"')
    if runtime == "swift":
        lines.append('# Swift is included with Xcode on macOS')
    if runtime == "ruby":
        lines.append('brew "ruby"')
    if 'brew "git"' not in lines:
        lines.insert(0, 'brew "git"')
    if not lines:
        lines.append('# Add your packages here')

    out_path = Path(project_path, "Brewfile")
    out_path.write_text("\n".join(lines) + "\n")
    return str(out_path)
