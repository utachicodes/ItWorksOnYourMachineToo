# ItWorksOnYourMachineToo - Gestionnaire d'Environnement de Développement Multiplateforme
[![CI](https://github.com/utachicodes/ItWorksOnYourMachineToo/actions/workflows/ci.yml/badge.svg)](https://github.com/utachicodes/ItWorksOnYourMachineToo/actions/workflows/ci.yml)

**ItWorksOnYourMachineToo** est un outil open-source qui permet d'exécuter n'importe quel projet logiciel sur n'importe quel système d'exploitation sans configuration manuelle. Il résout le problème "ça marche sur ma machine" en gérant automatiquement les différences d'environnement entre les systèmes.

## Fonctionnalités

- Multiplateforme : Windows, macOS et Linux
- Zéro configuration
- Détection automatique des projets et dépendances
- Architecture Core PUR agnostique
- Sécurité renforcée
- Adaptation intelligente des chemins et scripts
- Résilience éprouvée
- Cache pour des scans rapides
- Support de nombreux langages (Python, Go, Rust, C++, etc.)
- Moteur heuristique pour Make/CMake
- ItWorksOnYourMachineToo Doctor

### Commandes
| Commande | Description |
| :--- | :--- |
| `itworks scan` | Analyse le projet et génère un plan |
| `itworks run` | Prépare et exécute le projet |
| `itworks doctor` | Vérifie la santé du système ou du projet |
| `itworks capture` | Sauvegarde la configuration système |
| `itworks export --kind devcontainer` | Génère un devcontainer |
| `itworks export --kind brewfile|winget|apt|nix` | Génère des fichiers d'installation |
| `--lang fr|en` | Langue de sortie de la CLI |

## Installation

```bash
pip install itworksonyourmachinetoo
```

## Utilisation

```bash
itworks scan /path/to/project
itworks doctor --project-path /path/to/project
itworks doctor --apply --project-path /path/to/project
itworks export --kind devcontainer -p /path/to/project
itworks export --kind brewfile -p /path/to/project
itworks export --kind winget -p /path/to/project
itworks export --kind apt -p /path/to/project
itworks export --kind nix -p /path/to/project
itworks run -p /path/to/project
```

## Architecture

1. Core PUR : Project Planner, Execution Engine, Environment Validator  
2. Adapters OS : macOS, Windows, Linux  
3. Security Layer
4. CI/CD multi-OS

## Tests

```bash
python -m pytest -q
```

## Licence

MIT. Voir [LICENSE](LICENSE).

## Auteur

Abdoullah Ndao

## Signaler un Bug

Ouvrir une [issue](https://github.com/utachicodes/ItWorksOnYourMachineToo/issues) sur GitHub.

## Support

Si vous aimez ce projet, donnez une ⭐ sur GitHub !
