import sys
from command_processor import CommandProcessor, ShellHandler

class UaiBot:
    """Main UaiBot class that handles user interaction."""
    
    def __init__(self):
        self.shell_handler = ShellHandler()
        self.command_processor = CommandProcessor(self.shell_handler)
        self.welcome_message = """
🤖 Welcome to UaiBot!
I'm your AI assistant.
Type commands or questions for help.
"""
    
    def start(self):
        """Start the UaiBot interactive session."""
        print(self.welcome_message)
        self._interactive_loop()
    
    def _interactive_loop(self):
        """Main interactive loop for UaiBot."""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("UaiBot: 👋 Goodbye! Have a great day!")
                    break
                
                response = self.command_processor.process_command(user_input)
                print(f"\nUaiBot: {response}")
                
            except KeyboardInterrupt:
                print("\nUaiBot: 👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nUaiBot: ❌ An error occurred: {str(e)}")
                print("UaiBot: 🔄 Let's continue. What else can I help you with?")
    
    def process_single_command(self, command):
        """Process a single command and return the result."""
        return self.command_processor.process_command(command)


if __name__ == "__main__":
    bot = UaiBot()
    
    if len(sys.argv) > 1:
        # If command line arguments are provided, process them as a single command
        command = " ".join(sys.argv[1:])
        result = bot.process_single_command(command)
        print(f"UaiBot: {result}")
    else:
        # Otherwise start interactive mode
        bot.start()
