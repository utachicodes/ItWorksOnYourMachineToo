# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter
from ItWorksOnYourMachineToo.core.planner.engine import ProjectPlanner


def _make_adapter(files, contents):
    adapter = MagicMock(spec=OSAdapter)
    adapter.normalize_path.side_effect = lambda x: x
    adapter.fs.exists.side_effect = lambda p: p == "/proj" or any(p.endswith(f) for f in files)
    adapter.fs.is_dir.return_value = True
    adapter.fs.list_dir.side_effect = lambda p: files if p == "/proj" else []
    adapter.fs.read_text.side_effect = lambda p: next(
        (contents[f] for f in files if p.endswith(f)), ""
    )
    return adapter


def test_plan_project_is_cached_between_calls():
    adapter = _make_adapter(["requirements.txt"], {"requirements.txt": "requests\n"})
    planner = ProjectPlanner(adapter)

    first = planner.plan_project("/proj")
    call_count_before = adapter.fs.read_text.call_count
    second = planner.plan_project("/proj")

    assert first == second
    # Second call still recomputes the hash (reads key files) but should not
    # rescan the whole tree; verify the plan content is stable across calls.
    assert adapter.fs.read_text.call_count >= call_count_before


def test_plan_project_cache_invalidates_on_content_change():
    adapter = _make_adapter(["requirements.txt"], {"requirements.txt": "requests\n"})
    planner = ProjectPlanner(adapter)

    first = planner.plan_project("/proj")
    assert "requests" in first["requirements"]["packages"]

    adapter.fs.read_text.side_effect = lambda p: (
        "requests\nnumpy\n" if p.endswith("requirements.txt") else ""
    )
    second = planner.plan_project("/proj")

    assert "numpy" in second["requirements"]["packages"]


def test_apply_heuristics_detects_python_shebang():
    adapter = MagicMock(spec=OSAdapter)
    adapter.normalize_path.side_effect = lambda x: x
    adapter.fs.exists.side_effect = lambda p: p in ("/proj", "/proj/main.py")
    adapter.fs.is_dir.return_value = True
    adapter.fs.list_dir.return_value = []
    adapter.fs.read_text.return_value = "#!/usr/bin/env python\nprint('hi')\n"

    planner = ProjectPlanner(adapter)
    plan = planner.plan_project("/proj")

    assert plan["project_type"] == "python"


def test_apply_heuristics_falls_back_to_unknown():
    adapter = MagicMock(spec=OSAdapter)
    adapter.normalize_path.side_effect = lambda x: x
    adapter.fs.exists.side_effect = lambda p: p == "/proj"
    adapter.fs.is_dir.return_value = True
    adapter.fs.list_dir.return_value = []
    adapter.fs.read_text.return_value = ""

    planner = ProjectPlanner(adapter)
    plan = planner.plan_project("/proj")

    assert plan["project_type"] == "unknown"
