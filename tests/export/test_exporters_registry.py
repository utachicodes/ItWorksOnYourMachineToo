import pytest

from ItWorksOnYourMachineToo import exporters


def test_registry_contains_all_kinds():
    expected = {"devcontainer", "brewfile", "winget", "apt", "nix", "ansible", "docker-compose"}
    assert expected.issubset(exporters.EXPORTERS.keys())


def test_export_raises_on_unknown_kind(tmp_path):
    with pytest.raises(ValueError, match="Unknown export kind"):
        exporters.export("not-a-real-kind", str(tmp_path), {"project_type": "python", "requirements": {}})
