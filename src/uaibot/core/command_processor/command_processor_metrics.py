"""
Command Processor Metrics module for UaiBot.

This module provides metrics collection for command processors,
including performance metrics, resource usage, and system health.

The module includes:
- Metrics collection
- Performance monitoring
- Resource tracking
- System health checks

Example:
    >>> from .command_processor_metrics import CommandProcessorMetrics
    >>> metrics = CommandProcessorMetrics()
    >>> metrics.collect_metrics()
"""
import logging
import json
import os
import psutil
import time
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from .command_processor_types import Command, CommandResult
from .command_processor_exceptions import CommandValidationError, CommandSafetyError, CommandProcessingError, AIError

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for metrics responses
T = TypeVar('T')
MetricsResponse = TypeVar('MetricsResponse')

@dataclass
class MetricsConfig:
    """Configuration for the command processor metrics."""
    metrics_file: str = "metrics/processor_metrics.json"
    collect_interval: float = 60.0  # seconds
    track_cpu: bool = True
    track_memory: bool = True
    track_disk: bool = True
    track_network: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """System metrics for command processing."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessMetrics:
    """Process metrics for command processing."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    num_threads: int = 0
    num_handles: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessorMetrics:
    """Metrics collector for command processors."""
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        """Initialize the command processor metrics.
        
        Args:
            config: Optional metrics configuration
        """
        self.config = config or MetricsConfig()
        self.process = psutil.Process()
        self.last_network_io = psutil.net_io_counters()
        self.last_collection_time = time.time()
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics.
        
        Returns:
            Collected system metrics
        """
        try:
            metrics = SystemMetrics()
            
            if self.config.track_cpu:
                metrics.cpu_percent = psutil.cpu_percent()
                
            if self.config.track_memory:
                metrics.memory_percent = psutil.virtual_memory().percent
                
            if self.config.track_disk:
                metrics.disk_usage_percent = psutil.disk_usage('/').percent
                
            if self.config.track_network:
                current_network_io = psutil.net_io_counters()
                metrics.network_bytes_sent = current_network_io.bytes_sent - self.last_network_io.bytes_sent
                metrics.network_bytes_recv = current_network_io.bytes_recv - self.last_network_io.bytes_recv
                self.last_network_io = current_network_io
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise
            
    def collect_process_metrics(self) -> ProcessMetrics:
        """Collect process metrics.
        
        Returns:
            Collected process metrics
        """
        try:
            metrics = ProcessMetrics()
            
            if self.config.track_cpu:
                metrics.cpu_percent = self.process.cpu_percent()
                
            if self.config.track_memory:
                metrics.memory_percent = self.process.memory_percent()
                
            metrics.num_threads = self.process.num_threads()
            metrics.num_handles = self.process.num_handles()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            raise
            
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect all metrics.
        
        Returns:
            Collected metrics
        """
        try:
            current_time = time.time()
            
            # Check if it's time to collect metrics
            if current_time - self.last_collection_time < self.config.collect_interval:
                return {}
                
            # Collect metrics
            system_metrics = self.collect_system_metrics()
            process_metrics = self.collect_process_metrics()
            
            # Update last collection time
            self.last_collection_time = current_time
            
            return {
                "system": system_metrics.__dict__,
                "process": process_metrics.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            raise
            
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file.
        
        Args:
            metrics: Metrics to save
        """
        try:
            if not metrics:
                return
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config.metrics_file), exist_ok=True)
            
            # Save metrics
            with open(self.config.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=4)
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            raise
            
    def load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file.
        
        Returns:
            Loaded metrics
        """
        try:
            if os.path.exists(self.config.metrics_file):
                with open(self.config.metrics_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            logger.error(f"Error loading metrics: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    metrics = CommandProcessorMetrics()
    
    # Collect metrics
    collected_metrics = metrics.collect_metrics()
    print(f"Collected metrics: {collected_metrics}")
    
    # Save metrics
    metrics.save_metrics(collected_metrics)
    
    # Load metrics
    loaded_metrics = metrics.load_metrics()
    print(f"Loaded metrics: {loaded_metrics}") 