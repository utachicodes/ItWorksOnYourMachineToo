from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_winget_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "winget", "-p", str(p)])
    assert result.exit_code == 0
    winget = (p / "winget.txt").read_text()
    assert "Python.Python.3" in winget and "Git.Git" in winget


def test_export_winget_for_java(tmp_path):
    p = tmp_path / "proj_java"
    p.mkdir()
    (p / "pom.xml").write_text("<project></project>")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "winget", "-p", str(p)])
    assert result.exit_code == 0
    winget = (p / "winget.txt").read_text()
    assert "Microsoft.OpenJDK.17" in winget
