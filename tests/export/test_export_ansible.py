import yaml
from click.testing import CliRunner
from ItWorksOnYourMachineToo.cli.main import main


def test_export_ansible_for_python(tmp_path):
    p = tmp_path / "proj_py"
    p.mkdir()
    (p / "requirements.txt").write_text("requests==2.31.0\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "ansible", "-p", str(p)])
    assert result.exit_code == 0
    playbook = yaml.safe_load((p / "playbook.yml").read_text())
    assert playbook[0]["hosts"] == "all"
    task_names = [t["name"] for t in playbook[0]["tasks"]]
    assert "Install Git" in task_names
    assert "Install Python3" in task_names


def test_export_ansible_for_rust(tmp_path):
    p = tmp_path / "proj_rust"
    p.mkdir()
    (p / "Cargo.toml").write_text("[package]\nname = \"x\"\n")
    runner = CliRunner()
    result = runner.invoke(main, ["export", "--kind", "ansible", "-p", str(p)])
    assert result.exit_code == 0
    playbook = yaml.safe_load((p / "playbook.yml").read_text())
    task_names = [t["name"] for t in playbook[0]["tasks"]]
    assert "Install Rust" in task_names
