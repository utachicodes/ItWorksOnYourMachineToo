import json
from click.testing import CliRunner
from lexworkseverywhere.cli.main import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "2.1.0" in result.output


def test_doctor_basic():
    runner = CliRunner()
    result = runner.invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "LexWorksEverywhere" in result.output


def test_scan_plan(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    (p / "main.py").write_text("print('ok')")
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "-p", str(p)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "project_type" in data
