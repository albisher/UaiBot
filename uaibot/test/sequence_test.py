import os
import subprocess

def run_test_sequence():
    """Run a sequence of tests for UaiBot."""
    # Step 1: Set up the environment
    print("Step 1: Setting up the environment...")
    os.environ["PYTHONPATH"] = "/Users/amac/Documents/code/UaiBot"
    
    # Step 2: Run the first command
    print("Step 2: Running the first command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "where is Kuwait"])
    
    # Step 3: Run the second command
    print("Step 3: Running the second command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "in that browser click the middle link"])
    
    # Step 4: Run the third command
    print("Step 4: Running the third command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "make that browser more focused on the text"])
    
    # Step 5: Run the fourth command
    print("Step 5: Running the fourth command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "increase volume to 80%"])
    
    # Step 6: Run the fifth command
    print("Step 6: Running the fifth command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "now in safari go to youtube"])
    
    # Step 7: Run the sixth command
    print("Step 7: Running the sixth command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "in there search for Quran by Al Husay"])
    
    # Step 8: Run the seventh command
    print("Step 8: Running the seventh command...")
    subprocess.run(["python3", "uaibot/main.py", "--fast", "--debug", "play that and cast it to my tv"])

if __name__ == "__main__":
    run_test_sequence() 