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

from app.core.command_processor.ai_command_extractor import AICommandExtractor
from app.core.command_processor.error_handler import error_handler, ErrorCategory
from app.core.parallel_utils import ParallelTaskManager
from app.core.browser_controller import BrowserController

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
            
            # Execute operation
            operation = step.get('operation')
            parameters = step.get('parameters', {})
            
            # Update state variables
            self._update_state_variables(parameters)
            
            # Execute the operation
            result = self._execute_operation(operation, parameters)
            
            return {
                'step': step['step'],
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
    
    def _execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a specific operation.
        
        Args:
            operation: The operation to execute
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        if not operation or not isinstance(operation, str):
            logger.error(f"Invalid or missing operation: {operation!r}")
            raise ValueError(f"Invalid or missing operation: {operation!r}")
        
        # --- BROWSER AUTOMATION ---
        if operation in ['open_browser', 'launch_browser', 'browser.open']:
            browser = parameters.get('browser') or parameters.get('application')
            url = parameters.get('url') or parameters.get('website')
            if browser:
                return self.browser_controller.open_browser(browser, url)
            return "Error: No browser specified"
        
        elif operation in ['execute_javascript', 'browser.execute_js']:
            browser = parameters.get('browser')
            js_code = parameters.get('js_code')
            if browser and js_code:
                return self.browser_controller.execute_javascript(browser, js_code)
            return "Error: Missing browser or JavaScript code"
        
        elif operation in ['click_element', 'browser.click']:
            browser = parameters.get('browser')
            selector = parameters.get('selector')
            if browser and selector:
                return self.browser_controller.click_element(browser, selector)
            return "Error: Missing browser or element selector"
        
        # --- UNIVERSAL APPLICATION LAUNCH ---
        app_keys = ['application_name', 'application', 'app', 'program']
        app_name = None
        for key in app_keys:
            if key in parameters:
                app_name = parameters[key]
                break
        if (app_name or any(k in operation.lower() for k in ['open', 'launch'])):
            if not app_name:
                for v in parameters.values():
                    if isinstance(v, str) and v.strip():
                        app_name = v.strip()
                        break
            if app_name:
                if os.name == 'nt':
                    cmd = f'start "" "{app_name}"'
                elif os.name == 'posix':
                    if os.path.exists('/Applications'):
                        cmd = f'open -a "{app_name}"'
                    else:
                        cmd = f'{app_name} &'
                else:
                    raise ValueError(f"Unsupported operating system: {os.name}")
                return self.shell_handler.execute_command(cmd)
        # --- END UNIVERSAL APPLICATION LAUNCH ---

        if operation == 'execute_shell_command':
            command = parameters.get('command')
            if not command:
                raise ValueError("No command specified for execute_shell_command")
            return self.shell_handler.execute_command(command)
        elif operation.startswith('file.'):
            if operation == 'file.read_and_append':
                return self._handle_file_read_and_append(parameters)
            return self._handle_file_operation(operation, parameters)
        elif operation.startswith('directory.'):
            return self._handle_directory_operation(operation, parameters)
        elif operation.startswith('shell.'):
            if operation == 'shell.execute_and_read':
                return self._handle_shell_execute_and_read(parameters)
            return self._handle_shell_operation(operation, parameters)
        elif operation == 'conditional_file_operation':
            return self._handle_conditional_file_operation(parameters)
        else:
            # Show a user-friendly message for unsupported operations
            msg = f"⚠️ Sorry, I can't automate the step '{operation}' yet."
            logger.warning(msg)
            return msg
    
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
        import subprocess
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
        import subprocess
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