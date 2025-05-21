# UaiBot Sequence Test Documentation

## Overview
The sequence test is a comprehensive integration test that verifies UaiBot's ability to execute a series of commands in a specific order. This test ensures that UaiBot can handle various types of interactions including web searches, browser control, system volume adjustment, and media playback.

## Test Location
The test is implemented in `tests/integration/test_sequence_commands.py`

## Test Sequence
The test executes the following commands in sequence:

1. **Environment Setup**
   - Sets the `PYTHONPATH` environment variable
   - Ensures proper module importation

2. **Web Search**
   - Command: "where is Kuwait"
   - Tests basic search functionality

3. **Browser Interaction**
   - Command: "in that browser click the middle link"
   - Tests link clicking capability

4. **Browser Focus**
   - Command: "make that browser more focused on the text"
   - Tests browser focus adjustment

5. **System Control**
   - Command: "increase volume to 80%"
   - Tests system volume control

6. **Browser Navigation**
   - Command: "now in safari go to youtube"
   - Tests browser-specific navigation

7. **Contextual Search**
   - Command: "in there search for Quran by Al Husay"
   - Tests search within specific context

8. **Media Playback**
   - Command: "play that and cast it to my tv"
   - Tests media playback and casting

## Implementation Details

### Test Structure
- Uses pytest fixtures for UaiBot instance management
- Implements proper logging for visibility
- Includes assertions for each command execution
- Handles cleanup after test completion

### Dependencies
- pytest
- UaiBot core modules
- System utilities for browser and media control

### Running the Test
```bash
# From project root
pytest tests/integration/test_sequence_commands.py -v
```

## Logging
Each step is logged to provide visibility into the test progress. Logs include:
- Step number and description
- Command execution status
- Any errors or failures

## Error Handling
- Each command execution is wrapped in assertions
- Detailed error messages are provided for failed commands
- Proper cleanup is performed regardless of test outcome

## Maintenance
- Test should be updated if command syntax changes
- New commands can be added to the sequence
- Browser and system-specific commands may need adjustment for different platforms 