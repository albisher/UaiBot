"""
Calculator tool with A2A, MCP, and SmolAgents compliance.

This tool provides calculation functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import math
from typing import Dict, Any, List, Optional, Union
from src.app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the calculator tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="calculator",
            description="Tool for performing mathematical calculations",
            config=config
        )
        self._precision = config.get('precision', 10)
        self._angle_mode = config.get('angle_mode', 'radians')
        self._history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate configuration
            if self._angle_mode not in ['radians', 'degrees']:
                logger.error(f"Invalid angle mode: {self._angle_mode}")
                return False
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize CalculatorTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up CalculatorTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'basic_arithmetic': True,
            'trigonometric': True,
            'logarithmic': True,
            'exponential': True,
            'statistical': True,
            'unit_conversion': True,
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
            'precision': self._precision,
            'angle_mode': self._angle_mode,
            'history_size': len(self._history),
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
        if command == 'calculate':
            return await self._calculate(args)
        elif command == 'convert_units':
            return await self._convert_units(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, result: Any) -> None:
        """Add an operation and its result to history.
        
        Args:
            operation: Operation performed
            result: Result of the operation
        """
        self._history.append({
            'operation': operation,
            'result': result,
            'timestamp': math.floor(time.time())
        })
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    async def _calculate(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a calculation.
        
        Args:
            args: Calculation arguments
            
        Returns:
            Dict[str, Any]: Result of calculation
        """
        try:
            if not args or 'expression' not in args:
                return {'error': 'Missing expression parameter'}
            
            expression = args['expression']
            precision = args.get('precision', self._precision)
            
            # Convert angle mode if needed
            if self._angle_mode == 'degrees':
                expression = expression.replace('sin', 'math.sin(math.radians')
                expression = expression.replace('cos', 'math.cos(math.radians')
                expression = expression.replace('tan', 'math.tan(math.radians')
                expression = expression.replace('asin', 'math.degrees(math.asin')
                expression = expression.replace('acos', 'math.degrees(math.acos')
                expression = expression.replace('atan', 'math.degrees(math.atan')
            
            # Evaluate expression
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            
            # Round result if needed
            if isinstance(result, (int, float)):
                result = round(result, precision)
            
            # Add to history
            self._add_to_history(expression, result)
            
            return {
                'status': 'success',
                'action': 'calculate',
                'expression': expression,
                'result': result,
                'precision': precision
            }
        except Exception as e:
            logger.error(f"Error calculating expression: {e}")
            return {'error': str(e)}
    
    async def _convert_units(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert between units.
        
        Args:
            args: Unit conversion arguments
            
        Returns:
            Dict[str, Any]: Result of unit conversion
        """
        try:
            if not args or not all(k in args for k in ['value', 'from_unit', 'to_unit']):
                return {'error': 'Missing required parameters'}
            
            value = args['value']
            from_unit = args['from_unit']
            to_unit = args['to_unit']
            precision = args.get('precision', self._precision)
            
            # Define conversion factors
            conversions = {
                'length': {
                    'm': 1.0,
                    'km': 1000.0,
                    'cm': 0.01,
                    'mm': 0.001,
                    'in': 0.0254,
                    'ft': 0.3048,
                    'yd': 0.9144,
                    'mi': 1609.344
                },
                'mass': {
                    'kg': 1.0,
                    'g': 0.001,
                    'mg': 0.000001,
                    'lb': 0.45359237,
                    'oz': 0.028349523125
                },
                'temperature': {
                    'c': lambda x: x,
                    'f': lambda x: (x - 32) * 5/9,
                    'k': lambda x: x - 273.15
                }
            }
            
            # Determine conversion type
            conversion_type = None
            for type_name, units in conversions.items():
                if from_unit in units and to_unit in units:
                    conversion_type = type_name
                    break
            
            if not conversion_type:
                return {'error': f'Unsupported unit conversion: {from_unit} to {to_unit}'}
            
            # Perform conversion
            if conversion_type == 'temperature':
                # Handle temperature conversions
                if from_unit == 'c' and to_unit == 'f':
                    result = value * 9/5 + 32
                elif from_unit == 'f' and to_unit == 'c':
                    result = (value - 32) * 5/9
                elif from_unit == 'c' and to_unit == 'k':
                    result = value + 273.15
                elif from_unit == 'k' and to_unit == 'c':
                    result = value - 273.15
                elif from_unit == 'f' and to_unit == 'k':
                    result = (value - 32) * 5/9 + 273.15
                elif from_unit == 'k' and to_unit == 'f':
                    result = (value - 273.15) * 9/5 + 32
            else:
                # Handle other conversions
                from_factor = conversions[conversion_type][from_unit]
                to_factor = conversions[conversion_type][to_unit]
                result = value * from_factor / to_factor
            
            # Round result
            result = round(result, precision)
            
            # Add to history
            self._add_to_history(f"{value} {from_unit} to {to_unit}", result)
            
            return {
                'status': 'success',
                'action': 'convert_units',
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': result,
                'precision': precision
            }
        except Exception as e:
            logger.error(f"Error converting units: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get calculation history.
        
        Returns:
            Dict[str, Any]: Calculation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear calculation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)} 