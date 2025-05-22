import pexpect
import time
import sys
import os

def process_task(task):
    """Process a single task through main.py"""
    if not task.strip() or task.strip().startswith('#'):
        return
    
    print(f"\nProcessing: {task}")
    print("-" * 50)
    
    try:
        # Start main.py as a child process
        child = pexpect.spawn('python app/main.py')
        
        # Wait for the prompt
        child.expect('Enter your command')
        
        # Send the task
        child.sendline(task)
        
        # Wait for processing to complete
        child.expect(pexpect.EOF, timeout=30)
        
        # Print the output
        print(child.before.decode('utf-8'))
        
    except pexpect.TIMEOUT:
        print("Task timed out")
    except Exception as e:
        print(f"Error processing task: {e}")
    finally:
        try:
            child.close()
        except:
            pass
    
    print("-" * 50)
    time.sleep(1)  # Small delay between tasks

def main():
    try:
        with open('master/patch1_shuf.txt', 'r') as f:
            tasks = f.readlines()
        
        for task in tasks:
            process_task(task)
            
    except FileNotFoundError:
        print("Error: patch1_shuf.txt not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 