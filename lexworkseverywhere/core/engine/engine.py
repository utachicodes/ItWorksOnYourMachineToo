# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Execution Engine - Moteur d'exécution
==========================================

Ce module gère l'orchestration de l'exécution en utilisant l'adaptateur OS.
Il n'a aucune dépendance directe vers 'os', 'sys' ou 'subprocess'.

Projet développé par : Alexandre Albert Ndour
"""

from typing import Dict, List, Any, Optional
from ..contracts.adapter import OSAdapter


class ExecutionEngine:
    """
    Orchestrates project execution via a strict OS contract.
    """
    
    def __init__(self, adapter: OSAdapter):
        self.adapter = adapter
        self.environment_stack = []

    def check_system_requirements(self, project_type: str) -> bool:
        """Vérifie que les outils système nécessaires sont installés."""
        req_map = {
            "python": ["python3", "pip"],
            "nodejs": ["node", "npm"],
            "bun": ["bun"],
            "go": ["go"],
            "rust": ["cargo"],
            "php": ["php", "composer"],
            "ruby": ["ruby", "gem"],
            "java": ["java"],
            "kotlin": ["kotlinc"],
            "swift": ["swift"],
            "dart": ["dart"],
            "flutter": ["flutter"],
            "laravel": ["php", "composer"],
            "django": ["python3", "pip"],
            "rails": ["ruby", "gem", "bundle"],
            "dotnet": ["dotnet"],
            "elixir": ["elixir", "mix"],
            "scala": ["scala", "sbt"],
            "clojure": ["clojure", "lein"],
            "haskell": ["ghc", "stack"],
            "cpp": ["g++", "cmake"],
            "c": ["gcc", "make"],
            "zig": ["zig"],
            "nim": ["nim"],
            "docker": ["docker"],
            "kubernetes": ["kubectl", "helm"],
            "terraform": ["terraform"],
            "ansible": ["ansible-playbook"],
            "generic-make": ["make"],
            "generic-cmake": ["cmake", "make"]
        }
        
        needed = req_map.get(project_type, [])
        for binary in needed:
            if not self.adapter.process.has_binary(binary):
                suggestion = self.adapter.get_install_suggestion(binary)
                from rich.console import Console
                from rich.panel import Panel
                console = Console()
                console.print(Panel(
                    f"[bold red]ERREUR :[/bold red] L'outil '[bold]{binary}[/bold]' est manquant pour ce projet.\n\n{suggestion}",
                    title="Résolution d'Environnement 🇸🇳",
                    border_style="red"
                ))
                return False
        return True

    def prepare(self, plan: Dict[str, Any]) -> bool:
        """Prépare l'environnement via l'adaptateur."""
        try:
            project_type = plan.get("project_type")
            p_path = plan.get("project_path")

            # 0. Vérification proactive des outils système
            runtime = plan.get("requirements", {}).get("runtime", project_type)
            
            if not self.check_system_requirements(runtime):
                return False

            # Capture de l'état actuel (via l'adapter si nécessaire, ou géré ici)
            # Pour simplifier, on stocke les env vars actuelles
            self.environment_stack.append({"env": {}}) # Placeholder
            
            # Installation des dépendances via l'interface process de l'adapter
            project_type = plan.get("project_type")
            p_path = plan.get("project_path")
            
            if (project_type == "python" or project_type == "django") and self.adapter.fs.exists(f"{p_path}/requirements.txt"):
                self.adapter.process.run(["pip", "install", "-r", "requirements.txt"], cwd=p_path)
            elif project_type == "nodejs":
                if self.adapter.fs.exists(f"{p_path}/yarn.lock"):
                    self.adapter.process.run(["yarn", "install"], cwd=p_path)
                elif self.adapter.fs.exists(f"{p_path}/pnpm-lock.yaml"):
                    self.adapter.process.run(["pnpm", "install"], cwd=p_path)
                elif self.adapter.fs.exists(f"{p_path}/bun.lockb") or self.adapter.fs.exists(f"{p_path}/bun.lock"):
                    self.adapter.process.run(["bun", "install"], cwd=p_path)
                elif self.adapter.fs.exists(f"{p_path}/package.json"):
                    self.adapter.process.run(["npm", "install"], cwd=p_path)
            elif (project_type == "php" or project_type == "laravel") and self.adapter.fs.exists(f"{p_path}/composer.json"):
                self.adapter.process.run(["composer", "install"], cwd=p_path)
            elif project_type == "go" and self.adapter.fs.exists(f"{p_path}/go.mod"):
                self.adapter.process.run(["go", "mod", "download"], cwd=p_path)
            elif project_type == "rust" and self.adapter.fs.exists(f"{p_path}/Cargo.toml"):
                self.adapter.process.run(["cargo", "build"], cwd=p_path)
            elif project_type == "rails" and self.adapter.fs.exists(f"{p_path}/Gemfile"):
                self.adapter.process.run(["bundle", "install"], cwd=p_path)
            
            return True
        except Exception as e:
            self.rollback()
            return False

    def execute(self, plan: Dict[str, Any], args: List[str] = None) -> Dict[str, Any]:
        """Exécute le projet dans le bac à sable de l'adaptateur."""
        import time
        if args is None:
            args = []
            
        cmd = self._build_command(plan, args)
        
        # Telemetry Start
        start_time = time.perf_counter()
        print(f"METRIC: Starting execution for {plan.get('project_path')}")

        # Determine sandbox policy
        policy = "default"
        if plan.get("project_type") == "docker":
            policy = "limited" # More permissive for container socket access if needed
        elif plan.get("project_type") in ["shell", "generic-make"]:
            policy = "strict" # Scripts are high risk

        # Entrée dans le sandbox avec politique calculée
        self.adapter.sandbox.enter(policy, {"path": plan.get("project_path")})
        
        try:
            result = self.adapter.process.run(cmd, cwd=plan.get("project_path"))
            
            # Telemetry Success
            duration = time.perf_counter() - start_time
            print(f"METRIC: Execution successful in {duration:.4f}s")
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration
            }
        except Exception as e:
            # Telemetry Error
            print(f"EVENT: Execution error: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            self.adapter.sandbox.exit()

    def _build_command(self, plan: Dict[str, Any], args: List[str]) -> List[str]:
        p_type = plan.get("project_type")
        p_path = plan.get("project_path")
        
        # Helper to find first file with extension
        def find_ext(ext):
            try:
                files = self.adapter.fs.list_dir(p_path)
                for f in files:
                    if f.endswith(ext): return f
            except: pass
            return None

        if p_type == "django":
            return ["python3", "manage.py", "runserver"] + args
        elif p_type == "laravel":
            return ["php", "artisan", "serve"] + args
        elif p_type == "rails":
            return ["bundle", "exec", "rails", "server"] + args
        elif p_type == "flutter":
            return ["flutter", "run"] + args
        elif p_type == "dotnet":
            return ["dotnet", "run"] + args
        elif p_type == "python":
            entry = "main.py"
            if not self.adapter.fs.exists(f"{p_path}/{entry}"):
                entry = find_ext(".py") or entry
            return ["python3", entry] + args
            
        elif p_type == "nodejs":
            # server.js est très commun pour les apps backend
            entry = "server.js"
            if not self.adapter.fs.exists(f"{p_path}/{entry}"):
                entry = "index.js"
            if not self.adapter.fs.exists(f"{p_path}/{entry}"):
                entry = find_ext(".js") or entry
            return ["node", entry] + args
            
        elif p_type == "go":
            return ["go", "run", "."] + args
        elif p_type == "rust":
            return ["cargo", "run"] + args
        elif p_type == "generic-make":
            return ["make", "run"] + args
        elif p_type == "php":
            entry = "index.php"
            if not self.adapter.fs.exists(f"{p_path}/{entry}"):
                entry = find_ext(".php") or entry
            return ["php", entry] + args
        elif p_type == "ruby":
            entry = "main.rb"
            if not self.adapter.fs.exists(f"{p_path}/{entry}"):
                entry = find_ext(".rb") or entry
            return ["ruby", entry] + args
        elif p_type == "dart":
            return ["dart", "run"] + args
            
        return ["echo", f"Project type '{p_type}' detected but no default run command defined."] + args

    def rollback(self):
        """Restaure l'état via l'adaptateur."""
        if self.environment_stack:
            self.environment_stack.pop()
