# -*- coding: utf-8 -*-
"""Nix shell.nix export artifact generator."""

from pathlib import Path
from typing import Any, Dict


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `shell.nix` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    pkgs = []
    if runtime in ("nodejs", "bun"):
        pkgs.append("nodejs")
    if runtime in ("python", "django"):
        pkgs.append("python3")
    if runtime == "rust":
        pkgs.append("rustc")
        pkgs.append("cargo")
    if runtime == "go":
        pkgs.append("go")
    if runtime in ("php", "laravel"):
        pkgs.append("php")
        pkgs.append("composer")
    if runtime in ("java", "kotlin"):
        pkgs.append("jdk17")
    if runtime == "ruby":
        pkgs.append("ruby")
    if "git" not in pkgs:
        pkgs.insert(0, "git")
    if not pkgs:
        pkgs.append("# add packages")

    build_inputs = " ".join(f"pkgs.{p}" if p and p[0] != "#" else "" for p in pkgs)
    shell_nix = f"""{{ pkgs ? import <nixpkgs> {{ }} }}:
pkgs.mkShell {{
  buildInputs = [ {build_inputs} ];
}}
"""
    out_path = Path(project_path, "shell.nix")
    out_path.write_text(shell_nix)
    return str(out_path)
