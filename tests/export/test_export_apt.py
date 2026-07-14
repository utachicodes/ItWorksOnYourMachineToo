from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_apt_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "apt", "-p", str(p)])
    assert result.exit_code == 0
    apt = (p / "apt.txt").read_text()
    assert "python3" in apt and "git" in apt


def test_export_apt_for_go(tmp_path):
    p = tmp_path / "proj_go"
    p.mkdir()
    (p / "go.mod").write_text("module example.com/x\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "apt", "-p", str(p)])
    assert result.exit_code == 0
    apt = (p / "apt.txt").read_text()
    assert "golang" in apt
