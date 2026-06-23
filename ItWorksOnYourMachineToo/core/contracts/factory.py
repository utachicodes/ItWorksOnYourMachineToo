# -*- coding: utf-8 -*-
"""
ItWorksOnYourMachineToo Adapter Factory - Usine d'adaptateurs
==========================================

Détecte le système actuel et retourne l'adaptateur approprié.

Projet développé par : Abdoullah Ndao
"""

import platform
from .adapter import OSAdapter
from ...adapters.windows.windows_adapter import WindowsAdapter
from ...adapters.macos.macos_adapter import MacOSAdapter
from ...adapters.linux.linux_adapter import LinuxAdapter


class AdapterFactory:
    """Detects the current platform and instantiates the correct adapter."""

    @staticmethod
    def detect() -> OSAdapter:
        sys_name = platform.system().lower()
        if sys_name == "windows":
            return WindowsAdapter()
        if sys_name == "darwin":
            return MacOSAdapter()
        return LinuxAdapter()
