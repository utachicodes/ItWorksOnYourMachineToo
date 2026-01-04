# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from ...core.contracts.adapter import OSAdapter, FileSystemInterface, ProcessRunnerInterface, SandboxInterface, IntegrityInterface

class WindowsFileSystem(FileSystemInterface):
    def exists(self, path: str) -> bool:
        return os.path.exists(path)
    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)
    def mkdir(self, path: str, parents: bool = True, exist_ok: bool = True) -> None:
        Path(path).mkdir(parents=parents, exist_ok=exist_ok)
    def read_text(self, path: str) -> str:
        with open(path, 'r') as f: return f.read()
    def write_text(self, path: str, content: str) -> None:
        with open(path, 'w') as f: f.write(content)
    def list_dir(self, path: str) -> List[str]:
        return os.listdir(path)
    def resolve_path(self, path: str) -> str:
        return str(Path(path).resolve())

class WindowsProcessRunner(ProcessRunnerInterface):
    def run(self, cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None, 
            timeout: int = 300, capture_output: bool = True, policy: Optional[str] = "default") -> subprocess.CompletedProcess:
        return subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout, capture_output=capture_output, text=True)

    def has_binary(self, name: str) -> bool:
        """Vérifie si un binaire est disponible sur Windows via 'where'."""
        import subprocess
        try:
            return subprocess.run(["where", name], capture_output=True).returncode == 0
        except:
            return False

class WindowsIntegrity(IntegrityInterface):
    def get_binary_hash(self, binary_path: str) -> str:
        import hashlib
        sha256_hash = hashlib.sha256()
        try:
            with open(binary_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return ""

    def verify_signature(self, binary_path: str) -> bool:
        # Placeholder pour SignTool sur Windows
        return True

class WindowsSandbox(SandboxInterface):
    def enter(self, policy: str, context: Dict[str, Any]) -> bool:
        # Windows-specific sandboxing logic
        return True
    def exit(self) -> bool:
        return True

class WindowsAdapter(OSAdapter):
    def __init__(self):
        self._fs = WindowsFileSystem()
        self._process = WindowsProcessRunner()
        self._sandbox = WindowsSandbox()
        self._integrity = WindowsIntegrity()
    
    @property
    def fs(self) -> FileSystemInterface: return self._fs
    @property
    def process(self) -> ProcessRunnerInterface: return self._process
    @property
    def sandbox(self) -> SandboxInterface: return self._sandbox
    @property
    def integrity(self) -> IntegrityInterface: return self._integrity
    
    def get_os_name(self) -> str: return "windows"
    def normalize_path(self, path: str) -> str: return str(Path(path)).replace("/", "\\")
    def get_install_suggestion(self, binary_name: str) -> str:
        mapping = {
            "npm": "winget install OpenJS.NodeJS",
            "node": "winget install OpenJS.NodeJS",
            "python": "winget install Python.Python.3",
            "go": "winget install Google.Go",
            "composer": "winget install Microsoft.Composer",
            "cargo": "winget install Rustlang.Rustup",
            "make": "winget install GnuWin32.Make",
            "cmake": "winget install Kitware.CMake",
            "flutter": "winget install Flutter.Flutter",
            "java": "winget install Oracle.JDK.21",
            "dotnet": "winget install Microsoft.DotNet.SDK.8",
            "ruby": "winget install RubyInstallerTeam.RubyWithDevKit",
            "docker": "winget install Docker.DockerDesktop"
        }
        cmd = mapping.get(binary_name, f"winget install {binary_name}")
        return f"Veuillez exécuter : [bold cyan]{cmd}[/bold cyan]"
