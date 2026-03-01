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
    """Analyzes execution failures and suggests fixes via OSAdapter."""

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
                "pattern": (
                    r"npm: command not found|yarn: command not found|"
                    r"pnpm: command not found|node: command not found"
                ),
                "category": "missing_runtime",
                "recommendation": "📦 Node.js tooling missing. Install Node.js (corepack enables yarn/pnpm).",
            },
            {
                "pattern": r"cargo: command not found|rustc: command not found",
                "category": "missing_runtime",
                "recommendation": "🦀 Rust toolchain missing. Install rustup/cargo.",
            },
            {
                "pattern": r"go: command not found",
                "category": "missing_runtime",
                "recommendation": "🐹 Go toolchain missing. Install Go.",
            },
            {
                "pattern": r"mvn: command not found|gradle: command not found",
                "category": "missing_runtime",
                "recommendation": "☕ Java build tool missing. Install Maven/Gradle.",
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
                "pattern": (
                    r"Cannot find module '(.+)'|ERR_MODULE_NOT_FOUND|"
                    r"Error: Cannot find package '(.+)'"
                ),
                "category": "missing_node_package",
                "recommendation": "📦 JavaScript package missing. Run your package manager install.",
            },
            {
                "pattern": r"TS2307: Cannot find module '(.+)'",
                "category": "missing_ts_package",
                "recommendation": "📦 TypeScript types or package missing. Install corresponding @types or package.",
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
        if issue["category"] in ("missing_node_package", "missing_ts_package"):
            # Par défaut, tenter une installation des dépendances
            return ["npm", "install"]
        return None
