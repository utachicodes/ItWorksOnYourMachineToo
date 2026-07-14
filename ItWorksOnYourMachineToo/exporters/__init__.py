# -*- coding: utf-8 -*-
"""Export artifact generators, one module per target kind."""

from typing import Any, Callable, Dict

from . import ansible, apt, brewfile, devcontainer, docker_compose, nix, winget

EXPORTERS: Dict[str, Callable[[str, Dict[str, Any]], str]] = {
    "devcontainer": devcontainer.export,
    "brewfile": brewfile.export,
    "winget": winget.export,
    "apt": apt.export,
    "nix": nix.export,
    "ansible": ansible.export,
    "docker-compose": docker_compose.export,
}


def export(kind: str, project_path: str, plan: Dict[str, Any]) -> str:
    """Dispatch to the exporter registered for `kind`.

    Returns the path of the written artifact.
    """
    try:
        exporter = EXPORTERS[kind]
    except KeyError:
        raise ValueError(f"Unknown export kind: {kind}") from None
    return exporter(project_path, plan)
