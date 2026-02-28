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
import logging


def validate_and_sanitize_path(user_path: str, base_path: Optional[str] = None) -> str:
    """
    Valide et nettoie un chemin utilisateur pour prévenir la traversée de répertoires.
    
    Args:
        user_path: Chemin fourni par l'utilisateur
        base_path: Chemin de base pour restreindre l'accès (optionnel)
        
    Returns:
        Chemin nettoyé et validé
        
    Raises:
        ValueError: Si le chemin est invalide ou dangereux
    """
    if not user_path:
        raise ValueError("Le chemin ne peut pas être vide")
    
    # Convertir en Path pour une manipulation sécurisée
    path_obj = Path(user_path).resolve()
    
    # Empêcher les caractères dangereux dans les chemins
    dangerous_patterns = [
        r'\.\.\/',  # Traversée de répertoires
        r'\.\.\\',  # Traversée de répertoires (Windows)
        r'\.\.',    # Traversée de répertoires (sous forme de répertoire)
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, user_path):
            raise ValueError(f"Potentiel risque de traversée de répertoire détecté dans: {user_path}")
    
    # Si un chemin de base est spécifié, s'assurer que le chemin est à l'intérieur
    if base_path:
        base_path_obj = Path(base_path).resolve()
        try:
            # Cela lèvera une ValueError si le chemin est en dehors de base_path
            path_obj.relative_to(base_path_obj)
        except ValueError:
            raise ValueError(f"Le chemin {user_path} est en dehors du chemin de base autorisé {base_path}")
    
    return str(path_obj)


def sanitize_command_args(args: Union[str, List[str]]) -> List[str]:
    """
    Nettoie les arguments de commande pour prévenir l'injection de commandes.
    
    Args:
        args: Arguments de commande (soit une chaîne, soit une liste)
        
    Returns:
        Liste d'arguments nettoyés et sécurisés
    """
    if isinstance(args, str):
        # Utiliser shlex.split pour séparer les arguments de manière sécurisée
        try:
            args_list = shlex.split(args)
        except ValueError:
            # Si shlex.split échoue, on suppose que c'est une seule commande
            args_list = [args]
    else:
        args_list = args
    
    # Nettoyer chaque argument individuellement
    sanitized_args = []
    for arg in args_list:
        if not isinstance(arg, str):
            arg = str(arg)
        
        # Empêcher les caractères dangereux dans les commandes
        dangerous_chars = [';', '&', '|', '`', '$(', ')', '{', '}', '<', '>']
        for char in dangerous_chars:
            if char in arg:
                # Nettoyer l'argument en le citant correctement
                sanitized_args.append(shlex.quote(arg))
                break
        else:
            # Aucun caractère dangereux trouvé, ajouter tel quel
            sanitized_args.append(arg)
    
    return sanitized_args


def execute_secure_command(
    cmd: Union[str, List[str]], 
    cwd: Optional[str] = None, 
    timeout: int = 300,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """
    Exécute une commande de manière sécurisée avec protection contre l'injection.
    
    Args:
        cmd: Commande à exécuter
        cwd: Répertoire de travail (optionnel)
        timeout: Délai d'attente en secondes
        capture_output: Capturer la sortie ou non
        
    Returns:
        Résultat de l'exécution de la commande
    """
    # Nettoyer les arguments de la commande
    if isinstance(cmd, str):
        # Séparer la commande de ses arguments de manière sécurisée
        try:
            cmd_parts = shlex.split(cmd)
            cmd_sanitized = sanitize_command_args(cmd_parts)
        except ValueError:
            # Si shlex.split échoue, traiter comme une seule commande
            cmd_sanitized = sanitize_command_args([cmd])
    else:
        cmd_sanitized = sanitize_command_args(cmd)
    
    # Valider le répertoire de travail s'il est spécifié
    if cwd:
        cwd = validate_and_sanitize_path(cwd)
    
    try:
        # Exécuter la commande avec subprocess
        result = subprocess.run(
            cmd_sanitized,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=False  # Ne pas lever d'exception, renvoyer le résultat
        )
        return result
    except subprocess.TimeoutExpired:
        raise subprocess.TimeoutExpired(cmd_sanitized, timeout)
    except Exception as e:
        raise e


def is_safe_path(path: str, allowed_base_paths: List[str]) -> bool:
    """
    Vérifie si un chemin est sûr à utiliser (pas de traversée de répertoires).
    
    Args:
        path: Chemin à vérifier
        allowed_base_paths: Liste des chemins de base autorisés
        
    Returns:
        True si le chemin est sûr, False sinon
    """
    try:
        resolved_path = Path(path).resolve()
        
        for base_path in allowed_base_paths:
            base_path_obj = Path(base_path).resolve()
            try:
                # Si relative_to ne lève pas d'exception, le chemin est dans le base_path
                resolved_path.relative_to(base_path_obj)
                return True
            except ValueError:
                # Le chemin n'est pas dans ce base_path, essayer le suivant
                continue
        
        # Si on arrive ici, le chemin n'est dans aucun des chemins autorisés
        return False
    except Exception:
        # En cas d'erreur (chemin invalide, etc.), considérer comme non sûr
        return False


def create_secure_temp_directory(prefix: str = "lexworkseverywhere_") -> str:
    """
    Crée un répertoire temporaire sécurisé.
    
    Args:
        prefix: Préfixe pour le nom du répertoire temporaire
        
    Returns:
        Chemin du répertoire temporaire sécurisé
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    # S'assurer que les permissions sont correctes (lecture/écriture pour l'utilisateur seulement)
    os.chmod(temp_dir, 0o700)
    return temp_dir


def validate_project_path(project_path: str) -> bool:
    """
    Valide si un chemin de projet est sûr à utiliser.
    
    Args:
        project_path: Chemin du projet à valider
        
    Returns:
        True si le chemin est valide et sûr, False sinon
    """
    try:
        # Vérifier que le chemin n'est pas vide
        if not project_path or not project_path.strip():
            return False
        
        # Nettoyer le chemin
        clean_path = validate_and_sanitize_path(project_path)
        
        # Vérifier que le chemin existe
        path_obj = Path(clean_path)
        if not path_obj.exists():
            return False
        
        # Vérifier que c'est un répertoire
        if not path_obj.is_dir():
            return False
        
        # Vérifier que le chemin est accessible en lecture
        if not os.access(clean_path, os.R_OK):
            return False
        
        return True
    except Exception:
        return False