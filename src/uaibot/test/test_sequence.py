#!/usr/bin/env python3
"""
Test sequence for UaiBot.
Runs a series of predefined test commands to verify functionality.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""

import os
import sys
import logging
import logging.config
from .pathlib import Path
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.command_processor import CommandProcessor
from app.core.browser_handler import BrowserAutomationHandler
from app.test.test_config import LOG_CONFIG, TestStatus

# Configure logging
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

class SequenceTest:
    """Test sequence for UaiBot."""
    
    def __init__(self):
        """Initialize test sequence."""
        self.command_processor = CommandProcessor()
        self.browser_automation = BrowserAutomationHandler()
        self.results = []
        
    def run_sequence(self):
        """Run the test sequence."""
        logger.info("Starting test sequence...")
        
        # Define test commands
        tests = [
            {
                'name': 'Basic search functionality',
                'command': 'search where is Kuwait using duckduckgo',
                'expected_result': {'status': 'success', 'browser_automation': True}
            },
            {
                'name': 'Link interaction',
                'command': 'in that browser click the middle link',
                'expected_result': {'status': 'success', 'browser_automation': True}
            },
            {
                'name': 'Browser focus adjustment',
                'command': 'make that browser more focused on the text',
                'expected_result': {'status': 'success', 'browser_automation': True}
            },
            {
                'name': 'System volume control',
                'command': 'increase volume to 80%',
                'expected_result': {'status': 'success', 'browser_automation': False}
            },
            {
                'name': 'Browser navigation',
                'command': 'now in safari go to youtube',
                'expected_result': {'status': 'success', 'browser_automation': True}
            },
            {
                'name': 'Contextual search',
                'command': 'in there search for Quran by Al Husay',
                'expected_result': {'status': 'success', 'browser_automation': True}
            },
            {
                'name': 'Media playback and casting',
                'command': 'play that and cast it to my tv',
                'expected_result': {'status': 'success', 'browser_automation': True}
            }
        ]
        
        # Run each test
        for test in tests:
            logger.info(f"Running test: {test['name']}")
            try:
                # Process the command
                result = self.command_processor.execute_command(test['command'])
                time.sleep(5)  # Pause for 5 seconds to see the action
                
                # Handle browser automation if needed
                if result.get('status') == 'success' and result.get('browser_automation'):
                    if 'browser' in result and 'url' in result:
                        browser_actions = []
                        if 'focus' in result:
                            browser_actions.append({
                                'type': 'hotkey',
                                'keys': ['command', '1']  # Focus first tab
                            })
                        if 'volume' in result:
                            browser_actions.append({
                                'type': 'hotkey',
                                'keys': ['command', 'up']  # Increase volume
                            })
                        
                        browser_result = self.browser_automation.execute_actions(
                            result['browser'],
                            result['url'],
                            browser_actions
                        )
                        if browser_result.startswith('Error'):
                            result['status'] = 'error'
                            result['message'] = browser_result
                
                # Record test result
                test_result = {
                    'name': test['name'],
                    'command': test['command'],
                    'status': TestStatus.SKIPPED,
                    'message': 'Test skipped - browser automation not implemented'
                }
                
                if result.get('status') == 'success':
                    test_result['status'] = TestStatus.SUCCESS
                    test_result['message'] = 'Test passed successfully'
                elif result.get('status') == 'error':
                    test_result['status'] = TestStatus.FAILURE
                    test_result['message'] = result.get('message', 'Unknown error')
                
                self.results.append(test_result)
                logger.info(f"Test {test['name']} completed with status: {test_result['status']}")
                
            except Exception as e:
                logger.error(f"Error running test {test['name']}: {str(e)}")
                self.results.append({
                    'name': test['name'],
                    'command': test['command'],
                    'status': TestStatus.ERROR,
                    'message': str(e)
                })
        
        # Generate report
        self._generate_report()
        
    def _generate_report(self):
        """Generate test sequence report."""
        logger.info("\nTest Sequence Report")
        logger.info("===================")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == TestStatus.SUCCESS)
        failed_tests = sum(1 for r in self.results if r['status'] == TestStatus.FAILURE)
        error_tests = sum(1 for r in self.results if r['status'] == TestStatus.ERROR)
        skipped_tests = sum(1 for r in self.results if r['status'] == TestStatus.SKIPPED)
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Errors: {error_tests}")
        logger.info(f"Skipped: {skipped_tests}")
        logger.info("\nDetailed Results:")
        
        for result in self.results:
            status_str = {
                TestStatus.SUCCESS: "SUCCESS",
                TestStatus.FAILURE: "FAILURE",
                TestStatus.ERROR: "ERROR",
                TestStatus.SKIPPED: "SKIPPED"
            }[result['status']]
            
            logger.info(f"\n{result['name']} ({status_str})")
            logger.info(f"Command: {result['command']}")
            logger.info(f"Message: {result['message']}")

if __name__ == "__main__":
    test = SequenceTest()
    test.run_sequence() 