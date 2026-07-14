# -*- coding: utf-8 -*-
"""Docker Compose export artifact generator."""

from pathlib import Path
from typing import Any, Dict

import yaml

_SERVICE_BY_RUNTIME = {
    "nodejs": {
        "image": "node:20-alpine",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "npm start",
    },
    "bun": {
        "image": "node:20-alpine",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "npm start",
    },
    "python": {
        "image": "python:3.12-slim",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "python manage.py runserver 0.0.0.0:8000",
        "ports": ["8000:8000"],
    },
    "django": {
        "image": "python:3.12-slim",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "python manage.py runserver 0.0.0.0:8000",
        "ports": ["8000:8000"],
    },
    "go": {
        "image": "golang:1.22-alpine",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "go run .",
    },
    "rust": {
        "image": "rust:1.77-slim",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "cargo run",
    },
    "php": {
        "image": "php:8.3-cli",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "php artisan serve --host=0.0.0.0",
        "ports": ["8000:8000"],
    },
    "laravel": {
        "image": "php:8.3-cli",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "php artisan serve --host=0.0.0.0",
        "ports": ["8000:8000"],
    },
    "java": {
        "image": "eclipse-temurin:17-jdk",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "java -jar app.jar",
    },
    "kotlin": {
        "image": "eclipse-temurin:17-jdk",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "java -jar app.jar",
    },
    "swift": {
        "image": "swift:5.9",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "swift run",
    },
    "ruby": {
        "image": "ruby:3.3-slim",
        "working_dir": "/app",
        "volumes": [".:/app"],
        "command": "ruby main.rb",
    },
}

_DEFAULT_SERVICE = {
    "image": "alpine:latest",
    "working_dir": "/app",
    "volumes": [".:/app"],
    "command": "echo 'Configure your service'",
}


def export(project_path: str, plan: Dict[str, Any]) -> str:
    """Write a `docker-compose.yml` covering the runtime detected for the project."""
    req = plan.get("requirements", {})
    runtime = (req.get("runtime") or plan.get("project_type") or "").lower()

    service = dict(_SERVICE_BY_RUNTIME.get(runtime, _DEFAULT_SERVICE))
    compose = {"services": {"app": service}}

    out_path = Path(project_path) / "docker-compose.yml"
    out_path.write_text(yaml.dump(compose, default_flow_style=False, sort_keys=False))
    return str(out_path)
