# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Dependency Manager - Gestionnaire de dépendances
====================================================

Ce module gère les dépendances des projets avec isolation et résolution de conflits :
- Gestion des environnements virtuels
- Isolation des dépendances par projet
- Résolution des conflits de dépendances
- Installation sécurisée des dépendances

Projet développé par : Alexandre Albert Ndour
Date de naissance : 29 janvier 2005
Nationalité : Sénégalaise
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple
import venv
import json
from ..core.utils.logging_utils import (
    get_logger,
    log_operation,
    log_error,
    start_timer,
    stop_timer,
)
from ..core.utils.security_utils import (
    execute_secure_command,
    validate_and_sanitize_path,
)


class DependencyManager:
    """Gestionnaire de dépendances pour LexWorksEverywhere avec isolation et résolution de conflits."""

    def __init__(self, project_path: str):
        """Initialise le gestionnaire de dépendances."""
        self.project_path = validate_and_sanitize_path(project_path)
        self.logger = get_logger()
        self.venv_path = Path(self.project_path) / ".lexworkseverywhere" / "venv"
        self.deps_cache_path = Path(self.project_path) / ".lexworkseverywhere" / "deps_cache.json"

    def create_isolated_environment(self) -> bool:
        """Crée un environnement isolé pour le projet."""
        start_timer("create_isolated_environment")

        try:
            self.logger.info(f"Création d'un environnement isolé pour: {self.project_path}")
            # Créer le répertoire .lexworkseverywhere s'il n'existe pas
            lexworkseverywhere_dir = Path(self.project_path) / ".lexworkseverywhere"
            lexworkseverywhere_dir.mkdir(parents=True, exist_ok=True)
            # Créer l'environnement virtuel
            venv.create(self.venv_path, with_pip=True)
            # Installer les outils de base
            pip_path = self.get_pip_path()
            if pip_path:
                # Mettre à jour pip
                result = execute_secure_command(
                    [pip_path, "install", "--upgrade", "pip"],
                    cwd=self.project_path,
                    timeout=300,
                )
                if result.returncode != 0:
                    self.logger.error(f"Échec de la mise à jour de pip: {result.stderr}")
                    return False
            elapsed = stop_timer("create_isolated_environment")
            self.logger.info(f"Environnement isolé créé en {elapsed:.2f} secondes")
            log_operation("create_isolated_environment", {
                "project_path": self.project_path,
                "venv_path": str(self.venv_path),
                "elapsed_time": elapsed
            })
            return True
        except Exception as e:
            elapsed = stop_timer("create_isolated_environment")
            self.logger.error(f"Erreur lors de la création de l'environnement isolé: {e}")
            log_error("create_isolated_environment", e, {
                "project_path": self.project_path,
                "elapsed_time": elapsed
            })
            return False

    def get_python_path(self) -> Optional[str]:
        """
        Retourne le chemin de l'interpréteur Python de l'environnement isolé.

        Returns:
            Chemin de Python ou None si non disponible
        """
        if self.venv_path.exists():
            if sys.platform == "win32":
                return str(self.venv_path / "Scripts" / "python.exe")
            else:
                return str(self.venv_path / "bin" / "python")
        return sys.executable

    def get_pip_path(self) -> Optional[str]:
        """Retourne le chemin de pip de l'environnement isolé."""
        if self.venv_path.exists():
            if sys.platform == "win32":
                return str(self.venv_path / "Scripts" / "pip.exe")
            else:
                return str(self.venv_path / "bin" / "pip")
        return str(Path(sys.executable).parent / "pip") if hasattr(sys, "executable") else None

    def resolve_conflicts(self, dependencies: List[str]) -> Tuple[List[str], List[str]]:
        """Résout les conflits potentiels entre dépendances.

        Args:
            dependencies: Liste des dépendances à installer

        Returns:
            Tuple de (dépendances résolues, conflits détectés)
        """
        start_timer("resolve_conflicts")
        try:
            self.logger.info(
                f"Résolution des conflits pour {len(dependencies)} dépendances"
            )
            # Pour l'instant, une implémentation simple - dans une version complète,
            # on utiliserait des outils comme pip-tools ou poetry pour résoudre les conflits
            resolved_deps = []
            conflicts = []
            # Vérifier les conflits de version possibles
            dep_dict = {}
            for dep in dependencies:
                # Extraire le nom de la dépendance (simplifié)
                dep_name = (
                    dep.split("==")[0]
                    .split(">=")[0]
                    .split("<=")[0]
                    .split(">")[0]
                    .split("<")[0]
                    .split("!=")[0]
                )
                dep_name = dep_name.split("[")[0]
                if dep_name in dep_dict:
                    # Conflit détecté - même dépendance avec différentes versions
                    conflicts.append(f"Conflit pour {dep_name}: {dep_dict[dep_name]} vs {dep}")
                else:
                    dep_dict[dep_name] = dep
                    resolved_deps.append(dep)
            elapsed = stop_timer("resolve_conflicts")
            self.logger.info(f"Résolution des conflits terminée en {elapsed:.2f} secondes")
            log_operation("resolve_conflicts", {
                "dependencies_count": len(dependencies),
                "resolved_count": len(resolved_deps),
                "conflicts_count": len(conflicts),
                "elapsed_time": elapsed
            })
            return resolved_deps, conflicts
        except Exception as e:
            elapsed = stop_timer("resolve_conflicts")
            self.logger.error(f"Erreur lors de la résolution des conflits: {e}")
            log_error("resolve_conflicts", e, {
                "dependencies_count": len(dependencies),
                "elapsed_time": elapsed
            })
            return dependencies, [str(e)]

    def install_dependencies(self, dependencies: List[str], project_type: str = "python") -> bool:
        """Installe les dépendances dans l'environnement isolé."""
        start_timer("install_dependencies")
        try:
            self.logger.info(f"Installation de {len(dependencies)} dépendances pour le projet {project_type}")
            # Résoudre les conflits avant installation
            resolved_deps, conflicts = self.resolve_conflicts(dependencies)
            if conflicts:
                self.logger.warning(f"Conflits détectés: {conflicts}")
            if not resolved_deps:
                self.logger.info("Aucune dépendance à installer")
                return True
            # Installer selon le type de projet
            if project_type == "python":
                pip_path = self.get_pip_path()
                if not pip_path:
                    self.logger.error("pip non trouvé pour l'installation des dépendances Python")
                    return False
                # Utiliser l'environnement virtuel si disponible
                cmd = [pip_path, "install"] + resolved_deps
                result = execute_secure_command(
                    cmd, cwd=self.project_path, timeout=600
                )
                if result.returncode != 0:
                    self.logger.error(f"Échec de l'installation des dépendances Python: {result.stderr}")
                    return False
            elif project_type == "nodejs":
                # Pour Node.js, utiliser npm dans le répertoire du projet
                cmd = ["npm", "install"] + resolved_deps
                result = execute_secure_command(
                    cmd, cwd=self.project_path, timeout=600
                )
                if result.returncode != 0:
                    self.logger.error(f"Échec de l'installation des dépendances Node.js: {result.stderr}")
                    return False
            else:
                # Pour les autres types, on suppose que les dépendances sont gérées ailleurs
                self.logger.info(f"Type de projet {project_type} non pris en charge pour l'installation automatique")
                return True
            # Sauvegarder les dépendances installées dans le cache
            self._save_dependency_cache(resolved_deps)
            elapsed = stop_timer("install_dependencies")
            self.logger.info(f"Dépendances installées en {elapsed:.2f} secondes")
            log_operation("install_dependencies", {
                "project_type": project_type,
                "dependencies_count": len(resolved_deps),
                "elapsed_time": elapsed
            })
            return True
        except Exception as e:
            elapsed = stop_timer("install_dependencies")
            self.logger.error(f"Erreur lors de l'installation des dépendances: {e}")
            log_error("install_dependencies", e, {
                "project_type": project_type,
                "dependencies_count": len(dependencies),
                "elapsed_time": elapsed
            })
            return False

    def _save_dependency_cache(self, dependencies: List[str]):
        """Sauvegarde les dépendances installées dans un cache."""
        try:
            cache_data = {
                "dependencies": dependencies,
                "timestamp": str(Path(self.project_path).stat().st_mtime)
            }
            with open(self.deps_cache_path, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du cache de dépendances: {e}")

    def are_dependencies_installed(self, dependencies: List[str]) -> bool:
        """Vérifie si les dépendances sont installées dans l'environnement."""
        try:
            # Pour Python, vérifier avec pip list
            pip_path = self.get_pip_path()
            if pip_path and dependencies:
                result = execute_secure_command(
                    [pip_path, "list", "--format", "json"],
                    cwd=self.project_path,
                    timeout=30,
                )
                if result.returncode == 0:
                    try:
                        installed_packages = json.loads(result.stdout)
                        installed_names = {pkg["name"].lower() for pkg in installed_packages}
                        required_names = {
                            (
                                dep.split("==")[0]
                                .split(">=")[0]
                                .split("<=")[0]
                                .split(">")[0]
                                .split("<")[0]
                                .split("!=")[0]
                                .split("[")[0]
                                .lower()
                            )
                            for dep in dependencies
                        }
                        return required_names.issubset(installed_names)
                    except json.JSONDecodeError:
                        pass
            # Si on ne peut pas vérifier ou si ce n'est pas Python, supposer que non installé
            return False
        except Exception:
            return False

    def cleanup(self):
        """
        Nettoie les ressources temporaires du gestionnaire de dépendances.
        """
        try:
            # Ne pas supprimer l'environnement virtuel - c'est une optimisation
            # pour les exécutions suivantes, mais on pourrait ajouter une option
            pass
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du gestionnaire de dépendances: {e}")


# Fonction utilitaire pour créer un gestionnaire de dépendances
def create_dependency_manager(project_path: str) -> DependencyManager:
    """Crée un gestionnaire de dépendances pour un projet."""
    return DependencyManager(project_path)
