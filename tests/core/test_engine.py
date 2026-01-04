# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from lexworkseverywhere.core.engine.engine import ExecutionEngine
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def test_engine_executes_via_adapter():
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.process.run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
    
    engine = ExecutionEngine(mock_adapter)
    plan = {"project_type": "python", "project_path": "/test"}
    
    result = engine.execute(plan)
    
    assert result["success"] is True
    assert result["stdout"] == "Success"
    mock_adapter.sandbox.enter.assert_called()
    mock_adapter.process.run.assert_called()
    mock_adapter.sandbox.exit.assert_called()
