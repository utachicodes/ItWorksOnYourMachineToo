from click.testing import CliRunner

from ItWorksOnYourMachineToo.cli.main import main


def test_list_reports_detected_type_and_runtimes(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\nnumpy\n")
    runner = CliRunner()

    result = runner.invoke(main, ["list", "-p", str(p)])

    assert result.exit_code == 0
    assert "Detected type" in result.output
    assert "python" in result.output
    assert "requests==2.31.0" in result.output


def test_list_truncates_long_dependency_lists(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    deps = "\n".join(f"pkg{i}" for i in range(25))
    (p / "requirements.txt").write_text(deps + "\n")
    runner = CliRunner()

    result = runner.invoke(main, ["list", "-p", str(p)])

    assert result.exit_code == 0
    assert "and 5 more" in result.output
