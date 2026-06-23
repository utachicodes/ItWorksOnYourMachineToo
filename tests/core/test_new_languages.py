# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from ItWorksOnYourMachineToo.core.planner.engine import ProjectPlanner
from ItWorksOnYourMachineToo.core.engine.engine import ExecutionEngine
from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter


def _make_adapter(indicators, extra_files=None):
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.normalize_path.side_effect = lambda x: x

    def mock_exists(p):
        if p == "/test":
            return True
        return any(p.endswith(ind) for ind in indicators)

    def mock_list_dir(p):
        return indicators

    mock_adapter.fs.exists.side_effect = mock_exists
    mock_adapter.fs.list_dir.side_effect = mock_list_dir
    mock_adapter.fs.read_text.return_value = ""
    mock_adapter.fs.is_dir.return_value = True
    return mock_adapter


def test_java_maven_detection():
    adapter = _make_adapter(["pom.xml"])
    adapter.fs.read_text.return_value = """
    <project>
        <dependencies>
            <dependency><artifactId>spring-boot</artifactId></dependency>
            <dependency><artifactId>junit</artifactId></dependency>
        </dependencies>
        <properties><java.version>17</java.version></properties>
    </project>
    """
    planner = ProjectPlanner(adapter)
    plan = planner.plan_project("/test")
    assert plan["project_type"] == "java"
    assert "spring-boot" in plan["requirements"]["packages"]
    assert plan["requirements"]["engines"]["java"] == "17"


def test_php_composer_detection():
    adapter = _make_adapter(["composer.json"])
    adapter.fs.read_text.return_value = '{"require": {"php": ">=8.1", "laravel/framework": "^10.0"}}'
    planner = ProjectPlanner(adapter)
    plan = planner.plan_project("/test")
    assert plan["project_type"] == "php"
    assert "laravel/framework" in plan["requirements"]["packages"]


def test_swift_package_detection():
    adapter = _make_adapter(["Package.swift"])
    adapter.fs.read_text.return_value = """
    // swift-tools-version: 5.9
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0")
    """
    planner = ProjectPlanner(adapter)
    plan = planner.plan_project("/test")
    assert plan["project_type"] == "swift"
    assert any("Alamofire" in p for p in plan["requirements"]["packages"])


def test_java_gradle_build_command():
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.fs.exists.side_effect = lambda p: "build.gradle" in p or p == "/test"
    mock_adapter.fs.is_dir.return_value = True
    mock_adapter.fs.list_dir.return_value = []
    mock_adapter.process.run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    mock_adapter.process.has_binary.return_value = True
    mock_adapter.sandbox.enter.return_value = None
    mock_adapter.sandbox.exit.return_value = None

    engine = ExecutionEngine(mock_adapter)
    plan = {"project_type": "java", "project_path": "/test", "requirements": {"runtime": "java"}}
    engine.prepare(plan)


def test_validator_detects_php_error():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    stderr = "Could not find composer.json in current directory"
    results = validator.validate_failure(stderr)
    assert results["is_fixable"] is True
    assert any(i["category"] == "missing_php_package" for i in results["detected_issues"])


def test_validator_detects_swift_error():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    stderr = "error: 'SomeModule' is not a member of package 'MyPackage'"
    results = validator.validate_failure(stderr)
    assert results["is_fixable"] is True
    assert any(i["category"] == "missing_swift_package" for i in results["detected_issues"])


def test_validator_detects_kotlin_error():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    stderr = "Unresolved reference: OkHttpClient"
    results = validator.validate_failure(stderr)
    assert results["is_fixable"] is True
    assert any(i["category"] == "missing_kotlin_dependency" for i in results["detected_issues"])


def test_validator_fix_php():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    fix = validator.propose_fix({"category": "missing_php_package"})
    assert fix == ["composer", "install"]


def test_validator_fix_swift():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    fix = validator.propose_fix({"category": "missing_swift_package"})
    assert fix == ["swift", "package", "resolve"]


def test_validator_fix_kotlin():
    mock_adapter = MagicMock(spec=OSAdapter)
    validator = EnvironmentValidator(mock_adapter)
    fix = validator.propose_fix({"category": "missing_kotlin_dependency"})
    assert fix == ["gradle", "build"]
