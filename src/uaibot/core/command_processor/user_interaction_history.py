"""
User Interaction History Module

This module maintains a history of user interactions and commands
for context-aware processing and learning.
"""

import os
import json
import time
from datetime import datetime
from collections import deque  # Fix: Import from standard library collections
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class UserInteractionHistory:
    """
    Maintains a history of user interactions and commands.
    Provides methods for adding, retrieving, and analyzing interactions.
    """
    
    def __init__(self, 
                max_history: int = 20, 
                persistent_storage: bool = True,
                storage_path: str = None):
        """
        Initialize the interaction history manager.
        
        Args:
            max_history: Maximum number of interactions to keep in memory
            persistent_storage: Whether to store history on disk
            storage_path: Path to store history files (uses default if None)
        """
        self.max_history = max_history
        self.persistent_storage = persistent_storage
        self.history = deque(maxlen=max_history)
        self.command_frequency = {}
        self.last_interaction_time = None
        
        # Set up storage path
        if persistent_storage:
            if storage_path:
                self.storage_path = storage_path
            else:
                # Default to user home directory
                self.storage_path = os.path.join(
                    os.path.expanduser("~"), 
                    ".uaibot", 
                    "history"
                )
                
            # Create directory if it doesn't exist
            if not os.path.exists(self.storage_path):
                try:
                    os.makedirs(self.storage_path)
                except Exception as e:
                    logger.warning(f"Failed to create history storage directory: {e}")
                    self.persistent_storage = False
                    
        # Load history from disk if persistent storage is enabled
        if self.persistent_storage:
            self._load_history()
    
    def add_interaction(self, 
                       user_request: str, 
                       ai_response: Dict[str, Any],
                       command_executed: Optional[str] = None,
                       success: bool = True,
                       metadata: Dict[str, Any] = None) -> None:
        """
        Add a new interaction to the history.
        
        Args:
            user_request: The original user request
            ai_response: The AI's response data
            command_executed: The command that was executed (if any)
            success: Whether the interaction was successful
            metadata: Additional metadata about the interaction
        """
        if metadata is None:
            metadata = {}
            
        # Create interaction record
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "ai_response_type": ai_response.get("type", "unknown"),
            "success": success,
            "metadata": metadata
        }
        
        # Include executed command if available
        if command_executed:
            interaction["command_executed"] = command_executed
            
        # Add relevant parts of the AI response
        ai_response_data = {}
        for key in ["command", "file_operation", "info_type", "error"]:
            if key in ai_response:
                ai_response_data[key] = ai_response[key]
                
        if ai_response_data:
            interaction["ai_response_data"] = ai_response_data
            
        # Add to in-memory history
        self.history.append(interaction)
        
        # Save to disk if persistent storage is enabled
        if self.persistent_storage:
            self._save_interaction(interaction)
        
        # Update command frequency
        if command_executed:
            self.command_frequency[command_executed] = self.command_frequency.get(command_executed, 0) + 1
        
        self.last_interaction_time = datetime.now()
    
    def get_recent_interactions(self, 
                              count: int = None, 
                              filter_func = None) -> List[Dict[str, Any]]:
        """
        Get recent interactions, optionally filtered.
        
        Args:
            count: Maximum number of interactions to return (defaults to all)
            filter_func: Optional function to filter interactions
            
        Returns:
            List of recent interaction records
        """
        if count is None:
            count = self.max_history
            
        # Get recent interactions
        recent = list(self.history)[-count:]
        
        # Apply filter if provided
        if filter_func is not None:
            recent = [i for i in recent if filter_func(i)]
            
        return recent
    
    def get_context_for_prompt(self, 
                             related_terms: List[str] = None,
                             max_items: int = 3) -> Dict[str, Any]:
        """
        Get contextual information for adaptive prompting.
        
        Args:
            related_terms: Terms to use for finding related interactions
            max_items: Maximum number of related interactions to include
            
        Returns:
            Dictionary with context information for prompt enhancement
        """
        if not self.history:
            return {"has_history": False}
            
        context = {
            "has_history": True,
            "interaction_count": len(self.history),
            "recent_interactions": []
        }
        
        # Get most recent interaction
        if self.history:
            last_interaction = list(self.history)[-1]
            context["last_interaction"] = {
                "user_request": last_interaction["user_request"],
                "success": last_interaction.get("success", True),
                "timestamp": last_interaction["timestamp"]
            }
        
        # Find related interactions based on terms
        if related_terms and len(related_terms) > 0:
            related = []
            
            for interaction in reversed(list(self.history)[:-1]):  # Exclude the most recent one
                request = interaction["user_request"].lower()
                
                # Check if any term appears in the request
                if any(term.lower() in request for term in related_terms):
                    related.append({
                        "user_request": interaction["user_request"],
                        "success": interaction.get("success", True),
                        "command": interaction.get("command_executed")
                    })
                    
                    if len(related) >= max_items:
                        break
                        
            if related:
                context["related_interactions"] = related
        
        # Include success patterns
        success_count = sum(1 for i in self.history if i.get("success", True))
        context["success_rate"] = success_count / len(self.history) if self.history else 0
        
        return context
    
    def get_topic_trends(self) -> Dict[str, int]:
        """
        Analyze the history to find common topics/commands.
        
        Returns:
            Dictionary mapping topics to frequency counts
        """
        # Common command words to track
        common_topics = {
            "file": 0,
            "directory": 0,
            "list": 0,
            "create": 0,
            "delete": 0,
            "search": 0,
            "install": 0,
            "network": 0,
            "system": 0,
            "process": 0,
            "help": 0
        }
        
        # Count occurrences in history
        for interaction in self.history:
            request = interaction["user_request"].lower()
            
            for topic in common_topics:
                if topic in request:
                    common_topics[topic] += 1
                    
        return common_topics
    
    def get_command_frequency(self) -> Dict[str, int]:
        """
        Get the frequency of commands in the history.
        
        Returns:
            Dictionary mapping commands to their frequency
        """
        return self.command_frequency.copy()
    
    def _save_interaction(self, interaction: Dict[str, Any]) -> None:
        """
        Save a single interaction to persistent storage.
        
        Args:
            interaction: The interaction record to save
        """
        if not self.persistent_storage:
            return
            
        try:
            # Use timestamp as part of filename
            timestamp = datetime.fromisoformat(interaction["timestamp"])
            filename = f"interaction_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(interaction, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"Saved interaction to {filepath}")
        except Exception as e:
            logger.warning(f"Failed to save interaction to disk: {e}")
    
    def _load_history(self) -> None:
        """Load interaction history from persistent storage."""
        if not self.persistent_storage or not os.path.exists(self.storage_path):
            return
            
        try:
            # Get all JSON files in the storage directory
            files = [f for f in os.listdir(self.storage_path) 
                    if f.startswith("interaction_") and f.endswith(".json")]
            
            # Sort by filename (which contains timestamp)
            files.sort()
            
            # Load the most recent files up to max_history
            loaded_count = 0
            for filename in files[-self.max_history:]:
                filepath = os.path.join(self.storage_path, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        interaction = json.load(f)
                        self.history.append(interaction)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to load interaction from {filepath}: {e}")
                    
            logger.info(f"Loaded {loaded_count} interactions from history")
        except Exception as e:
            logger.warning(f"Failed to load interaction history: {e}")
    
    def clear_history(self) -> None:
        """Clear the interaction history from memory and optionally disk."""
        # Clear memory
        self.history.clear()
        self.command_frequency.clear()
        self.last_interaction_time = None
        
        # Clear disk storage if enabled
        if self.persistent_storage and os.path.exists(self.storage_path):
            try:
                for filename in os.listdir(self.storage_path):
                    if filename.startswith("interaction_") and filename.endswith(".json"):
                        os.remove(os.path.join(self.storage_path, filename))
                        
                logger.info("Cleared interaction history from disk")
            except Exception as e:
                logger.warning(f"Failed to clear interaction history from disk: {e}")

# Create a global instance for convenience
interaction_history = UserInteractionHistory()
