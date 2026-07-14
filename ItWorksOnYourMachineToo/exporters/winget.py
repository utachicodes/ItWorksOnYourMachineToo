# -*- coding: utf-8 -*-
"""Windows winget package list export artifact generator."""

from pathlib import Path
from typing import Any, Dict


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `winget.txt` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    lines = []
    if runtime in ("nodejs", "bun"):
        lines.append("winget install OpenJS.NodeJS")
    if runtime in ("python", "django"):
        lines.append("winget install Python.Python.3")
    if runtime == "rust":
        lines.append("winget install Rustlang.Rustup")
    if runtime == "go":
        lines.append("winget install Google.Go")
    if runtime in ("php", "laravel"):
        lines.append("winget install PHP.PHP")
        lines.append("winget install Microsoft.Composer")
    if runtime in ("java", "kotlin"):
        lines.append("winget install Microsoft.OpenJDK.17")
    if runtime == "ruby":
        lines.append("winget install RubyInstallerTeam.Ruby")
    if "winget install Git.Git" not in lines:
        lines.insert(0, "winget install Git.Git")
    if not lines:
        lines.append("# Add your installers here")

    out_path = Path(project_path, "winget.txt")
    out_path.write_text("\n".join(lines) + "\n")
    return str(out_path)
