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
from ..core.config import load_config, get_config_value


@click.group()
@click.version_option(version="2.1.0")
@click.option('--lang', type=click.Choice(['en', 'fr']), default='en', help='Language for CLI output')
def main(lang: str):
    """ItWorksOnYourMachineToo: Universal development environment manager (v2 Core PUR)."""
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
@click.option('--verbose', '-v', is_flag=True, default=False, help='Show detailed scan output')
def scan(project_path: str, verbose: bool):
    """Analyze a project and generate a universal execution plan."""
    try:
        config = load_config(project_path)
        if get_config_value(config, "verbose"):
            verbose = True
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        if verbose:
            console = Console()
            console.print(f"[bold]Project path:[/bold] {plan.get('project_path')}")
            console.print(f"[bold]Project type:[/bold] {plan.get('project_type')}")
            console.print(f"[bold]OS origin:[/bold] {plan.get('os_origin')}")
            reqs = plan.get("requirements", {})
            if reqs.get("runtime"):
                console.print(f"[bold]Runtime:[/bold] {reqs['runtime']}")
            if reqs.get("packages"):
                console.print(f"[bold]Packages:[/bold] {len(reqs['packages'])} detected")
            if reqs.get("engines"):
                console.print(f"[bold]Engines:[/bold] {reqs['engines']}")
        click.echo(json.dumps(plan, indent=2))
    except Exception as e:
        click.echo(f"{t('fatal_error')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Show detailed execution output')
def run(project_path: str, verbose: bool):
    """Run a project in a secure and isolated environment."""
    try:
        config = load_config(project_path)
        if get_config_value(config, "verbose"):
            verbose = True
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        engine = ExecutionEngine(adapter)
        if verbose:
            click.echo(f"[scan] {t('scan_start')}")
        plan = planner.plan_project(project_path)
        if verbose:
            click.echo(f"[prepare] {t('prepare_env')} (type={plan.get('project_type')})")
        else:
            click.echo(f"  {t('prepare_env')}")
        if not engine.prepare(plan):
            click.echo("Preparation failed", err=True)
            return
        if verbose:
            click.echo(f"[execute] {t('execute')}")
        result = engine.execute(plan)
        if result['success']:
            click.echo(f"  {t('success')}")
            click.echo(result['stdout'])
        else:
            click.echo(f"  {t('failure')}", err=True)
            click.echo(result['stderr'], err=True)
    except Exception as e:
        click.echo(f"{t('fatal_error')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), required=False)
@click.option('--apply', is_flag=True, default=False, help='Apply safe local fixes when possible')
@click.option('--json', 'json_out', is_flag=True, default=False, help='Output JSON report')
def doctor(project_path: str = None, apply: bool = False, json_out: bool = False):
    """Verify host and optionally project compatibility with ItWorksOnYourMachineToo."""
    run_doctor(project_path=project_path, apply=apply, json_output=json_out)


@main.command()
def capture():
    """Capture the current environment configuration."""
    try:
        adapter = AdapterFactory.detect()
        profiler = EnvironmentProfiler(adapter)
        profile = profiler.capture_profile()
        output_path = ".itworksonyourmachinetoo.json"
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2)
        click.echo(f"  {t('profile_saved')} {output_path}")
    except Exception as e:
        click.echo(f"  {t('capture_failed')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
def list(project_path: str):
    """List detected languages and their status in a project."""
    try:
        adapter = AdapterFactory.detect()
        profiler = EnvironmentProfiler(adapter)
        runtime_versions = profiler._detect_runtimes()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        p_type = plan.get("project_type", "unknown")
        reqs = plan.get("requirements", {})
        runtime = reqs.get("runtime", p_type)
        console = Console()
        console.print(f"\n[bold blue]Project:[/bold blue] {project_path}")
        console.print(f"[bold blue]Detected type:[/bold blue] {p_type}")
        console.print(f"[bold blue]Runtime:[/bold blue] {runtime}\n")
        all_runtimes = ["python", "node", "npm", "go", "cargo", "php", "composer", "ruby", "java", "dotnet"]
        console.print("[bold]Available runtimes:[/bold]")
        for r in all_runtimes:
            ver = runtime_versions.get(r, "not found")
            status = "[green]installed[/green]" if ver != "not found" else "[red]missing[/red]"
            console.print(f"  {r:12} {ver:20} {status}")
        packages = reqs.get("packages", [])
        if packages:
            console.print(f"\n[bold]Dependencies ({len(packages)}):[/bold]")
            for pkg in packages[:20]:
                console.print(f"  - {pkg}")
            if len(packages) > 20:
                console.print(f"  ... and {len(packages) - 20} more")
        engines = reqs.get("engines", {})
        if engines:
            console.print("\n[bold]Engine requirements:[/bold]")
            for k, v in engines.items():
                console.print(f"  {k}: {v}")
    except Exception as e:
        click.echo(f"{t('fatal_error')}: {e}", err=True)


@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
@click.option(
    '--kind',
    type=click.Choice([
        'devcontainer', 'brewfile', 'winget', 'apt', 'nix',
        'ansible', 'docker-compose',
    ]),
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
        if languages in ("java", "kotlin"):
            features.append({"ghcr.io/devcontainers/features/java:1": {"version": "17"}})
        if languages == "php":
            features.append({"ghcr.io/devcontainers/features/php:1": {"version": "8.3"}})
        if languages == "swift":
            features.append({"ghcr.io/devcontainers/features/swift:1": {}})
        if not features:
            features.append({"ghcr.io/devcontainers/features/common-utils:2": {}})
        devcontainer = {
            "name": "ItWorksOnYourMachineToo Dev Container",
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
        click.echo("Exported .devcontainer/devcontainer.json")
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
            if runtime in ("java", "kotlin"):
                lines.append('brew "openjdk"')
            if runtime == "swift":
                lines.append('# Swift is included with Xcode on macOS')
            if runtime == "ruby":
                lines.append('brew "ruby"')
            if 'brew "git"' not in lines:
                lines.insert(0, 'brew "git"')
            if not lines:
                lines.append('# Add your packages here')
            Path(project_path, "Brewfile").write_text("\n".join(lines) + "\n")
            click.echo("Exported Brewfile")
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
            if runtime in ("java", "kotlin"):
                lines.append("winget install Microsoft.OpenJDK.17")
            if runtime == "ruby":
                lines.append("winget install RubyInstallerTeam.Ruby")
            if "winget install Git.Git" not in lines:
                lines.insert(0, "winget install Git.Git")
            if not lines:
                lines.append("# Add your installers here")
            Path(project_path, "winget.txt").write_text("\n".join(lines) + "\n")
            click.echo("Exported winget.txt")
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
            if runtime in ("java", "kotlin"):
                lines.append("sudo apt install -y openjdk-17-jdk")
            if runtime == "ruby":
                lines.append("sudo apt install -y ruby-full")
            if "sudo apt install -y git" not in lines:
                lines.insert(0, "sudo apt install -y git")
            if not lines:
                lines.append("# Add your apt packages here")
            Path(project_path, "apt.txt").write_text("\n".join(lines) + "\n")
            click.echo("Exported apt.txt")
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
            if runtime in ("java", "kotlin"):
                pkgs.append("jdk17")
            if runtime == "ruby":
                pkgs.append("ruby")
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
            click.echo("Exported shell.nix")
        if kind == "ansible":
            tasks = []
            if runtime in ("nodejs", "bun"):
                tasks.append({
                    "name": "Install Node.js",
                    "apt": {"name": "nodejs", "state": "present"},
                })
            if runtime in ("python", "django"):
                tasks.append({
                    "name": "Install Python3",
                    "apt": {"name": "python3", "state": "present"},
                })
            if runtime == "go":
                tasks.append({
                    "name": "Install Go",
                    "apt": {"name": "golang", "state": "present"},
                })
            if runtime == "rust":
                tasks.append({
                    "name": "Install Rust",
                    "shell": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
                    "creates": "{{ ansible_env.HOME }}/.cargo/bin/rustc",
                })
            if runtime in ("php", "laravel"):
                tasks.append({
                    "name": "Install PHP and Composer",
                    "apt": {"name": ["php", "composer"], "state": "present"},
                })
            if runtime in ("java", "kotlin"):
                tasks.append({
                    "name": "Install OpenJDK 17",
                    "apt": {"name": "openjdk-17-jdk", "state": "present"},
                })
            if runtime == "ruby":
                tasks.append({
                    "name": "Install Ruby",
                    "apt": {"name": "ruby-full", "state": "present"},
                })
            tasks.insert(0, {"name": "Install Git", "apt": {"name": "git", "state": "present"}})
            playbook = [{"hosts": "all", "become": True, "tasks": tasks}]
            import yaml
            Path(project_path, "playbook.yml").write_text(yaml.dump(playbook, default_flow_style=False))
            click.echo("Exported playbook.yml")
        if kind == "docker-compose":
            services = {}
            if runtime in ("nodejs", "bun"):
                services["app"] = {
                    "image": "node:20-alpine",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "npm start",
                }
            elif runtime in ("python", "django"):
                services["app"] = {
                    "image": "python:3.12-slim",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "python manage.py runserver 0.0.0.0:8000",
                    "ports": ["8000:8000"],
                }
            elif runtime == "go":
                services["app"] = {
                    "image": "golang:1.22-alpine",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "go run .",
                }
            elif runtime == "rust":
                services["app"] = {
                    "image": "rust:1.77-slim",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "cargo run",
                }
            elif runtime in ("php", "laravel"):
                services["app"] = {
                    "image": "php:8.3-cli",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "php artisan serve --host=0.0.0.0",
                    "ports": ["8000:8000"],
                }
            elif runtime in ("java", "kotlin"):
                services["app"] = {
                    "image": "eclipse-temurin:17-jdk",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "java -jar app.jar",
                }
            elif runtime == "swift":
                services["app"] = {
                    "image": "swift:5.9",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "swift run",
                }
            elif runtime == "ruby":
                services["app"] = {
                    "image": "ruby:3.3-slim",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "ruby main.rb",
                }
            else:
                services["app"] = {
                    "image": "alpine:latest",
                    "working_dir": "/app",
                    "volumes": [".:/app"],
                    "command": "echo 'Configure your service'",
                }
            compose = {"version": "3.8", "services": services}
            with open(Path(project_path) / "docker-compose.yml", "w") as f:
                json.dump(compose, f, indent=2)
            click.echo("Exported docker-compose.yml")


if __name__ == '__main__':
    main()
