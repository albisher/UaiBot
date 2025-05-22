#!/usr/bin/env python3
"""
Tests for the AI response caching mechanism.
Validates that the cache correctly stores and retrieves responses.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import time

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.command_processor.ai_response_cache import AIResponseCache
from app.command_processor.ai_driven_processor import AIDrivenProcessor


class TestAIResponseCache(unittest.TestCase):
    """Test the AI response caching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = AIResponseCache(max_size=5, ttl=1)  # Short TTL for testing
    
    def test_cache_put_get(self):
        """Test basic cache put and get operations."""
        # Put an item in the cache
        query = "list files in directory"
        response = {"command": "ls -la", "explanation": "Lists all files"}
        
        self.cache.put(query, response)
        
        # Get the item from cache
        cached_response = self.cache.get(query)
        
        self.assertEqual(cached_response, response)
    
    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        # Put an item in the cache
        query = "list files in directory"
        response = {"command": "ls -la", "explanation": "Lists all files"}
        
        self.cache.put(query, response)
        
        # Wait for the cache entry to expire
        time.sleep(1.1)
        
        # Try to get the expired item
        cached_response = self.cache.get(query)
        
        self.assertIsNone(cached_response)
    
    def test_cache_eviction(self):
        """Test LRU eviction policy."""
        # Fill the cache to max_size
        for i in range(5):
            query = f"test query {i}"
            response = {"command": f"command {i}"}
            self.cache.put(query, response)
        
        # Add one more item to trigger eviction
        new_query = "new query"
        new_response = {"command": "new command"}
        self.cache.put(new_query, new_response)
        
        # Check that the least recently used item is evicted
        evicted_query = "test query 0"
        self.assertIsNone(self.cache.get(evicted_query))
        
        # Check that the new item is in the cache
        self.assertEqual(self.cache.get(new_query), new_response)
    
    def test_query_normalization(self):
        """Test that similar queries map to the same cache entry."""
        # Put an item in the cache
        query1 = "list files in directory"
        response = {"command": "ls -la", "explanation": "Lists all files"}
        
        self.cache.put(query1, response)
        
        # Try slightly different query
        query2 = "  list files in directory  "  # Extra whitespace
        cached_response = self.cache.get(query2)
        
        self.assertEqual(cached_response, response)


class TestAIDrivenProcessorWithCache(unittest.TestCase):
    """Test the AI-driven processor with caching enabled."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = AIDrivenProcessor(use_cache=True, cache_ttl=1)
        self.mock_ai_handler = MagicMock()
    
    @patch('command_processor.ai_driven_processor.AIResponseCache')
    def test_cache_integration(self, mock_cache_class):
        """Test that the processor uses the cache correctly."""
        # Create a mock cache instance
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache
        
        # Create a processor with the mocked cache
        processor = AIDrivenProcessor(use_cache=True)
        
        # Test that the cache is queried during request processing
        mock_cache.get.return_value = None  # Simulate cache miss
        
        # Mock the AI response for test
        mock_ai_response = """```json
        {
          "command": "ls -la",
          "explanation": "Lists all files in current directory with details"
        }
        ```"""
        self.mock_ai_handler.get_ai_response.return_value = mock_ai_response
        
        # Process a request
        processor.process_request(self.mock_ai_handler, "list files")
        
        # Verify cache was checked
        mock_cache.get.assert_called_once()
        
        # Verify response was stored in cache
        mock_cache.put.assert_called_once()
    
    def test_cache_hit(self):
        """Test that cached responses are returned without calling the AI."""
        # Mock AI handler
        mock_ai_handler = MagicMock()
        
        # Create a test request and response
        test_request = "show system info"
        test_platform = {"system": "Linux"}
        cached_result = {
            'success': True,
            'command': 'uname -a',
            'metadata': {'explanation': 'Shows system information'}
        }
        
        # Insert into cache manually
        cache_key = f"{test_request}_{test_platform.get('system', '')}"
        self.processor.response_cache.put(cache_key, cached_result)
        
        # Process the same request
        success, command, metadata = self.processor.process_request(
            mock_ai_handler, test_request, test_platform
        )
        
        # Verify AI was not called
        mock_ai_handler.get_ai_response.assert_not_called()
        
        # Verify cached result was returned
        self.assertTrue(success)
        self.assertEqual(command, 'uname -a')
        self.assertEqual(metadata, {'explanation': 'Shows system information'})
    
    def test_cache_miss_then_hit(self):
        """Test the full cache cycle - miss, store, then hit."""
        # Mock AI handler with a canned response
        mock_ai_handler = MagicMock()
        mock_ai_handler.get_ai_response.return_value = """```json
        {
          "command": "df -h",
          "explanation": "Shows disk usage in human-readable format"
        }
        ```"""
        
        # First request (cache miss)
        test_request = "show disk space"
        success1, command1, metadata1 = self.processor.process_request(mock_ai_handler, test_request)
        
        # Verify AI was called
        mock_ai_handler.get_ai_response.assert_called_once()
        
        # Reset mock and call again
        mock_ai_handler.get_ai_response.reset_mock()
        
        # Second request (should hit cache)
        success2, command2, metadata2 = self.processor.process_request(mock_ai_handler, test_request)
        
        # Verify AI was not called again
        mock_ai_handler.get_ai_response.assert_not_called()
        
        # Verify results match
        self.assertEqual(command1, command2)
        self.assertEqual(success1, success2)
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Set up processor with mock cache
        processor = AIDrivenProcessor(use_cache=True)
        processor.response_cache = MagicMock()
        
        # Call clear_cache method
        processor.clear_cache()
        
        # Verify cache's clear method was called
        processor.response_cache.clear.assert_called_once()


if __name__ == '__main__':
    unittest.main()
