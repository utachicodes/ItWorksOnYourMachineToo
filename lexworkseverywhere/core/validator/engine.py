# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Environment Validator - Moteur de validation/diagnostic
=============================================================

Ce module analyse les échecs via l'adaptateur OS injecté.
Il propose des corrections basées sur des contrats d'exécution.

Projet développé par : Alexandre Albert Ndour
"""

import re
from typing import Dict, List, Any, Optional
from ..contracts.adapter import OSAdapter


class EnvironmentValidator:
    """
    Analyzes execution failures and suggests fixes via OSAdapter.
    """
    
    def __init__(self, adapter: OSAdapter):
        self.adapter = adapter
        self.common_patterns = [
            {
                "pattern": r"command '(.+)' not found|(.+): command not found|not recognized",
                "category": "missing_runtime",
                "recommendation": (
                    "📦 Install the missing runtime. Tip: Use 'lexworks install-runtime <name>' "
                    "or check the docs."
                ),
            },
            {
                "pattern": r"No module named '(.+)'|ModuleNotFoundError",
                "category": "missing_python_package",
                "recommendation": (
                    "🐍 Python package missing. Ensure requirements.txt is up to date and run "
                    "'pip install -r requirements.txt'."
                ),
            },
            {
                "pattern": r"Permission denied|EACCES",
                "category": "permission_error",
                "recommendation": (
                    "🔐 Permission denied. Check folder permissions or run with elevated privileges if safe."
                ),
            },
        ]

    def validate_failure(self, stderr: str) -> Dict[str, Any]:
        """Analyse le stderr pour identifier le type d'échec."""
        results = {"detected_issues": [], "is_fixable": False}
        
        for p in self.common_patterns:
            match = re.search(p["pattern"], stderr, re.IGNORECASE)
            if match:
                results["detected_issues"].append({
                    "category": p["category"],
                    "recommendation": p["recommendation"],
                    "context": match.group(0)
                })
                results["is_fixable"] = True
                
        return results

    def propose_fix(self, issue: Dict[str, Any]) -> Optional[List[str]]:
        """Propose une commande de correction basée sur l'OS actuel."""
        if issue["category"] == "missing_python_package":
            # Extraire le nom du package du contexte si possible
            match = re.search(r"module named '(.+)'", issue.get("context", ""))
            pkg_name = match.group(1) if match else "module_name"
            return ["pip", "install", pkg_name]
        return None
