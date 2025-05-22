# UaiBot Test Suite

This directory contains the test suite for UaiBot. The tests are organized by module and type, following a structured approach to ensure comprehensive coverage and maintainability.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py
├── pytest.ini
├── requirements-test.txt
├── run_tests.py
├── core/
│   ├── command_processor/
│   ├── file_operations/
│   └── ai/
├── integration/
│   └── api/
├── system/
│   └── performance/
└── data/
    ├── test_files/
    └── test_configs/
```

## Test Categories

### Unit Tests
- Location: `tests/core/`
- Purpose: Test individual components
- Coverage: 80% minimum
- Timeout: 5 seconds

### Integration Tests
- Location: `tests/integration/`
- Purpose: Test component interactions
- Coverage: 70% minimum
- Timeout: 30 seconds

### System Tests
- Location: `tests/system/`
- Purpose: Test system-wide functionality
- Coverage: 60% minimum
- Timeout: 60 seconds

## Running Tests

### Prerequisites
1. Python 3.8 or higher
2. Virtual environment (recommended)
3. Test dependencies installed

### Installation
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install test dependencies
pip install -r tests/requirements-test.txt
```

### Running All Tests
```bash
python tests/run_tests.py
```

### Running Specific Test Categories
```bash
# Run unit tests
python tests/run_tests.py -m unit

# Run integration tests
python tests/run_tests.py -m integration

# Run system tests
python tests/run_tests.py -m system
```

### Running with Coverage
```bash
python tests/run_tests.py --cov=app --cov-report=html
```

## Test Configuration

### pytest.ini
Contains test configuration settings, including:
- Test discovery patterns
- Markers
- Coverage settings
- Output formats

### conftest.py
Contains shared test fixtures and configuration:
- Test data directory
- Mock objects
- Common utilities
- Environment setup

## Test Data

### Test Files
- Location: `tests/data/test_files/`
- Purpose: Sample files for file operation tests
- Types: Text files, configuration files, etc.

### Test Configurations
- Location: `tests/data/test_configs/`
- Purpose: Configuration files for different test scenarios
- Types: Development, production, testing configurations

## Test Reports

### Coverage Reports
- HTML coverage reports
- XML coverage reports
- Console coverage summary

### Test Reports
- HTML test reports
- JUnit XML reports
- Console test summary

## Best Practices

### Writing Tests
1. Follow the AAA pattern (Arrange, Act, Assert)
2. Use descriptive test names
3. Keep tests independent
4. Use appropriate fixtures
5. Mock external dependencies

### Test Organization
1. Group related tests in classes
2. Use appropriate markers
3. Follow the directory structure
4. Maintain test data separately

### Test Maintenance
1. Regular review of test coverage
2. Update tests with code changes
3. Clean up obsolete tests
4. Maintain test documentation

## Troubleshooting

### Common Issues
1. Import errors
   - Check PYTHONPATH
   - Verify import statements
   - Check module structure

2. Test discovery issues
   - Verify test file naming
   - Check directory structure
   - Verify __init__.py files

3. Coverage issues
   - Check coverage configuration
   - Verify source paths
   - Check exclusion patterns

### Getting Help
1. Check test documentation
2. Review test logs
3. Check test reports
4. Contact development team

## Contributing

### Adding New Tests
1. Follow the directory structure
2. Use appropriate test categories
3. Add necessary fixtures
4. Update documentation

### Modifying Tests
1. Maintain test independence
2. Update related documentation
3. Verify test coverage
4. Run all affected tests

### Test Review Process
1. Code review required
2. Verify test coverage
3. Check test documentation
4. Run all tests 