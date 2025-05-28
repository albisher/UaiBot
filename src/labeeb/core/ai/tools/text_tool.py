"""
Text Tool Implementation

This module provides the TextTool for text processing operations,
implementing A2A (Agent-to-Agent), MCP (Model Context Protocol), and SmolAgents patterns.
"""

import logging
import asyncio
import time
import re
import unicodedata
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class TextTool(BaseTool):
    """Tool for text processing operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the TextTool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="TextTool",
            description="Handles text processing operations including formatting, parsing, and analysis",
            config=config
        )
        self._max_text_length = config.get('max_text_length', 1000000)  # 1M characters
        self._allowed_languages = config.get('allowed_languages', ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'])
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Text cache
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
            logger.error(f"Failed to initialize TextTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up TextTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'clean': True,
            'normalize': True,
            'tokenize': True,
            'detect_language': True,
            'translate': True,
            'summarize': True,
            'extract_keywords': True,
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
            'max_text_length': self._max_text_length,
            'allowed_languages': self._allowed_languages,
            'cache_duration': self._cache_duration,
            'cache_size': len(self._cache),
            'history_size': len(self._operation_history),
            'max_history': self._max_history
        }
        return {**base_status, **tool_status}
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a text processing operation.
        
        Args:
            action (str): The action to execute
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the operation
        """
        try:
            if not self.validate_input(action, **kwargs):
                return self.handle_error(ValueError("Invalid input"))
            
            if action == "format_text":
                return self._format_text(**kwargs)
            elif action == "parse_json":
                return self._parse_json(**kwargs)
            elif action == "extract_pattern":
                return self._extract_pattern(**kwargs)
            elif action == "analyze_text":
                return self._analyze_text(**kwargs)
            else:
                return self.handle_error(ValueError(f"Unknown action: {action}"))
                
        except Exception as e:
            return self.handle_error(e)
    
    def get_available_actions(self) -> Dict[str, str]:
        """
        Get available text processing operations.
        
        Returns:
            Dict[str, str]: Available operations and their descriptions
        """
        return {
            "format_text": "Format text according to specified rules",
            "parse_json": "Parse JSON text into a Python object",
            "extract_pattern": "Extract text matching a pattern",
            "analyze_text": "Analyze text for various metrics"
        }
    
    def _format_text(self, text: str, case: str = "lower", strip: bool = True, 
                    replace: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """Format text according to specified rules."""
        try:
            result = text
            
            # Apply case transformation
            if case == "lower":
                result = result.lower()
            elif case == "upper":
                result = result.upper()
            elif case == "title":
                result = result.title()
            elif case == "capitalize":
                result = result.capitalize()
            
            # Strip whitespace
            if strip:
                result = result.strip()
            
            # Apply replacements
            if replace:
                for old, new in replace.items():
                    result = result.replace(old, new)
            
            return {
                "original": text,
                "formatted": result,
                "length": len(result)
            }
        except Exception as e:
            return self.handle_error(e)
    
    def _parse_json(self, text: str, **kwargs) -> Dict[str, Any]:
        """Parse JSON text into a Python object."""
        try:
            data = json.loads(text)
            return {
                "data": data,
                "type": type(data).__name__
            }
        except json.JSONDecodeError as e:
            return self.handle_error(e)
    
    def _extract_pattern(self, text: str, pattern: str, flags: int = 0, **kwargs) -> Dict[str, Any]:
        """Extract text matching a pattern."""
        try:
            matches = re.finditer(pattern, text, flags)
            results = []
            for match in matches:
                results.append({
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "groups": match.groups()
                })
            
            return {
                "matches": results,
                "count": len(results)
            }
        except re.error as e:
            return self.handle_error(e)
    
    def _analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Analyze text for various metrics."""
        try:
            # Basic metrics
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            paragraphs = text.split('\n\n')
            
            # Character analysis
            char_count = len(text)
            word_count = len(words)
            sentence_count = len([s for s in sentences if s.strip()])
            paragraph_count = len([p for p in paragraphs if p.strip()])
            
            # Word length analysis
            word_lengths = [len(word) for word in words]
            avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
            
            # Character frequency
            char_freq = {}
            for char in text:
                char_freq[char] = char_freq.get(char, 0) + 1
            
            return {
                "metrics": {
                    "characters": char_count,
                    "words": word_count,
                    "sentences": sentence_count,
                    "paragraphs": paragraph_count,
                    "avg_word_length": avg_word_length
                },
                "character_frequency": char_freq
            }
        except Exception as e:
            return self.handle_error(e)
    
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
    
    def _get_cache_key(self, text: str, operation: str, **kwargs) -> str:
        """Generate a cache key for text data.
        
        Args:
            text: Text data
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [hashlib.md5(text.encode()).hexdigest(), operation]
        for key, value in sorted(kwargs.items()):
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
    
    def _validate_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate text data.
        
        Args:
            text: Text data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if len(text) > self._max_text_length:
            return False, f'Text exceeds maximum length ({self._max_text_length} characters)'
        
        if not text.strip():
            return False, 'Text is empty or contains only whitespace'
        
        return True, None
    
    async def _process_text(self, text: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Process text data with the given operation.
        
        Args:
            text: Text data to process
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Validate text
            is_valid, error = self._validate_text(text)
            if not is_valid:
                return {'error': error}
            
            # Check cache
            cache_key = self._get_cache_key(text, operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process text
            if operation == 'clean':
                # Remove extra whitespace
                cleaned_text = re.sub(r'\s+', ' ', text.strip())
                # Remove special characters
                cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
                processed_data = cleaned_text
            
            elif operation == 'normalize':
                # Normalize unicode characters
                normalized_text = unicodedata.normalize('NFKC', text)
                # Convert to lowercase
                normalized_text = normalized_text.lower()
                processed_data = normalized_text
            
            elif operation == 'tokenize':
                # Split into words
                tokens = text.split()
                # Remove punctuation
                tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
                # Remove empty tokens
                tokens = [token for token in tokens if token]
                processed_data = tokens
            
            elif operation == 'detect_language':
                # Simple language detection based on character frequency
                # This is a basic implementation - in production, use a proper language detection library
                char_freq = {}
                for char in text.lower():
                    if char.isalpha():
                        char_freq[char] = char_freq.get(char, 0) + 1
                
                # Calculate language scores based on character frequency
                language_scores = {}
                for lang in self._allowed_languages:
                    score = 0
                    # Add language-specific scoring logic here
                    language_scores[lang] = score
                
                # Get the language with the highest score
                detected_language = max(language_scores.items(), key=lambda x: x[1])[0]
                processed_data = detected_language
            
            elif operation == 'translate':
                target_language = kwargs.get('target_language')
                if target_language not in self._allowed_languages:
                    return {'error': f'Unsupported target language: {target_language}'}
                
                # Simple translation using a dictionary
                # This is a basic implementation - in production, use a proper translation API
                translations = {
                    'en': {'hello': 'hello', 'world': 'world'},
                    'es': {'hello': 'hola', 'world': 'mundo'},
                    'fr': {'hello': 'bonjour', 'world': 'monde'},
                    # Add more translations as needed
                }
                
                words = text.lower().split()
                translated_words = []
                for word in words:
                    if word in translations.get(target_language, {}):
                        translated_words.append(translations[target_language][word])
                    else:
                        translated_words.append(word)
                
                processed_data = ' '.join(translated_words)
            
            elif operation == 'summarize':
                # Simple summarization by taking the first sentence
                # This is a basic implementation - in production, use a proper summarization algorithm
                sentences = re.split(r'[.!?]+', text)
                summary = sentences[0].strip() if sentences else ''
                processed_data = summary
            
            elif operation == 'extract_keywords':
                # Simple keyword extraction based on word frequency
                # This is a basic implementation - in production, use a proper keyword extraction algorithm
                words = text.lower().split()
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get the most frequent words
                keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                processed_data = [word for word, _ in keywords]
            
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
            logger.error(f"Error processing text: {e}")
            return {'error': str(e)}
    
    async def _clean_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Clean text.
        
        Args:
            args: Clean arguments
            
        Returns:
            Dict[str, Any]: Clean result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'clean'
            )
            
            if 'error' not in result:
                self._add_to_history('clean', {
                    'length': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return {'error': str(e)}
    
    async def _normalize_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Normalize text.
        
        Args:
            args: Normalize arguments
            
        Returns:
            Dict[str, Any]: Normalize result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'normalize'
            )
            
            if 'error' not in result:
                self._add_to_history('normalize', {
                    'length': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error normalizing text: {e}")
            return {'error': str(e)}
    
    async def _tokenize_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Tokenize text.
        
        Args:
            args: Tokenize arguments
            
        Returns:
            Dict[str, Any]: Tokenize result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'tokenize'
            )
            
            if 'error' not in result:
                self._add_to_history('tokenize', {
                    'token_count': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error tokenizing text: {e}")
            return {'error': str(e)}
    
    async def _detect_language(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect language of text.
        
        Args:
            args: Detect language arguments
            
        Returns:
            Dict[str, Any]: Detect language result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'detect_language'
            )
            
            if 'error' not in result:
                self._add_to_history('detect_language', {
                    'language': result['result']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return {'error': str(e)}
    
    async def _translate_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Translate text.
        
        Args:
            args: Translate arguments
            
        Returns:
            Dict[str, Any]: Translate result
        """
        try:
            if not args or 'text' not in args or 'target_language' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_text(
                args['text'],
                'translate',
                target_language=args['target_language']
            )
            
            if 'error' not in result:
                self._add_to_history('translate', {
                    'target_language': args['target_language'],
                    'length': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {'error': str(e)}
    
    async def _summarize_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Summarize text.
        
        Args:
            args: Summarize arguments
            
        Returns:
            Dict[str, Any]: Summarize result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'summarize'
            )
            
            if 'error' not in result:
                self._add_to_history('summarize', {
                    'length': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return {'error': str(e)}
    
    async def _extract_keywords(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract keywords from text.
        
        Args:
            args: Extract keywords arguments
            
        Returns:
            Dict[str, Any]: Extract keywords result
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text data'}
            
            result = await self._process_text(
                args['text'],
                'extract_keywords'
            )
            
            if 'error' not in result:
                self._add_to_history('extract_keywords', {
                    'keyword_count': len(result['result'])
                })
            
            return result
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
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