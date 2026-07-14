# -*- coding: utf-8 -*-
"""Ansible playbook export artifact generator."""

from pathlib import Path
from typing import Any, Dict

import yaml


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `playbook.yml` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    tasks = [{"name": "Install Git", "apt": {"name": "git", "state": "present"}}]
    if runtime in ("nodejs", "bun"):
        tasks.append({"name": "Install Node.js", "apt": {"name": "nodejs", "state": "present"}})
    if runtime in ("python", "django"):
        tasks.append({"name": "Install Python3", "apt": {"name": "python3", "state": "present"}})
    if runtime == "go":
        tasks.append({"name": "Install Go", "apt": {"name": "golang", "state": "present"}})
    if runtime == "rust":
        tasks.append({
            "name": "Install Rust",
            "shell": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
            "creates": "{{ ansible_env.HOME }}/.cargo/bin/rustc",
        })
    if runtime in ("php", "laravel"):
        tasks.append({"name": "Install PHP and Composer", "apt": {"name": ["php", "composer"], "state": "present"}})
    if runtime in ("java", "kotlin"):
        tasks.append({"name": "Install OpenJDK 17", "apt": {"name": "openjdk-17-jdk", "state": "present"}})
    if runtime == "ruby":
        tasks.append({"name": "Install Ruby", "apt": {"name": "ruby-full", "state": "present"}})

    playbook = [{"hosts": "all", "become": True, "tasks": tasks}]
    out_path = Path(project_path, "playbook.yml")
    out_path.write_text(yaml.dump(playbook, default_flow_style=False))
    return str(out_path)
