# Input Control Test Suite

This directory contains test scripts for the UaiBot input control system.

## Test Files

- `debug_mouse_keyboard.py`: Detailed debugging tool for mouse and keyboard handlers
- `basic_simulation_test.py`: Simple test for simulation mode
- `comprehensive_simulation_test.py`: In-depth test of all input control features in simulation mode
- `minimal_simulation_test.py`: Minimal test case for simulation mode
- `test_input_control.py`: Main test suite for the input control system

## Running Tests

To run all tests:

```bash
cd /path/to/UaiBot
python -m unittest discover tests/input_control
```

To run a specific test:

```bash
python tests/input_control/test_input_control.py
```

## Forcing Simulation Mode

You can force simulation mode by setting the DISPLAY environment variable to an empty string:

```bash
DISPLAY= python tests/input_control/test_input_control.py
```

## Test Categories

1. **Basic Functionality Tests**
   - Tests basic mouse and keyboard operations
   - Verifies that the handlers can be instantiated

2. **Cross-Platform Tests**
   - Tests platform detection and handler selection
   - Ensures that the correct handler is loaded based on the platform

3. **Simulation Mode Tests**
   - Tests behavior in environments without display access
   - Verifies that operations are properly simulated

4. **Compatibility Tests**
   - Tests the backward compatibility layer
   - Ensures that code using the old API continues to work
