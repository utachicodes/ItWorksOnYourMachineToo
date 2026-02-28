import json
from click.testing import CliRunner
from lexworkseverywhere.cli.main import main


def _extract_json(output: str):
    start = output.find("{")
    end = output.rfind("}")
    assert start != -1 and end != -1 and end > start
    return json.loads(output[start : end + 1])


def test_doctor_json_output():
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", "--json"])
    assert result.exit_code == 0
    data = _extract_json(result.output)
    assert "system" in data
    assert "ready" in data
    assert "python" in data["system"]
    assert "os" in data["system"]
