# -*- coding: utf-8 -*-
from ItWorksOnYourMachineToo.core.config import get_config_value, load_config


def test_load_config_defaults_when_missing(tmp_path):
    config = load_config(str(tmp_path))

    assert config["verbose"] is False
    assert config["skip_detection"] == []
    assert config["export_defaults"] == {"kind": "devcontainer"}


def test_load_config_merges_with_defaults(tmp_path):
    (tmp_path / ".itworks.toml").write_text('verbose = true\n[project]\nname = "x"\n')

    config = load_config(str(tmp_path))

    assert config["verbose"] is True
    assert config["skip_detection"] == []
    assert config["project"]["name"] == "x"


def test_load_config_falls_back_to_defaults_on_invalid_toml(tmp_path):
    (tmp_path / ".itworks.toml").write_text("not = [valid toml")

    config = load_config(str(tmp_path))

    assert config["verbose"] is False
    assert config["export_defaults"] == {"kind": "devcontainer"}


def test_get_config_value_returns_default_for_missing_key():
    assert get_config_value({}, "missing", "fallback") == "fallback"


def test_get_config_value_returns_present_key():
    assert get_config_value({"verbose": True}, "verbose") is True
