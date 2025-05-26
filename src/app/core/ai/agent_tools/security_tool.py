"""
Security tool with A2A, MCP, and SmolAgents compliance.

This tool provides security operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import hashlib
import hmac
import base64
import secrets
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class SecurityTool(BaseTool):
    """Tool for performing security operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the security tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="security",
            description="Tool for performing security operations",
            config=config
        )
        self._min_password_length = config.get('min_password_length', 8)
        self._max_password_length = config.get('max_password_length', 128)
        self._hash_algorithm = config.get('hash_algorithm', 'sha256')
        self._salt_length = config.get('salt_length', 16)
        self._token_length = config.get('token_length', 32)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate hash algorithm
            if self._hash_algorithm not in hashlib.algorithms_available:
                logger.error(f"Invalid hash algorithm: {self._hash_algorithm}")
                return False
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize SecurityTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up SecurityTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'hash': True,
            'hmac': True,
            'encrypt': True,
            'decrypt': True,
            'generate_token': True,
            'validate_password': True,
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
            'min_password_length': self._min_password_length,
            'max_password_length': self._max_password_length,
            'hash_algorithm': self._hash_algorithm,
            'salt_length': self._salt_length,
            'token_length': self._token_length,
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
        if command == 'hash':
            return await self._hash(args)
        elif command == 'hmac':
            return await self._hmac(args)
        elif command == 'encrypt':
            return await self._encrypt(args)
        elif command == 'decrypt':
            return await self._decrypt(args)
        elif command == 'generate_token':
            return await self._generate_token(args)
        elif command == 'validate_password':
            return await self._validate_password(args)
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
    
    async def _hash(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hash data with specified algorithm.
        
        Args:
            args: Hash arguments
            
        Returns:
            Dict[str, Any]: Hash result
        """
        try:
            if not args or 'data' not in args:
                return {'error': 'Missing required arguments'}
            
            data = args['data']
            algorithm = args.get('algorithm', self._hash_algorithm)
            salt = args.get('salt')
            
            # Validate algorithm
            if algorithm not in hashlib.algorithms_available:
                return {
                    'status': 'error',
                    'action': 'hash',
                    'error': f'Invalid hash algorithm: {algorithm}'
                }
            
            # Generate salt if not provided
            if not salt:
                salt = secrets.token_bytes(self._salt_length)
            
            # Hash data
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(salt)
            hash_obj.update(data.encode() if isinstance(data, str) else data)
            hash_value = hash_obj.hexdigest()
            
            self._add_to_history('hash', {
                'algorithm': algorithm,
                'salt': base64.b64encode(salt).decode(),
                'hash': hash_value
            })
            
            return {
                'status': 'success',
                'action': 'hash',
                'algorithm': algorithm,
                'salt': base64.b64encode(salt).decode(),
                'hash': hash_value
            }
        except Exception as e:
            logger.error(f"Error hashing data: {e}")
            return {'error': str(e)}
    
    async def _hmac(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate HMAC for data.
        
        Args:
            args: HMAC arguments
            
        Returns:
            Dict[str, Any]: HMAC result
        """
        try:
            if not args or 'data' not in args or 'key' not in args:
                return {'error': 'Missing required arguments'}
            
            data = args['data']
            key = args['key']
            algorithm = args.get('algorithm', self._hash_algorithm)
            
            # Validate algorithm
            if algorithm not in hashlib.algorithms_available:
                return {
                    'status': 'error',
                    'action': 'hmac',
                    'error': f'Invalid hash algorithm: {algorithm}'
                }
            
            # Generate HMAC
            hmac_obj = hmac.new(
                key.encode() if isinstance(key, str) else key,
                data.encode() if isinstance(data, str) else data,
                getattr(hashlib, algorithm)
            )
            hmac_value = hmac_obj.hexdigest()
            
            self._add_to_history('hmac', {
                'algorithm': algorithm,
                'hmac': hmac_value
            })
            
            return {
                'status': 'success',
                'action': 'hmac',
                'algorithm': algorithm,
                'hmac': hmac_value
            }
        except Exception as e:
            logger.error(f"Error generating HMAC: {e}")
            return {'error': str(e)}
    
    async def _encrypt(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encrypt data.
        
        Args:
            args: Encryption arguments
            
        Returns:
            Dict[str, Any]: Encryption result
        """
        try:
            if not args or 'data' not in args:
                return {'error': 'Missing required arguments'}
            
            # Placeholder for encryption implementation
            return {
                'status': 'error',
                'action': 'encrypt',
                'error': 'Encryption not implemented'
            }
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return {'error': str(e)}
    
    async def _decrypt(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Decrypt data.
        
        Args:
            args: Decryption arguments
            
        Returns:
            Dict[str, Any]: Decryption result
        """
        try:
            if not args or 'data' not in args:
                return {'error': 'Missing required arguments'}
            
            # Placeholder for decryption implementation
            return {
                'status': 'error',
                'action': 'decrypt',
                'error': 'Decryption not implemented'
            }
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return {'error': str(e)}
    
    async def _generate_token(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate secure token.
        
        Args:
            args: Token generation arguments
            
        Returns:
            Dict[str, Any]: Token generation result
        """
        try:
            length = args.get('length', self._token_length) if args else self._token_length
            
            # Generate token
            token = secrets.token_urlsafe(length)
            
            self._add_to_history('generate_token', {
                'length': length,
                'token': token
            })
            
            return {
                'status': 'success',
                'action': 'generate_token',
                'length': length,
                'token': token
            }
        except Exception as e:
            logger.error(f"Error generating token: {e}")
            return {'error': str(e)}
    
    async def _validate_password(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate password strength.
        
        Args:
            args: Password validation arguments
            
        Returns:
            Dict[str, Any]: Password validation result
        """
        try:
            if not args or 'password' not in args:
                return {'error': 'Missing required arguments'}
            
            password = args['password']
            
            # Check length
            if len(password) < self._min_password_length:
                return {
                    'status': 'error',
                    'action': 'validate_password',
                    'error': f'Password too short (minimum {self._min_password_length} characters)'
                }
            if len(password) > self._max_password_length:
                return {
                    'status': 'error',
                    'action': 'validate_password',
                    'error': f'Password too long (maximum {self._max_password_length} characters)'
                }
            
            # Check complexity
            checks = {
                'length': len(password) >= self._min_password_length,
                'uppercase': bool(re.search(r'[A-Z]', password)),
                'lowercase': bool(re.search(r'[a-z]', password)),
                'digit': bool(re.search(r'\d', password)),
                'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
            }
            
            # Calculate strength score
            strength = sum(checks.values()) / len(checks)
            
            self._add_to_history('validate_password', {
                'checks': checks,
                'strength': strength
            })
            
            return {
                'status': 'success',
                'action': 'validate_password',
                'checks': checks,
                'strength': strength
            }
        except Exception as e:
            logger.error(f"Error validating password: {e}")
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