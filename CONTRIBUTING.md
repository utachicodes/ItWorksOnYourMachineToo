# Contributing to ItWorksOnYourMachineToo

Thanks for your interest in contributing.

## Quick Start

```bash
git clone https://github.com/utachicodes/ItWorksOnYourMachineToo.git
cd ItWorksOnYourMachineToo
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e .
pip install pytest flake8
```

## Development Workflow

1. Create a branch for your change
2. Make your changes
3. Run linting and tests:

```bash
flake8 ItWorksOnYourMachineToo
python -m pytest -q
```

4. Submit a pull request

## Coding Standards

- PEP 8 style (enforced by flake8, 120 char line limit)
- Type hints on all function signatures
- Docstrings on all public functions and classes
- Tests for new functionality

## Project Layout

- `ItWorksOnYourMachineToo/cli/` -- command-line interface
- `ItWorksOnYourMachineToo/core/` -- planner, engine, validator, profiler
- `ItWorksOnYourMachineToo/adapters/` -- OS-specific adapters (Windows, macOS, Linux)
- `ItWorksOnYourMachineToo/dependencies/` -- dependency resolution
- `tests/` -- test suite

For detailed architecture docs, see `ItWorksOnYourMachineToo/docs/contributor_guide.md`.
