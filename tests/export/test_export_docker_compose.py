import yaml
from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_docker_compose_for_node(tmp_path):
    p = tmp_path / "proj_node"
    p.mkdir()
    (p / "package.json").write_text('{"name":"x","version":"1.0.0"}')
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "docker-compose", "-p", str(p)])
    assert result.exit_code == 0
    compose = yaml.safe_load((p / "docker-compose.yml").read_text())
    assert "version" not in compose
    assert compose["services"]["app"]["image"].startswith("node:")


def test_export_docker_compose_defaults_for_unknown_project(tmp_path):
    p = tmp_path / "proj_unknown"
    p.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "docker-compose", "-p", str(p)])
    assert result.exit_code == 0
    compose = yaml.safe_load((p / "docker-compose.yml").read_text())
    assert compose["services"]["app"]["image"] == "alpine:latest"
