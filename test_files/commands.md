# UaiBot Test Commands

This document contains common commands for testing the UaiBot project. All commands should be run from the project root directory.

## Basic Test Commands

Run all tests:
```bash
python test_files/run_tests.py --all
```

Run unit tests only:
```bash
python test_files/run_tests.py --unit
```

Run flag tests:
```bash
python test_files/run_tests.py --flag-tests
```

Run human-like interaction tests:
```bash
python test_files/run_tests.py --interaction
```

## Testing main.py with -f Flag

Test main.py with a single file:
```bash
python main.py -f test_files/unit/sample.txt
```

Test main.py with multiple files:
```bash
python main.py -f test_files/unit/sample1.txt test_files/unit/sample2.txt
```

Using the test runner to test main.py with -f flag:
```bash
python test_files/run_tests.py --main-f test_files/unit/sample.txt
```

## Platform-specific Tests

### macOS/Linux

Running main.py with a file containing spaces:
```bash
python main.py -f "test_files/unit/sample file.txt"
```

Using file with special characters:
```bash
python main.py -f "test_files/unit/sample_\$pecial.txt"
```

### Windows

Running main.py with a file containing spaces:
```batch
python main.py -f "test_files\unit\sample file.txt"
```

> **Note**: On macOS/Linux, use forward slashes (`/`). On Windows, use backslashes (`\`).

## Creating Test Files and Directories

First, create required test directories:
```bash
# Create test directory structure
mkdir -p test_files/unit test_files/integration test_files/system test_files/human_interaction
```

Create sample test file:
```bash
echo "This is a test file" > test_files/unit/sample.txt
```

Create binary test file:
```python
python -c "with open('test_files/unit/sample_binary.bin', 'wb') as f: f.write(bytes(range(256)))"
```

## Running Script Issues

### macOS/Linux Users
For shell scripts, make them executable first:
```bash
chmod +x test_files/run_pytest.sh
./test_files/run_pytest.sh --all
```

### Windows Users
For batch files, run them directly:
```cmd
test_files\run_pytest.bat --all
```

> **Note**: On macOS, don't try to run Windows batch files with backslashes. Use the macOS version of the script instead.

## Mouse and Keyboard Tests

Run mouse simulation test:
```bash
python test_files/mouse_simulator.py
```

Run keyboard simulation test:
```bash
python test_files/keyboard_simulator.py
```

Run sound simulation test:
```bash
python test_files/sound_simulator.py
```

## Troubleshooting

If you encounter a `KeyboardInterrupt` with the human interaction test, try running it with a timeout:
```bash
python test_files/run_tests.py --interaction --timeout 30
```

If you see "No test files found" error, ensure you've created the required test directories and files.
