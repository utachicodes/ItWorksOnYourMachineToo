# ItWorksOnYourMachineToo — Universal Development Environment Manager
[![CI](https://github.com/utachicodes/ItWorksOnYourMachineToo/actions/workflows/ci.yml/badge.svg)](https://github.com/utachicodes/ItWorksOnYourMachineToo/actions/workflows/ci.yml) ![Coverage](badges/coverage.svg)

ItWorksOnYourMachineToo lets you run any software project on any OS without manual setup. It eliminates "works on my machine" by automatically handling OS differences.

## Features

- Cross‑platform: Windows, macOS, Linux
- Zero configuration
- Automatic project detection and dependency mapping
- System‑agnostic Core PUR architecture
- Safety: sandboxing and integrity hooks
- Smart path/script adaptation
- Resilience under adverse conditions
- Caching for fast scans
- Broad language support (Python, Node.js, Go, Rust, C/C++, etc.)
- Heuristic support for Make/CMake
- Built‑in Doctor for host/project checks

## CLI
| Command | Description |
| :--- | :--- |
| `itworks scan -p PATH` | Analyze project and generate an execution plan |
| `itworks run -p PATH` | Prepare environment and execute the project |
| `itworks doctor [-p PATH]` | Check host and optional project requirements |
| `itworks capture` | Save the current system profile |
| `itworks export --kind devcontainer -p PATH` | Generate a Dev Container |
| `itworks export --kind brewfile|winget|apt|nix -p PATH` | Generate OS setup files |
| `--lang en|fr` | Switch CLI language (default: en) |

## Install

```bash
pip install itworksonyourmachinetoo
```

From source:

```bash
git clone https://github.com/utachicodes/ItWorksOnYourMachineToo.git
cd ItWorksOnYourMachineToo
pip install -r requirements.txt
pip install .
```

## Usage

```bash
itworks scan -p /path/to/project
itworks doctor -p /path/to/project
itworks doctor --apply -p /path/to/project
itworks export --kind devcontainer -p /path/to/project
itworks export --kind brewfile -p /path/to/project
itworks export --kind winget -p /path/to/project
itworks export --kind apt -p /path/to/project
itworks export --kind nix -p /path/to/project
itworks run -p /path/to/project
```

## Architecture (v2 Core PUR)

1. Core PUR: Project Planner, Execution Engine, Environment Validator  
2. OS Adapters: macOS, Windows, Linux  
3. Exporters: one module per export target (devcontainer, brewfile, winget,
   apt, nix, ansible, docker-compose), dispatched through a registry
4. Security Layer
5. Multi‑OS CI/CD

## Tests

```bash
python -m pytest -q
```

## Contributing

Issues and pull requests are welcome.

## License

MIT — see [LICENSE](LICENSE).

## Author

Abdoullah Ndao

## Support

If you like this project, give it a ⭐ on GitHub.

French version: see [README.fr.md](README.fr.md).
