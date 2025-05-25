"""
UaiBot Agent implementation.

This module provides the main UaiBot agent implementation, which:
- Manages tools and plugins
- Handles command planning and execution
- Integrates with model providers
- Manages authentication and caching
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import asyncio

from uaibot.core.ai.agent import Agent, MultiStepPlan, PlanStep
from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.cache import Cache
from uaibot.core.auth_manager import AuthManager
from uaibot.core.plugin_manager import PluginManager
from uaibot.core.awareness.system_awareness import SystemAwarenessTool
from uaibot.core.awareness.user_routine_awareness import UserRoutineAwarenessTool
from uaibot.core.awareness.device_awareness import DeviceAwarenessTool

class UaiAgent(Agent):
    """Main UaiBot agent implementation."""
    
    def __init__(self, config: ConfigManager, model_manager: ModelManager,
                 cache: Cache, auth_manager: AuthManager,
                 plugin_manager: PluginManager):
        """Initialize the UaiBot agent."""
        super().__init__(name="UaiBot")
        
        # Store components
        self.config = config
        self.model_manager = model_manager
        self.cache = cache
        self.auth_manager = auth_manager
        self.plugin_manager = plugin_manager
        
        # Load plugins
        self._load_plugins()
        
        # Set up logging
        self.logger = logging.getLogger("UaiBot.Agent")
        
        self.system_awareness_tool = SystemAwarenessTool()
        self.register_tool(self.system_awareness_tool)
        
        self.user_routine_awareness_tool = UserRoutineAwarenessTool()
        self.register_tool(self.user_routine_awareness_tool)
        
        self.device_awareness_tool = DeviceAwarenessTool()
        self.register_tool(self.device_awareness_tool)
    
    def _load_plugins(self):
        """Load enabled plugins."""
        for plugin in self.plugin_manager.get_plugins():
            if hasattr(plugin, 'is_enabled') and plugin.is_enabled:
                if hasattr(plugin, 'register_tools'):
                    for tool in plugin.register_tools():
                        self.register_tool(tool)
                self.logger.info(f"Loaded plugin: {plugin.__class__.__name__}")
    
    async def plan_and_execute(self, command: str, **kwargs) -> Any:
        """
        Plan and execute a command.
        
        Args:
            command (str): The command to execute
            **kwargs: Additional parameters for the command
            
        Returns:
            Any: The result of the command execution
        """
        self.logger.info(f"Processing command: {command}")
        
        # Check authentication
        if not self.auth_manager.is_authenticated():
            return {"error": "Not authenticated. Please log in first."}
        
        # Check cache
        cache_key = f"cmd:{command}:{str(kwargs)}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.logger.debug("Returning cached result")
            return cached_result
        
        # Create and execute plan
        plan = self._create_plan(command, **kwargs)
        result = self._execute_plan(plan)
        
        # Cache result
        if result is not None:
            self.cache.set(cache_key, result)
        
        return result
    
    def _create_plan(self, command: str, **kwargs) -> MultiStepPlan:
        """Create a plan for executing the command."""
        # Check if any plugin can handle this command
        for plugin in self.plugin_manager.get_plugins():
            if hasattr(plugin, 'handle_command'):
                result = plugin.handle_command(command, **kwargs)
                if result is not None:
                    return MultiStepPlan(steps=[
                        PlanStep(action="plugin", parameters={"result": result})
                    ])
        
        # Use model for planning if available
        if self.model_manager.is_available():
            try:
                # Get model's plan
                model_plan = self.model_manager.get_plan(command, **kwargs)
                if model_plan:
                    return model_plan
            except Exception as e:
                self.logger.error(f"Error getting model plan: {str(e)}")
        
        # Fallback to simple plan
        return MultiStepPlan(steps=[
            PlanStep(action=command, parameters=kwargs)
        ])
    
    def _execute_plan(self, plan: MultiStepPlan) -> Any:
        """Execute a plan step by step."""
        plan.status = "in_progress"
        
        for i, step in enumerate(plan.steps):
            plan.current_step = i
            step.status = "in_progress"
            
            try:
                # Handle plugin results
                if step.action == "plugin":
                    step.result = step.parameters.get("result")
                    step.status = "completed"
                    continue
                
                # Execute the step
                if step.action in self.tools:
                    step.result = self.tools[step.action].execute(**step.parameters)
                    step.status = "completed"
                else:
                    step.status = "failed"
                    step.error = f"Unknown action: {step.action}"
                    break
                
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                self.logger.error(f"Error executing step {i}: {str(e)}")
                break
        
        # Update plan status
        if all(step.status == "completed" for step in plan.steps):
            plan.status = "completed"
            plan.completed_at = datetime.now()
        else:
            plan.status = "failed"
        
        return plan.steps[-1].result if plan.steps else None

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger('UaiAgent')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f'agent_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def collect_and_graph(self, folder: str = ".", debug: bool = False) -> dict:
        if debug:
            print(f"[DEBUG] UaiAgent: Collecting info from {folder}")
        # Step 1: Collect info
        file_list = self.information_collector.file_tool.execute("list", {"directory": folder})
        if debug:
            print(f"[DEBUG] UaiAgent: Files collected: {file_list}")
        # Step 2: Pass info to graph maker
        result = self.graph_maker.plan_and_execute(
            command="analyze folder",
            params={"folder": folder, "debug": debug}
        )
        if debug:
            print(f"[DEBUG] UaiAgent: Graph result: {result}")
        return result

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return a token."""
        token = self.auth_manager.authenticate(username, password)
        if token:
            return {
                "status": "success",
                "token": token
            }
        return {
            "status": "error",
            "message": "Invalid username or password"
        }

    def create_user(self, username: str, password: str, roles: List[str] = None) -> Dict[str, Any]:
        """Create a new user."""
        try:
            user = self.auth_manager.create_user(username, password, roles)
            return {
                "status": "success",
                "username": user.username,
                "roles": user.roles
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def list_users(self) -> Dict[str, Any]:
        """List all users."""
        users = self.auth_manager.list_users()
        return {
            "status": "success",
            "users": users
        } 