# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock
from ItWorksOnYourMachineToo.core.engine.engine import ExecutionEngine
from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter

def test_chaos_rollback_on_failure():
    print("\n🌪 Démarrage du Chaos Testing sur ExecutionEngine...")
    
    failures = [
        IOError("Disk Full"),
        PermissionError("Access Denied"),
        TimeoutError("Process Timeout"),
        Exception("Unknown Fatal Error")
    ]
    
    mock_adapter = MagicMock(spec=OSAdapter)
    engine = ExecutionEngine(mock_adapter)
    
    for failure in failures:
        # Configurer le mock pour lever une exception lors de l'exécution
        mock_adapter.process.run.side_effect = failure
        
        plan = {"project_type": "python", "project_path": "/fake/project"}
        
        print(f"Injection d'erreur : {type(failure).__name__}")
        
        # L'engine doit capturer l'erreur et tenter un rollback
        success = engine.prepare(plan)
        assert success is False
        
        # Vérifier que le rollback a été appelé (ici via l'etat du engine)
        assert len(engine.environment_stack) == 0
        
    print("✅ Chaos Testing terminé : Tous les échecs ont été gérés proprement.")

if __name__ == "__main__":
    test_chaos_rollback_on_failure()
