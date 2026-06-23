# -*- coding: utf-8 -*-
import random
import string
import os
from unittest.mock import MagicMock
from ItWorksOnYourMachineToo.core.planner.engine import ProjectPlanner
from ItWorksOnYourMachineToo.core.contracts.adapter import OSAdapter

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_fuzz_planner(iterations=100):
    print(f"🕵️ Démarrage du Fuzzing sur ProjectPlanner ({iterations} itérations)...")
    
    mock_adapter = MagicMock(spec=OSAdapter)
    planner = ProjectPlanner(mock_adapter)
    
    for i in range(iterations):
        # Générer des scénarios aléatoires
        has_req = random.choice([True, False])
        has_pkg = random.choice([True, False])
        path_depth = random.randint(1, 5)
        path = "/".join([generate_random_string() for _ in range(path_depth)])
        
        # Simuler un FS qui contient des fichiers aléatoires
        mock_adapter.fs.exists.side_effect = lambda p: random.choice([True, False])
        mock_adapter.fs.read_text.return_value = generate_random_string(100)
        mock_adapter.normalize_path.side_effect = lambda x: x
        
        try:
            planner.plan_project(f"/{path}")
        except ValueError:
            pass # Chemin n'existe pas, c'est un comportement attendu
        except Exception as e:
            print(f"💥 CRASH détecté à l'itération {i} : {e}")
            raise e
            
    print("✅ Fuzzing terminé : Aucun crash inattendu détecté.")

if __name__ == "__main__":
    run_fuzz_planner()
