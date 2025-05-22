"""
AI Performance Tracker Module

This module tracks and manages performance metrics for AI model interactions,
including response times, success rates, and token usage.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Data class for storing model-specific metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_response_time: float = 0.0
    last_used: Optional[datetime] = None
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

class AIPerformanceTracker:
    """Tracks and manages AI model performance metrics."""
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.metrics: Dict[str, ModelMetrics] = defaultdict(ModelMetrics)
        self.start_time = time.time()
    
    def track_request(
        self,
        model_name: str,
        start_time: float,
        success: bool,
        token_count: Optional[int] = None,
        error_type: Optional[str] = None
    ) -> None:
        """
        Track a single AI model request.
        
        Args:
            model_name: Name of the AI model
            start_time: Start time of the request
            success: Whether the request was successful
            token_count: Number of tokens used (if available)
            error_type: Type of error if request failed
        """
        metrics = self.metrics[model_name]
        metrics.total_requests += 1
        metrics.last_used = datetime.now()
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            if error_type:
                metrics.error_counts[error_type] += 1
        
        if token_count is not None:
            metrics.total_tokens += token_count
        
        metrics.total_response_time += time.time() - start_time
    
    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific model.
        
        Args:
            model_name: Name of the AI model
            
        Returns:
            Dictionary containing the model's performance metrics
        """
        metrics = self.metrics[model_name]
        total_time = metrics.total_response_time
        
        return {
            "total_requests": metrics.total_requests,
            "success_rate": (metrics.successful_requests / metrics.total_requests * 100 
                           if metrics.total_requests > 0 else 0),
            "average_response_time": (total_time / metrics.total_requests 
                                    if metrics.total_requests > 0 else 0),
            "total_tokens": metrics.total_tokens,
            "error_distribution": dict(metrics.error_counts),
            "last_used": metrics.last_used.isoformat() if metrics.last_used else None
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for all models.
        
        Returns:
            Dictionary containing metrics for all models
        """
        return {
            model_name: self.get_model_metrics(model_name)
            for model_name in self.metrics
        }
    
    def reset_metrics(self, model_name: Optional[str] = None) -> None:
        """
        Reset metrics for a specific model or all models.
        
        Args:
            model_name: Name of the model to reset, or None for all models
        """
        if model_name:
            self.metrics[model_name] = ModelMetrics()
        else:
            self.metrics.clear()
            self.start_time = time.time()
    
    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to a JSON file.
        
        Args:
            filepath: Path to save the metrics
        """
        import json
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "models": self.get_all_metrics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2) 