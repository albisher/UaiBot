#!/usr/bin/env python3
"""
UaiBot CLI Launcher (Agentic)
- Uses agentic core (Agent, ToolRegistry, etc.)
- All file outputs use safe_path
- If you see import errors, run with: PYTHONPATH=src python3 scripts/launch.py
"""
import sys
from pathlib import Path
import argparse

project_root = Path(__file__).parent.resolve()
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from uaibot.core.ai.agent import Agent, ToolRegistry, EchoTool, safe_path
    from uaibot.core.ai.agent_tools import FileTool
    from uaibot.core.ai.agents.information_collector import InformationCollectorAgent
    from uaibot.core.ai.agents.researcher import ResearcherAgent
    from uaibot.core.ai.agents.research_evaluator import ResearchEvaluatorAgent
except ModuleNotFoundError as e:
    print("[ERROR] Could not import agentic core. Try running with: PYTHONPATH=src python3 scripts/launch.py")
    raise e

def main():
    parser = argparse.ArgumentParser(description="UaiBot CLI (Agentic)")
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to process (interactive mode if omitted)')
    args = parser.parse_args()

    if args.command:
        command = ' '.join(args.command)
        print(run_command(command))
    else:
        print("UaiBot CLI (Agentic) Interactive Mode. Type 'exit' to quit.")
        while True:
            try:
                command = input('> ').strip()
                if command.lower() in ('exit', 'quit'):
                    print('Goodbye!')
                    break
                print(run_command(command))
            except (KeyboardInterrupt, EOFError):
                print('\nGoodbye!')
                break

def run_command(command: str):
    try:
        if command.startswith('collect'):
            agent = InformationCollectorAgent()
            query = command[len('collect'):].strip()
            result = agent.collect_info(query)
            return result
        elif command.startswith('research'):
            agent = ResearcherAgent()
            topic = command[len('research'):].strip()
            result = agent.research(topic)
            return result['report']
        elif command.startswith('evaluate'):
            agent = ResearchEvaluatorAgent()
            # For demo, use a dummy report or ask user for report
            print('Paste research report to evaluate (end with a blank line):')
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            report = {'report': '\n'.join(lines), 'raw': {}}
            result = agent.evaluate(report)
            return result
        else:
            return cli_agent.process_command(command)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    main() 