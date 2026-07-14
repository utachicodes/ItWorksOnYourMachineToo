import json
from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_devcontainer_for_node(tmp_path):
    p = tmp_path / "proj_node"
    p.mkdir()
    (p / "package.json").write_text('{"name":"x","version":"1.0.0","dependencies":{"left-pad":"1.3.0"}}')
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "devcontainer", "-p", str(p)])
    assert result.exit_code == 0
    dc = json.loads((p / ".devcontainer" / "devcontainer.json").read_text())
    assert "features" in dc and any("node" in k for k in dc["features"].keys())


def test_export_devcontainer_falls_back_to_common_utils(tmp_path):
    p = tmp_path / "proj_unknown"
    p.mkdir()
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "devcontainer", "-p", str(p)])
    assert result.exit_code == 0
    dc = json.loads((p / ".devcontainer" / "devcontainer.json").read_text())
    assert any("common-utils" in k for k in dc["features"].keys())
