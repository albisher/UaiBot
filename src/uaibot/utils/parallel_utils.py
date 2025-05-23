#!/usr/bin/env python3
"""
Parallel Processing Utilities for UaiBot

This module provides utilities for parallel processing in UaiBot,
including thread pools for I/O-bound operations and process pools
for CPU-intensive operations.
"""

import concurrent.futures
import threading
import logging
from .typing import Callable, List, Any, Dict, Optional, Union, Tuple
import time

logger = logging.getLogger(__name__)

class ParallelTaskManager:
    """
    Manages parallel task execution using thread pools for I/O-bound tasks
    and process pools for CPU-intensive tasks.
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Initialize the parallel task manager.
        
        Args:
            max_workers: Maximum number of workers (threads or processes)
            use_processes: If True, use process pool instead of thread pool
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self._executor = None
        self._lock = threading.RLock()
        logger.debug(f"Initialized ParallelTaskManager with max_workers={max_workers}, use_processes={use_processes}")
    
    def __enter__(self):
        """
Context manager entry point.
        """
        self._create_executor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
Context manager exit point.
        """
        self.shutdown()
    
    def _create_executor(self):
        """
Create the appropriate executor based on configuration.
        """
        with self._lock:
            if self._executor is None:
                if self.use_processes:
                    self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
                    logger.debug("Created ProcessPoolExecutor")
                else:
                    self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
                    logger.debug("Created ThreadPoolExecutor")
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the executor.
        
        Args:
            wait: If True, wait for all pending tasks to complete
        """
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None
                logger.debug(f"Shutdown executor with wait={wait}")
    
    def submit(self, fn: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """
        Submit a task for execution.
        
        Args:
            fn: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future object representing the execution of the task
        """
        self._create_executor()
        future = self._executor.submit(fn, *args, **kwargs)
        logger.debug(f"Submitted task {fn.__name__} for execution")
        return future
    
    def map(self, fn: Callable, *iterables, timeout: Optional[float] = None, chunksize: int = 1) -> List[Any]:
        """
        Execute a function on each item in the iterables in parallel.
        
        Args:
            fn: Function to execute
            *iterables: Iterables containing arguments for the function
            timeout: Maximum time to wait for results
            chunksize: Size of chunks for process pool execution
            
        Returns:
            List of results
        """
        self._create_executor()
        results = list(self._executor.map(fn, *iterables, timeout=timeout, chunksize=chunksize))
        logger.debug(f"Mapped {fn.__name__} over {len(results)} items")
        return results


def run_parallel(tasks: List[Tuple[Callable, List, Dict]], 
                max_workers: Optional[int] = None, 
                use_processes: bool = False,
                timeout: Optional[float] = None) -> List[Any]:
    """
    Run multiple tasks in parallel and return their results.
    
    Args:
        tasks: List of tuples (function, args, kwargs) to execute
        max_workers: Maximum number of workers (threads or processes)
        use_processes: If True, use process pool instead of thread pool
        timeout: Maximum time to wait for results
        
    Returns:
        List of results in the same order as the tasks
    """
    with ParallelTaskManager(max_workers=max_workers, use_processes=use_processes) as manager:
        futures = []
        for fn, args, kwargs in tasks:
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            futures.append(manager.submit(fn, *args, **kwargs))
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except Exception as exc:
                logger.error(f"Task generated an exception: {exc}")
                results.append(None)
        
        return results


def run_with_timeout(fn: Callable, args: List = None, kwargs: Dict = None, 
                    timeout: float = 5.0, default_result: Any = None) -> Any:
    """
    Run a function with a timeout and return a default result if it times out.
    
    Args:
        fn: Function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        timeout: Maximum time to wait for the function to complete
        default_result: Result to return if the function times out
        
    Returns:
        Function result or default_result if timed out
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    
    with ParallelTaskManager(max_workers=1) as manager:
        future = manager.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            logger.warning(f"Function {fn.__name__} timed out after {timeout} seconds")
            return default_result
        except Exception as exc:
            logger.error(f"Function {fn.__name__} raised an exception: {exc}")
            return default_result