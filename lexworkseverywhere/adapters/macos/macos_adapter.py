# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from ...core.contracts.adapter import OSAdapter, FileSystemInterface, ProcessRunnerInterface, SandboxInterface, IntegrityInterface

class MacOSFileSystem(FileSystemInterface):
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

class MacOSProcessRunner(ProcessRunnerInterface):
    def run(self, cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None, 
            timeout: int = 300, capture_output: bool = True, policy: Optional[str] = "default") -> subprocess.CompletedProcess:
        # En production, 'policy' adapterait l'exécution (ex: sandbox-exec)
        return subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout, capture_output=capture_output, text=True)

    def has_binary(self, name: str) -> bool:
        """Vérifie si un binaire est disponible dans le PATH sur macOS."""
        import subprocess
        try:
            return subprocess.run(["which", name], capture_output=True).returncode == 0
        except:
            return False

class MacOSIntegrity(IntegrityInterface):
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
        # Utilisation de 'codesign' sur macOS
        try:
            result = subprocess.run(["codesign", "-v", binary_path], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

class MacOSSandbox(SandboxInterface):
    def enter(self, policy: str, context: Dict[str, Any]) -> bool:
        # macOS-specific sandboxing logic
        return True
    def exit(self) -> bool:
        return True

class MacOSAdapter(OSAdapter):
    def __init__(self):
        self._fs = MacOSFileSystem()
        self._process = MacOSProcessRunner()
        self._sandbox = MacOSSandbox()
        self._integrity = MacOSIntegrity()
    
    @property
    def fs(self) -> FileSystemInterface: return self._fs
    @property
    def process(self) -> ProcessRunnerInterface: return self._process
    @property
    def sandbox(self) -> SandboxInterface: return self._sandbox
    @property
    def integrity(self) -> IntegrityInterface: return self._integrity
    
    def get_os_name(self) -> str: return "macos"
    def normalize_path(self, path: str) -> str: return str(Path(path).resolve())
    def get_install_suggestion(self, binary_name: str) -> str:
        mapping = {
            "npm": "brew install node",
            "node": "brew install node",
            "bun": "curl -fsSL https://bun.sh/install | bash",
            "python3": "brew install python",
            "pip": "brew install python",
            "go": "brew install go",
            "composer": "brew install composer",
            "cargo": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "rustc": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "make": "xcode-select --install",
            "cmake": "brew install cmake",
            "flutter": "brew install --cask flutter",
            "java": "brew install openjdk",
            "kotlinc": "brew install kotlin",
            "dotnet": "brew install --cask dotnet-sdk",
            "ruby": "brew install ruby",
            "gem": "brew install ruby",
            "bundle": "gem install bundler",
            "elixir": "brew install elixir",
            "scala": "brew install scala",
            "sbt": "brew install sbt",
            "ghc": "brew install ghc",
            "clojure": "brew install clojure",
            "zig": "brew install zig",
            "nim": "brew install nim",
            "docker": "brew install --cask docker",
            "kubectl": "brew install kubernetes-cli",
            "terraform": "brew install terraform",
            "ansible-playbook": "brew install ansible"
        }
        cmd = mapping.get(binary_name, f"brew install {binary_name}")
        return f"Veuillez exécuter : [bold cyan]{cmd}[/bold cyan]"
