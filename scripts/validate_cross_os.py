# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Cross-OS Validation Utility - Validation multi-plateforme
==============================================================

Ce script vérifie que le 'Core' produit des résultats identiques peu importe
l'adaptateur OS utilisé (mocké).

Projet développé par : Abdoullah Ndao
"""

import sys
from unittest.mock import MagicMock
from ItWorksOnYourMachineToo.core.planner.engine import ProjectPlanner
from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter

def run_validation():
    print("🚀 Démarrage de la validation Cross-OS...")
    
    # Mocking adapters
    mock_macos = MagicMock(spec=OSAdapter)
    mock_macos.get_os_name.return_value = "macos"
    mock_macos.normalize_path.side_effect = lambda x: x
    mock_macos.fs.exists.return_value = True
    mock_macos.fs.read_text.return_value = "requests==2.31.0\nflask==3.0.0"
    
    mock_win = MagicMock(spec=OSAdapter)
    mock_win.get_os_name.return_value = "windows"
    mock_win.normalize_path.side_effect = lambda x: x.replace("/", "\\")
    mock_win.fs.exists.return_value = True
    mock_win.fs.read_text.return_value = "requests==2.31.0\nflask==3.0.0"

    # Planning with MacOS Adapter
    planner_mac = ProjectPlanner(mock_macos)
    plan_mac = planner_mac.plan_project("/test/project")
    
    # Planning with Windows Adapter
    planner_win = ProjectPlanner(mock_win)
    plan_win = planner_win.plan_project("/test/project")
    
    # Compare core parts of the plan
    print(f"Plan MacOS: {plan_mac['requirements']}")
    print(f"Plan Windows: {plan_win['requirements']}")
    
    assert plan_mac["requirements"] == plan_win["requirements"]
    assert plan_mac["project_type"] == plan_win["project_type"]
    
    print("✅ Validation Cross-OS réussie : Le Core est agnostique au système !")

if __name__ == "__main__":
    try:
        run_validation()
    except Exception as e:
        print(f"❌ Échec de la validation : {e}")
        sys.exit(1)
