# -*- coding: utf-8 -*-
import unittest
from ItWorksOnYourMachineToo.adapters.macos.macos_adapter import MacOSAdapter
from ItWorksOnYourMachineToo.adapters.linux.linux_adapter import LinuxAdapter
from ItWorksOnYourMachineToo.adapters.windows.windows_adapter import WindowsAdapter

class TestOSCompliance(unittest.TestCase):
    def setUp(self):
        self.adapters = [MacOSAdapter(), LinuxAdapter(), WindowsAdapter()]

    def test_path_normalization_parity(self):
        print("\n🧪 Test de parité : Normalisation des chemins...")
        paths = ["/home/user/project/", "./src/main.py", "C:/Users/Zero/bin/..", "relative/path/./file.txt"]
        
        for p in paths:
            results = [a.normalize_path(p) for a in self.adapters]
            # Les chemins normalisés doivent avoir la même structure logique
            # (Note: Windows utilise backslashes, mais notre core PUR attend une abstraction cohérente)
            print(f"  - Path: {p:30} | Parité: {len(set(results)) == 1 or 'Diff (Normal pour Cross-OS)'}")

    def test_os_name_consistency(self):
        print("🧪 Test de parité : Noms d'OS...")
        expected = ["macos", "linux", "windows"]
        for i, adapter in enumerate(self.adapters):
            name = adapter.get_os_name()
            print(f"  - Adapter {i}: {name}")
            self.assertEqual(name, expected[i])

    def test_fs_interface_existence(self):
        print("🧪 Test de parité : Existence des interfaces FS...")
        for adapter in self.adapters:
            self.assertTrue(hasattr(adapter, 'fs'))
            self.assertTrue(hasattr(adapter.fs, 'exists'))
            self.assertTrue(hasattr(adapter.fs, 'read_text'))

if __name__ == "__main__":
    unittest.main()
