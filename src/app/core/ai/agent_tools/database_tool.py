"""
Database tool with A2A, MCP, and SmolAgents compliance.

This tool provides database operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import aiomysql
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class DatabaseTool(BaseTool):
    """Tool for performing database operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the database tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="database",
            description="Tool for performing database operations",
            config=config
        )
        self._host = config.get('host', 'localhost')
        self._port = config.get('port', 3306)
        self._user = config.get('user', '')
        self._password = config.get('password', '')
        self._database = config.get('database', '')
        self._max_connections = config.get('max_connections', 10)
        self._max_query_time = config.get('max_query_time', 30)  # seconds
        self._max_results = config.get('max_results', 1000)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._pool = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if not all([self._user, self._password, self._database]):
                logger.error("Database credentials are required")
                return False
            
            # Initialize connection pool
            self._pool = await aiomysql.create_pool(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                db=self._database,
                maxsize=self._max_connections,
                autocommit=True
            )
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize DatabaseTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._pool:
                self._pool.close()
                await self._pool.wait_closed()
                self._pool = None
            
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up DatabaseTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'query': True,
            'execute': True,
            'transaction': True,
            'schema': True,
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
            'host': self._host,
            'port': self._port,
            'database': self._database,
            'max_connections': self._max_connections,
            'max_query_time': self._max_query_time,
            'max_results': self._max_results,
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
        if command == 'query':
            return await self._query(args)
        elif command == 'execute':
            return await self._execute(args)
        elif command == 'transaction':
            return await self._transaction(args)
        elif command == 'schema':
            return await self._schema(args)
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
    
    def _validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate SQL query.
        
        Args:
            query: SQL query to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Basic SQL injection prevention
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT',
            'UPDATE', 'GRANT', 'REVOKE', 'SHUTDOWN', '--', ';'
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False, f'Query contains dangerous keyword: {keyword}'
        
        return True, None
    
    async def _query(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a SELECT query.
        
        Args:
            args: Query arguments
            
        Returns:
            Dict[str, Any]: Query results
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            query = args['query']
            params = args.get('params', [])
            
            # Validate query
            is_valid, error = self._validate_query(query)
            if not is_valid:
                return {'error': error}
            
            if not self._pool:
                return {'error': 'Database connection not initialized'}
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    results = await cur.fetchall()
                    
                    # Get column names
                    columns = [desc[0] for desc in cur.description]
                    
                    # Convert results to list of dictionaries
                    rows = []
                    for row in results[:self._max_results]:
                        rows.append(dict(zip(columns, row)))
                    
                    self._add_to_history('query', {
                        'query': query,
                        'params': params,
                        'rows_returned': len(rows)
                    })
                    
                    return {
                        'status': 'success',
                        'action': 'query',
                        'columns': columns,
                        'rows': rows,
                        'total': len(rows)
                    }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {'error': str(e)}
    
    async def _execute(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a non-SELECT query.
        
        Args:
            args: Query arguments
            
        Returns:
            Dict[str, Any]: Execution result
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing required arguments'}
            
            query = args['query']
            params = args.get('params', [])
            
            # Validate query
            is_valid, error = self._validate_query(query)
            if not is_valid:
                return {'error': error}
            
            if not self._pool:
                return {'error': 'Database connection not initialized'}
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    affected_rows = cur.rowcount
                    
                    self._add_to_history('execute', {
                        'query': query,
                        'params': params,
                        'affected_rows': affected_rows
                    })
                    
                    return {
                        'status': 'success',
                        'action': 'execute',
                        'affected_rows': affected_rows
                    }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {'error': str(e)}
    
    async def _transaction(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a transaction.
        
        Args:
            args: Transaction arguments
            
        Returns:
            Dict[str, Any]: Transaction result
        """
        try:
            if not args or 'queries' not in args:
                return {'error': 'Missing required arguments'}
            
            queries = args['queries']
            params_list = args.get('params_list', [[]] * len(queries))
            
            if len(queries) != len(params_list):
                return {'error': 'Number of queries and parameters must match'}
            
            # Validate queries
            for query in queries:
                is_valid, error = self._validate_query(query)
                if not is_valid:
                    return {'error': error}
            
            if not self._pool:
                return {'error': 'Database connection not initialized'}
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        # Start transaction
                        await conn.begin()
                        
                        results = []
                        for query, params in zip(queries, params_list):
                            await cur.execute(query, params)
                            affected_rows = cur.rowcount
                            results.append({
                                'query': query,
                                'params': params,
                                'affected_rows': affected_rows
                            })
                        
                        # Commit transaction
                        await conn.commit()
                        
                        self._add_to_history('transaction', {
                            'queries': queries,
                            'params_list': params_list,
                            'results': results
                        })
                        
                        return {
                            'status': 'success',
                            'action': 'transaction',
                            'results': results
                        }
                    except Exception as e:
                        # Rollback transaction
                        await conn.rollback()
                        raise e
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return {'error': str(e)}
    
    async def _schema(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get database schema information.
        
        Args:
            args: Schema arguments
            
        Returns:
            Dict[str, Any]: Schema information
        """
        try:
            if not self._pool:
                return {'error': 'Database connection not initialized'}
            
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Get tables
                    await cur.execute("SHOW TABLES")
                    tables = [row[0] for row in await cur.fetchall()]
                    
                    # Get table information
                    table_info = {}
                    for table in tables:
                        await cur.execute(f"DESCRIBE {table}")
                        columns = await cur.fetchall()
                        table_info[table] = [{
                            'field': col[0],
                            'type': col[1],
                            'null': col[2],
                            'key': col[3],
                            'default': col[4],
                            'extra': col[5]
                        } for col in columns]
                    
                    self._add_to_history('schema', {
                        'tables': tables,
                        'table_info': table_info
                    })
                    
                    return {
                        'status': 'success',
                        'action': 'schema',
                        'tables': tables,
                        'table_info': table_info
                    }
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
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