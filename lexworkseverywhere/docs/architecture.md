# LexWorksEverywhere Architecture

LexWorksEverywhere is built with a modular architecture that enables cross-platform development environment management. This document describes the system architecture and how components interact.

## Overview

LexWorksEverywhere consists of six core modules that work together to provide cross-platform development environment management:

1. **Project Scanner** - Detects project types and dependencies
2. **Environment Profiler** - Captures system-specific environment information
3. **OS Adapters** - Handles OS-specific differences (Windows, macOS, Linux)
4. **Runtime Orchestrator** - Manages environment setup and project execution
5. **Diagnostic Engine** - Analyzes and fixes environment-related issues
6. **CLI Interface** - Provides command-line access to all functionality

## Module Architecture

### Project Scanner

The Project Scanner module is responsible for analyzing project directories to determine:

- Project type (Python, Node.js, Java, etc.)
- Project entrypoint
- Dependencies
- Build scripts
- Configuration files

The scanner uses file extension patterns, dependency files, and entrypoint conventions to identify project characteristics.

### Environment Profiler

The Environment Profiler captures system-specific information including:

- Operating system details
- Installed runtimes and versions
- Hardware specifications
- Environment variables
- Network configuration
- File system characteristics

This information is saved in `.lexworkseverywhere.json` files for environment reproduction.

### OS Adapters

The OS Adapter module is the core of LexWorksEverywhere's cross-platform capability. It includes:

- **BaseAdapter**: Abstract interface for all OS adapters
- **WindowsAdapter**: Windows-specific path, command, and environment handling
- **MacOSAdapter**: macOS-specific path, command, and environment handling
- **LinuxAdapter**: Linux-specific path, command, and environment handling

Adapters handle:
- Path conversion between OS formats
- Script conversion between shell types
- Package manager command mapping
- Environment variable normalization

### Runtime Orchestrator

The Runtime Orchestrator manages the complete project execution lifecycle:

- Environment preparation and setup
- Runtime installation if needed
- Dependency installation
- Project execution
- Environment rollback on failure

### Diagnostic Engine

The Diagnostic Engine analyzes execution errors and provides:

- Error pattern matching
- Issue classification
- Automated fix suggestions
- Automatic fix application
- Re-testing after fixes

### CLI Interface

The CLI provides the user-facing commands:

- `lexworkseverywhere scan` - Analyze project structure
- `lexworkseverywhere capture` - Profile current environment
- `lexworkseverywhere run` - Execute project in managed environment
- `lexworkseverywhere diagnose` - Analyze and fix environment issues
- `lexworkseverywhere test` - Validate environment compatibility

## Data Flow

The typical data flow in LexWorksEverywhere is:

1. **Scan**: Project Scanner analyzes project directory
2. **Profile**: Environment Profiler captures system state
3. **Adapt**: OS Adapters convert requirements for target OS
4. **Orchestrate**: Runtime Orchestrator sets up environment
5. **Execute**: Project runs in managed environment
6. **Diagnose**: Diagnostic Engine handles any issues

## Cross-Platform Strategy

LexWorksEverywhere achieves cross-platform compatibility through:

- **Declarative mappings**: OS-specific configurations are defined declaratively
- **Adapter pattern**: Each OS has specific handling logic
- **Path normalization**: Automatic conversion between path formats
- **Command mapping**: Translation of OS-specific commands
- **Environment abstraction**: Normalization of environment variables

This architecture ensures that projects can run consistently across different operating systems without manual configuration.