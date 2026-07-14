# -*- coding: utf-8 -*-
from ItWorksOnYourMachineToo.adapters.linux.linux_adapter import LinuxAdapter
from ItWorksOnYourMachineToo.adapters.macos.macos_adapter import MacOSAdapter
from ItWorksOnYourMachineToo.adapters.windows.windows_adapter import WindowsAdapter
from ItWorksOnYourMachineToo.core.i18n import set_locale


def _reset_locale():
    set_locale("en")


def test_install_suggestion_follows_lang_setting():
    for adapter_cls in (LinuxAdapter, MacOSAdapter, WindowsAdapter):
        adapter = adapter_cls()
        try:
            set_locale("en")
            assert "Please run" in adapter.get_install_suggestion("git")

            set_locale("fr")
            assert "Veuillez exécuter" in adapter.get_install_suggestion("git")
        finally:
            _reset_locale()
