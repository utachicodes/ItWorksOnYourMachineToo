# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Distribution Verifier - Vérification de la distribution
==============================================================

Simule une installation propre et vérifie que les points d'entrée CLI sont fonctionnels.

Projet développé par : Alexandre Albert Ndour
"""

import subprocess
import os
import sys
import tempfile
import shutil

def run_dist_check():
    print("🚀 Vérification de la distribution de Production...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Création d'un environnement de test isolé : {tmpdir}")
        
        # 1. Création d'un venv
        subprocess.run([sys.executable, "-m", "venv", os.path.join(tmpdir, "venv")], check=True)
        
        venv_python = os.path.join(tmpdir, "venv", "bin", "python") if os.name != "nt" else os.path.join(tmpdir, "venv", "Scripts", "python")
        
        # 2. Installation locale
        print("📦 Installation de LexWorksEverywhere...")
        try:
            subprocess.run([venv_python, "-m", "pip", "install", "."], cwd=os.getcwd(), check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Échec de l'installation.\nStdout: {e.stdout}\nStderr: {e.stderr}")
            sys.exit(1)
        
        # 3. Test de la commande CLI
        print("🧪 Test de la commande 'lexworkseverywhere doctor'...")
        lexworkseverywhere_cmd = os.path.join(tmpdir, "venv", "bin", "lexworkseverywhere") if os.name != "nt" else os.path.join(tmpdir, "venv", "Scripts", "lexworkseverywhere")
        
        result = subprocess.run([lexworkseverywhere_cmd, "doctor"], capture_output=True, text=True)
        
        if "LexWorksEverywhere Doctor" in result.stdout:
            print("✅ Succès : La CLI est correctement installée et accessible.")
        else:
            print(f"❌ Échec : La CLI n'a pas répondu comme attendu.\nStdout: {result.stdout}\nStderr: {result.stderr}")
            sys.exit(1)

if __name__ == "__main__":
    run_dist_check()
