# UaiBot Reorganization Plan

## Directory Structure Consolidation

### 1. Test Organization
- Move all test files to `tests/` directory
  - Move `test_files/input_control/` → `tests/input_control/`
  - Move `test_files/results/` → `tests/results/`
  - Move `test_files/t250521/` → `tests/results/t250521/`
  - Keep `test_files/` only for test data and fixtures

### 2. Command Processor Consolidation
- Consolidate all command processor files under `uaibot/core/command_processor/`
  - Move `command_processor.py` (root) → `uaibot/core/command_processor/`
  - Move `command_processor/` directory contents → `uaibot/core/command_processor/`
  - Move `uaibot/command_processor.py` → `uaibot/core/command_processor/`
  - Update imports accordingly

### 3. Documentation Consolidation
- Move all documentation to `documentation/` (root)
  - Move `uaibot/documentation/` contents → `documentation/`
  - Organize by component/feature
  - Remove empty `uaibot/documentation/` directory

### 4. Utils Consolidation
- Consolidate all utility files under `uaibot/utils/`
  - Move `utils/` (root) contents → `uaibot/utils/`
  - Move `uaibot/file_utils.py` → `uaibot/utils/file_utils.py`
  - Move `uaibot/parallel_utils.py` → `uaibot/utils/parallel_utils.py`
  - Update imports accordingly

### 5. Log Consolidation
- Consolidate all logs under `logs/` (root)
  - Move `uaibot/log/` contents → `logs/uaibot/`
  - Move `test_files/logs/` contents → `logs/tests/`
  - Update logging configuration to use new paths

## Implementation Steps

1. Create new directory structure
2. Move files to new locations
3. Update imports and references
4. Update configuration files
5. Test the changes
6. Remove old directories

## Configuration Updates Needed

1. Update `uaibot/config/output_paths.py`
2. Update `uaibot/logging_config.py`
3. Update `tests/conftest.py`
4. Update `.gitignore`

## Testing Plan

1. Run all tests after each major move
2. Verify logging works correctly
3. Verify documentation is accessible
4. Verify command processor functionality
5. Verify utility functions work

## Notes
- regex = false at all times
- Focus on AI-driven approach for command interpretation
- Ensure cross-platform compatibility
- Maintain virtual environment setup

## Next Steps
1. Run the test suite to verify all changes
2. Update any remaining import paths in other files
3. Verify all documentation is up to date
4. Check for any remaining files that need to be moved 