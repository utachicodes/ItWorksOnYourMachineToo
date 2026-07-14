# -*- coding: utf-8 -*-
"""
ItWorksOnYourMachineToo Adapter Factory
==========================================

Detects the current platform and returns the appropriate adapter.
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
