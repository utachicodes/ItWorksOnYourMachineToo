# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Project Planner - Moteur de planification
==============================================

Ce module analyse un projet logiciel en utilisant l'adaptateur OS injecté.
Il est totalement agnostique vis-à-vis du système d'exploitation.

Projet développé par : Alexandre Albert Ndour
"""

from typing import Dict, Any
import json
from ..contracts.adapter import OSAdapter


class ProjectPlanner:
    """
    Analyses a project directory using an injected OS adapter.
    Identifies project type, dependencies, and execution plan.
    """

    def __init__(self, adapter: OSAdapter):
        self.adapter = adapter
        self.project_types = {
            # Mobile & Cross-platform
            "flutter": ["pubspec.yaml", "dart-tool"],
            "react-native": ["app.json", "metro.config.js"],
            "android": ["build.gradle", "settings.gradle", "build.gradle.kts", "AndroidManifest.xml"],
            "ios": ["Podfile", "project.pbxproj", "Info.plist", "Runner.xcworkspace"],
            # Backend & Web Frameworks
            "laravel": ["artisan"],
            "django": ["manage.py", "wsgi.py", "asgi.py"],
            "rails": ["config/application.rb", "bin/rails", "Rakefile"],
            "symfony": ["symfony.lock", "bin/console"],
            "dotnet": [".sln", ".csproj", ".fsproj"],
            # Languages
            "python": [".py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "nodejs": ["package.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock", ".js", ".ts"],
            "php": [".php", "composer.json", "composer.lock"],
            "java": [".java", "pom.xml", "build.gradle", "gradlew"],
            "kotlin": [".kt", ".kts"],
            "swift": [".swift", "Package.swift"],
            "go": [".go", "go.mod", "go.sum"],
            "rust": [".rs", "Cargo.toml", "Cargo.lock"],
            "ruby": [".rb", "Gemfile", "Gemfile.lock", "Rakefile"],
            "cpp": [".cpp", ".hpp", ".cxx", "CMakeLists.txt", "conanfile.txt"],
            "c": [".c", ".h", "configure.ac"],
            "dart": [".dart", "pubspec.yaml"],
            "elixir": [".ex", ".exs", "mix.exs"],
            "haskell": [".hs", "stack.yaml", "package.yaml"],
            "scala": [".scala", "build.sbt"],
            "perl": [".pl", ".pm", "Makefile.PL"],
            "lua": [".lua"],
            "clojure": [".clj", "project.clj"],
            "zig": [".zig", "build.zig"],
            "nim": [".nim", ".nimble"],
            # DevOps & Config
            "docker": ["Dockerfile", "docker-compose.yml"],
            "shell": [".sh", ".bash", ".zsh"],
            "kubernetes": ["k8s", "chart.yaml", "values.yaml"],
            "terraform": [".tf", ".tfvars"],
            "ansible": ["playbook.yml", "ansible.cfg"],
        }
        self._cache = {}  # Simple memory cache

    def _calculate_project_hash(self, project_path: str) -> str:
        """Calcule un hash basé sur les fichiers clés du projet pour l'invalidation du cache."""
        import hashlib

        key_files = ["requirements.txt", "package.json", "go.mod", "pyproject.toml", "composer.json", "Cargo.toml"]
        combined_content = ""
        for kb in key_files:
            p = f"{project_path}/{kb}"
            if self.adapter.fs.exists(p):
                combined_content += self.adapter.fs.read_text(p)
        return hashlib.sha256(combined_content.encode()).hexdigest()

    def plan_project(self, project_path: str) -> Dict[str, Any]:
        """
        Scans building a plan for the project using the adapter's abstract FS.
        """
        normalized_path = self.adapter.normalize_path(project_path)
        if not self.adapter.fs.exists(normalized_path):
            raise ValueError(f"Project path does not exist: {normalized_path}")

        # Cache lookup
        project_hash = self._calculate_project_hash(normalized_path)
        if normalized_path in self._cache:
            cached_hash, cached_plan = self._cache[normalized_path]
            if cached_hash == project_hash:
                return cached_plan

        project_type = self._detect_project_type(normalized_path)

        # Heuristic fallback for unknown types
        if project_type == "unknown":
            project_type = self._apply_heuristics(normalized_path)

        plan = {
            "project_path": normalized_path,
            "project_type": project_type,
            "os_origin": self.adapter.get_os_name(),
            "is_portable": True,
            "requirements": self._extract_requirements(normalized_path, project_type),
        }

        # Store in cache
        self._cache[normalized_path] = (project_hash, plan)
        return plan

    def _detect_project_type(self, project_path: str) -> str:
        """Détecte le type de projet via l'interface FS (récursif limité + pondération)."""
        check_dirs = ["", "src", "app", "backend", "frontend", "server", "packages", "services"]
        ignore_dirs = {".git", "node_modules", "dist", "build", "target", "venv", ".venv", "__pycache__"}

        manifest_names = {
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "go.mod",
            "Cargo.toml",
            "composer.json",
            "Gemfile",
            "pom.xml",
            "build.gradle",
        }
        lock_names = {
            "yarn.lock",
            "pnpm-lock.yaml",
            "bun.lock",
            "bun.lockb",
            "Cargo.lock",
            "go.sum",
            "composer.lock",
        }

        def score_indicator(name: str) -> int:
            if name in manifest_names:
                return 3
            if name in lock_names:
                return 2
            if name.startswith("."):
                return 1
            return 1

        def has_indicator(path: str, indicator: str, depth: int) -> int:
            try:
                entries = self.adapter.fs.list_dir(path)
            except Exception:
                entries = []
            # File check in current directory
            if indicator.startswith("."):
                if any(e.endswith(indicator) for e in entries):
                    return score_indicator(indicator)
            else:
                # Prefer direct existence check for manifest-style indicators
                try:
                    if self.adapter.fs.exists(f"{path}/{indicator}"):
                        return score_indicator(indicator)
                except Exception:
                    pass
                if indicator in entries:
                    return score_indicator(indicator)
            # Recurse limited depth
            if depth <= 0:
                return 0
            s = 0
            for e in entries:
                sub = f"{path}/{e}"
                try:
                    if e in ignore_dirs:
                        continue
                    if self.adapter.fs.is_dir(sub):
                        s = max(s, has_indicator(sub, indicator, depth - 1))
                        if s >= 3:
                            return s
                except Exception:
                    continue
            return s

        best_type = "unknown"
        best_score = 0
        for p_type, indicators in self.project_types.items():
            type_score = 0
            for d in check_dirs:
                test_dir = f"{project_path}/{d}".rstrip("/")
                if not self.adapter.fs.exists(test_dir) or not self.adapter.fs.is_dir(test_dir):
                    continue
                for indicator in indicators:
                    type_score = max(type_score, has_indicator(test_dir, indicator, depth=2))
                    if type_score >= 3:
                        break
                if type_score >= 3:
                    break
            if type_score > best_score:
                best_score = type_score
                best_type = p_type
        return best_type

    def _apply_heuristics(self, project_path: str) -> str:
        """Applique des heuristiques pour deviner le type de projet si inconnu."""
        entry_candidates = ["main.py", "index.js", "app.py", "script.sh"]
        for cand in entry_candidates:
            p = f"{project_path}/{cand}"
            if self.adapter.fs.exists(p):
                content = self.adapter.fs.read_text(p)
                if content.startswith("#!"):
                    first_line = content.splitlines()[0]
                    if "python" in first_line:
                        return "python"
                    if "node" in first_line:
                        return "nodejs"
                    if "ruby" in first_line:
                        return "ruby"
                    if "perl" in first_line:
                        return "perl"
                    if "bash" in first_line or "sh" in first_line:
                        return "shell"

        # 2. Folder-based heuristics
        if self.adapter.fs.exists(f"{project_path}/src") and self.adapter.fs.exists(f"{project_path}/include"):
            return "cpp"
        if self.adapter.fs.exists(f"{project_path}/Makefile"):
            return "generic-make"
        if self.adapter.fs.exists(f"{project_path}/CMakeLists.txt"):
            return "generic-cmake"

        return "unknown"

    def _extract_requirements(self, project_path: str, project_type: str) -> Dict[str, Any]:
        """Extrait les besoins du projet sans accès système direct."""
        requirements = {"runtime": project_type, "packages": [], "engines": {}}

        # Specialized runtimes
        if project_type == "nodejs":
            if (
                self.adapter.fs.exists(f"{project_path}/bun.lock")
                or self.adapter.fs.exists(f"{project_path}/bun.lockb")
            ):
                requirements["runtime"] = "bun"
            elif self.adapter.fs.exists(f"{project_path}/yarn.lock"):
                requirements["runtime"] = "nodejs"  # Default but explicit
        elif project_type == "laravel":
            requirements["runtime"] = "php"
        elif project_type == "django":
            requirements["runtime"] = "python"
        elif project_type == "rails":
            requirements["runtime"] = "ruby"
        elif project_type == "flutter":
            requirements["runtime"] = "dart"

        # Python specific
        if project_type in ("python", "django"):
            req_file = f"{project_path}/requirements.txt"
            if self.adapter.fs.exists(req_file):
                content = self.adapter.fs.read_text(req_file)
                requirements["packages"] = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith("#")
                ]

        # Node.js specific
        elif project_type == "nodejs":
            pkg_file = f"{project_path}/package.json"
            if self.adapter.fs.exists(pkg_file):
                try:
                    data = json.loads(self.adapter.fs.read_text(pkg_file))
                    requirements["packages"] = list(data.get("dependencies", {}).keys())
                    eng = data.get("engines", {})
                    if isinstance(eng, dict):
                        for k, v in eng.items():
                            requirements["engines"][k] = v
                except Exception:
                    pass

        pyproj = f"{project_path}/pyproject.toml"
        if self.adapter.fs.exists(pyproj):
            try:
                import toml as _toml

                data = _toml.loads(self.adapter.fs.read_text(pyproj))
                req_py = (
                    data.get("project", {}).get("requires-python")
                    or data.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python")
                )
                if req_py:
                    requirements["engines"]["python"] = req_py
            except Exception:
                pass

        return requirements
