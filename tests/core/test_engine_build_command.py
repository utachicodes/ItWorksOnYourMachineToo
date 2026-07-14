# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

import pytest

from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter
from ItWorksOnYourMachineToo.core.engine.engine import ExecutionEngine


def _make_adapter(existing_files=()):
    adapter = MagicMock(spec=OSAdapter)
    adapter.fs.exists.side_effect = lambda p: any(p.endswith(f) for f in existing_files)
    adapter.fs.list_dir.return_value = []
    return adapter


@pytest.mark.parametrize(
    "project_type,expected_prefix",
    [
        ("django", ["python3", "manage.py", "runserver"]),
        ("laravel", ["php", "artisan", "serve"]),
        ("rails", ["bundle", "exec", "rails", "server"]),
        ("flutter", ["flutter", "run"]),
        ("dotnet", ["dotnet", "run"]),
        ("go", ["go", "run", "."]),
        ("rust", ["cargo", "run"]),
        ("generic-make", ["make", "run"]),
        ("dart", ["dart", "run"]),
        ("swift", ["swift", "run"]),
        ("scala", ["sbt", "run"]),
    ],
)
def test_build_command_fixed_frameworks(project_type, expected_prefix):
    adapter = _make_adapter()
    engine = ExecutionEngine(adapter)
    plan = {"project_type": project_type, "project_path": "/proj"}

    cmd = engine._build_command(plan, [])

    assert cmd == expected_prefix


def test_build_command_python_prefers_main_py():
    adapter = _make_adapter(["main.py"])
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "python", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["python3", "main.py"]


def test_build_command_python_falls_back_to_first_py_file():
    adapter = _make_adapter()
    adapter.fs.list_dir.return_value = ["app.py", "README.md"]
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "python", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["python3", "app.py"]


def test_build_command_nodejs_prefers_server_js():
    adapter = _make_adapter(["server.js"])
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "nodejs", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["node", "server.js"]


def test_build_command_nodejs_falls_back_to_index_js():
    adapter = _make_adapter(["index.js"])
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "nodejs", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["node", "index.js"]


def test_build_command_java_uses_maven_when_pom_present():
    adapter = _make_adapter(["pom.xml"])
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "java", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["mvn", "exec:java"]


def test_build_command_java_uses_gradle_without_pom():
    adapter = _make_adapter()
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "java", "project_path": "/proj"}

    assert engine._build_command(plan, []) == ["gradle", "run"]


def test_build_command_unknown_type_returns_echo_notice():
    adapter = _make_adapter()
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "cobol", "project_path": "/proj"}

    cmd = engine._build_command(plan, [])

    assert cmd[0] == "echo"
    assert "cobol" in cmd[1]


def test_build_command_appends_extra_args():
    adapter = _make_adapter()
    engine = ExecutionEngine(adapter)
    plan = {"project_type": "go", "project_path": "/proj"}

    assert engine._build_command(plan, ["--flag"]) == ["go", "run", ".", "--flag"]
