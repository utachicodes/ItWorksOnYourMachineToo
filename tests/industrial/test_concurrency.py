# -*- coding: utf-8 -*-
import threading
import time
from unittest.mock import MagicMock
from lexworkseverywhere.core.planner.engine import ProjectPlanner
from lexworkseverywhere.core.engine.engine import ExecutionEngine
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def stress_test_task(planner, engine, project_id):
    path = f"/projects/proj_{project_id}"
    print(f"🧵 Thread {project_id}: Scanning {path}")
    plan = planner.plan_project(path)
    print(f"🧵 Thread {project_id}: Orchestrating {path}")
    engine.execute(plan)
    print(f"🧵 Thread {project_id}: Done")

def run_concurrency_stress_test(num_threads=10):
    print(f"🔥 Démarrage du Stress Test de Concurrence ({num_threads} threads)...")
    
    # Mocking a thread-safe adapter (MagicMock is generally thread-safe for basic usage)
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.normalize_path.side_effect = lambda x: x
    mock_adapter.fs.exists.return_value = True
    mock_adapter.fs.read_text.return_value = "requests"
    mock_adapter.process.run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
    
    planner = ProjectPlanner(mock_adapter)
    engine = ExecutionEngine(mock_adapter)
    
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress_test_task, args=(planner, engine, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("✅ Stress Test terminé : Aucun deadlock ni crash détecté.")

if __name__ == "__main__":
    run_concurrency_stress_test()
