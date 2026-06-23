# -*- coding: utf-8 -*-
import toml
from pathlib import Path
from typing import Dict, Any


_DEFAULT_CONFIG = {
    "skip_detection": [],
    "custom_run_commands": {},
    "export_defaults": {"kind": "devcontainer"},
    "verbose": False,
}


def load_config(project_path: str) -> Dict[str, Any]:
    config_path = Path(project_path) / ".itworks.toml"
    if not config_path.exists():
        return dict(_DEFAULT_CONFIG)
    try:
        data = toml.load(config_path)
        merged = dict(_DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except Exception:
        return dict(_DEFAULT_CONFIG)


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    return config.get(key, default)
