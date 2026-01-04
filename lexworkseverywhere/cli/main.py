# -*- coding: utf-8 -*-
import click
import json
import os
from pathlib import Path
from typing import List

from ..core.contracts.factory import AdapterFactory
from ..core.planner.engine import ProjectPlanner
from ..core.engine.engine import ExecutionEngine
from ..core.validator.engine import EnvironmentValidator
from .doctor import run_doctor
from rich.console import Console
from rich.panel import Panel
from ..core.security.license import LicenseManager
from ..core.profiler import EnvironmentProfiler

@click.group()
@click.version_option(version="2.1.0")
def main():
    """LexWorksEverywhere: Gestionnaire d'environnement de développement universel (v2 Core PUR)."""
    console = Console()
    branding = LicenseManager.get_branding_header()
    console.print(Panel(branding, border_style="blue"))

@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
def scan(project_path: str):
    """Analyse un projet et génère un plan d'exécution universel."""
    try:
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        plan = planner.plan_project(project_path)
        click.echo(json.dumps(plan, indent=2))
    except Exception as e:
        click.echo(f"Erreur d'analyse : {e}", err=True)

@main.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), default='.')
def run(project_path: str):
    """Exécute un projet dans un environnement sécurisé et isolé."""
    try:
        adapter = AdapterFactory.detect()
        planner = ProjectPlanner(adapter)
        engine = ExecutionEngine(adapter)
        
        click.echo("🔍 Scan du projet...")
        plan = planner.plan_project(project_path)
        
        click.echo("🛠️ Préparation de l'environnement...")
        if not engine.prepare(plan):
            click.echo("❌ Échec de la préparation", err=True)
            return

        click.echo("🚀 Exécution...")
        result = engine.execute(plan)
        
        if result['success']:
            click.echo("✅ Succès !")
            click.echo(result['stdout'])
        else:
            click.echo("❌ Échec de l'exécution", err=True)
            click.echo(result['stderr'], err=True)
            
    except Exception as e:
        click.echo(f"Erreur fatale : {e}", err=True)

@main.command()
def doctor():
    """Vérifie la compatibilité de l'hôte avec LexWorksEverywhere."""
    run_doctor()

@main.command()
def capture():
    """Capture la configuration de l'environnement actuel."""
    try:
        adapter = AdapterFactory.detect()
        profiler = EnvironmentProfiler(adapter)
        profile = profiler.capture_profile()
        
        output_path = ".lexworkseverywhere.json"
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2)
            
        click.echo(f"✅ Profil capturé et sauvegardé dans {output_path}")
    except Exception as e:
        click.echo(f"❌ Échec de la capture : {e}", err=True)

if __name__ == '__main__':
    main()
