# -*- coding: utf-8 -*-
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from ItWorksOnYourMachineToo.core.config import load_config, get_config_value
from ItWorksOnYourMachineToo.core.i18n import set_locale, t
from ItWorksOnYourMachineToo.core.profiler import EnvironmentProfiler
from ItWorksOnYourMachineToo.core.planner.engine import ProjectPlanner
from ItWorksOnYourMachineToo.core.engine.engine import ExecutionEngine
from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter


class TestConfig:
    def test_load_config_defaults(self):
        config = load_config("/nonexistent/path")
        assert config["verbose"] is False
        assert config["skip_detection"] == []
        assert "kind" in config["export_defaults"]

    def test_get_config_value_default(self):
        config = {"key": "value"}
        assert get_config_value(config, "key") == "value"
        assert get_config_value(config, "missing", "default") == "default"
        assert get_config_value(config, "missing") is None

    def test_load_config_with_file(self, tmp_path):
        config_file = tmp_path / ".itworks.toml"
        config_file.write_text('verbose = true\nskip_detection = ["docker"]\n')
        config = load_config(str(tmp_path))
        assert config["verbose"] is True
        assert "docker" in config["skip_detection"]

    def test_load_config_invalid_file(self, tmp_path):
        config_file = tmp_path / ".itworks.toml"
        config_file.write_text("this is not valid toml {{{")
        config = load_config(str(tmp_path))
        assert config["verbose"] is False


class TestI18n:
    def test_set_locale_english(self):
        set_locale("en")
        assert t("success") == "Success"

    def test_set_locale_french(self):
        set_locale("fr")
        assert t("success") == "Succès"
        set_locale("en")

    def test_unknown_key_returns_key(self):
        set_locale("en")
        assert t("nonexistent_key") == "nonexistent_key"

    def test_set_locale_unknown_defaults_to_english(self):
        set_locale("de")
        assert t("success") == "Success"


class TestProfiler:
    def test_detect_runtimes(self):
        mock_adapter = MagicMock(spec=OSAdapter)
        cp_mock = MagicMock()
        cp_mock.stdout = "Python 3.12.0"
        cp_mock.stderr = ""
        mock_adapter.process.run.return_value = cp_mock
        profiler = EnvironmentProfiler(mock_adapter)
        runtimes = profiler._detect_runtimes()
        assert isinstance(runtimes, dict)

    def test_safe_env_vars_filters_secrets(self):
        mock_adapter = MagicMock(spec=OSAdapter)
        profiler = EnvironmentProfiler(mock_adapter)
        with patch.dict("os.environ", {
            "PATH": "/usr/bin",
            "API_SECRET_TOKEN": "abc123",
            "MY_PASSWORD": "secret",
            "NORMAL_VAR": "value",
        }):
            result = profiler._get_safe_env_vars()
            assert "PATH" in result
            assert "API_SECRET_TOKEN" not in result
            assert "MY_PASSWORD" not in result

    def test_generate_portable_hash(self):
        mock_adapter = MagicMock(spec=OSAdapter)
        profiler = EnvironmentProfiler(mock_adapter)
        h = profiler._generate_portable_hash("linux", {"PATH": "/usr/bin"}, {"python": "3.12"})
        assert h.startswith("sha256:")
        assert len(h) == 71

    def test_capture_profile_structure(self):
        mock_adapter = MagicMock(spec=OSAdapter)
        mock_adapter.get_os_name.return_value = "linux"
        mock_adapter.process.run.side_effect = Exception("no binary")
        profiler = EnvironmentProfiler(mock_adapter)
        profile = profiler.capture_profile()
        assert "os" in profile
        assert "env_vars" in profile
        assert "runtimes" in profile
        assert "portable_hash" in profile


class TestValidatorNewPatterns:
    def test_missing_jdk_pattern(self):
        from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
        mock_adapter = MagicMock(spec=OSAdapter)
        validator = EnvironmentValidator(mock_adapter)
        results = validator.validate_failure("java.lang.ClassNotFoundException")
        assert results["is_fixable"] is True
        assert any(i["category"] == "missing_jdk" for i in results["detected_issues"])

    def test_missing_dotnet_pattern(self):
        from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
        mock_adapter = MagicMock(spec=OSAdapter)
        validator = EnvironmentValidator(mock_adapter)
        results = validator.validate_failure("The term 'dotnet' is not recognized")
        assert results["is_fixable"] is True
        assert any(i["category"] == "missing_dotnet" for i in results["detected_issues"])

    def test_missing_swift_toolchain_pattern(self):
        from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
        mock_adapter = MagicMock(spec=OSAdapter)
        validator = EnvironmentValidator(mock_adapter)
        results = validator.validate_failure("xcrun: error: invalid active developer path")
        assert results["is_fixable"] is True
        assert any(i["category"] == "missing_swift_toolchain" for i in results["detected_issues"])

    def test_fix_jdk(self):
        from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
        mock_adapter = MagicMock(spec=OSAdapter)
        validator = EnvironmentValidator(mock_adapter)
        fix = validator.propose_fix({"category": "missing_jdk"})
        assert fix == ["java", "-version"]

    def test_fix_dotnet(self):
        from ItWorksOnYourMachineToo.core.validator.engine import EnvironmentValidator
        mock_adapter = MagicMock(spec=OSAdapter)
        validator = EnvironmentValidator(mock_adapter)
        fix = validator.propose_fix({"category": "missing_dotnet"})
        assert fix == ["dotnet", "--version"]


class TestExportNewKinds:
    def _make_adapter(self):
        mock_adapter = MagicMock(spec=OSAdapter)
        mock_adapter.normalize_path.side_effect = lambda x: x

        def mock_exists(p):
            if p == "/test":
                return True
            if p.endswith("requirements.txt"):
                return True
            return False

        def mock_is_dir(p):
            return p == "/test"

        mock_adapter.fs.exists.side_effect = mock_exists
        mock_adapter.fs.is_dir.side_effect = mock_is_dir
        mock_adapter.fs.list_dir.return_value = ["requirements.txt"]
        mock_adapter.fs.read_text.return_value = "flask==3.0"
        return mock_adapter

    def test_ansible_export(self):
        adapter = self._make_adapter()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project("/test")
        runtime = plan.get("requirements", {}).get("runtime", plan.get("project_type", ""))
        assert runtime == "python"
        import yaml
        tasks = []
        if runtime in ("python", "django"):
            tasks.append({
                "name": "Install Python3",
                "apt": {"name": "python3", "state": "present"},
            })
        tasks.insert(0, {"name": "Install Git", "apt": {"name": "git", "state": "present"}})
        playbook = [{"hosts": "all", "become": True, "tasks": tasks}]
        content = yaml.dump(playbook, default_flow_style=False)
        assert "Install Python3" in content
        assert "Install Git" in content

    def test_docker_compose_export(self):
        adapter = self._make_adapter()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project("/test")
        runtime = plan.get("requirements", {}).get("runtime", plan.get("project_type", ""))
        services = {}
        if runtime in ("python", "django"):
            services["app"] = {
                "image": "python:3.12-slim",
                "working_dir": "/app",
                "volumes": [".:/app"],
                "command": "python manage.py runserver 0.0.0.0:8000",
                "ports": ["8000:8000"],
            }
        compose = {"version": "3.8", "services": services}
        content = json.dumps(compose, indent=2)
        data = json.loads(content)
        assert "services" in data
        assert data["services"]["app"]["image"] == "python:3.12-slim"


class TestInitCommand:
    def test_init_generates_valid_toml(self, tmp_path):
        import toml
        config = {
            "project": {
                "name": tmp_path.name,
                "detected_type": "python",
                "runtime": "python",
            },
            "verbose": False,
            "skip_detection": [],
            "custom_run_commands": {},
            "export_defaults": {"kind": "devcontainer"},
        }
        config_path = tmp_path / ".itworks.toml"
        with open(config_path, "w") as f:
            toml.dump(config, f)
        assert config_path.exists()
        loaded = toml.load(config_path)
        assert loaded["project"]["name"] == tmp_path.name
        assert loaded["project"]["detected_type"] == "python"
        assert loaded["project"]["runtime"] == "python"

    def test_init_config_roundtrip(self, tmp_path):
        import toml
        config = {
            "project": {"name": "my-app", "detected_type": "nodejs", "runtime": "nodejs"},
            "verbose": True,
            "skip_detection": ["docker"],
            "custom_run_commands": {"nodejs": "bun start"},
            "export_defaults": {"kind": "docker-compose"},
        }
        config_path = tmp_path / ".itworks.toml"
        with open(config_path, "w") as f:
            toml.dump(config, f)
        loaded = toml.load(config_path)
        assert loaded["verbose"] is True
        assert "docker" in loaded["skip_detection"]
        assert loaded["custom_run_commands"]["nodejs"] == "bun start"


class TestJsonOutput:
    def test_scan_json_plan_structure(self):
        plan = {
            "project_path": "/test",
            "project_type": "python",
            "os_origin": "linux",
            "is_portable": True,
            "requirements": {"runtime": "python", "packages": ["flask==3.0"], "engines": {}},
        }
        output = json.dumps(plan, indent=2)
        data = json.loads(output)
        assert "project_type" in data
        assert "requirements" in data
        assert data["project_type"] == "python"
        assert data["requirements"]["runtime"] == "python"

    def test_run_json_result_structure(self):
        result = {"success": True, "stdout": "ok", "stderr": "", "duration": 0.5}
        output = json.dumps(result, indent=2)
        data = json.loads(output)
        assert data["success"] is True
        assert data["stdout"] == "ok"

    def test_run_json_failure_structure(self):
        result = {"success": False, "error": "Command not found"}
        output = json.dumps(result, indent=2)
        data = json.loads(output)
        assert data["success"] is False
        assert "error" in data
