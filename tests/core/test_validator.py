# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from lexworkseverywhere.core.validator.engine import EnvironmentValidator
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def test_validator_detects_missing_runtime():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    
    stderr = "sh: python: command not found"
    results = validator.validate_failure(stderr)
    
    assert results["is_fixable"] is True
    assert any(issue["category"] == "missing_runtime" for issue in results["detected_issues"])

def test_validator_detects_missing_package():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    
    stderr = "ModuleNotFoundError: No module named 'requests'"
    results = validator.validate_failure(stderr)
    
    assert results["is_fixable"] is True
    assert any(issue["category"] == "missing_python_package" for issue in results["detected_issues"])
