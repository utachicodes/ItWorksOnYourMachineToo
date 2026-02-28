# -*- coding: utf-8 -*-
"""
LexWorksEverywhere OS Adapter Interface - Contrat d'interface pour les adaptateurs OS
========================================================================

Ce module définit les contrats d'interface que chaque adaptateur OS doit implémenter.
Cela permet au 'Core' de LexWorksEverywhere de rester totalement agnostique vis-à-vis du système.

Projet développé par : Alexandre Albert Ndour
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import subprocess


class FileSystemInterface(ABC):
    """Contrat pour les opérations sur le système de fichiers."""

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        pass

    @abstractmethod
    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        pass

    @abstractmethod
    def read_text(self, path: str) -> str:
        pass

    @abstractmethod
    def write_text(self, path: str, content: str) -> None:
        pass

    @abstractmethod
    def list_dir(self, path: str) -> List[str]:
        """Liste les fichiers et dossiers dans un répertoire."""
        pass

    @abstractmethod
    def resolve_path(self, path: str) -> str:
        """Résout un chemin absolu et gère les symlinks."""
        pass


class ProcessRunnerInterface(ABC):
    """Contrat pour l'exécution de processus."""

    @abstractmethod
    def run(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300,
        capture_output: bool = True,
        policy: Optional[str] = "default",
    ) -> subprocess.CompletedProcess:
        pass

    @abstractmethod
    def has_binary(self, name: str) -> bool:
        """Vérifie si un binaire est disponible dans le PATH."""
        pass


class IntegrityInterface(ABC):
    """Contrat pour la vérification d'intégrité des binaires."""

    @abstractmethod
    def get_binary_hash(self, binary_path: str) -> str:
        """Calcule le hash SHA256 d'un exécutable."""
        pass

    @abstractmethod
    def verify_signature(self, binary_path: str) -> bool:
        """Vérifie la signature cryptographique (si applicable)."""
        pass


class SandboxInterface(ABC):
    """Contrat pour l'isolation et le sandboxing."""

    @abstractmethod
    def enter(self, policy: str, context: Dict[str, Any]) -> bool:
        """
        Entre dans un sandbox avec une politique spécifique :
        - 'strict' : Lecture seule, pas de réseau.
        - 'limited' : Ecriture projet uniquement, réseau restreint.
        - 'default' : Politique standard LexWorksEverywhere.
        """
        pass

    @abstractmethod
    def exit(self) -> bool:
        pass


class OSAdapter(ABC):
    """Interface globale de l'adaptateur OS."""

    __author__ = "Alexandre Albert Ndour"

    @staticmethod
    def get_author() -> str:
        return "Alexandre Albert Ndour"

    @property
    @abstractmethod
    def fs(self) -> FileSystemInterface:
        pass

    @property
    @abstractmethod
    def process(self) -> ProcessRunnerInterface:
        pass

    @property
    @abstractmethod
    def sandbox(self) -> SandboxInterface:
        pass

    @property
    @abstractmethod
    def integrity(self) -> IntegrityInterface:
        pass

    @abstractmethod
    def get_os_name(self) -> str:
        """Retourne le nom de l'OS (macos, linux, windows)."""
        pass

    @abstractmethod
    def get_install_suggestion(self, binary_name: str) -> str:
        """Retourne une suggestion de commande pour installer un binaire manquant."""
        pass

    @abstractmethod
    def normalize_path(self, path: str) -> str:
        pass
