# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

import pytest

from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter
from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator


@pytest.fixture
def validator():
    return EnvironmentValidator(MagicMock(spec=OSAdapter))


def test_propose_fix_python_package_extracts_name(validator):
    fix = validator.propose_fix({
        "category": "missing_python_package",
        "context": "No module named 'requests'",
    })
    assert fix == ["pip", "install", "requests"]


def test_propose_fix_python_package_without_context_uses_placeholder(validator):
    fix = validator.propose_fix({"category": "missing_python_package", "context": ""})
    assert fix == ["pip", "install", "module_name"]


def test_propose_fix_node_and_ts_package(validator):
    assert validator.propose_fix({"category": "missing_node_package"}) == ["npm", "install"]
    assert validator.propose_fix({"category": "missing_ts_package"}) == ["npm", "install"]


def test_propose_fix_jdk(validator):
    assert validator.propose_fix({"category": "missing_jdk"}) == ["java", "-version"]


def test_propose_fix_dotnet(validator):
    assert validator.propose_fix({"category": "missing_dotnet"}) == ["dotnet", "--version"]


def test_propose_fix_unknown_category_returns_none(validator):
    assert validator.propose_fix({"category": "missing_runtime"}) is None


def test_validate_failure_detects_dotnet_sdk_missing(validator):
    results = validator.validate_failure("NETSDK1045: The current .NET SDK does not support")
    assert results["is_fixable"] is True
    assert any(i["category"] == "missing_dotnet" for i in results["detected_issues"])


def test_validate_failure_no_match_returns_not_fixable(validator):
    results = validator.validate_failure("all good, nothing to see here")
    assert results["is_fixable"] is False
    assert results["detected_issues"] == []
