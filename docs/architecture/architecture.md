# Project Architecture

## Directory Structure

```
.
├── .git
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── .venv/                          # Virtual environment (gitignored)
├── .vscode/                        # Optional: For team editor consistency
│   ├── mcp.json
│   └── settings.json
├── COMMERCIAL_LICENSE
├── LICENSE
├── README.md
├── TODO.md
├── config/                         # Application configuration
│   ├── command_patterns.json
│   ├── keys/
│   │   └── encrypted_keys.json
│   ├── output_styles.json
│   └── settings.json
├── docs/                           # All project documentation
│   ├── agents_tools/
│   ├── architecture/
│   ├── features/
│   ├── research/                   # Consolidated research documents
│   └── ...                         # Other .md files
├── locales/                        # Internationalization files
│   ├── ar/
│   │   └── LC_MESSAGES/
│   │       ├── labeeb.mo
│   │       └── labeeb.po
│   └── en/
├── pyproject.toml                  # Main project definition
├── requirements.txt                # Optional: For specific pip-based envs or generated
├── setup.py                        # Optional: May be minimal with modern pyproject.toml
├── scripts/                        # Utility scripts
│   ├── audit_project.py
│   ├── compile_translations.py
│   └── ...
├── src/                            # Main source code
│   ├── __init__.py
│   └── labeeb/                     # Main application package
│       ├── __init__.py
│       ├── __main__.py             # Entry point if run as a module
│       ├── ai/                     # AI-related modules
│       ├── awareness/              # Awareness modules and tools
│       ├── command_processing/     # Command processing logic
│       ├── config_loader/          # For loading app-specific configurations
│       ├── constants/              # Application-wide constants
│       ├── core/                   # Other core business logic
│       ├── data_models/            # Pydantic models or data structures
│       ├── exceptions/             # Custom exceptions
│       ├── platform_services/      # Platform-specific abstractions
│       │   ├── __init__.py
│       │   ├── common_interface.py
│       │   ├── linux/
│       │   ├── macos/
│       │   └── windows/
│       ├── services/               # Higher-level services
│       ├── tools/                  # General application tools
│       ├── ui/                     # User interface components
│       └── utils/                  # Utilities specific to the package
├── tests/                          # All tests
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures and hooks
│   ├── fixtures/                   # Test fixtures data
│   ├── integration/                # Integration tests
│   │   └── labeeb/                 # Mirror src structure
│   ├── unit/                       # Unit tests
│   │   └── labeeb/                 # Mirror src structure
│   ├── e2e/                        # End-to-end tests
│   ├── test_files/                 # Files needed for running tests
│   └── screenshots/                # Test screenshots
└── reports/                        # Gitignored: For test results, coverage reports
    ├── coverage/
    │   ├── htmlcov/
    │   └── coverage.xml
    └── test_results/
```

## Key Principles

1. **Source Code Organization**
   - All source code lives in `src/labeeb/`
   - Clear separation of concerns with modular packages
   - Platform-specific code isolated in `platform_services/`
   - Tools and utilities properly categorized

2. **Testing Structure**
   - All tests in top-level `tests/` directory
   - Tests mirror source code structure
   - Separate directories for unit, integration, and e2e tests
   - Test fixtures and data in dedicated directories

3. **Documentation**
   - All documentation in `docs/`
   - Research materials consolidated in `docs/research/`
   - Architecture and feature documentation maintained
   - Clear separation of concerns in documentation

4. **Configuration**
   - All configuration in `config/`
   - Sensitive data properly handled
   - Environment-specific configs supported

5. **Build and Dependencies**
   - Modern Python packaging with `pyproject.toml`
   - Virtual environment management
   - Clear dependency specification
   - Build artifacts properly gitignored

6. **Reports and Outputs**
   - All reports in `reports/`
   - Coverage reports in `reports/coverage/`
   - Test results in `reports/test_results/`
   - Logs in top-level `logs/`

7. **Internationalization**
   - All translations in `locales/`
   - Clear structure for language support
   - Easy to add new languages

8. **Scripts and Utilities**
   - All utility scripts in `scripts/`
   - Clear purpose for each script
   - Well-documented functionality

## Best Practices

1. **Version Control**
   - Comprehensive `.gitignore`
   - No backup files or directories
   - No sensitive data in repository
   - Clear commit messages

2. **Code Quality**
   - Type hints throughout
   - Comprehensive testing
   - Clear documentation
   - Consistent style

3. **Security**
   - Sensitive data properly handled
   - Keys and credentials gitignored
   - Secure configuration management

4. **Maintainability**
   - Clear directory structure
   - Consistent naming conventions
   - Modular design
   - Separation of concerns

5. **Development Workflow**
   - Virtual environment usage
   - Pre-commit hooks
   - CI/CD integration
   - Clear development guidelines 