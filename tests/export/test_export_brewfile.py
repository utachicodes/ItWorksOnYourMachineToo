from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_brewfile_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "brewfile", "-p", str(p)])
    assert result.exit_code == 0
    brew = (p / "Brewfile").read_text()
    assert 'brew "python"' in brew and 'brew "git"' in brew


def test_export_brewfile_for_rust(tmp_path):
    p = tmp_path / "proj_rust"
    p.mkdir()
    (p / "Cargo.toml").write_text("[package]\nname = \"x\"\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "brewfile", "-p", str(p)])
    assert result.exit_code == 0
    brew = (p / "Brewfile").read_text()
    assert 'brew "rust"' in brew
