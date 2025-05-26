"""
Execution Controller Module

This module implements the core execution controller that orchestrates
multi-step plan execution, manages state, and handles errors.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import shlex
import subprocess

from labeeb.core.command_processor.ai_command_extractor import AICommandExtractor
from labeeb.core.command_processor.error_handler import error_handler, ErrorCategory
from labeeb.core.parallel_utils import ParallelTaskManager
from labeeb.core.browser_controller import BrowserController
from labeeb.core.controller.macos_calendar_controller import MacOSCalendarController

logger = logging.getLogger(__name__)

class ExecutionController:
    """
    Core execution controller that orchestrates plan execution and state management.
    Handles multi-step plans, state persistence, and error recovery.
    """
    
    def __init__(self, shell_handler, ai_handler, quiet_mode=False):
        """Initialize the execution controller."""
        self.shell_handler = shell_handler
        self.ai_handler = ai_handler
        self.quiet_mode = quiet_mode
        
        # Initialize components
        self.command_extractor = AICommandExtractor()
        self.parallel_manager = ParallelTaskManager()
        self.browser_controller = BrowserController()
        
        # State management
        self.current_plan = None
        self.execution_state = {
            'current_step': 0,
            'completed_steps': [],
            'failed_steps': [],
            'state_variables': {},
            'start_time': None,
            'end_time': None
        }
        
        # Error handling
        self.error_recovery_attempts = 0
        self.max_recovery_attempts = 3
        
        # Load state if exists
        self._load_state()
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a multi-step plan.
        
        Args:
            plan: The plan to execute (following the AI Plan JSON Schema)
            
        Returns:
            Dictionary containing execution results and metadata
        """
        try:
            # Initialize execution
            self.current_plan = plan
            self.execution_state['start_time'] = datetime.now()
            self.execution_state['current_step'] = 0
            self.execution_state['completed_steps'] = []
            self.execution_state['failed_steps'] = []
            self.execution_state['state_variables'] = {}
            
            # Execute each step
            steps = plan.get('plan', [])
            results = []
            
            for step in steps:
                step_result = self._execute_step(step)
                results.append(step_result)
                
                # Handle step result
                if step_result['status'] == 'success':
                    self.execution_state['completed_steps'].append(step['step'])
                    # Process success path
                    next_steps = step.get('on_success', [])
                    if next_steps:
                        for next_step in next_steps:
                            next_step_data = self._find_step(next_step, steps)
                            if next_step_data:
                                next_result = self._execute_step(next_step_data)
                                results.append(next_result)
                else:
                    self.execution_state['failed_steps'].append(step['step'])
                    # Process failure path
                    failure_steps = step.get('on_failure', [])
                    if failure_steps:
                        for failure_step in failure_steps:
                            failure_step_data = self._find_step(failure_step, steps)
                            if failure_step_data:
                                failure_result = self._execute_step(failure_step_data)
                                results.append(failure_result)
            
            # Finalize execution
            self.execution_state['end_time'] = datetime.now()
            self._save_state()
            
            return {
                'status': 'success' if not self.execution_state['failed_steps'] else 'partial_success',
                'results': results,
                'execution_state': self.execution_state,
                'plan': plan
            }
            
        except Exception as e:
            logger.error(f"Error executing plan: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'execution_state': self.execution_state,
                'plan': plan
            }
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step in the plan.
        
        Args:
            step: The step to execute
            
        Returns:
            Dictionary containing step execution results
        """
        try:
            # Check condition if present
            if step.get('condition'):
                condition_met = self._evaluate_condition(step['condition'])
                if not condition_met:
                    return {
                        'step': step['step'],
                        'status': 'skipped',
                        'reason': 'condition_not_met',
                        'output': None
                    }
            # Build operation dict for this step
            operation = step.get('operation')
            parameters = step.get('parameters', {})
            # If 'command' is present at the step level, add it to parameters
            if 'command' in step and 'command' not in parameters:
                parameters['command'] = step['command']
            op_dict = {'type': operation, 'parameters': parameters}
            # Update state variables
            self._update_state_variables(parameters)
            # Execute the operation
            result = self._execute_operation(op_dict)
            return {
                'step': step.get('step'),
                'status': 'success',
                'output': result,
                'operation': operation,
                'parameters': parameters
            }
        except Exception as e:
            logger.error(f"Error executing step {step.get('step')}: {str(e)}")
            return {
                'step': step.get('step'),
                'status': 'error',
                'error': str(e),
                'operation': step.get('operation'),
                'parameters': step.get('parameters', {})
            }
    
    def _execute_operation(self, operation: Dict[str, Any]) -> str:
        """
        Execute a single operation step from an agentic plan.

        This method handles operation aliasing, actionable and non-actionable (stub) operations, shell command execution,
        application launching, browser and file operations, and provides stubs or helpful messages for unimplemented types.
        Any operation with a 'command' parameter is executed as a shell command. Unrecognized operations are logged and
        return a stub message with their parameters.
        """
        try:
            op_type = operation.get('type', '').lower()
            parameters = operation.get('parameters', {})
            
            # (1) Expanded operation aliases and stubs
            operation_aliases = {
                # Not actionable (skipped)
                'intent_recognition': None,
                'analyze_text': None,
                'user_query': None,
                'analyze_intent': None,
                'text_processing': None,
                'display_output': None,
                'string_format': None,
                'web_search': None,
                'analyze_results': None,
                'display_information': None,
                'file_navigate': None,
                'file_sort': None,
                # Actionable/aliased
                'ui_element_interaction': 'browser_click',
                'click_element': 'browser_click',
                'browser_search': 'execute_search',
                'close_application': 'close_application',
                'calculator_input': 'calculator_input',
                'respond_to_user': 'respond_to_user',
                # System/shell/file/process aliases
                'system_command': 'execute_shell_command',
                'shell_command': 'execute_shell_command',
                'execute_command': 'execute_shell_command',
                'execute_shell_command': 'execute_shell_command',
                'system_info': 'system_info',
                'system_query': 'system_query',
                'file_system_search': 'file_system_search',
                'file_system_query': 'file_system_query',
                'file_system_action': 'file_system_action',
                'process_info': 'process_info',
                'system_check': 'system_check',
                'system_lookup': 'system_lookup',
                'run_application': 'run_application',
                # Add more as needed
            }
            if op_type in operation_aliases:
                mapped = operation_aliases[op_type]
                if mapped is None:
                    logger.info(f"Operation '{op_type}' is not actionable. Skipping.")
                    return f"Operation '{op_type}' is not actionable."
                op_type = mapped

            # (2) Always execute a 'command' parameter as a shell command
            if 'command' in parameters and isinstance(parameters['command'], str):
                command = parameters['command']
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    return f"Shell command executed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                except Exception as e:
                    return f"Error executing shell command: {e}"

            # (3) Not actionable operations (already handled above)

            # (4) Improved application name mapping and fallback
            if op_type in ['launch_application', 'open_application', 'run_application']:
                app_name = parameters.get('application', '') or parameters.get('application_name', '')
                mode = parameters.get('mode', '')
                if not app_name:
                    return "Error: Application name is required"
                browser_mapping = {
                    'chrome': 'Google Chrome',
                    'firefox': 'Firefox',
                    'safari': 'Safari',
                    'edge': 'Microsoft Edge',
                    'opera': 'Opera',
                    'calculator': 'Calculator',
                    'calc': 'Calculator',
                }
                app_name_mapped = browser_mapping.get(app_name.lower(), app_name)
                # Try fallback: remove ' settings', try lowercased, etc.
                if not os.path.exists(f"/Applications/{app_name_mapped}.app") and ' ' in app_name_mapped:
                    alt_name = app_name_mapped.split(' ')[0].capitalize()
                    if os.path.exists(f"/Applications/{alt_name}.app"):
                        app_name_mapped = alt_name
                # Private/incognito mode handling
                if mode == 'private':
                    if app_name_mapped == 'Google Chrome':
                        cmd = f'open -a "{app_name_mapped}" --args --incognito'
                    elif app_name_mapped == 'Firefox':
                        cmd = f'open -a "{app_name_mapped}" --args -private-window'
                    elif app_name_mapped == 'Safari':
                        script = f'''
                        tell application "Safari"
                            activate
                            tell application "System Events"
                                keystroke "n" using {{command down, shift down}}
                            end tell
                        end tell
                        '''
                        try:
                            subprocess.run(['osascript', '-e', script], check=True)
                            return f"Opened private window in Safari"
                        except subprocess.CalledProcessError as e:
                            return f"Error opening private window in Safari: {str(e)}"
                    else:
                        cmd = f'open -a "{app_name_mapped}"'
                else:
                    if os.name == 'nt':
                        cmd = f'start {shlex.quote(app_name_mapped)}'
                    elif os.name == 'posix' and os.path.exists('/Applications'):
                        cmd = f'open -a {shlex.quote(app_name_mapped)}'
                    else:
                        cmd = f'{shlex.quote(app_name_mapped)}'
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    return f"Launched {app_name_mapped}{' in private mode' if mode == 'private' else ''}"
                except subprocess.CalledProcessError as e:
                    return f"Error launching {app_name_mapped}: {str(e)}"

            # (5) Stubs for file/directory operations
            if op_type in ['file_system_action', 'file_system_query']:
                return f"Stub: Operation '{op_type}' is not implemented. Parameters: {parameters}"
            if op_type == 'system_check':
                return f"Stub: Operation 'system_check' is not implemented. Parameters: {parameters}"
            if op_type == 'system_lookup':
                return f"Stub: Operation 'system_lookup' is not implemented. Parameters: {parameters}"
            # (NEW) Stubs for common unhandled types
            if op_type == 'calendar_navigation':
                now = datetime.datetime.now()
                year = parameters.get('year')
                month = parameters.get('month')
                # Handle relative years like 'last year'
                if isinstance(year, str) and 'last' in year:
                    try:
                        offset = int(year.split(' ')[0].replace('last', '-1'))
                        year = now.year + offset
                    except Exception:
                        year = now.year - 1
                elif isinstance(year, int):
                    pass
                else:
                    year = now.year
                # If month is a string, try to convert to number
                if isinstance(month, str):
                    try:
                        month_num = datetime.datetime.strptime(month, '%B').month
                    except Exception:
                        month_num = now.month
                elif isinstance(month, int):
                    month_num = month
                else:
                    month_num = now.month
                # Platform-specific delegation
                if os.name == 'posix' and os.path.exists('/Applications/Calendar.app'):
                    return MacOSCalendarController.navigate_to_month_year(month_num, year)
                else:
                    return f"Calendar navigation is not yet implemented for this platform (os.name={os.name}). Please open your calendar manually."
            if op_type == 'control_device':
                return "Device control is not implemented. Please specify the device and action you want to perform."
            if op_type == 'browser_navigate':
                url = parameters.get('url', None)
                if url:
                    return f"Browser navigation is not yet implemented. Please open this URL manually: {url}"
                else:
                    return "Browser navigation is not yet implemented. Please specify a URL."
            if op_type == 'ui_interaction':
                action = parameters.get('action', None)
                model_name = parameters.get('model_name', None)
                if action:
                    return f"UI interaction for action '{action}' is not implemented. Please specify the UI element and action."
                elif model_name:
                    return f"UI interaction for model selection ('{model_name}') is not implemented. Please select the model manually."
                else:
                    return "UI interaction is not implemented. Please specify the UI element and action."
            if op_type == 'application_list':
                # (NEW) Implement a basic application_list for macOS
                if os.name == 'posix' and os.path.exists('/Applications'):
                    try:
                        apps = [f for f in os.listdir('/Applications') if f.endswith('.app')]
                        return f"Installed applications: {', '.join(apps)}"
                    except Exception as e:
                        return f"Error listing applications: {e}"
                else:
                    return "Application listing is only implemented for macOS."

            # User-facing response for respond_to_user
            if op_type == 'respond_to_user':
                # Prefer 'message', fallback to 'text', else generic greeting
                msg = parameters.get('message') or parameters.get('text') or "Hello! How can I assist you today?"
                return msg

            # Browser operations
            if op_type == 'browser_click':
                browser = parameters.get('browser', 'Safari')
                selector = parameters.get('selector', '')
                if not selector:
                    return "Error: No selector specified for browser_click"
                return self.browser_controller.click_element(browser, selector)
            if op_type == 'browser_navigate':
                browser = parameters.get('browser', 'Safari')
                url = parameters.get('url', None)
                if not url:
                    return "Error: No URL specified for browser_navigate"
                return self.browser_controller.open_browser(browser, url=url)

            # (6) Log and return a message for any unhandled operation type
            logger.info(f"Unhandled operation type: {op_type} with parameters: {parameters}")
            # Improved stub output
            pretty_params = ', '.join(f"{k}: {v}" for k, v in parameters.items()) if parameters else "no details provided"
            return f"Sorry, I don't yet know how to handle the operation '{op_type}'. (Details: {pretty_params})"
                
        except Exception as e:
            logger.error(f"Error executing operation: {str(e)}")
            return f"Error: {str(e)}"
    
    def _handle_file_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        """Handle file operations."""
        op_type = operation.split('.')[1]
        
        if op_type == 'create':
            filename = parameters.get('filename')
            content = parameters.get('content', '')
            with open(filename, 'w') as f:
                f.write(content)
            return f"Created file: {filename}"
            
        elif op_type == 'read':
            filename = parameters.get('filename')
            with open(filename, 'r') as f:
                return f.read()
                
        elif op_type == 'delete':
            filename = parameters.get('filename')
            Path(filename).unlink()
            return f"Deleted file: {filename}"
            
        else:
            raise ValueError(f"Unknown file operation: {op_type}")
    
    def _handle_shell_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        """Handle shell operations."""
        op_type = operation.split('.')[1]
        
        if op_type == 'execute':
            command = parameters.get('command')
            if not command:
                raise ValueError("No command specified")
            return self.shell_handler.execute_command(command)
            
        else:
            raise ValueError(f"Unknown shell operation: {op_type}")
    
    def _handle_ai_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        """Handle AI operations."""
        op_type = operation.split('.')[1]
        
        if op_type == 'process':
            prompt = parameters.get('prompt')
            if not prompt:
                raise ValueError("No prompt specified")
            return self.ai_handler.process_prompt(prompt)
            
        else:
            raise ValueError(f"Unknown AI operation: {op_type}")
    
    def _handle_directory_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        op_type = operation.split('.')[1]
        if op_type == 'create':
            dirname = parameters.get('dirname')
            if not dirname:
                raise ValueError("No directory name specified")
            Path(dirname).mkdir(parents=True, exist_ok=True)
            return f"Created directory: {dirname}"
        elif op_type == 'list':
            dirname = parameters.get('dirname', '.')
            if not Path(dirname).exists():
                return f"Directory does not exist: {dirname}"
            files = os.listdir(dirname)
            return f"Contents of {dirname}: {files}"
        else:
            raise ValueError(f"Unknown directory operation: {op_type}")
    
    def _handle_file_read_and_append(self, parameters: Dict[str, Any]) -> Any:
        filename = parameters.get('filename')
        append_content = parameters.get('content', '')
        if not filename:
            raise ValueError("No filename specified")
        # Read
        content = ''
        if Path(filename).exists():
            with open(filename, 'r') as f:
                content = f.read()
        # Append
        with open(filename, 'a') as f:
            f.write(append_content)
        return f"Original content: {content}\nAppended: {append_content}"
    
    def _handle_shell_execute_and_read(self, parameters: Dict[str, Any]) -> Any:
        filename = parameters.get('filename')
        if not filename:
            raise ValueError("No script filename specified")
        # Make executable
        os.chmod(filename, 0o755)
        # Execute and capture output
        result = subprocess.run([f'./{filename}'], capture_output=True, text=True, shell=True)
        return f"Script output: {result.stdout.strip()}"
    
    def _handle_conditional_file_operation(self, parameters: Dict[str, Any]) -> Any:
        filename = parameters.get('filename')
        if not filename:
            raise ValueError("No filename specified for conditional operation")
        # If file exists, read it
        if Path(filename).exists():
            with open(filename, 'r') as f:
                return f"File exists. Content: {f.read()}"
        # If not, create and then read
        content = parameters.get('content', 'This file was missing')
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            f.write(content)
        with open(filename, 'r') as f:
            return f"File created. Content: {f.read()}"
    
    def _handle_system_info_gathering(self, parameters: Dict[str, Any]) -> Any:
        pwd = subprocess.getoutput('pwd')
        ls = subprocess.getoutput('ls')
        info = f"Current directory: {pwd}\nContents:\n{ls}"
        out_file = parameters.get('output_file', 'system_info.txt')
        with open(out_file, 'w') as f:
            f.write(info)
        return f"System info written to {out_file}"
    
    def _handle_application_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        """
        Handle application-related operations.
        
        Args:
            operation: The operation to execute
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        if operation == 'application.launch':
            app_name = parameters.get('application_name')
            if not app_name:
                raise ValueError("Missing required parameter: application_name")
            
            # Use the shell handler to launch the application
            if os.name == 'nt':  # Windows
                cmd = f'start "" "{app_name}"'
            elif os.name == 'posix':  # macOS and Linux
                if os.path.exists('/Applications'):  # macOS
                    cmd = f'open -a "{app_name}"'
                else:  # Linux
                    cmd = f'{app_name} &'
            else:
                raise ValueError(f"Unsupported operating system: {os.name}")
            
            return self.shell_handler.execute_command(cmd)
        else:
            raise ValueError(f"Unsupported application operation: {operation}")
    
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a condition based on current state.
        
        Args:
            condition: The condition to evaluate
            
        Returns:
            True if condition is met, False otherwise
        """
        # TODO: Implement condition evaluation logic
        return True
    
    def _update_state_variables(self, parameters: Dict[str, Any]) -> None:
        """
        Update state variables based on operation parameters.
        
        Args:
            parameters: Operation parameters
        """
        # Extract variables marked for state storage
        for key, value in parameters.items():
            if key.startswith('$'):
                state_key = key[1:]  # Remove $ prefix
                self.execution_state['state_variables'][state_key] = value
    
    def _find_step(self, step_number: int, steps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find a step by its number.
        
        Args:
            step_number: The step number to find
            steps: List of all steps
            
        Returns:
            The step if found, None otherwise
        """
        for step in steps:
            if step.get('step') == step_number:
                return step
        return None
    
    def _save_state(self) -> None:
        """Save current execution state to disk."""
        state_file = Path('execution_state.json')
        with open(state_file, 'w') as f:
            json.dump(self.execution_state, f, indent=2, default=str)
    
    def _load_state(self) -> None:
        """Load execution state from disk if it exists."""
        state_file = Path('execution_state.json')
        if state_file.exists():
            with open(state_file, 'r') as f:
                self.execution_state = json.load(f)
    
    def get_execution_state(self) -> Dict[str, Any]:
        """Get current execution state."""
        return self.execution_state
    
    def clear_state(self) -> None:
        """Clear current execution state."""
        self.execution_state = {
            'current_step': 0,
            'completed_steps': [],
            'failed_steps': [],
            'state_variables': {},
            'start_time': None,
            'end_time': None
        }
        self._save_state() 