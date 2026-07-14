import json

from click.testing import CliRunner

from ItWorksOnYourMachineToo.cli.main import main


def test_capture_writes_profile_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ["capture"])

    assert result.exit_code == 0
    profile_path = tmp_path / ".itworksonyourmachinetoo.json"
    assert profile_path.exists()
    profile = json.loads(profile_path.read_text())
    assert isinstance(profile, dict)
