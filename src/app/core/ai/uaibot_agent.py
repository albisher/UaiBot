"""
Labeeb Agent implementation.

This module provides the main Labeeb agent implementation, which:
- Manages tools and plugins
- Handles command planning and execution
- Integrates with model providers
- Manages authentication and caching
- Delegates all platform-specific logic to PlatformManager (see platform_core/platform_manager.py)
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import asyncio
from pathlib import Path
import platform

from app.core.ai.agent import Agent, MultiStepPlan, PlanStep
from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.cache import Cache
from uaibot.core.auth_manager import AuthManager
from uaibot.core.plugin_manager import PluginManager
from uaibot.core.learning import LearningManager
from uaibot.core.ai.agent_tools.system_awareness_tool import SystemAwarenessTool
from uaibot.core.awareness.user_routine_awareness import UserRoutineAwarenessTool
from uaibot.core.awareness.device_awareness import DeviceAwarenessTool
from uaibot.core.awareness.speech_tool import SpeechTool
from uaibot.core.awareness.display_tool import DisplayTool
from uaibot.core.tools.json_tools import JSONTool

class DefaultTool:
    """Fallback tool for unknown or unsupported actions."""
    name = 'default'
    description = "Handles unknown or unsupported actions with a friendly message."
    def execute(self, action: str, **kwargs):
        # Friendly fallback for greetings or boolean True
        greetings = ["hi", "hello", "hey", "salam", "مرحبا", "السلام عليكم", True, "True", 1]
        if action.lower() in [str(g).lower() for g in greetings]:
            return {"output": "👋 Hello! I'm Labeeb (لبيب), your intelligent assistant. How can I help you today?"}
        return {"error": "Sorry, I didn't understand that command. Please try rephrasing or ask for help."}

class LabeebAgent(Agent):
    """Main Labeeb agent implementation."""
    
    def __init__(self, config: ConfigManager, model_manager: ModelManager,
                 cache: Cache, auth_manager: AuthManager,
                 plugin_manager: PluginManager):
        """Initialize the Labeeb agent."""
        super().__init__(name="Labeeb")  # Changed name to Labeeb
        
        # Store components
        self.config = config
        self.model_manager = model_manager
        self.cache = cache
        self.auth_manager = auth_manager
        self.plugin_manager = plugin_manager
        self.learning_manager = LearningManager()
        
        # Initialize memory
        self.memory = {
            "identity": {
                "name": "Labeeb",
                "meaning": "Intelligent, wise, sensible",
                "language": "Arabic",
                "description": "An AI assistant focused on smart assistance and thoughtful decision-making"
            },
            "conversation_history": [],
            "learned_patterns": {},
            "last_interaction": None
        }
        
        # Load plugins
        self._load_plugins()
        
        # Set up logging
        self.logger = logging.getLogger("Labeeb.Agent")
        
        # Initialize tools
        self.system_awareness_tool = SystemAwarenessTool()
        self.register_tool(self.system_awareness_tool)
        
        self.user_routine_awareness_tool = UserRoutineAwarenessTool()
        self.register_tool(self.user_routine_awareness_tool)
        
        self.device_awareness_tool = DeviceAwarenessTool()
        self.register_tool(self.device_awareness_tool)
        
        self.speech_tool = SpeechTool()
        self.register_tool(self.speech_tool)
        
        self.display_tool = DisplayTool()
        self.register_tool(self.display_tool)
        
        self.default_tool = DefaultTool()
        self.register_tool(self.default_tool)
    
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
        Returns a dict with 'output', 'error', or 'raw' for CLI formatting.
        """
        self.logger.info(f"Processing command: {command}")
        self.memory["last_interaction"] = datetime.now().isoformat()
        self.memory["conversation_history"].append({
            "timestamp": self.memory["last_interaction"],
            "command": command,
            "parameters": kwargs
        })
        if not self.auth_manager.is_authenticated():
            return {"error": "Not authenticated. Please log in first."}
        cache_key = f"cmd:{command}:{str(kwargs)}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.logger.debug("Returning cached result")
            return cached_result
        plan = await self._create_plan(command, **kwargs)
        result = await self._execute_plan(plan)
        if result is not None:
            self.learning_manager.learn_from_result(command, {
                "status": "success" if result else "failed",
                "action": plan.steps[0].action if plan.steps else None,
                "os": platform.system(),
                "capability": "general"
            })
            self.cache.set(cache_key, result)
        # Always return a dict for CLI formatting
        if isinstance(result, dict):
            if "error" in result:
                return {"error": result["error"]}
            if "output" in result:
                return {"output": result["output"]}
            if "message" in result:
                return {"output": result["message"]}
            if "text" in result:
                return {"output": result["text"]}
            if "raw" in result:
                return {"raw": result["raw"]}
            return {"raw": str(result)}
        elif isinstance(result, str):
            # Detect fallback/model errors
            if "Failed to parse model response as JSON" in result or "not sure" in result.lower():
                return {"error": result}
            return {"output": result}
        elif result is False or result is None:
            return {"error": "No output."}
        else:
            return {"raw": str(result)}
    
    async def _create_plan(self, command: str, **kwargs) -> MultiStepPlan:
        """Create a plan for executing the command."""
        # Check if any plugin can handle this command
        for plugin in self.plugin_manager.get_plugins():
            if hasattr(plugin, 'handle_command'):
                result = plugin.handle_command(command, **kwargs)
                if result is not None:
                    return MultiStepPlan(steps=[
                        PlanStep(action="plugin", parameters={"result": result})
                    ])
        # Map common device/system commands to correct tools
        cmd_lower = command.lower()
        if any(x in cmd_lower for x in ["move mouse", "click", "mouse", "screen", "screenshot"]):
            return MultiStepPlan(steps=[
                PlanStep(action="device_awareness_tool", parameters={"command": command, **kwargs})
            ])
        if any(x in cmd_lower for x in ["open calculator", "launch calculator", "start calculator"]):
            return MultiStepPlan(steps=[
                PlanStep(action="system_awareness_tool", parameters={"command": command, **kwargs})
            ])
        # Use model for planning if available
        if self.model_manager.is_available():
            try:
                # Get model's plan
                model_plan = await self.model_manager.get_plan(command, **kwargs)
                if model_plan:
                    return model_plan
            except Exception as e:
                self.logger.error(f"Error getting model plan: {str(e)}")
        # Fallback to simple plan
        return MultiStepPlan(steps=[
            PlanStep(action=command, parameters=kwargs)
        ])
    
    async def _execute_plan(self, plan: MultiStepPlan) -> Any:
        """Execute a plan step by step. Returns the last step's result or error."""
        plan.status = "in_progress"
        for i, step in enumerate(plan.steps):
            plan.current_step = i
            step.status = "in_progress"
            try:
                if step.action == "plugin":
                    step.result = step.parameters.get("result")
                    step.status = "completed"
                    continue
                tool = self.tools.get(step.action)
                if not tool:
                    # Use DefaultTool for unknown actions
                    tool = self.default_tool
                if asyncio.iscoroutinefunction(tool.execute):
                    step.result = await tool.execute(action=step.action, **step.parameters)
                else:
                    step.result = tool.execute(action=step.action, **step.parameters)
                step.status = "completed"
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                self.logger.error(f"Error executing step {i}: {str(e)}")
                break
        if all(step.status == "completed" for step in plan.steps):
            plan.status = "completed"
            plan.completed_at = datetime.now()
        else:
            plan.status = "failed"
        last_result = plan.steps[-1].result if plan.steps else None
        last_error = plan.steps[-1].error if plan.steps and hasattr(plan.steps[-1], 'error') else None
        # If the result is True or 'True', treat as greeting
        if last_result is True or last_result == "True":
            return {"output": "👋 Hello! I'm Labeeb (لبيب), your intelligent assistant. How can I help you today?"}
        if last_error:
            return {"error": last_error}
        if last_result is None:
            return {"error": "No output."}
        elif last_result is False:
            return {"error": "No output."}
        elif isinstance(last_result, dict):
            if "error" in last_result:
                return {"error": last_result["error"]}
            if "output" in last_result:
                return {"output": last_result["output"]}
            if "message" in last_result:
                return {"output": last_result["message"]}
            if "text" in last_result:
                return {"output": last_result["text"]}
            if "raw" in last_result:
                return {"raw": last_result["raw"]}
            return {"raw": str(last_result)}
        return {"output": str(last_result)}

    def get_identity(self) -> Dict[str, Any]:
        """Get the agent's identity information."""
        return self.memory["identity"]

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the agent's conversation history."""
        return self.memory["conversation_history"]

    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get the agent's learned patterns."""
        return self.memory["learned_patterns"]

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger('LabeebAgent')
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
            print(f"[DEBUG] LabeebAgent: Collecting info from {folder}")
        # Step 1: Collect info
        file_list = self.information_collector.file_tool.execute("list", {"directory": folder})
        if debug:
            print(f"[DEBUG] LabeebAgent: Files collected: {file_list}")
        # Step 2: Pass info to graph maker
        result = self.graph_maker.plan_and_execute(
            command="analyze folder",
            params={"folder": folder, "debug": debug}
        )
        if debug:
            print(f"[DEBUG] LabeebAgent: Graph result: {result}")
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