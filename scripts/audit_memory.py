# -*- coding: utf-8 -*-
import os
import psutil
from unittest.mock import MagicMock
from lexworkseverywhere.core.planner.engine import ProjectPlanner
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def run_memory_audit(iterations=1000):
    print(f"🧠 Démarrage de l'Audit Mémoire ({iterations} itérations)...")
    
    process = psutil.Process(os.getpid())
    mem_initial = process.memory_info().rss
    
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.normalize_path.side_effect = lambda x: x
    mock_adapter.fs.exists.return_value = True
    mock_adapter.fs.read_text.return_value = "requests"
    
    planner = ProjectPlanner(mock_adapter)
    
    for i in range(iterations):
        planner.plan_project(f"/path/proj_{i}")
        if i % 100 == 0:
            current_mem = process.memory_info().rss
            print(f"Itération {i}: Mémoire = {current_mem / 1024 / 1024:.2f} MB")
            
    mem_final = process.memory_info().rss
    leak = (mem_final - mem_initial) / (1024 * 1024)
    
    print(f"Audit terminé. Delta Mémoire: {leak:.2f} MB")
    
    # Un delta raisonnable est attendu à cause du cache, mais il ne doit pas être infini.
    assert leak < 50 # 50MB max pour 1000 itérations (principalement le cache)
    print("✅ Audit Mémoire réussi : Aucune fuite majeure détectée.")

if __name__ == "__main__":
    run_memory_audit()
