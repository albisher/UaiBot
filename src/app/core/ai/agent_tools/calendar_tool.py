"""
Calendar tool with A2A, MCP, and SmolAgents compliance.

This tool provides calendar capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class CalendarTool(BaseTool):
    """Tool for performing calendar operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the calendar tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="calendar",
            description="Tool for performing calendar operations",
            config=config
        )
        self._calendar_id = config.get('calendar_id')
        self._timezone = config.get('timezone', 'UTC')
        self._max_events = config.get('max_events', 100)
        self._max_recurrence = config.get('max_recurrence', 52)  # weeks
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._events = {}  # In-memory event storage
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate configuration
            if not self._calendar_id:
                logger.error("Calendar ID is required")
                return False
            
            # Initialize event storage
            self._events = {}
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize CalendarTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._events = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up CalendarTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'search': True,
            'history': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'calendar_id': self._calendar_id,
            'timezone': self._timezone,
            'max_events': self._max_events,
            'max_recurrence': self._max_recurrence,
            'event_count': len(self._events),
            'history_size': len(self._operation_history),
            'max_history': self._max_history
        }
        return {**base_status, **tool_status}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if command == 'create':
            return await self._create_event(args)
        elif command == 'read':
            return await self._read_event(args)
        elif command == 'update':
            return await self._update_event(args)
        elif command == 'delete':
            return await self._delete_event(args)
        elif command == 'search':
            return await self._search_events(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]) -> None:
        """Add an operation to history.
        
        Args:
            operation: Operation performed
            details: Operation details
        """
        self._operation_history.append({
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        })
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """Validate an event.
        
        Args:
            event: Event to validate
            
        Returns:
            bool: True if event is valid, False otherwise
        """
        required_fields = ['title', 'start_time', 'end_time']
        if not all(field in event for field in required_fields):
            return False
        
        try:
            start_time = datetime.fromisoformat(event['start_time'])
            end_time = datetime.fromisoformat(event['end_time'])
            if end_time <= start_time:
                return False
        except ValueError:
            return False
        
        return True
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID.
        
        Returns:
            str: Unique event ID
        """
        return f"event_{int(time.time() * 1000)}_{len(self._events)}"
    
    async def _create_event(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a calendar event.
        
        Args:
            args: Event arguments
            
        Returns:
            Dict[str, Any]: Result of create operation
        """
        try:
            if not args or not self._validate_event(args):
                return {'error': 'Invalid event data'}
            
            # Check event limit
            if len(self._events) >= self._max_events:
                return {'error': f'Maximum number of events reached ({self._max_events})'}
            
            # Generate event ID
            event_id = self._generate_event_id()
            
            # Create event
            event = {
                'id': event_id,
                'title': args['title'],
                'description': args.get('description', ''),
                'start_time': args['start_time'],
                'end_time': args['end_time'],
                'location': args.get('location', ''),
                'attendees': args.get('attendees', []),
                'recurrence': args.get('recurrence', None),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Handle recurrence
            if event['recurrence']:
                if event['recurrence'].get('count', 0) > self._max_recurrence:
                    return {'error': f'Maximum recurrence count exceeded ({self._max_recurrence})'}
                
                # Create recurring events
                start_time = datetime.fromisoformat(event['start_time'])
                end_time = datetime.fromisoformat(event['end_time'])
                duration = end_time - start_time
                
                for i in range(event['recurrence'].get('count', 1)):
                    if i == 0:
                        self._events[event_id] = event
                    else:
                        recur_id = f"{event_id}_recur_{i}"
                        recur_start = start_time + timedelta(weeks=i)
                        recur_end = recur_start + duration
                        
                        recur_event = event.copy()
                        recur_event['id'] = recur_id
                        recur_event['start_time'] = recur_start.isoformat()
                        recur_event['end_time'] = recur_end.isoformat()
                        recur_event['recurrence'] = None
                        
                        self._events[recur_id] = recur_event
            else:
                self._events[event_id] = event
            
            result = {
                'status': 'success',
                'action': 'create',
                'event_id': event_id,
                'event': event
            }
            
            self._add_to_history('create', {
                'event_id': event_id,
                'title': event['title']
            })
            
            return result
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {'error': str(e)}
    
    async def _read_event(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read a calendar event.
        
        Args:
            args: Read arguments
            
        Returns:
            Dict[str, Any]: Result of read operation
        """
        try:
            if not args or 'event_id' not in args:
                return {'error': 'Missing event ID'}
            
            event_id = args['event_id']
            if event_id not in self._events:
                return {'error': 'Event not found'}
            
            result = {
                'status': 'success',
                'action': 'read',
                'event': self._events[event_id]
            }
            
            self._add_to_history('read', {
                'event_id': event_id
            })
            
            return result
        except Exception as e:
            logger.error(f"Error reading event: {e}")
            return {'error': str(e)}
    
    async def _update_event(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update a calendar event.
        
        Args:
            args: Update arguments
            
        Returns:
            Dict[str, Any]: Result of update operation
        """
        try:
            if not args or 'event_id' not in args or not self._validate_event(args):
                return {'error': 'Invalid update data'}
            
            event_id = args['event_id']
            if event_id not in self._events:
                return {'error': 'Event not found'}
            
            # Update event
            event = self._events[event_id]
            event.update({
                'title': args['title'],
                'description': args.get('description', event['description']),
                'start_time': args['start_time'],
                'end_time': args['end_time'],
                'location': args.get('location', event['location']),
                'attendees': args.get('attendees', event['attendees']),
                'updated_at': datetime.now().isoformat()
            })
            
            result = {
                'status': 'success',
                'action': 'update',
                'event_id': event_id,
                'event': event
            }
            
            self._add_to_history('update', {
                'event_id': event_id,
                'title': event['title']
            })
            
            return result
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return {'error': str(e)}
    
    async def _delete_event(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete a calendar event.
        
        Args:
            args: Delete arguments
            
        Returns:
            Dict[str, Any]: Result of delete operation
        """
        try:
            if not args or 'event_id' not in args:
                return {'error': 'Missing event ID'}
            
            event_id = args['event_id']
            if event_id not in self._events:
                return {'error': 'Event not found'}
            
            # Delete event
            event = self._events.pop(event_id)
            
            # Delete recurring events
            if event.get('recurrence'):
                for recur_id in list(self._events.keys()):
                    if recur_id.startswith(f"{event_id}_recur_"):
                        self._events.pop(recur_id)
            
            result = {
                'status': 'success',
                'action': 'delete',
                'event_id': event_id
            }
            
            self._add_to_history('delete', {
                'event_id': event_id,
                'title': event['title']
            })
            
            return result
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return {'error': str(e)}
    
    async def _search_events(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search calendar events.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Result of search operation
        """
        try:
            if not args:
                return {'error': 'Missing search criteria'}
            
            query = args.get('query', '').lower()
            start_time = args.get('start_time')
            end_time = args.get('end_time')
            location = args.get('location', '').lower()
            
            # Convert time strings to datetime objects
            if start_time:
                start_time = datetime.fromisoformat(start_time)
            if end_time:
                end_time = datetime.fromisoformat(end_time)
            
            # Search events
            matching_events = []
            for event in self._events.values():
                # Skip recurring event instances
                if '_recur_' in event['id']:
                    continue
                
                # Check query match
                if query and query not in event['title'].lower() and query not in event['description'].lower():
                    continue
                
                # Check time range
                event_start = datetime.fromisoformat(event['start_time'])
                event_end = datetime.fromisoformat(event['end_time'])
                
                if start_time and event_end < start_time:
                    continue
                if end_time and event_start > end_time:
                    continue
                
                # Check location
                if location and location not in event['location'].lower():
                    continue
                
                matching_events.append(event)
            
            result = {
                'status': 'success',
                'action': 'search',
                'events': matching_events
            }
            
            self._add_to_history('search', {
                'query': query,
                'result_count': len(matching_events)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get operation history.
        
        Returns:
            Dict[str, Any]: Operation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._operation_history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear operation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._operation_history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)} 