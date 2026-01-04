# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Adapter Factory - Usine d'adaptateurs
==========================================

Détecte le système actuel et retourne l'adaptateur approprié.

Projet développé par : Alexandre Albert Ndour
"""

import platform
from .adapter import OSAdapter
from ...adapters.windows.windows_adapter import WindowsAdapter
from ...adapters.macos.macos_adapter import MacOSAdapter
from ...adapters.linux.linux_adapter import LinuxAdapter


class AdapterFactory:
    """
    Detects the current platform and instantiates the correct adapter.
    """
    
    @staticmethod
    def detect() -> OSAdapter:
        sys_name = platform.system().lower()
        if sys_name == "windows":
            return WindowsAdapter()
        elif sys_name == "darwin":
            return MacOSAdapter()
        else:
            return LinuxAdapter()
