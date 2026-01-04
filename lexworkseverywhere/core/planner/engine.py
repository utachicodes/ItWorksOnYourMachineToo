# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Project Planner - Moteur de planification
==============================================

Ce module analyse un projet logiciel en utilisant l'adaptateur OS injecté.
Il est totalement agnostique vis-à-vis du système d'exploitation.

Projet développé par : Alexandre Albert Ndour
"""

from typing import Dict, List, Optional, Any
import json
import yaml
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
            'flutter': ['pubspec.yaml', 'dart-tool'],
            'react-native': ['app.json', 'metro.config.js'],
            'android': ['build.gradle', 'settings.gradle', 'build.gradle.kts', 'AndroidManifest.xml'],
            'ios': ['Podfile', 'project.pbxproj', 'Info.plist', 'Runner.xcworkspace'],
            
            # Backend & Web Frameworks
            'laravel': ['artisan', 'composer.json'],
            'django': ['manage.py', 'wsgi.py', 'asgi.py'],
            'rails': ['Gemfile', 'config/application.rb', 'bin/rails', 'Rakefile'],
            'symfony': ['symfony.lock', 'bin/console'],
            'dotnet': ['.sln', '.csproj', '.fsproj'],
            
            # Languages
            'python': ['.py', 'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'nodejs': ['package.json', 'yarn.lock', 'pnpm-lock.yaml', 'bun.lockb', 'bun.lock', '.js', '.ts'],
            'php': ['.php', 'composer.json', 'composer.lock'],
            'java': ['.java', 'pom.xml', 'build.gradle', 'gradlew'],
            'kotlin': ['.kt', '.kts'],
            'swift': ['.swift', 'Package.swift'],
            'go': ['.go', 'go.mod', 'go.sum'],
            'rust': ['.rs', 'Cargo.toml', 'Cargo.lock'],
            'ruby': ['.rb', 'Gemfile', 'Gemfile.lock', 'Rakefile'],
            'cpp': ['.cpp', '.hpp', '.cxx', 'CMakeLists.txt', 'conanfile.txt'],
            'c': ['.c', '.h', 'configure.ac'],
            'dart': ['.dart', 'pubspec.yaml'],
            'elixir': ['.ex', '.exs', 'mix.exs'],
            'haskell': ['.hs', 'stack.yaml', 'package.yaml'],
            'scala': ['.scala', 'build.sbt'],
            'perl': ['.pl', '.pm', 'Makefile.PL'],
            'lua': ['.lua'],
            'clojure': ['.clj', 'project.clj'],
            'zig': ['.zig', 'build.zig'],
            'nim': ['.nim', '.nimble'],
            
            # DevOps & Config
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'shell': ['.sh', '.bash', '.zsh'],
            'kubernetes': ['k8s', 'chart.yaml', 'values.yaml'],
            'terraform': ['.tf', '.tfvars'],
            'ansible': ['playbook.yml', 'ansible.cfg'],
        }
        self._cache = {} # Simple memory cache

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
            "requirements": self._extract_requirements(normalized_path, project_type)
        }
        
        # Store in cache
        self._cache[normalized_path] = (project_hash, plan)
        return plan

    def _detect_project_type(self, project_path: str) -> str:
        """Détecte le type de projet via l'interface FS."""
        # On vérifie à la racine et dans src/
        check_dirs = ["", "src"]
        
        for p_type, indicators in self.project_types.items():
            for d in check_dirs:
                test_dir = f"{project_path}/{d}".rstrip("/")
                if not self.adapter.fs.exists(test_dir) or not self.adapter.fs.is_dir(test_dir):
                    continue

                files = self.adapter.fs.list_dir(test_dir)
                for indicator in indicators:
                    if indicator.startswith("."):
                        # Recherche d'extension
                        if any(f.endswith(indicator) for f in files):
                            return p_type
                    else:
                        # Fichier exact
                        # Filename check (clean names from path if necessary)
                        filenames = [f.split("/")[-1].split("\\")[-1] for f in files]
                        if indicator in filenames:
                            return p_type
        return "unknown"

    def _apply_heuristics(self, project_path: str) -> str:
        """Applique des heuristiques pour deviner le type de projet si inconnu."""
        # 1. Shebang Detection
        # Check for a main/entry file if possible, or scan first few files
        entry_candidates = ["main.py", "index.js", "app.py", "script.sh"]
        for cand in entry_candidates:
            p = f"{project_path}/{cand}"
            if self.adapter.fs.exists(p):
                content = self.adapter.fs.read_text(p)
                if content.startswith("#!"):
                    first_line = content.splitlines()[0]
                    if "python" in first_line: return "python"
                    if "node" in first_line: return "nodejs"
                    if "ruby" in first_line: return "ruby"
                    if "perl" in first_line: return "perl"
                    if "bash" in first_line or "sh" in first_line: return "shell"

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
        requirements = {"runtime": project_type, "packages": []}
        
        # Specialized runtimes
        if project_type == "nodejs":
            if self.adapter.fs.exists(f"{project_path}/bun.lock") or self.adapter.fs.exists(f"{project_path}/bun.lockb"):
                requirements["runtime"] = "bun"
            elif self.adapter.fs.exists(f"{project_path}/yarn.lock"):
                requirements["runtime"] = "nodejs" # Default but explicit
        elif project_type == "laravel":
            requirements["runtime"] = "php"
        elif project_type == "django":
            requirements["runtime"] = "python"
        elif project_type == "rails":
            requirements["runtime"] = "ruby"
        elif project_type == "flutter":
            requirements["runtime"] = "dart"

        # Python specific
        if project_type == "python" or project_type == "django":
            req_file = f"{project_path}/requirements.txt"
            if self.adapter.fs.exists(req_file):
                content = self.adapter.fs.read_text(req_file)
                requirements["packages"] = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith('#')]
        
        # Node.js specific
        elif project_type == "nodejs":
            pkg_file = f"{project_path}/package.json"
            if self.adapter.fs.exists(pkg_file):
                try:
                    import json
                    data = json.loads(self.adapter.fs.read_text(pkg_file))
                    requirements["packages"] = list(data.get("dependencies", {}).keys())
                except:
                    pass
                    
        return requirements
