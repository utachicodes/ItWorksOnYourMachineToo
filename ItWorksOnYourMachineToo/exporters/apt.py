# -*- coding: utf-8 -*-
"""Debian/Ubuntu apt package list export artifact generator."""

from pathlib import Path
from typing import Any, Dict


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write an `apt.txt` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    lines = []
    if runtime in ("nodejs", "bun"):
        lines.append("sudo apt install -y nodejs npm")
    if runtime in ("python", "django"):
        lines.append("sudo apt install -y python3 python3-pip")
    if runtime == "rust":
        lines.append("# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
    if runtime == "go":
        lines.append("sudo apt install -y golang")
    if runtime in ("php", "laravel"):
        lines.append("sudo apt install -y php composer")
    if runtime in ("java", "kotlin"):
        lines.append("sudo apt install -y openjdk-17-jdk")
    if runtime == "ruby":
        lines.append("sudo apt install -y ruby-full")
    if "sudo apt install -y git" not in lines:
        lines.insert(0, "sudo apt install -y git")
    if not lines:
        lines.append("# Add your apt packages here")

    out_path = Path(project_path, "apt.txt")
    out_path.write_text("\n".join(lines) + "\n")
    return str(out_path)
