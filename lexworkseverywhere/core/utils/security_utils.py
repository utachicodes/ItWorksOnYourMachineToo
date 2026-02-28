# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Security Utilities - Utilitaires de sécurité
================================================

Ce module fournit des utilitaires de sécurité pour LexWorksEverywhere :
- Validation et nettoyage des entrées
- Protection contre l'injection de commandes
- Protection contre la traversée de répertoires
- Gestion sécurisée des chemins de fichiers

Projet développé par : Alexandre Albert Ndour
Date de naissance : 29 janvier 2005
Nationalité : Sénégalaise
"""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Union, List, Optional
import tempfile


def validate_and_sanitize_path(user_path: str, base_path: Optional[str] = None) -> str:
    """
    Valide et nettoie un chemin utilisateur pour prévenir la traversée de répertoires.
    """
    if not user_path:
        raise ValueError("Le chemin ne peut pas être vide")
    path_obj = Path(user_path).resolve()
    dangerous_patterns = [
        r"\.\.\/",
        r"\.\.\\",
        r"\.\.",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, user_path):
            raise ValueError(f"Potentiel risque de traversée de répertoire détecté dans: {user_path}")
    if base_path:
        base_path_obj = Path(base_path).resolve()
        try:
            path_obj.relative_to(base_path_obj)
        except ValueError:
            raise ValueError(f"Le chemin {user_path} est en dehors du chemin de base autorisé {base_path}")
    return str(path_obj)


def sanitize_command_args(args: Union[str, List[str]]) -> List[str]:
    """Nettoie les arguments de commande pour prévenir l'injection de commandes."""
    if isinstance(args, str):
        try:
            args_list = shlex.split(args)
        except ValueError:
            args_list = [args]
    else:
        args_list = args
    sanitized_args = []
    for arg in args_list:
        if not isinstance(arg, str):
            arg = str(arg)
        dangerous_chars = [";", "&", "|", "`", "$(", ")", "{", "}", "<", ">"]
        for char in dangerous_chars:
            if char in arg:
                sanitized_args.append(shlex.quote(arg))
                break
        else:
            sanitized_args.append(arg)
    return sanitized_args


def execute_secure_command(
    cmd: Union[str, List[str]],
    cwd: Optional[str] = None,
    timeout: int = 300,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Exécute une commande de manière sécurisée avec protection contre l'injection."""
    if isinstance(cmd, str):
        try:
            cmd_parts = shlex.split(cmd)
            cmd_sanitized = sanitize_command_args(cmd_parts)
        except ValueError:
            cmd_sanitized = sanitize_command_args([cmd])
    else:
        cmd_sanitized = sanitize_command_args(cmd)
    if cwd:
        cwd = validate_and_sanitize_path(cwd)
    try:
        result = subprocess.run(
            cmd_sanitized,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result
    except subprocess.TimeoutExpired:
        raise subprocess.TimeoutExpired(cmd_sanitized, timeout)
    except Exception as e:
        raise e


def is_safe_path(path: str, allowed_base_paths: List[str]) -> bool:
    """Vérifie si un chemin est sûr à utiliser (pas de traversée de répertoires)."""
    try:
        resolved_path = Path(path).resolve()
        for base_path in allowed_base_paths:
            base_path_obj = Path(base_path).resolve()
            try:
                resolved_path.relative_to(base_path_obj)
                return True
            except ValueError:
                continue
        return False
    except Exception:
        return False


def create_secure_temp_directory(prefix: str = "lexworkseverywhere_") -> str:
    """Crée un répertoire temporaire sécurisé."""
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    os.chmod(temp_dir, 0o700)
    return temp_dir


def validate_project_path(project_path: str) -> bool:
    """Valide si un chemin de projet est sûr à utiliser."""
    try:
        if not project_path or not project_path.strip():
            return False
        clean_path = validate_and_sanitize_path(project_path)
        path_obj = Path(clean_path)
        if not path_obj.exists():
            return False
        if not path_obj.is_dir():
            return False
        if not os.access(clean_path, os.R_OK):
            return False
        return True
    except Exception:
        return False
