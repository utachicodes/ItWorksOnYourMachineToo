# LexWorksEverywhere - Gestionnaire d'Environnement de Développement Multiplateforme

**LexWorksEverywhere** est un outil open-source révolutionnaire qui permet d'exécuter n'importe quel projet logiciel sur n'importe quel système d'exploitation sans configuration manuelle. Il résout définitivement le problème fameux "ça marche sur ma machine" en gérant automatiquement les différences d'environnement entre les systèmes.

## 🚀 Fonctionnalités

- **Multiplateforme** : Fonctionne sur Windows, macOS et Linux
- **Zéro configuration** : Aucune configuration manuelle requise
- **Détection automatique** : Détecte automatiquement le type de projet et ses dépendances
- **Architecture Core PUR** : Coeur 100% agnostique au système pour une fiabilité maximale
- **Sécurité Hardened** : Sandboxing granulaire et vérification d'intégrité SHA256 des runtimes
- **Adaptation intelligente** : Convertit automatiquement les chemins et scripts entre systèmes
- **Chaos-Tested** : Résilience prouvée contre les pannes système (disque plein, timeout, etc.)
- **Performance X10** : Cache intelligent pour des scans quasi-instantanés
- **Support Universel** : Détecte et gère plus de 15 langages (Python, Go, Rust, C++, etc.)
- **Moteur Heuristique** : Supporte n'importe quel projet via Makefile ou CMake
- **LexWorksEverywhere Doctor** : Auto-diagnostic intégré pour vérifier la santé du système
- **Pipeline CI/CD Robuste** : Validation multi-OS et multi-architecture automatique

### ️ Commandes
| Commande | Description |
| :--- | :--- |
| `lexworks scan` | Analyse le projet et génère un plan universel |
| `lexworks run` | Prépare et exécute le projet en isolation |
| `lexworks doctor` | Vérifie les prérequis et la santé du host |
| `lexworks capture` | Sauvegarde la configuration système actuelle |

## 🛠️ Installation

### Prérequis
- Python 3.9 ou supérieur
- Système compatible pip

### Installation depuis PyPI
```bash
pip install lexworkseverywhere
```

### Installation depuis les sources
```bash
git clone https://github.com/alexandrealbertndour/lexworkseverywhere.git
cd lexworkseverywhere
pip install -r requirements.txt
pip install .
```

## 💡 Utilisation

### Analyser un projet
```bash
lexworks scan /path/to/your/project
```

### Exécuter un projet
```bash
lexworks run /path/to/your/project
```

### Diagnostiquer les problèmes
```bash
lexworks doctor
```

### Capturer l'environnement
```bash
lexworks capture
```

## 🏗️ Architecture (v2 Core PUR)

LexWorksEverywhere repose sur une architecture découplée "Core PUR" garantissant une portabilité totale :

1. **Core PUR (Agnostique)** :
   - **Project Planner** : Analyse et génère un plan d'exécution universel.
   - **Execution Engine** : Orchestre l'environnement sans dépendance système directe.
   - **Environment Validator** : Diagnostique les échecs via des contrats d'interface.
2. **Adapters OS (Spécifiques)** : Implémentent le contrat `OSAdapter` pour MacOS, Windows et Linux.
3. **Security Layer** : Vérification d'intégrité (SHA256) et Sandboxing par politique.
4. **CI/CD Automatisé** : Validation systématique sur les trois OS majeurs.

## 🧪 Tests

Pour exécuter les tests :
```bash
python -m pytest lexworkseverywhere/tests/
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Fork du projet
2. Création d'une branche pour la fonctionnalité (`git checkout -b feature/FonctionnaliteIncroyable`)
3. Commit de vos changements (`git commit -m 'Ajouter une fonctionnalité incroyable'`)
4. Push vers la branche (`git push origin feature/FonctionnaliteIncroyable`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**Alexandre Albert Ndour**
- Date de naissance : 29 janvier 2005
- Nationalité : Sénégalaise
- Passionné de développement Python

## 🐛 Signaler un Bug

Si vous trouvez un bug, veuillez ouvrir une [issue](https://github.com/alexandrealbertndour/lexworkseverywhere/issues) sur GitHub.

## 🌟 Support

Si vous aimez ce projet, n'oubliez pas de lui donner une ⭐ sur GitHub !