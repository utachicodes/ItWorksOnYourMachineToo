from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_nix_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "nix", "-p", str(p)])
    assert result.exit_code == 0
    nix = (p / "shell.nix").read_text()
    assert "pkgs.python3" in nix and "pkgs.git" in nix


def test_export_nix_for_rust(tmp_path):
    p = tmp_path / "proj_rust"
    p.mkdir()
    (p / "Cargo.toml").write_text("[package]\nname = \"x\"\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "nix", "-p", str(p)])
    assert result.exit_code == 0
    nix = (p / "shell.nix").read_text()
    assert "pkgs.rustc" in nix and "pkgs.cargo" in nix
