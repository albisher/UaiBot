#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/simple_log_test.py
import os
import json
import datetime

def test_logging():
    """Test if we can create logs in the logs directory"""
    try:
        # Create logs directory
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Test file paths
        test_file = os.path.join(logs_dir, 'test_log.log')
        
        # Create a simple log entry
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "test": "Simple log test",
            "message": "This is a test log entry"
        }
        
        # Write to log file
        with open(test_file, 'w') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        print(f"✅ Test log created at: {test_file}")
        
        # Verify we can read it back
        with open(test_file, 'r') as f:
            content = f.read().strip()
            print(f"Read log content: {content}")
        
        return True
    except Exception as e:
        print(f"❌ Error in logging test: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_logging()
    print(f"Test {'successful' if result else 'failed'}")
