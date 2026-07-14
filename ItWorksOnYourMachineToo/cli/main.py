# -*- coding: utf-8 -*-
import click
import json
import toml
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
from .. import exporters


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
@click.option('--json-output', 'json_out', is_flag=True, default=False, help='Output JSON only')
def scan(project_path: str, verbose: bool, json_out: bool):
    """Analyze a project and generate a universal execution plan."""
    try:
        config = load_config(project_path)
        if get_config_value(config, "verbose"):
            verbose = True
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        if json_out:
            click.echo(json.dumps(plan, indent=2))
            return
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
@click.option('--json-output', 'json_out', is_flag=True, default=False, help='Output JSON result only')
def run(project_path: str, verbose: bool, json_out: bool):
    """Run a project in a secure and isolated environment."""
    try:
        config = load_config(project_path)
        if get_config_value(config, "verbose"):
            verbose = True
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        engine = ExecutionEngine(adapter)
        if verbose and not json_out:
            click.echo(f"[scan] {t('scan_start')}")
        plan = planner.plan_project(project_path)
        if verbose and not json_out:
            click.echo(f"[prepare] {t('prepare_env')} (type={plan.get('project_type')})")
        elif not json_out:
            click.echo(f"  {t('prepare_env')}")
        if not engine.prepare(plan):
            if json_out:
                click.echo(json.dumps({"success": False, "error": "Preparation failed"}, indent=2))
            else:
                click.echo("Preparation failed", err=True)
            return
        if verbose and not json_out:
            click.echo(f"[execute] {t('execute')}")
        result = engine.execute(plan)
        if json_out:
            click.echo(json.dumps(result, indent=2))
        elif result['success']:
            click.echo(f"  {t('success')}")
            click.echo(result['stdout'])
        else:
            click.echo(f"  {t('failure')}", err=True)
            click.echo(result['stderr'], err=True)
    except Exception as e:
        if json_out:
            click.echo(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
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
@click.option('--project-path', '-p', type=click.Path(), default='.', help='Project directory')
@click.option('--force', is_flag=True, default=False, help='Overwrite existing config')
def init(project_path: str, force: bool):
    """Generate a .itworks.toml configuration file."""
    config_path = Path(project_path) / ".itworks.toml"
    if config_path.exists() and not force:
        click.echo(f"Config already exists at {config_path}")
        click.echo("Use --force to overwrite")
        return
    try:
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        p_type = plan.get("project_type", "unknown")
        runtime = plan.get("requirements", {}).get("runtime", p_type)
        config = {
            "project": {
                "name": Path(project_path).resolve().name,
                "detected_type": p_type,
                "runtime": runtime,
            },
            "verbose": False,
            "skip_detection": [],
            "custom_run_commands": {},
            "export_defaults": {"kind": "devcontainer"},
        }
        with open(config_path, "w") as f:
            toml.dump(config, f)
        click.echo(f"Created {config_path}")
        click.echo(f"Detected project type: {p_type}")
        click.echo(f"Detected runtime: {runtime}")
    except Exception as e:
        click.echo(f"Failed to create config: {e}", err=True)


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
    try:
        out_path = exporters.export(kind, project_path, plan)
    except ValueError as e:
        click.echo(str(e), err=True)
        return
    click.echo(f"Exported {Path(out_path).name}")


if __name__ == '__main__':
    main()
