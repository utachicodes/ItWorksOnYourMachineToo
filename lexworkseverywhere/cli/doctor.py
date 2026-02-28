# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Doctor - Outil d'auto-diagnostic
======================================

Vérifie que l'environnement hôte est prêt pour LexWorksEverywhere.

Projet développé par : Alexandre Albert Ndour
"""

import sys
import platform
import psutil
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..core.contracts.factory import AdapterFactory
from ..core.planner.engine import ProjectPlanner
from ..core.engine.engine import ExecutionEngine
from ..core.i18n import t

console = Console()

def run_doctor(project_path: str = None):
    console.print(f"[bold blue]🩺 {t('doctor_title')}[/bold blue]\n")
    
    table = Table(title=t("doctor_table_title"))
    table.add_column(t("component"), style="cyan")
    table.add_column(t("status"), style="magenta")
    table.add_column(t("details"), style="green")

    py_version = platform.python_version()
    is_py_ok = sys.version_info >= (3, 9)
    table.add_row(t("python_version"), "✅ " + t("ok") if is_py_ok else "❌ " + t("error"), py_version)

    os_name = platform.system()
    is_os_ok = os_name in ["Darwin", "Linux", "Windows"]
    table.add_row(t("os_name"), "✅ " + t("ok") if is_os_ok else "⚠️ " + t("warn"), os_name)

    mem = psutil.virtual_memory()
    mem_ok = mem.available > (500 * 1024 * 1024)
    table.add_row(t("memory"), "✅ " + t("ok") if mem_ok else "⚠️ " + t("low"), f"{mem.available / (1024**3):.2f} GB")

    usage = shutil.disk_usage("/")
    disk_ok = usage.free > (2 * 1024 * 1024 * 1024)
    table.add_row(t("disk"), "✅ " + t("ok") if disk_ok else "⚠️ " + t("low"), f"{usage.free / (1024**3):.2f} GB")

    try:
        adapter = AdapterFactory.detect()
        table.add_row(t("adapter"), "✅ " + t("ok"), adapter.get_os_name())
    except Exception as e:
        table.add_row(t("adapter"), "❌ " + t("error"), str(e))

    if project_path:
        try:
            adapter = AdapterFactory.detect()
            planner = ProjectPlanner(adapter)
            plan = planner.plan_project(project_path)
            engine = ExecutionEngine(adapter)
            runtime = plan.get("requirements", {}).get("runtime", plan.get("project_type"))
            ok = engine.check_system_requirements(runtime)
            status = "✅ " + t("ok") if ok else "❌ " + t("error")
            table.add_row(f"project:{runtime}", status, plan.get("project_type"))
        except Exception as e:
            table.add_row("project", "❌ " + t("error"), str(e))

    console.print(table)
    
    if is_py_ok and is_os_ok:
        console.print("\n[bold green]✅ " + t("ready") + " ![/bold green]")
        return True
    else:
        console.print("\n[bold red]❌ " + t("attention") + ".[/bold red]")
        return False

if __name__ == "__main__":
    run_doctor()
