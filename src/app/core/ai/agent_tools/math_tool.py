"""
Math tool with A2A, MCP, and SmolAgents compliance.

This tool provides mathematical operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import math
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class MathTool(BaseTool):
    """Tool for performing mathematical operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the math tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="math",
            description="Tool for performing mathematical operations",
            config=config
        )
        self._max_precision = config.get('max_precision', 10)
        self._max_matrix_size = config.get('max_matrix_size', 1000)
        self._max_vector_size = config.get('max_vector_size', 1000)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Math cache
        self._cache_duration = config.get('cache_duration', 3600)  # 1 hour
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize cache
            self._cache = {}
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize MathTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up MathTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'basic': True,
            'trigonometric': True,
            'logarithmic': True,
            'statistical': True,
            'matrix': True,
            'vector': True,
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
            'max_precision': self._max_precision,
            'max_matrix_size': self._max_matrix_size,
            'max_vector_size': self._max_vector_size,
            'cache_duration': self._cache_duration,
            'cache_size': len(self._cache),
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
        if command == 'basic':
            return await self._basic_operation(args)
        elif command == 'trigonometric':
            return await self._trigonometric_operation(args)
        elif command == 'logarithmic':
            return await self._logarithmic_operation(args)
        elif command == 'statistical':
            return await self._statistical_operation(args)
        elif command == 'matrix':
            return await self._matrix_operation(args)
        elif command == 'vector':
            return await self._vector_operation(args)
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
    
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate a cache key for math operation.
        
        Args:
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [operation]
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (list, tuple)):
                params.append(f"{key}={hashlib.md5(str(value).encode()).hexdigest()}")
            else:
                params.append(f"{key}={value}")
        return "|".join(params)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key]['timestamp']
        return time.time() - cache_time < self._cache_duration
    
    def _validate_matrix(self, matrix: List[List[float]]) -> Tuple[bool, Optional[str]]:
        """Validate matrix data.
        
        Args:
            matrix: Matrix data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not matrix:
            return False, 'Matrix is empty'
        
        rows = len(matrix)
        if rows > self._max_matrix_size:
            return False, f'Matrix exceeds maximum size ({self._max_matrix_size})'
        
        cols = len(matrix[0])
        if cols > self._max_matrix_size:
            return False, f'Matrix exceeds maximum size ({self._max_matrix_size})'
        
        for row in matrix:
            if len(row) != cols:
                return False, 'Matrix is not rectangular'
        
        return True, None
    
    def _validate_vector(self, vector: List[float]) -> Tuple[bool, Optional[str]]:
        """Validate vector data.
        
        Args:
            vector: Vector data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not vector:
            return False, 'Vector is empty'
        
        if len(vector) > self._max_vector_size:
            return False, f'Vector exceeds maximum size ({self._max_vector_size})'
        
        return True, None
    
    async def _process_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Process mathematical operation.
        
        Args:
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Check cache
            cache_key = self._get_cache_key(operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process operation
            if operation == 'basic':
                op = kwargs.get('op')
                a = kwargs.get('a')
                b = kwargs.get('b')
                
                if op == 'add':
                    result = a + b
                elif op == 'subtract':
                    result = a - b
                elif op == 'multiply':
                    result = a * b
                elif op == 'divide':
                    if b == 0:
                        return {'error': 'Division by zero'}
                    result = a / b
                elif op == 'power':
                    result = a ** b
                elif op == 'root':
                    if b == 0:
                        return {'error': 'Invalid root degree'}
                    result = a ** (1/b)
                else:
                    return {'error': f'Unsupported basic operation: {op}'}
                
                processed_data = round(result, self._max_precision)
            
            elif operation == 'trigonometric':
                func = kwargs.get('func')
                angle = kwargs.get('angle')
                is_radians = kwargs.get('is_radians', True)
                
                if not is_radians:
                    angle = math.radians(angle)
                
                if func == 'sin':
                    result = math.sin(angle)
                elif func == 'cos':
                    result = math.cos(angle)
                elif func == 'tan':
                    result = math.tan(angle)
                elif func == 'asin':
                    result = math.asin(angle)
                elif func == 'acos':
                    result = math.acos(angle)
                elif func == 'atan':
                    result = math.atan(angle)
                else:
                    return {'error': f'Unsupported trigonometric function: {func}'}
                
                processed_data = round(result, self._max_precision)
            
            elif operation == 'logarithmic':
                func = kwargs.get('func')
                x = kwargs.get('x')
                base = kwargs.get('base', math.e)
                
                if func == 'log':
                    if x <= 0:
                        return {'error': 'Invalid logarithm argument'}
                    result = math.log(x, base)
                elif func == 'ln':
                    if x <= 0:
                        return {'error': 'Invalid logarithm argument'}
                    result = math.log(x)
                else:
                    return {'error': f'Unsupported logarithmic function: {func}'}
                
                processed_data = round(result, self._max_precision)
            
            elif operation == 'statistical':
                func = kwargs.get('func')
                data = kwargs.get('data')
                
                if func == 'mean':
                    result = np.mean(data)
                elif func == 'median':
                    result = np.median(data)
                elif func == 'std':
                    result = np.std(data)
                elif func == 'var':
                    result = np.var(data)
                else:
                    return {'error': f'Unsupported statistical function: {func}'}
                
                processed_data = round(result, self._max_precision)
            
            elif operation == 'matrix':
                func = kwargs.get('func')
                matrix = kwargs.get('matrix')
                
                # Validate matrix
                is_valid, error = self._validate_matrix(matrix)
                if not is_valid:
                    return {'error': error}
                
                if func == 'add':
                    other = kwargs.get('other')
                    is_valid, error = self._validate_matrix(other)
                    if not is_valid:
                        return {'error': error}
                    result = np.add(matrix, other)
                elif func == 'multiply':
                    other = kwargs.get('other')
                    is_valid, error = self._validate_matrix(other)
                    if not is_valid:
                        return {'error': error}
                    result = np.matmul(matrix, other)
                elif func == 'transpose':
                    result = np.transpose(matrix)
                elif func == 'determinant':
                    result = np.linalg.det(matrix)
                elif func == 'inverse':
                    result = np.linalg.inv(matrix)
                else:
                    return {'error': f'Unsupported matrix operation: {func}'}
                
                if isinstance(result, np.ndarray):
                    processed_data = result.tolist()
                else:
                    processed_data = round(result, self._max_precision)
            
            elif operation == 'vector':
                func = kwargs.get('func')
                vector = kwargs.get('vector')
                
                # Validate vector
                is_valid, error = self._validate_vector(vector)
                if not is_valid:
                    return {'error': error}
                
                if func == 'add':
                    other = kwargs.get('other')
                    is_valid, error = self._validate_vector(other)
                    if not is_valid:
                        return {'error': error}
                    result = np.add(vector, other)
                elif func == 'dot':
                    other = kwargs.get('other')
                    is_valid, error = self._validate_vector(other)
                    if not is_valid:
                        return {'error': error}
                    result = np.dot(vector, other)
                elif func == 'cross':
                    other = kwargs.get('other')
                    is_valid, error = self._validate_vector(other)
                    if not is_valid:
                        return {'error': error}
                    result = np.cross(vector, other)
                elif func == 'norm':
                    result = np.linalg.norm(vector)
                else:
                    return {'error': f'Unsupported vector operation: {func}'}
                
                if isinstance(result, np.ndarray):
                    processed_data = result.tolist()
                else:
                    processed_data = round(result, self._max_precision)
            
            # Cache result
            self._cache[cache_key] = {
                'data': {
                    'status': 'success',
                    'action': operation,
                    'result': processed_data
                },
                'timestamp': time.time()
            }
            
            return self._cache[cache_key]['data']
        except Exception as e:
            logger.error(f"Error processing operation: {e}")
            return {'error': str(e)}
    
    async def _basic_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform basic mathematical operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'op' not in args or 'a' not in args or 'b' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'basic',
                op=args['op'],
                a=args['a'],
                b=args['b']
            )
            
            if 'error' not in result:
                self._add_to_history('basic', {
                    'operation': args['op'],
                    'a': args['a'],
                    'b': args['b'],
                    'result': result['result']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing basic operation: {e}")
            return {'error': str(e)}
    
    async def _trigonometric_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform trigonometric operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'func' not in args or 'angle' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'trigonometric',
                func=args['func'],
                angle=args['angle'],
                is_radians=args.get('is_radians', True)
            )
            
            if 'error' not in result:
                self._add_to_history('trigonometric', {
                    'function': args['func'],
                    'angle': args['angle'],
                    'is_radians': args.get('is_radians', True),
                    'result': result['result']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing trigonometric operation: {e}")
            return {'error': str(e)}
    
    async def _logarithmic_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform logarithmic operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'func' not in args or 'x' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'logarithmic',
                func=args['func'],
                x=args['x'],
                base=args.get('base', math.e)
            )
            
            if 'error' not in result:
                self._add_to_history('logarithmic', {
                    'function': args['func'],
                    'x': args['x'],
                    'base': args.get('base', math.e),
                    'result': result['result']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing logarithmic operation: {e}")
            return {'error': str(e)}
    
    async def _statistical_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform statistical operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'func' not in args or 'data' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'statistical',
                func=args['func'],
                data=args['data']
            )
            
            if 'error' not in result:
                self._add_to_history('statistical', {
                    'function': args['func'],
                    'data_length': len(args['data']),
                    'result': result['result']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing statistical operation: {e}")
            return {'error': str(e)}
    
    async def _matrix_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform matrix operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'func' not in args or 'matrix' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'matrix',
                func=args['func'],
                matrix=args['matrix'],
                other=args.get('other')
            )
            
            if 'error' not in result:
                self._add_to_history('matrix', {
                    'function': args['func'],
                    'matrix_size': [len(args['matrix']), len(args['matrix'][0])],
                    'result_size': len(result['result']) if isinstance(result['result'], list) else 1
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing matrix operation: {e}")
            return {'error': str(e)}
    
    async def _vector_operation(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform vector operation.
        
        Args:
            args: Operation arguments
            
        Returns:
            Dict[str, Any]: Operation result
        """
        try:
            if not args or 'func' not in args or 'vector' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_operation(
                'vector',
                func=args['func'],
                vector=args['vector'],
                other=args.get('other')
            )
            
            if 'error' not in result:
                self._add_to_history('vector', {
                    'function': args['func'],
                    'vector_size': len(args['vector']),
                    'result_size': len(result['result']) if isinstance(result['result'], list) else 1
                })
            
            return result
        except Exception as e:
            logger.error(f"Error performing vector operation: {e}")
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