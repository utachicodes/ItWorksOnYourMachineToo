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
import json
from rich.console import Console
from rich.table import Table
from ..core.contracts.factory import AdapterFactory
from ..core.planner.engine import ProjectPlanner
from ..core.engine.engine import ExecutionEngine
from ..core.i18n import t

console = Console()


def run_doctor(project_path: str = None, apply: bool = False, json_output: bool = False):
    if not json_output:
        console.print(f"[bold blue]🩺 {t('doctor_title')}[/bold blue]\n")

    table = None
    if not json_output:
        table = Table(title=t("doctor_table_title"))
        table.add_column(t("component"), style="cyan")
        table.add_column(t("status"), style="magenta")
        table.add_column(t("details"), style="green")

    py_version = platform.python_version()
    is_py_ok = sys.version_info >= (3, 9)
    if not json_output:
        table.add_row(t("python_version"), "✅ " + t("ok") if is_py_ok else "❌ " + t("error"), py_version)

    os_name = platform.system()
    is_os_ok = os_name in ["Darwin", "Linux", "Windows"]
    if not json_output:
        table.add_row(t("os_name"), "✅ " + t("ok") if is_os_ok else "⚠️ " + t("warn"), os_name)

    mem = psutil.virtual_memory()
    mem_ok = mem.available > (500 * 1024 * 1024)
    if not json_output:
        table.add_row(t("memory"), "✅ " + t("ok") if mem_ok else "⚠️ " + t("low"), f"{mem.available / (1024**3):.2f} GB")

    usage = shutil.disk_usage("/")
    disk_ok = usage.free > (2 * 1024 * 1024 * 1024)
    if not json_output:
        table.add_row(t("disk"), "✅ " + t("ok") if disk_ok else "⚠️ " + t("low"), f"{usage.free / (1024**3):.2f} GB")

    adapter_name = None
    adapter_ok = False
    try:
        adapter = AdapterFactory.detect()
        adapter_name = adapter.get_os_name()
        adapter_ok = True
        if not json_output:
            table.add_row(t("adapter"), "✅ " + t("ok"), adapter_name)
    except Exception as e:
        if not json_output:
            table.add_row(t("adapter"), "❌ " + t("error"), str(e))

    project_report = None
    if project_path:
        try:
            adapter = AdapterFactory.detect()
            planner = ProjectPlanner(adapter)
            plan = planner.plan_project(project_path)
            engine = ExecutionEngine(adapter)
            runtime = plan.get("requirements", {}).get("runtime", plan.get("project_type"))
            ok = engine.check_system_requirements(runtime)
            status = "✅ " + t("ok") if ok else "❌ " + t("error")
            if not json_output:
                table.add_row(f"project:{runtime}", status, plan.get("project_type"))
            project_report = {
                "path": project_path,
                "detected_type": plan.get("project_type"),
                "runtime": runtime,
                "requirements_ok": ok,
            }
            if apply:
                try:
                    p = plan.get("project_path")
                    r = runtime
                    if r == "nodejs":
                        adapter.process.run(
                            [
                                "bash",
                                "-lc",
                                "command -v corepack >/dev/null 2>&1 && corepack enable || true",
                            ],
                            cwd=p,
                            capture_output=True,
                        )
                        if adapter.fs.exists(f"{p}/package.json"):
                            adapter.process.run(["npm", "install"], cwd=p)
                    elif r in ("python", "django"):
                        if adapter.fs.exists(f"{p}/requirements.txt"):
                            adapter.process.run(["pip", "install", "-r", "requirements.txt"], cwd=p)
                    elif r in ("php", "laravel"):
                        if adapter.fs.exists(f"{p}/composer.json"):
                            adapter.process.run(["composer", "install"], cwd=p)
                    elif r == "rails":
                        if adapter.fs.exists(f"{p}/Gemfile"):
                            adapter.process.run(["bundle", "install"], cwd=p)
                    if not json_output:
                        table.add_row("autofix", "✅ " + t("ok"), f"{runtime}")
                    if project_report is not None:
                        project_report["apply"] = {"attempted": True, "ok": True}
                except Exception as e:
                    if not json_output:
                        table.add_row("autofix", "❌ " + t("error"), str(e))
                    if project_report is not None:
                        project_report["apply"] = {"attempted": True, "ok": False, "error": str(e)}
            else:
                if project_report is not None:
                    project_report["apply"] = {"attempted": False}
        except Exception as e:
            if not json_output:
                table.add_row("project", "❌ " + t("error"), str(e))
            project_report = {"path": project_path, "error": str(e)}

    if json_output:
        report = {
            "system": {
                "python": {"version": py_version, "ok": is_py_ok},
                "os": {"name": os_name, "ok": is_os_ok},
                "memory": {"available_bytes": mem.available, "ok": mem_ok},
                "disk": {"free_bytes": usage.free, "ok": disk_ok},
                "adapter": {"name": adapter_name, "ok": adapter_ok},
            },
            "project": project_report,
            "ready": bool(is_py_ok and is_os_ok),
        }
        print(json.dumps(report, indent=2))
        return bool(is_py_ok and is_os_ok)

    console.print(table)

    if is_py_ok and is_os_ok:
        console.print("\n[bold green]✅ " + t("ready") + " ![/bold green]")
        return True
    console.print("\n[bold red]❌ " + t("attention") + ".[/bold red]")
    return False


if __name__ == "__main__":
    run_doctor()
