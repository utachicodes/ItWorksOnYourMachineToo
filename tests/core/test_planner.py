# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from lexworkseverywhere.core.planner.engine import ProjectPlanner
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def test_planner_logic_is_isolated():
    # Setup mock adapter
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.fs.exists.side_effect = lambda p: "requirements.txt" in p or p == "/dummy/path"
    mock_adapter.fs.read_text.return_value = "numpy\npandas"
    mock_adapter.normalize_path.side_effect = lambda x: x
    
    planner = ProjectPlanner(mock_adapter)
    plan = planner.plan_project("/dummy/path")
    
    assert plan["project_type"] == "python"
    assert "numpy" in plan["requirements"]["packages"]
    assert "pandas" in plan["requirements"]["packages"]
    mock_adapter.fs.exists.assert_called()
