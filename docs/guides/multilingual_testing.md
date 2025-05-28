# Labeeb Multilingual Testing

This document explains how to test Labeeb's multilingual capabilities, particularly for Arabic and English language support. Labeeb is designed to process and respond to commands in multiple languages, and these tests ensure that this functionality works as expected.

## Testing Scripts

Labeeb's multilingual testing framework includes several key scripts:

1. **test_multilingual.py**: Main test script that runs a suite of tests in both Arabic and English
2. **run_multilingual_tests.py**: A convenient runner script with additional options
3. **verify_multilingual.py**: Script for focused verification of specific features

## Running Tests

### Basic Testing

To run tests in both languages:

```bash
python tests/run_multilingual_tests.py
```

### Testing Specific Languages

Test only Arabic commands:

```bash
python tests/run_multilingual_tests.py --language arabic
```

Test only English commands:

```bash
python tests/run_multilingual_tests.py --language english
```

### Comparing AI Providers

Compare results between different AI providers:

```bash
python tests/run_multilingual_tests.py --compare-providers
```

This will run the tests with both Ollama and Google AI providers and compare the results.

### Verification Testing

For targeted verification:

```bash
python tests/verify_multilingual.py
```

To verify specific categories:

```bash
python tests/verify_multilingual.py --category file_operations
```

## Test Categories

The multilingual tests cover several key areas:

1. **File Operations**: Creating, reading, and deleting files
2. **System Information**: Querying OS information, disk space, etc.
3. **Command Execution**: Running shell commands through Labeeb

## Test Results

Test results are saved in two formats:

1. **JSON**: Raw test results with detailed information about each test
2. **Markdown**: Human-readable reports summarizing test results

These files are saved in the `tests/results` and `tests/reports` directories, with timestamps to track different test runs.

## Arabic Language Support

Labeeb's Arabic language support includes:

1. Recognition of Arabic commands for file operations
2. Ability to process Arabic text in system queries
3. Handling Arabic text in file content
4. Generating appropriate Arabic responses

Example Arabic commands tested:

- `أنشئ ملف جديد باسم test_output_ar.txt واكتب فيه 'هذا ملف اختبار'` - Create a new file
- `اعرض محتوى الملف test_output_ar.txt` - Show file content
- `اعرض جميع الملفات في المجلد الحالي` - List all files
- `ما هو نظام التشغيل الذي أستخدمه؟` - What OS am I using?
- `أظهر المساحة المتاحة على القرص` - Show available disk space
- `احذف الملف test_output_ar.txt` - Delete the file

## Test Validation

Each test is validated by checking:

1. Whether the command executed successfully
2. Whether the output contains expected keywords or content
3. Whether any error messages are present
4. Whether file operations produced the expected changes

## Extending the Tests

To add new test cases:

1. Add new entries to the `ENGLISH_TEST_CASES` and `ARABIC_TEST_CASES` lists in `test_multilingual.py`
2. Add new categories or commands to `VERIFICATION_TESTS` in `verify_multilingual.py`
3. Run the tests to validate the new cases

## Troubleshooting

If tests fail:

1. Check if Labeeb's dependencies are properly installed
2. Verify that the AI provider (Ollama or Google) is correctly configured
3. Look for error messages in the test output
4. Check the detailed reports in the `tests/reports` directory
5. Try running individual tests to isolate the issue

For AI-specific issues, try switching between providers using the `--ai-provider` flag.
