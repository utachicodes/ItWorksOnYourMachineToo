import json
from click.testing import CliRunner
from lexworkseverywhere.cli.main import main


def test_export_devcontainer_for_node(tmp_path):
    p = tmp_path / "proj_node"
    p.mkdir()
    (p / "package.json").write_text('{"name":"x","version":"1.0.0","dependencies":{"left-pad":"1.3.0"}}')
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "devcontainer", "-p", str(p)])
    assert result.exit_code == 0
    dc = json.loads((p / ".devcontainer" / "devcontainer.json").read_text())
    assert "features" in dc and any("node" in k for k in dc["features"].keys())


def test_export_os_files_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result_brew = runner.invoke(main, ["export", "--kind", "brewfile", "-p", str(p)])
    result_apt = runner.invoke(main, ["export", "--kind", "apt", "-p", str(p)])
    result_winget = runner.invoke(main, ["export", "--kind", "winget", "-p", str(p)])
    result_nix = runner.invoke(main, ["export", "--kind", "nix", "-p", str(p)])
    assert result_brew.exit_code == 0
    assert result_apt.exit_code == 0
    assert result_winget.exit_code == 0
    assert result_nix.exit_code == 0
    brew = (p / "Brewfile").read_text()
    apt = (p / "apt.txt").read_text()
    winget = (p / "winget.txt").read_text()
    nix = (p / "shell.nix").read_text()
    assert 'brew "python"' in brew and 'brew "git"' in brew
    assert "python3" in apt and "git" in apt
    assert "Python.Python.3" in winget and "Git.Git" in winget
    assert "pkgs.python3" in nix and "pkgs.git" in nix
