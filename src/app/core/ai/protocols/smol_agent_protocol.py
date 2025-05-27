"""
SmolAgents Protocol Implementation

This module provides the SmolAgents protocol implementation for managing minimal
agent interactions and ensuring efficient communication between agents.
"""

from typing import Any, Dict, List, Optional, Union
from .base_protocol import BaseProtocol
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SmolAgentProtocol(BaseProtocol):
    """SmolAgents protocol implementation for minimal agent interactions."""
    
    def __init__(self, name: str, description: str):
        """Initialize the SmolAgents protocol.
        
        Args:
            name: The name of the SmolAgents implementation
            description: A description of the SmolAgents implementation's purpose
        """
        super().__init__(name, description)
        self._agent_tasks: Dict[str, List[Dict[str, Any]]] = {}
        self._agent_resources: Dict[str, Dict[str, Any]] = {}
        self._agent_priorities: Dict[str, int] = {}
        
    def initialize(self) -> bool:
        """Initialize the SmolAgents protocol implementation.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._agent_tasks = {}
            self._agent_resources = {}
            self._agent_priorities = {}
            self.add_capability('task_management')
            self.add_capability('resource_management')
            self.add_capability('priority_management')
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SmolAgents protocol: {str(e)}")
            return False
    
    def validate(self) -> bool:
        """Validate the SmolAgents protocol implementation.
        
        Returns:
            bool: True if validation was successful, False otherwise
        """
        try:
            required_capabilities = ['task_management', 'resource_management', 'priority_management']
            return all(cap in self._capabilities for cap in required_capabilities)
        except Exception as e:
            logger.error(f"Failed to validate SmolAgents protocol: {str(e)}")
            return False
    
    def add_task(self, agent_id: str, task: Dict[str, Any]) -> bool:
        """Add a task for an agent.
        
        Args:
            agent_id: The identifier of the agent
            task: The task to add
            
        Returns:
            bool: True if the task was added successfully, False otherwise
        """
        try:
            if agent_id not in self._agent_tasks:
                self._agent_tasks[agent_id] = []
            self._agent_tasks[agent_id].append(task)
            self.log(f"Task added for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add task: {str(e)}")
            return False
    
    def get_tasks(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for an agent.
        
        Args:
            agent_id: The identifier of the agent
            
        Returns:
            List[Dict[str, Any]]: The list of tasks
        """
        return self._agent_tasks.get(agent_id, [])
    
    def remove_task(self, agent_id: str, task_id: str) -> bool:
        """Remove a task for an agent.
        
        Args:
            agent_id: The identifier of the agent
            task_id: The identifier of the task to remove
            
        Returns:
            bool: True if the task was removed successfully, False otherwise
        """
        try:
            if agent_id not in self._agent_tasks:
                return False
            self._agent_tasks[agent_id] = [t for t in self._agent_tasks[agent_id] if t.get('id') != task_id]
            self.log(f"Task {task_id} removed for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove task: {str(e)}")
            return False
    
    def set_agent_resources(self, agent_id: str, resources: Dict[str, Any]) -> bool:
        """Set the resources for an agent.
        
        Args:
            agent_id: The identifier of the agent
            resources: The resources to set
            
        Returns:
            bool: True if the resources were set successfully, False otherwise
        """
        try:
            self._agent_resources[agent_id] = resources
            self.log(f"Resources set for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set agent resources: {str(e)}")
            return False
    
    def get_agent_resources(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the resources for an agent.
        
        Args:
            agent_id: The identifier of the agent
            
        Returns:
            Optional[Dict[str, Any]]: The agent resources, or None if not found
        """
        return self._agent_resources.get(agent_id)
    
    def set_agent_priority(self, agent_id: str, priority: int) -> bool:
        """Set the priority for an agent.
        
        Args:
            agent_id: The identifier of the agent
            priority: The priority to set
            
        Returns:
            bool: True if the priority was set successfully, False otherwise
        """
        try:
            self._agent_priorities[agent_id] = priority
            self.log(f"Priority set for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set agent priority: {str(e)}")
            return False
    
    def get_agent_priority(self, agent_id: str) -> Optional[int]:
        """Get the priority for an agent.
        
        Args:
            agent_id: The identifier of the agent
            
        Returns:
            Optional[int]: The agent priority, or None if not found
        """
        return self._agent_priorities.get(agent_id)
    
    def get_prioritized_agents(self) -> List[str]:
        """Get a list of agents sorted by priority.
        
        Returns:
            List[str]: The list of agents sorted by priority
        """
        return sorted(self._agent_priorities.keys(), key=lambda x: self._agent_priorities.get(x, 0), reverse=True)
    
    def clear_agent_tasks(self, agent_id: str) -> bool:
        """Clear all tasks for an agent.
        
        Args:
            agent_id: The identifier of the agent
            
        Returns:
            bool: True if the tasks were cleared successfully, False otherwise
        """
        try:
            if agent_id in self._agent_tasks:
                self._agent_tasks[agent_id] = []
                self.log(f"Tasks cleared for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear agent tasks: {str(e)}")
            return False
    
    def get_all_agent_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all agent tasks.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: All agent tasks
        """
        return self._agent_tasks.copy()
    
    def get_all_agent_resources(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent resources.
        
        Returns:
            Dict[str, Dict[str, Any]]: All agent resources
        """
        return self._agent_resources.copy()
    
    def get_all_agent_priorities(self) -> Dict[str, int]:
        """Get all agent priorities.
        
        Returns:
            Dict[str, int]: All agent priorities
        """
        return self._agent_priorities.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the SmolAgents protocol to a dictionary representation.
        
        Returns:
            Dict[str, Any]: The dictionary representation
        """
        data = super().to_dict()
        data.update({
            'agent_tasks': self._agent_tasks,
            'agent_resources': self._agent_resources,
            'agent_priorities': self._agent_priorities
        })
        return data
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load the SmolAgents protocol from a dictionary representation.
        
        Args:
            data: The dictionary representation
        """
        super().from_dict(data)
        self._agent_tasks = data.get('agent_tasks', {})
        self._agent_resources = data.get('agent_resources', {})
        self._agent_priorities = data.get('agent_priorities', {}) 