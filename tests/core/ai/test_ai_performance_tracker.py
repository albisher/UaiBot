"""
Tests for the AI Performance Tracker module.
"""
import pytest
import time
import json
from uaibot.datetime import datetime
from uaibot.core.ai_performance_tracker import AIPerformanceTracker, ModelMetrics

@pytest.fixture
def tracker():
    """Create a fresh performance tracker for each test."""
    return AIPerformanceTracker()

def test_track_successful_request(tracker):
    """Test tracking a successful request."""
    start_time = time.time()
    tracker.track_request(
        model_name="test-model",
        start_time=start_time,
        success=True,
        token_count=100
    )
    
    metrics = tracker.get_model_metrics("test-model")
    assert metrics["total_requests"] == 1
    assert metrics["successful_requests"] == 1
    assert metrics["failed_requests"] == 0
    assert metrics["total_tokens"] == 100
    assert metrics["success_rate"] == 100.0
    assert metrics["error_distribution"] == {}

def test_track_failed_request(tracker):
    """Test tracking a failed request."""
    start_time = time.time()
    tracker.track_request(
        model_name="test-model",
        start_time=start_time,
        success=False,
        error_type="ValueError"
    )
    
    metrics = tracker.get_model_metrics("test-model")
    assert metrics["total_requests"] == 1
    assert metrics["successful_requests"] == 0
    assert metrics["failed_requests"] == 1
    assert metrics["success_rate"] == 0.0
    assert metrics["error_distribution"] == {"ValueError": 1}

def test_multiple_models(tracker):
    """Test tracking requests for multiple models."""
    start_time = time.time()
    
    # Track requests for two different models
    tracker.track_request("model1", start_time, True, token_count=100)
    tracker.track_request("model2", start_time, False, error_type="TypeError")
    
    all_metrics = tracker.get_all_metrics()
    assert len(all_metrics) == 2
    assert all_metrics["model1"]["success_rate"] == 100.0
    assert all_metrics["model2"]["success_rate"] == 0.0

def test_reset_metrics(tracker):
    """Test resetting metrics."""
    start_time = time.time()
    tracker.track_request("test-model", start_time, True)
    
    # Reset specific model
    tracker.reset_metrics("test-model")
    metrics = tracker.get_model_metrics("test-model")
    assert metrics["total_requests"] == 0
    
    # Reset all models
    tracker.track_request("model1", start_time, True)
    tracker.track_request("model2", start_time, True)
    tracker.reset_metrics()
    assert len(tracker.get_all_metrics()) == 0

def test_export_metrics(tracker, tmp_path):
    """Test exporting metrics to a file."""
    start_time = time.time()
    tracker.track_request("test-model", start_time, True, token_count=100)
    
    # Export metrics to a temporary file
    export_path = tmp_path / "metrics.json"
    tracker.export_metrics(str(export_path))
    
    # Verify the exported file
    with open(export_path) as f:
        data = json.load(f)
        assert "timestamp" in data
        assert "uptime" in data
        assert "models" in data
        assert "test-model" in data["models"]
        assert data["models"]["test-model"]["total_requests"] == 1

def test_average_response_time(tracker):
    """Test calculating average response time."""
    start_time = time.time()
    time.sleep(0.1)  # Simulate some processing time
    tracker.track_request("test-model", start_time, True)
    
    metrics = tracker.get_model_metrics("test-model")
    assert metrics["average_response_time"] > 0.1  # Should be at least 0.1 seconds

def test_error_distribution(tracker):
    """Test tracking different types of errors."""
    start_time = time.time()
    tracker.track_request("test-model", start_time, False, error_type="ValueError")
    tracker.track_request("test-model", start_time, False, error_type="TypeError")
    tracker.track_request("test-model", start_time, False, error_type="ValueError")
    
    metrics = tracker.get_model_metrics("test-model")
    assert metrics["error_distribution"]["ValueError"] == 2
    assert metrics["error_distribution"]["TypeError"] == 1 