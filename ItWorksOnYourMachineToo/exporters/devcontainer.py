# -*- coding: utf-8 -*-
"""Dev Container export artifact generator."""

import json
from pathlib import Path
from typing import Any, Dict

_FEATURE_BY_TYPE = {
    "nodejs": {"ghcr.io/devcontainers/features/node:1": {"version": "lts", "nodeGypDependencies": True}},
    "python": {"ghcr.io/devcontainers/features/python:1": {"version": "3"}},
    "django": {"ghcr.io/devcontainers/features/python:1": {"version": "3"}},
    "go": {"ghcr.io/devcontainers/features/go:1": {"version": "latest"}},
    "rust": {"ghcr.io/devcontainers/features/rust:1": {}},
    "java": {"ghcr.io/devcontainers/features/java:1": {"version": "17"}},
    "kotlin": {"ghcr.io/devcontainers/features/java:1": {"version": "17"}},
    "php": {"ghcr.io/devcontainers/features/php:1": {"version": "8.3"}},
    "swift": {"ghcr.io/devcontainers/features/swift:1": {}},
}


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `.devcontainer/devcontainer.json` for the detected project type.

    Returns the path of the written file.
    """
    dc_dir = Path(project_path) / ".devcontainer"
    dc_dir.mkdir(parents=True, exist_ok=True)

    project_type = plan.get("project_type")
    features = dict(_FEATURE_BY_TYPE.get(project_type, {}))
    if not features:
        features = {"ghcr.io/devcontainers/features/common-utils:2": {}}

    devcontainer = {
        "name": "ItWorksOnYourMachineToo Dev Container",
        "image": "mcr.microsoft.com/devcontainers/base:latest",
        "features": features,
        "customizations": {
            "vscode": {
                "extensions": [
                    "ms-python.python",
                    "esbenp.prettier-vscode",
                    "ms-azuretools.vscode-docker",
                    "rust-lang.rust-analyzer",
                    "golang.go",
                ]
            }
        },
        "postCreateCommand": "echo Ready",
    }
    out_path = dc_dir / "devcontainer.json"
    out_path.write_text(json.dumps(devcontainer, indent=2))
    return str(out_path)
