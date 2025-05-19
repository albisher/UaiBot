#!/bin/bash
# Simple script to run pytest on UaiBot test files

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}Running UaiBot tests with pytest${NC}"
echo -e "${YELLOW}=======================================${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Test directory: $SCRIPT_DIR"
echo -e "Python: $(python --version)"
echo -e "${YELLOW}=======================================${NC}"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed.${NC}"
    echo "Please install pytest with: pip install pytest"
    exit 1
fi

# Run tests based on arguments
if [ "$1" == "--all" ]; then
    echo -e "${GREEN}Running all tests...${NC}"
    python -m pytest "$SCRIPT_DIR" -v
elif [ "$1" == "--unit" ]; then
    echo -e "${GREEN}Running unit tests...${NC}"
    python -m pytest "$SCRIPT_DIR/unit" -v
elif [ "$1" == "--human" ]; then
    echo -e "${GREEN}Running human interaction tests...${NC}"
    python "$SCRIPT_DIR/human_interaction_test.py"
elif [ "$1" == "--main-f" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}Error: No file specified for --main-f option.${NC}"
        echo "Usage: $0 --main-f <file_path>"
        exit 1
    fi
    
    echo -e "${GREEN}Testing main.py with -f flag and file: $2${NC}"
    python "$PROJECT_ROOT/main.py" -f "$2"
else
    # Default: show help
    echo -e "${YELLOW}UaiBot Test Runner${NC}"
    echo -e "Usage: $0 [option]"
    echo -e "Options:"
    echo -e "  --all      Run all tests"
    echo -e "  --unit     Run unit tests only"
    echo -e "  --human    Run human interaction tests"
    echo -e "  --main-f <file>  Test main.py with -f flag and specified file"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 --all"
    echo -e "  $0 --unit"
    echo -e "  $0 --main-f test_files/unit/sample.txt"
fi

exit 0
