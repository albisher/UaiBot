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
    from uaibot.core.ai.uaibot_agent import UaiAgent
    cli_agent = UaiAgent()
    from uaibot.core.ai.agent_tools.file_tool import FileTool
    from uaibot.core.ai.agents.information_collector import InformationCollectorAgent
    from uaibot.core.ai.agents.researcher import ResearcherAgent
    from uaibot.core.ai.agents.research_evaluator import ResearchEvaluatorAgent
except ModuleNotFoundError as e:
    print("[ERROR] Could not import agentic core. Try running with: PYTHONPATH=src python3 scripts/launch.py")
    raise e

# Global agent instance for CLI commands
cli_agent = UaiAgent()
# Register GraphMakerTool after agent instantiation to avoid circular import
try:
    from uaibot.core.ai.agent_tools.graph_maker_tool import GraphMakerTool
    cli_agent.tools.register(GraphMakerTool())
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(description="UaiBot CLI")
    parser.add_argument("command", type=str, help="Command to execute")
    parser.add_argument("--folder", type=str, default="todo", help="Folder to analyze (default: todo)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    if args.command in ["collect_and_graph", "collect graph", "graph from folder"]:
        from uaibot.core.ai.uaibot_agent import UaiAgent
        agent = UaiAgent(debug=args.debug)
        result = agent.collect_and_graph(folder=args.folder, debug=args.debug)
        print(result)
    else:
        # Fallback: pass command to agentic core
        from uaibot.core.ai.uaibot_agent import UaiAgent
        agent = UaiAgent(debug=args.debug)
        result = agent.plan_and_execute(args.command, {"debug": args.debug})
        print(result)

def run_command(command: str, debug: bool = False):
    try:
        if command.strip().startswith('collect graph from folder'):
            # Extract folder path
            parts = command.strip().split('collect graph from folder', 1)
            folder = parts[1].strip() if len(parts) > 1 else '.'
            result = cli_agent.plan_and_execute('graph_maker', {'folder': folder, 'debug': debug}, action='analyze_folder')
            if debug:
                print(f"[DEBUG] GraphMakerTool result: {result}")
            return result
        if command.startswith('collect'):
            agent = InformationCollectorAgent()
            query = command[len('collect'):].strip()
            result = agent.collect_info(query)
            if debug:
                print(f"[DEBUG] InformationCollectorAgent result: {result}")
            return result
        elif command.startswith('research'):
            agent = ResearcherAgent()
            topic = command[len('research'):].strip()
            result = agent.research(topic)
            if debug:
                print(f"[DEBUG] ResearcherAgent result: {result}")
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
            if debug:
                print(f"[DEBUG] ResearchEvaluatorAgent result: {result}")
            return result
        else:
            result = cli_agent.plan_and_execute(command, {'debug': debug})
            if debug:
                print(f"[DEBUG] UaiAgent result: {result}")
            return result
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    main() 