# -*- coding: utf-8 -*-
"""
ItWorksOnYourMachineToo OS Adapter Interface
========================================================================

Defines the interface contracts each OS adapter must implement, so that
the ItWorksOnYourMachineToo Core stays fully agnostic of the underlying
operating system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import subprocess


class FileSystemInterface(ABC):
    """Contract for filesystem operations."""

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
        """Lists the files and directories in a directory."""
        pass

    @abstractmethod
    def resolve_path(self, path: str) -> str:
        """Resolves an absolute path and follows symlinks."""
        pass


class ProcessRunnerInterface(ABC):
    """Contract for process execution."""

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
        """Checks whether a binary is available on the PATH."""
        pass


class IntegrityInterface(ABC):
    """Contract for binary integrity verification."""

    @abstractmethod
    def get_binary_hash(self, binary_path: str) -> str:
        """Computes the SHA256 hash of an executable."""
        pass

    @abstractmethod
    def verify_signature(self, binary_path: str) -> bool:
        """Verifies the cryptographic signature (if applicable)."""
        pass


class SandboxInterface(ABC):
    """Contract for sandboxing and isolation."""

    @abstractmethod
    def enter(self, policy: str, context: Dict[str, Any]) -> bool:
        """
        Enters a sandbox with a specific policy:
        - 'strict': Read-only, no network.
        - 'limited': Project write access only, restricted network.
        - 'default': Standard ItWorksOnYourMachineToo policy.
        """
        pass

    @abstractmethod
    def exit(self) -> bool:
        pass


class OSAdapter(ABC):
    """Global OS adapter interface."""

    __author__ = "Abdoullah Ndao"

    @staticmethod
    def get_author() -> str:
        return "Abdoullah Ndao"

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
        """Returns the OS name (macos, linux, windows)."""
        pass

    @abstractmethod
    def get_install_suggestion(self, binary_name: str) -> str:
        """Returns a suggested command to install a missing binary."""
        pass

    @abstractmethod
    def normalize_path(self, path: str) -> str:
        pass
