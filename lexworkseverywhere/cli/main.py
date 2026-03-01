# -*- coding: utf-8 -*-
import click
import json
from pathlib import Path
from ..core.contracts.factory import AdapterFactory
from ..core.planner.engine import ProjectPlanner
from ..core.engine.engine import ExecutionEngine
from .doctor import run_doctor
from rich.console import Console
from rich.panel import Panel
from ..core.security.license import LicenseManager
from ..core.profiler import EnvironmentProfiler
from ..core.i18n import set_locale, t


@click.group()
@click.version_option(version="2.1.0")
@click.option('--lang', type=click.Choice(['en', 'fr']), default='en', help='Language for CLI output')
def main(lang: str):
    """LexWorksEverywhere: Universal development environment manager (v2 Core PUR)."""
    set_locale(lang)
    console = Console()
    try:
        if console.is_terminal:
            branding = LicenseManager.get_branding_header()
            console.print(Panel(branding, border_style="blue"))
    except Exception:
        pass


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
def scan(project_path: str):
    """Analyze a project and generate a universal execution plan."""
    try:
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        click.echo(json.dumps(plan, indent=2))
    except Exception as e:
        click.echo(f"{t('fatal_error')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
def run(project_path: str):
    """Run a project in a secure and isolated environment."""
    try:
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        engine = ExecutionEngine(adapter)
        click.echo(f"🔍 {t('scan_start')}")
        plan = planner.plan_project(project_path)
        click.echo(f"🛠️ {t('prepare_env')}")
        if not engine.prepare(plan):
            click.echo("❌ Preparation failed", err=True)
            return
        click.echo(f"🚀 {t('execute')}")
        result = engine.execute(plan)
        if result['success']:
            click.echo(f"✅ {t('success')}")
            click.echo(result['stdout'])
        else:
            click.echo(f"❌ {t('failure')}", err=True)
            click.echo(result['stderr'], err=True)
    except Exception as e:
        click.echo(f"{t('fatal_error')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), required=False)
@click.option('--apply', is_flag=True, default=False, help='Apply safe local fixes when possible')
@click.option('--json', 'json_out', is_flag=True, default=False, help='Output JSON report')
def doctor(project_path: str = None, apply: bool = False, json_out: bool = False):
    """Verify host and optionally project compatibility with LexWorksEverywhere."""
    run_doctor(project_path=project_path, apply=apply, json_output=json_out)


@main.command()
def capture():
    """Capture the current environment configuration."""
    try:
        adapter = AdapterFactory.detect()
        profiler = EnvironmentProfiler(adapter)
        profile = profiler.capture_profile()
        output_path = ".lexworkseverywhere.json"
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2)
        click.echo(f"✅ {t('profile_saved')} {output_path}")
    except Exception as e:
        click.echo(f"❌ {t('capture_failed')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
@click.option(
    '--kind',
    type=click.Choice(['devcontainer', 'brewfile', 'winget', 'apt', 'nix']),
    required=True,
    help='Export artifact type',
)
def export(project_path: str, kind: str):
    """Export project environment artifacts (e.g., devcontainer)."""
    adapter = AdapterFactory.detect()
    planner = ProjectPlanner(adapter)
    plan = planner.plan_project(project_path)
    if kind == "devcontainer":
        dc_dir = Path(project_path) / ".devcontainer"
        dc_dir.mkdir(parents=True, exist_ok=True)
        languages = plan.get("project_type")
        features = []
        if languages == "nodejs":
            features.append({"ghcr.io/devcontainers/features/node:1": {"version": "lts", "nodeGypDependencies": True}})
        if languages in ["python", "django"]:
            features.append({"ghcr.io/devcontainers/features/python:1": {"version": "3"}})
        if languages == "go":
            features.append({"ghcr.io/devcontainers/features/go:1": {"version": "latest"}})
        if languages == "rust":
            features.append({"ghcr.io/devcontainers/features/rust:1": {}})
        if not features:
            features.append({"ghcr.io/devcontainers/features/common-utils:2": {}})
        devcontainer = {
            "name": "LexWorksEverywhere Dev Container",
            "image": "mcr.microsoft.com/devcontainers/base:latest",
            "features": {k: v for obj in features for k, v in obj.items()},
            "customizations": {
                "vscode": {
                    "extensions": [
                        "ms-python.python",
                        "esbenp.prettier-vscode",
                        "ms-azuretools.vscode-docker",
                        "rust-lang.rust-analyzer",
                        "golang.go"
                    ]
                }
            },
            "postCreateCommand": "echo Ready"
        }
        with open(dc_dir / "devcontainer.json", "w") as f:
            json.dump(devcontainer, f, indent=2)
        click.echo("✅ Exported .devcontainer/devcontainer.json")
    elif kind in ("brewfile", "winget", "apt", "nix"):
        req = plan.get("requirements", {})
        runtime = (req.get("runtime") or plan.get("project_type") or "").lower()
        if kind == "brewfile":
            lines = []
            if runtime in ("nodejs", "bun"):
                lines.append('brew "node"')
            if runtime in ("python", "django"):
                lines.append('brew "python"')
            if runtime == "rust":
                lines.append('brew "rust"')
            if runtime == "go":
                lines.append('brew "go"')
            if runtime in ("php", "laravel"):
                lines.append('brew "php"')
                lines.append('brew "composer"')
            if 'brew "git"' not in lines:
                lines.insert(0, 'brew "git"')
            if not lines:
                lines.append('# Add your packages here')
            Path(project_path, "Brewfile").write_text("\n".join(lines) + "\n")
            click.echo("✅ Exported Brewfile")
        if kind == "winget":
            lines = []
            if runtime in ("nodejs", "bun"):
                lines.append("winget install OpenJS.NodeJS")
            if runtime in ("python", "django"):
                lines.append("winget install Python.Python.3")
            if runtime == "rust":
                lines.append("winget install Rustlang.Rustup")
            if runtime == "go":
                lines.append("winget install Google.Go")
            if runtime in ("php", "laravel"):
                lines.append("winget install PHP.PHP")
                lines.append("winget install Microsoft.Composer")
            if "winget install Git.Git" not in lines:
                lines.insert(0, "winget install Git.Git")
            if not lines:
                lines.append("# Add your installers here")
            Path(project_path, "winget.txt").write_text("\n".join(lines) + "\n")
            click.echo("✅ Exported winget.txt")
        if kind == "apt":
            lines = []
            if runtime in ("nodejs", "bun"):
                lines.append("sudo apt install -y nodejs npm")
            if runtime in ("python", "django"):
                lines.append("sudo apt install -y python3 python3-pip")
            if runtime == "rust":
                lines.append("# curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
            if runtime == "go":
                lines.append("sudo apt install -y golang")
            if runtime in ("php", "laravel"):
                lines.append("sudo apt install -y php composer")
            if "sudo apt install -y git" not in lines:
                lines.insert(0, "sudo apt install -y git")
            if not lines:
                lines.append("# Add your apt packages here")
            Path(project_path, "apt.txt").write_text("\n".join(lines) + "\n")
            click.echo("✅ Exported apt.txt")
        if kind == "nix":
            pkgs = []
            if runtime in ("nodejs", "bun"):
                pkgs.append("nodejs")
            if runtime in ("python", "django"):
                pkgs.append("python3")
            if runtime == "rust":
                pkgs.append("rustc")
                pkgs.append("cargo")
            if runtime == "go":
                pkgs.append("go")
            if runtime in ("php", "laravel"):
                pkgs.append("php")
                pkgs.append("composer")
            if "git" not in pkgs:
                pkgs.insert(0, "git")
            if not pkgs:
                pkgs.append("# add packages")
            shell_nix = f'''{{ pkgs ? import <nixpkgs> {{ }} }}:
pkgs.mkShell {{
  buildInputs = [ {" ".join(f"pkgs.{p}" if p and p[0] != "#" else "" for p in pkgs)} ];
}}
'''
            Path(project_path, "shell.nix").write_text(shell_nix)
            click.echo("✅ Exported shell.nix")


if __name__ == '__main__':
    main()
