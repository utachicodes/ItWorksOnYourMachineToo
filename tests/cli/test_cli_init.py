from click.testing import CliRunner

from ItWorksOnYourMachineToo.cli.main import main


def test_init_creates_config_file(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    (p / "requirements.txt").write_text("requests\n")
    runner = CliRunner()

    result = runner.invoke(main, ["init", "-p", str(p)])

    assert result.exit_code == 0
    config_path = p / ".itworks.toml"
    assert config_path.exists()
    assert "python" in config_path.read_text()


def test_init_refuses_to_overwrite_without_force(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    (p / ".itworks.toml").write_text("verbose = true\n")
    runner = CliRunner()

    result = runner.invoke(main, ["init", "-p", str(p)])

    assert result.exit_code == 0
    assert "already exists" in result.output
    assert (p / ".itworks.toml").read_text() == "verbose = true\n"


def test_init_overwrites_with_force(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    (p / ".itworks.toml").write_text("verbose = true\n")
    runner = CliRunner()

    result = runner.invoke(main, ["init", "-p", str(p), "--force"])

    assert result.exit_code == 0
    assert "verbose = true" not in (p / ".itworks.toml").read_text()
