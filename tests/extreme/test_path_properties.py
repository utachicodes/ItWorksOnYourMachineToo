# -*- coding: utf-8 -*-
import random
import string
from lexworkseverywhere.adapters.macos.macos_adapter import MacOSAdapter
from lexworkseverywhere.adapters.windows.windows_adapter import WindowsAdapter
from lexworkseverywhere.adapters.linux.linux_adapter import LinuxAdapter

def generate_random_path(length=5, separator="/"):
    parts = [''.join(random.choices(string.ascii_letters, k=5)) for _ in range(length)]
    return separator.join(parts)

def test_normalization_properties():
    print("💎 Démarrage des tests de propriétés sur la normalisation...")
    
    adapters = [MacOSAdapter(), WindowsAdapter(), LinuxAdapter()]
    
    for adapter in adapters:
        os_name = adapter.get_os_name()
        print(f"Propriétés pour {os_name}:")
        
        for _ in range(100):
            path = generate_random_path(separator="/" if os_name != "windows" else "\\")
            
            # Propriété 1 : Idempotence (normalize(normalize(x)) == normalize(x))
            first_norm = adapter.normalize_path(path)
            second_norm = adapter.normalize_path(first_norm)
            assert first_norm == second_norm, f"Idempotence fail for {os_name}"
            
            # Propriété 2 : Pas de double separators (ex: // ou \\)
            if os_name == "windows":
                assert "\\\\" not in first_norm[1:], f"Double separator detected in {os_name}"
            else:
                assert "//" not in first_norm, f"Double separator detected in {os_name}"
                
    print("✅ Tests de propriétés terminés avec succès.")

if __name__ == "__main__":
    test_normalization_properties()
