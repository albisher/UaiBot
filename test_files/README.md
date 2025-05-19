# UaiBot File Operation Tests

This directory contains test scripts and sample files for testing UaiBot's file operation capabilities.

## Key Findings from Testing

1. **File Listing**: The most reliable command for listing files is `Display all files in test_files`
2. **Media Creation**: Media file creation requires the `--no-safe-mode` flag
3. **File Deletion**: File deletion operations require confirmation with 'y'
4. **Arabic Text**: Works well for file operations but needs proper quoting

## Test Utilities

### `direct_command_test.py`

Test a single command directly from the command line.

```bash
python test_files/direct_command_test.py "Display all files in test_files"
python test_files/direct_command_test.py "Create an image file test_files/drawing.png" --no-safe-mode
```

### `run_file_tests.py`

Run all tests from the `ai_human_requests.txt` file.

```bash
python test_files/run_file_tests.py
```

### `fix_list_files.py`

Test specifically for file listing operations.

```bash
python test_files/fix_list_files.py
```

### `media_test.py`

Test media file creation operations with the necessary `--no-safe-mode` flag.

```bash
python test_files/media_test.py
```

## Common Issues and Solutions

1. **File Listing Issues**: 
   - Use `Display all files in [directory]` instead of "List files" or "Show files"
   - This command translates to `ls [directory]` properly

2. **Media File Creation Issues**:
   - Always use `--no-safe-mode` flag
   - Commands like `convert` for image creation are blocked in safe mode

3. **File Deletion Confirmation**:
   - Use `echo y |` to pipe 'y' to deletion confirmation prompts

4. **Arabic Text Support**:
   - Works well for basic file operations
   - Use double quotes around Arabic text for best results
