@echo off
:: Simple script to run pytest on UaiBot test files for Windows

setlocal

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo =======================================
echo Running UaiBot tests with pytest
echo =======================================
echo Project root: %PROJECT_ROOT%
echo Test directory: %SCRIPT_DIR%
python --version
echo =======================================

:: Check if pytest is installed
python -c "import pytest" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: pytest is not installed.
    echo Please install pytest with: pip install pytest
    exit /b 1
)

:: Run tests based on arguments
if "%1"=="--all" (
    echo Running all tests...
    python -m pytest "%SCRIPT_DIR%" -v
) else if "%1"=="--unit" (
    echo Running unit tests...
    python -m pytest "%SCRIPT_DIR%unit" -v
) else if "%1"=="--human" (
    echo Running human interaction tests...
    python "%SCRIPT_DIR%human_interaction_test.py"
) else if "%1"=="--main-f" (
    if "%2"=="" (
        echo Error: No file specified for --main-f option.
        echo Usage: %0 --main-f ^<file_path^>
        exit /b 1
    )
    
    echo Testing main.py with -f flag and file: %2
    python "%PROJECT_ROOT%\main.py" -f "%2"
) else (
    :: Default: show help
    echo UaiBot Test Runner
    echo Usage: %0 [option]
    echo Options:
    echo   --all      Run all tests
    echo   --unit     Run unit tests only
    echo   --human    Run human interaction tests
    echo   --main-f ^<file^>  Test main.py with -f flag and specified file
    echo.
    echo Examples:
    echo   %0 --all
    echo   %0 --unit
    echo   %0 --main-f test_files\unit\sample.txt
)

exit /b 0
