# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Environment Profiler - Profileur d'environnement
==================================================

Ce module capture des informations sur l'environnement via l'adaptateur OS.
Il prépare un profil portable (JSON) du système.

Projet développé par : Alexandre Albert Ndour
"""

from typing import Dict, Any
from .contracts.adapter import OSAdapter
import os
import hashlib


class EnvironmentProfiler:
    """
    Groups environment metrics captured via an OSAdapter.
    """
    
    def __init__(self, adapter: OSAdapter):
        self.adapter = adapter
    
    def capture_profile(self) -> Dict[str, Any]:
        """
        Capture un profil complet via l'adaptateur.
        """
        env_vars = self._get_safe_env_vars()
        runtimes = self._detect_runtimes()
        os_name = self.adapter.get_os_name()
        return {"os": os_name, "env_vars": env_vars, "runtimes": runtimes, "portable_hash": self._generate_portable_hash(os_name, env_vars, runtimes)}

    def _get_safe_env_vars(self) -> Dict[str, str]:
        filtered = {}
        for k, v in os.environ.items():
            key = k.upper()
            if any(s in key for s in ["SECRET", "TOKEN", "PASSWORD", "KEY", "AUTH", "COOKIE"]):
                continue
            filtered[k] = v
        return {"PATH": filtered.get("PATH", "")}

    def _detect_runtimes(self) -> Dict[str, str]:
        candidates = {
            "python": [["python3", "--version"], ["python", "--version"]],
            "node": [["node", "--version"]],
            "npm": [["npm", "--version"]],
            "go": [["go", "version"]],
            "cargo": [["cargo", "--version"]],
            "php": [["php", "--version"]],
            "composer": [["composer", "--version"]],
            "ruby": [["ruby", "--version"]],
            "java": [["java", "-version"]],
            "dotnet": [["dotnet", "--version"]],
        }
        result = {}
        for name, cmds in candidates.items():
            ver = None
            for cmd in cmds:
                try:
                    cp = self.adapter.process.run(cmd, timeout=5)
                    out = (cp.stdout or "") + (cp.stderr or "")
                    digits = ""
                    for ch in out:
                        if ch.isdigit() or ch in ".-v":
                            digits += ch
                    ver = digits.strip().lstrip("v") if digits else out.strip()
                    if ver:
                        break
                except Exception:
                    continue
            if ver:
                result[name] = ver
        return result

    def _generate_portable_hash(self, os_name: str, env: Dict[str, str], rt: Dict[str, str]) -> str:
        data = os_name + "|" + env.get("PATH", "") + "|" + "|".join(f"{k}:{v}" for k, v in sorted(rt.items()))
        return "sha256:" + hashlib.sha256(data.encode()).hexdigest()
