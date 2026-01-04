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

console = Console()

def run_doctor():
    console.print("[bold blue]🩺 LexWorksEverywhere Doctor - Diagnostic du système[/bold blue]\n")
    
    table = Table(title="Vérifications de l'environnement")
    table.add_column("Composant", style="cyan")
    table.add_column("Statut", style="magenta")
    table.add_column("Détails", style="green")

    # 1. Version Python
    py_version = platform.python_version()
    is_py_ok = sys.version_info >= (3, 9)
    table.add_row("Version Python", "✅ OK" if is_py_ok else "❌ Erreur", py_version)

    # 2. OS Support
    os_name = platform.system()
    is_os_ok = os_name in ["Darwin", "Linux", "Windows"]
    table.add_row("Système d'exploitation", "✅ OK" if is_os_ok else "⚠️ Warning", os_name)

    # 3. Mémoire disponible
    mem = psutil.virtual_memory()
    mem_ok = mem.available > (500 * 1024 * 1024) # 500MB min
    table.add_row("Mémoire disponible", "✅ OK" if mem_ok else "⚠️ Bas", f"{mem.available / (1024**3):.2f} GB")

    # 4. Espace disque
    usage = shutil.disk_usage("/")
    disk_ok = usage.free > (2 * 1024 * 1024 * 1024) # 2GB min
    table.add_row("Espace disque (/) ", "✅ OK" if disk_ok else "⚠️ Bas", f"{usage.free / (1024**3):.2f} GB libres")

    # 5. Connectivité Adaptateur
    try:
        adapter = AdapterFactory.detect()
        table.add_row("Adaptateur OS", "✅ OK", adapter.get_os_name())
    except Exception as e:
        table.add_row("Adaptateur OS", "❌ Échec", str(e))

    console.print(table)
    
    if is_py_ok and is_os_ok:
        console.print("\n[bold green]✅ Votre système est prêt pour LexWorksEverywhere ![/bold green]")
        return True
    else:
        console.print("\n[bold red]❌ Certains composants critiques nécessitent votre attention.[/bold red]")
        return False

if __name__ == "__main__":
    run_doctor()
