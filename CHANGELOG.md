# Changelog

## Unreleased

- Refactored the `export` command's exporters (devcontainer, brewfile, winget,
  apt, nix, ansible, docker-compose) out of `cli/main.py` into a dedicated
  `exporters` package, dispatched through a registry
- Fixed `docker-compose` export to write real YAML instead of JSON and
  dropped the obsolete top-level `version` field
- Fixed `doctor`'s Python version check, which accepted 3.9 even though the
  package requires Python >=3.10
- Fixed install-suggestion messages (macOS/Linux/Windows adapters) and the
  missing-tool panel always showing French text regardless of `--lang`
- Moved CLI/export tests that lived under the installed package into the
  root `tests/` directory so they're actually collected by `pytest`/CI
  (previously silently excluded by `testpaths = ["tests"]`)
- Removed dead code: the unused `DependencyManager`, `core.utils`
  (`logging_utils`, `security_utils`, `performance`), and the v1-era
  `BaseAdapter`, none of which were referenced anywhere in the codebase
- Translated remaining French docstrings/comments in core modules and
  adapters to English for consistency with the rest of the codebase
- Added test coverage for the planner cache, `_build_command`, config
  loader, i18n, validator fix proposals, and the `init`/`list`/`capture`
  CLI commands

## 2.1.0

- Cross-platform development environment manager
- Project detection for Python, Node.js, Go, Rust, C/C++, Ruby, Dart, and more
- Execution plan generation with OS-adapted paths and scripts
- DevContainer, Brewfile, Winget, Apt, and Nix export support
- Built-in Doctor for host readiness checks and safe auto-fixes
- System profiler capturing runtime versions and environment variables
- Sandboxed execution with integrity verification
- CLI with English and French language support
- Multi-OS CI/CD (Ubuntu, macOS, Windows) with coverage reporting
