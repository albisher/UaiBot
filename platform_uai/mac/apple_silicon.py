"""
Apple Silicon Optimizations

This module contains optimizations specific to Apple Silicon M-series chips.
It attempts to leverage the specialized hardware on Apple Silicon for
improved performance in ML and other computationally intensive tasks.
"""

import platform
import os
import subprocess
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class AppleSiliconOptimizer:
    """Provides optimizations for Apple Silicon M-series processors"""
    
    def __init__(self):
        self.is_apple_silicon = False
        self.chip_details = {}
        self.neural_engine_available = False
        
        # Detect if running on Apple Silicon
        self._detect_apple_silicon()
        
    def _detect_apple_silicon(self) -> None:
        """Detect whether the system is using Apple Silicon and gather chip details"""
        # First check basic platform info
        system = platform.system()
        machine = platform.machine()
        
        if system != 'Darwin' or machine != 'arm64':
            logger.info("Not running on Apple Silicon")
            return
        
        try:
            # Run sysctl to get detailed chip information
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            chip_name = result.stdout.strip()
            
            # Check if this is an M-series chip
            if 'Apple M' in chip_name:
                self.is_apple_silicon = True
                self.chip_details['name'] = chip_name
                
                # Get more detailed info about the chip
                self._get_detailed_chip_info()
                
                logger.info(f"Detected Apple Silicon: {chip_name}")
                logger.info(f"Chip details: {self.chip_details}")
            else:
                logger.info(f"Running on Mac with non-M series ARM: {chip_name}")
        
        except Exception as e:
            logger.warning(f"Error detecting Apple Silicon details: {e}")
    
    def _get_detailed_chip_info(self) -> None:
        """Get detailed information about the Apple Silicon chip"""
        try:
            # Get CPU core count
            result = subprocess.run(
                ['sysctl', '-n', 'hw.ncpu'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            self.chip_details['cpu_cores'] = int(result.stdout.strip())
            
            # Try to determine GPU core count and neural engine presence
            # This is approximate based on chip model
            chip_name = self.chip_details.get('name', '')
            
            if 'M1' in chip_name:
                if 'Pro' in chip_name:
                    self.chip_details['gpu_cores'] = 16
                    self.neural_engine_available = True
                elif 'Max' in chip_name:
                    self.chip_details['gpu_cores'] = 32
                    self.neural_engine_available = True
                elif 'Ultra' in chip_name:
                    self.chip_details['gpu_cores'] = 64
                    self.neural_engine_available = True
                else:
                    # Base M1
                    self.chip_details['gpu_cores'] = 8
                    self.neural_engine_available = True
            elif 'M2' in chip_name:
                if 'Pro' in chip_name:
                    self.chip_details['gpu_cores'] = 19
                    self.neural_engine_available = True
                elif 'Max' in chip_name:
                    self.chip_details['gpu_cores'] = 38
                    self.neural_engine_available = True
                elif 'Ultra' in chip_name:
                    self.chip_details['gpu_cores'] = 76
                    self.neural_engine_available = True
                else:
                    # Base M2
                    self.chip_details['gpu_cores'] = 10
                    self.neural_engine_available = True
            elif 'M3' in chip_name:
                if 'Pro' in chip_name:
                    self.chip_details['gpu_cores'] = 19
                    self.neural_engine_available = True
                elif 'Max' in chip_name:
                    self.chip_details['gpu_cores'] = 40
                    self.neural_engine_available = True
                elif 'Ultra' in chip_name:
                    self.chip_details['gpu_cores'] = 80
                    self.neural_engine_available = True
                else:
                    # Base M3
                    self.chip_details['gpu_cores'] = 10
                    self.neural_engine_available = True
            else:
                # Unknown M series
                self.chip_details['gpu_cores'] = 'unknown'
                self.neural_engine_available = True
            
        except Exception as e:
            logger.warning(f"Error getting detailed chip info: {e}")
    
    def get_optimized_ml_config(self) -> Dict[str, Any]:
        """
        Return optimized configuration for machine learning operations.
        
        Returns:
            Dictionary of optimized settings
        """
        config = {
            'use_metal': False,
            'use_neural_engine': False,
            'optimized_threading': True,
            'thread_count': os.cpu_count() or 4,
            'memory_limit': None  # in MB
        }
        
        if not self.is_apple_silicon:
            return config
            
        # Enable Metal performance shaders for ML
        config['use_metal'] = True
        
        # Set Neural Engine usage if available
        if self.neural_engine_available:
            config['use_neural_engine'] = True
        
        # Optimize thread count based on available cores
        cpu_cores = self.chip_details.get('cpu_cores', os.cpu_count() or 4)
        # Use half the cores by default to avoid thermal throttling
        config['thread_count'] = max(1, cpu_cores // 2)
        
        # Set a reasonable memory limit based on system RAM
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            total_memory = int(result.stdout.strip()) / (1024 * 1024)  # Convert to MB
            # Use up to 25% of system RAM
            config['memory_limit'] = int(total_memory * 0.25)
        except Exception:
            # Default to 2GB if we can't determine system memory
            config['memory_limit'] = 2048
            
        return config
        
    def get_optimized_tensor_config(self) -> Dict[str, Any]:
        """
        Return optimized configuration for tensor operations.
        Particularly useful for AI-driven processing.
        
        Returns:
            Dictionary of optimized tensor settings
        """
        config = {
            'backend': 'default',
            'precision': 'float32',
            'use_gpu': False,
            'use_metal': False
        }
        
        if not self.is_apple_silicon:
            return config
            
        # On Apple Silicon, we can use Metal for tensor operations
        config['backend'] = 'metal'
        config['use_metal'] = True
        config['use_gpu'] = True
        
        # Use mixed precision for better performance on newer chips
        if 'M2' in self.chip_details.get('name', '') or 'M3' in self.chip_details.get('name', ''):
            config['precision'] = 'mixed_float16'
        
        return config
    
    def optimize_process_priority(self) -> None:
        """
        Optimize the process priority for better performance.
        This is particularly useful for long-running AI operations.
        """
        if not self.is_apple_silicon:
            return
            
        try:
            # Set process to high priority
            os.nice(-10)
            logger.info("Process priority optimized for Apple Silicon")
        except Exception as e:
            logger.warning(f"Failed to optimize process priority: {e}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get the current optimization status.
        
        Returns:
            Dictionary containing optimization status information
        """
        status = {
            'platform': 'Apple Silicon' if self.is_apple_silicon else platform.processor(),
            'optimizations_available': self.is_apple_silicon,
            'chip_details': self.chip_details,
            'neural_engine_available': self.neural_engine_available
        }
        
        if self.is_apple_silicon:
            status['ml_config'] = self.get_optimized_ml_config()
            status['tensor_config'] = self.get_optimized_tensor_config()
            
        return status

# Create a global instance for convenience
apple_silicon_optimizer = AppleSiliconOptimizer()
