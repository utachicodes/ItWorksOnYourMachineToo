# LexWorksEverywhere Contributor Guide

Thank you for your interest in contributing to LexWorksEverywhere! This guide will help you get started with contributing to the project.

## Getting Started

### Prerequisites

To contribute to LexWorksEverywhere, you need:

- Python 3.12 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. Fork the LexWorksEverywhere repository on GitHub
2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/lexworkseverywhere.git
cd lexworkseverywhere
```

3. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install LexWorksEverywhere in development mode:

```bash
pip install -e ".[dev]"
```

## Project Structure

LexWorksEverywhere follows a modular architecture:

```
lexworkseverywhere/
├── cli/                 # Command-line interface
├── scanner/             # Project scanning functionality
├── profiler/            # Environment profiling
├── adapters/            # OS-specific adapters
│   ├── windows/         # Windows adapter
│   ├── macos/           # macOS adapter
│   └── linux/           # Linux adapter
├── runtime/             # Runtime orchestration
├── diagnostics/         # Diagnostic engine
├── tests/               # Test suite
└── docs/                # Documentation
```

## Contributing Code

### Finding Issues

- Look for issues labeled `good first issue` if you're new to the project
- Check issues labeled `help wanted` for more substantial contributions
- Create an issue if you've found a bug or have a feature request

### Making Changes

1. Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the coding standards below
3. Add or update tests as needed
4. Update documentation if necessary
5. Run the tests to ensure everything works:

```bash
python -m pytest tests/
```

6. Commit your changes with a descriptive commit message
7. Push your branch to your fork
8. Create a pull request to the main repository

### Coding Standards

- Follow PEP 8 style guidelines
- Write clear, descriptive function and variable names
- Add type hints to all function signatures
- Include docstrings for all public functions and classes
- Keep functions focused and small when possible
- Write comprehensive tests for new functionality

### Testing

LexWorksEverywhere maintains high test coverage. All contributions must include:

- Unit tests for new functionality
- Integration tests where appropriate
- Tests that cover edge cases

Run all tests before submitting a pull request:

```bash
python -m pytest tests/ -v
```

To check test coverage:

```bash
python -m pytest tests/ --cov=lexworkseverywhere --cov-report=html
```

## Architecture Guidelines

### Project Scanner Module

- Detect project types using file extensions and dependency files
- Identify project entrypoints using conventional names
- Extract dependencies from project-specific files
- Return structured JSON data

### Environment Profiler Module

- Capture system-specific information comprehensively
- Filter sensitive environment variables
- Include hardware and network information
- Save profiles in `.lexworkseverywhere.json` format

### OS Adapters Module

- Implement the `BaseAdapter` interface
- Handle path conversions between OS formats
- Convert scripts between shell types
- Map package manager commands appropriately
- Normalize environment variables

### Runtime Orchestrator Module

- Prepare environments safely with rollback capability
- Install runtimes and dependencies as needed
- Execute projects in isolated environments
- Handle errors gracefully

### Diagnostic Engine Module

- Identify common error patterns
- Classify errors into meaningful categories
- Provide actionable solutions
- Implement automated fixes where possible

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use the Google Python docstring style
- Document all parameters, return values, and exceptions

### User Documentation

- Update the user guide when adding new features
- Add architecture documentation for significant changes
- Include examples for new functionality

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Add tests for new functionality
3. Update documentation as needed
4. Run all tests to ensure they pass
5. Submit your pull request with a clear description of the changes
6. Address any feedback from code reviews
7. Wait for approval before merging

## Community Guidelines

- Be respectful and inclusive in all interactions
- Provide constructive feedback during code reviews
- Help new contributors get started
- Follow the project's code of conduct

## Getting Help

If you need help with your contribution:

- Open an issue with your question
- Check the existing documentation
- Look at similar implementations in the codebase

Thank you for contributing to LexWorksEverywhere! Your efforts help make cross-platform development easier for everyone.