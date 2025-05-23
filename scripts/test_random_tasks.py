#!/usr/bin/env python3
"""
Script to run random system task tests and generate a report.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import pytest

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tests() -> dict:
    """Run the random tasks tests and return results."""
    # Run pytest with the random tasks test file
    test_file = Path(__file__).parent.parent / "tests" / "unit" / "test_random_tasks.py"
    
    # Run tests and capture results
    result = pytest.main([
        str(test_file),
        "-v",
        "--json-report",
        "--json-report-file=none"
    ])
    
    return {
        "timestamp": datetime.now().isoformat(),
        "exit_code": result,
        "test_file": str(test_file)
    }

def generate_report(results: dict) -> None:
    """Generate a test report."""
    report_dir = Path("test_reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"random_tasks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Test report generated: {report_file}")

def main():
    """Main function to run tests and generate report."""
    try:
        logger.info("Starting random tasks tests...")
        results = run_tests()
        generate_report(results)
        logger.info("Tests completed successfully")
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 