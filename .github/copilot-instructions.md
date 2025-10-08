# GitHub Copilot Instructions for svtplay-dl

## Project Overview

svtplay-dl is a command-line program to download videos from various video on demand sites, primarily Swedish streaming services. The project is written in Python and requires Python 3.8 or higher.

## Project Structure

```
svtplay-dl/
├── lib/
│   └── svtplay_dl/         # Main source code
│       ├── fetcher/        # Download protocols (HLS, DASH, HTTP)
│       ├── service/        # Service-specific implementations
│       ├── subtitle/       # Subtitle handling
│       └── utils/          # Utility functions (parser, output, etc.)
├── bin/                    # Entry point scripts
├── scripts/                # Build and CI scripts
├── tests/                  # Test files
└── docs/                   # Documentation

```

## Coding Standards

### Style Guidelines
- **Formatter**: Black with line-length of 150 characters
- **Target Version**: Python 3.9+ (use pyupgrade with --py39-plus)
- **Import Ordering**: Use reorder_python_imports
- **Linting**: flake8

### Pre-commit Hooks
The project uses pre-commit hooks for automatic code quality checks:
- trailing-whitespace removal
- end-of-file-fixer
- black formatter
- flake8 linter
- pyupgrade for Python 3.9+ syntax
- reorder_python_imports
- add-trailing-comma

Run `pre-commit run --all-files` before committing changes.

## Dependencies

### Core Dependencies
- **requests**: HTTP client library (>=2.0.0)
- **PySocks**: Proxy support
- **cryptography**: For encrypted HLS streams
- **pyyaml**: Configuration file support

### Development Dependencies
- pytest and pytest-cov for testing
- pre-commit for code quality
- tox for testing across environments
- cx_Freeze for Windows builds

## Building and Testing

### Running Tests
```bash
# Run all tests
pytest -v --cov

# Run pre-commit checks
pre-commit run --all-files
```

### Building the Application
```bash
# Build svtplay-dl executable
make

# Run the built executable
./svtplay-dl --version
```

### Windows Builds
```bash
python setversion.py
python setup.py build_exe
```

## Configuration System

The project uses YAML configuration files:
- Default location: `~/.svtplay-dl.yaml` (or `XDG_CONFIG_HOME/svtplay-dl/svtplay-dl.yaml`)
- Configuration can specify service-specific settings
- Supports presets for common download scenarios

Configuration is parsed in `lib/svtplay_dl/utils/parser.py`.

## Service Implementation Pattern

When adding support for a new streaming service:
1. Create a new file in `lib/svtplay_dl/service/`
2. Inherit from the base service class
3. Implement required methods for URL parsing and stream extraction
4. Register the service in the service registry

## Common Patterns

### Error Handling
Use the custom error classes defined in `lib/svtplay_dl/error.py`.

### Output Formatting
Use utilities from `lib/svtplay_dl/utils/output.py` for consistent output formatting.

### Parser Options
Command-line options are defined in `lib/svtplay_dl/utils/parser.py` using argparse.

## Important Guidelines

1. **Minimal Changes**: Make the smallest possible changes to achieve the goal
2. **Backward Compatibility**: Maintain compatibility with existing configuration files and command-line options
3. **Cross-Platform**: Ensure changes work on Linux, macOS, and Windows
4. **Testing**: Add or update tests for any new functionality
5. **Documentation**: Update README.md and docstrings for significant changes

## Version Management

The project uses versioneer for automatic version management from git tags:
- Version is automatically derived from git tags
- Format: `MAJOR.MINOR.PATCH` (e.g., 1.9.11)
- Don't manually edit version numbers

## CI/CD

The project uses GitHub Actions for CI:
- Tests run on multiple Python versions (3.9-3.13)
- Tests run on Linux and Windows (including x86)
- Pre-commit hooks are validated
- Binaries are built for distribution

## License

MIT License - be mindful of this when adding new dependencies or code.
