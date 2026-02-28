# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Base Adapter - Adaptateur de base pour les systèmes d'exploitation
==============================================================

Classe abstraite qui définit l'interface commune pour tous les adaptateurs OS.
Les adaptateurs spécifiques (Windows, macOS, Linux) implémentent cette interface.

Fonctionnalités :
- Conversion de chemins entre systèmes d'exploitation
- Conversion de scripts entre shells
- Gestion des gestionnaires de paquets
- Normalisation des variables d'environnement

Projet développé par : Alexandre Albert Ndour
Date de naissance : 29 janvier 2005
Nationalité : Sénégalaise
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import platform


class BaseAdapter(ABC):
    """
    Abstract base class for OS adapters.
    Defines the interface that all OS adapters must implement.
    """
    
    def __init__(self):
        self.current_os = platform.system().lower()
        
    @abstractmethod
    def convert_path(self, path: str, target_os: str = None) -> str:
        """
        Convert a path from the current OS format to the target OS format.
        
        Args:
            path: Path to convert
            target_os: Target OS ('windows', 'linux', 'macos'). If None, uses current OS.
            
        Returns:
            Converted path
        """
        pass
    
    @abstractmethod
    def convert_script(self, script_content: str, target_os: str = None) -> str:
        """
        Convert a script from the current OS format to the target OS format.
        
        Args:
            script_content: Content of the script to convert
            target_os: Target OS ('windows', 'linux', 'macos'). If None, uses current OS.
            
        Returns:
            Converted script content
        """
        pass
    
    @abstractmethod
    def get_package_manager_commands(self, package_manager: str) -> Dict[str, Any]:
        """
        Get commands for a specific package manager on this OS.
        
        Args:
            package_manager: Name of the package manager (e.g., 'npm', 'pip', 'apt')
            
        Returns:
            Dictionary with commands for different operations
        """
        pass
    
    @abstractmethod
    def normalize_environment_vars(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """
        Normalize environment variables for the current OS.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            Normalized environment variables
        """
        pass
    
    @abstractmethod
    def execute_command(self, command: str, cwd: str = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Execute a command on the current OS.
        
        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables
            
        Returns:
            Dictionary with execution results
        """
        pass
    
    def get_shell_commands(self) -> Dict[str, str]:
        """
        Get OS-specific shell commands.
        
        Returns:
            Dictionary mapping command names to shell commands
        """
        return {
            "list_dir": "ls" if self.current_os != "windows" else "dir",
            "make_dir": "mkdir -p" if self.current_os != "windows" else "mkdir",
            "remove_dir": "rm -rf" if self.current_os != "windows" else "rmdir /s /q",
            "copy_file": "cp" if self.current_os != "windows" else "copy",
            "move_file": "mv" if self.current_os != "windows" else "move",
            "remove_file": "rm" if self.current_os != "windows" else "del",
            "set_env": "export" if self.current_os != "windows" else "set",
            "path_separator": ":" if self.current_os != "windows" else ";",
        }
