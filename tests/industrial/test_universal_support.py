# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
from lexworkseverywhere.core.planner.engine import ProjectPlanner
from lexworkseverywhere.core.contracts.adapter import OSAdapter

def test_language_detection_matrix():
    print("🧪 Démarrage de la Matrice de Test Multi-Langages...")
    
    mock_adapter = MagicMock(spec=OSAdapter)
    mock_adapter.normalize_path.side_effect = lambda x: x
    mock_adapter.fs.exists.return_value = True
    mock_adapter.fs.is_dir.return_value = True
    mock_adapter.fs.read_text.return_value = ""
    
    planner = ProjectPlanner(mock_adapter)

    def set_indicators(inds, proj_path):
        def mock_exists(p):
            if p == proj_path or p == f"{proj_path}/src": return True
            return any(p.endswith(ind) for ind in inds)
        
        def mock_list_dir(p):
            # Return files that end with indicators
            return inds

        mock_adapter.fs.exists.side_effect = mock_exists
        mock_adapter.fs.list_dir.side_effect = mock_list_dir

    # Test Matrix
    test_cases = [
        (['requirements.txt'], 'python'),
        (['package.json'], 'nodejs'),
        (['go.mod'], 'go'),
        (['Cargo.toml'], 'rust'),
        (['composer.json'], 'php'),
        (['Gemfile'], 'ruby'),
        (['CMakeLists.txt'], 'cpp'),
        (['Makefile', '.c'], 'c'),
        (['pubspec.yaml'], 'dart'),
        (['mix.exs'], 'elixir'),
        (['Dockerfile'], 'docker'),
    ]

    for indicators, expected in test_cases:
        path = f"/dummy/{expected}_project"
        set_indicators(indicators, path)
        plan = planner.plan_project(path)
        print(f"  - Attendu: {expected:10} | Détecté: {plan['project_type']}")
        assert plan['project_type'] == expected

    # Test Shebang Heuristics
    path = "/dummy/shebang_ruby_project"
    set_indicators(['main.rb'], path)
    # Mock read_text to return a ruby shebang
    mock_adapter.fs.read_text.side_effect = lambda p: "#!/usr/bin/env ruby\nputs 'hello'" if p.endswith("main.rb") else ""
    
    # We need to add main.rb to entry_candidates in the test context
    # Actually, ProjectPlanner._apply_heuristics uses specific candidates.
    # Let's mock a 'script.sh' which is in the candidates.
    path = "/dummy/shebang_shell_project"
    set_indicators(['script.sh'], path)
    mock_adapter.fs.read_text.side_effect = lambda p: "#!/bin/bash\necho 'hello'" if p.endswith("script.sh") else ""
    
    plan = planner.plan_project(path)
    print(f"  - Test Heuristique (Shebang Bash) | Détecté: {plan['project_type']}")
    assert plan['project_type'] == 'shell'

    print("✅ Matrice de Test Multi-Langages & Shebangs : RÉUSSIE")

if __name__ == "__main__":
    test_language_detection_matrix()
