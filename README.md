# LexWorksEverywhere — Universal Development Environment Manager

LexWorksEverywhere lets you run any software project on any OS without manual setup. It eliminates “works on my machine” by automatically handling OS differences.

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
| `lexworks scan -p PATH` | Analyze project and generate an execution plan |
| `lexworks run -p PATH` | Prepare environment and execute the project |
| `lexworks doctor [-p PATH]` | Check host and optional project requirements |
| `lexworks capture` | Save the current system profile |
| `lexworks export --kind devcontainer -p PATH` | Generate a Dev Container |
| `--lang en|fr` | Switch CLI language (default: en) |

## Install

```bash
pip install lexworkseverywhere
```

From source:

```bash
git clone https://github.com/alexandrealbertndour/lexworkseverywhere.git
cd lexworkseverywhere
pip install -r requirements.txt
pip install .
```

## Usage

```bash
lexworks scan -p /path/to/project
lexworks doctor -p /path/to/project
lexworks export --kind devcontainer -p /path/to/project
lexworks run -p /path/to/project
```

## Architecture (v2 Core PUR)

1. Core PUR: Project Planner, Execution Engine, Environment Validator  
2. OS Adapters: macOS, Windows, Linux  
3. Security Layer  
4. Multi‑OS CI/CD

## Tests

```bash
python -m pytest -q
```

## Contributing

Issues and pull requests are welcome.

## License

MIT — see [LICENSE](LICENSE).

## Author

Alexandre Albert Ndour

## Support

If you like this project, give it a ⭐ on GitHub.

French version: see [README.fr.md](README.fr.md).
