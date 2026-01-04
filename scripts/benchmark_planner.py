# -*- coding: utf-8 -*-
import time
from unittest.mock import MagicMock
from lexworkseverywhere.core.planner.engine import ProjectPlanner
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def run_benchmark():
    print("🚀 Démarrage du Benchmark : ProjectPlanner Caching...")
    
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.normalize_path.side_effect = lambda x: x
    mock_adapter.fs.exists.return_value = True
    mock_adapter.fs.read_text.return_value = "requests\nflask\nnumpy\npandas"
    
    planner = ProjectPlanner(mock_adapter)
    path = "/test/big_project"
    
    # Premier passage (froid)
    start = time.perf_counter()
    planner.plan_project(path)
    cold_duration = time.perf_counter() - start
    print(f"Passage à froid : {cold_duration:.6f}s")
    
    # Second passage (chaud)
    start = time.perf_counter()
    planner.plan_project(path)
    hot_duration = time.perf_counter() - start
    print(f"Passage à chaud (Cache hit) : {hot_duration:.6f}s")
    
    improvement = (cold_duration / hot_duration) if hot_duration > 0 else 1
    print(f"Gain de performance : x{improvement:.1f}")
    
    assert hot_duration < cold_duration
    print("✅ Benchmark réussi.")

if __name__ == "__main__":
    run_benchmark()
