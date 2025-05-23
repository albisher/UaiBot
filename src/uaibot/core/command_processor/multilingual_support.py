"""Multilingual support module for handling multiple languages in commands."""

from typing import Dict, Optional, List, Union
import re
from dataclasses import dataclass
from langdetect import detect, LangDetectException
from googletrans import Translator

@dataclass
class LanguageResult:
    """Result of language detection."""
    language: str
    confidence: float
    is_reliable: bool

class MultilingualSupport:
    """Handles multilingual support for command processing."""
    
    def __init__(self):
        """Initialize the multilingual support handler."""
        self.translator = Translator()
        self.supported_languages = ['en', 'ar', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ru']
        self.language_patterns = {
            'ar': r'[\u0600-\u06FF]',  # Arabic
            'zh': r'[\u4e00-\u9fff]',  # Chinese
            'ja': r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]',  # Japanese
            'ko': r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\ud7b0-\ud7ff]',  # Korean
            'ru': r'[\u0400-\u04FF]',  # Russian
        }
    
    def detect_language(self, text: str) -> LanguageResult:
        """Detect the language of the given text.
        
        Args:
            text: The text to detect language for.
            
        Returns:
            LanguageResult containing detected language and confidence.
        """
        try:
            # First try pattern matching for specific scripts
            for lang, pattern in self.language_patterns.items():
                if re.search(pattern, text):
                    return LanguageResult(language=lang, confidence=0.9, is_reliable=True)
            
            # Fall back to langdetect
            detected = detect(text)
            return LanguageResult(
                language=detected,
                confidence=0.8,
                is_reliable=True
            )
        except LangDetectException:
            return LanguageResult(
                language='en',  # Default to English
                confidence=0.0,
                is_reliable=False
            )
    
    def translate_text(self, text: str, target_lang: str = 'en') -> Dict[str, Union[str, bool]]:
        """Translate text to target language.
        
        Args:
            text: Text to translate.
            target_lang: Target language code.
            
        Returns:
            Dictionary containing translation result.
        """
        if target_lang not in self.supported_languages:
            return {
                'status': 'error',
                'message': 'Invalid language specified'
            }
        
        try:
            result = self.translator.translate(text, dest=target_lang)
            return {
                'status': 'success',
                'original_text': text,
                'translated_text': result.text,
                'source_language': result.src,
                'target_language': result.dest
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def extract_command_multilingual(self, text: str) -> Dict[str, Union[str, bool]]:
        """Extract command from multilingual text.
        
        Args:
            text: Text containing potential command.
            
        Returns:
            Dictionary containing extracted command and metadata.
        """
        # Detect language
        lang_result = self.detect_language(text)
        
        # If not English, translate to English first
        if lang_result.language != 'en':
            translation = self.translate_text(text, 'en')
            if translation['status'] == 'error':
                return {
                    'status': 'error',
                    'message': f'Translation failed: {translation["message"]}'
                }
            text = translation['translated_text']
        
        # Extract command (basic implementation)
        # This is a placeholder - actual command extraction would be more sophisticated
        command_match = re.search(r'(?:run|execute|perform)\s+([a-zA-Z0-9\s\-_]+)', text.lower())
        if command_match:
            return {
                'status': 'success',
                'command': command_match.group(1).strip(),
                'original_language': lang_result.language,
                'confidence': lang_result.confidence
            }
        
        return {
            'status': 'error',
            'message': 'No command found in text'
        }
    
    def handle_multilingual_input(self, text: str) -> Dict[str, Union[str, bool]]:
        """Handle multilingual input and return appropriate response.
        
        Args:
            text: Input text in any supported language.
            
        Returns:
            Dictionary containing processed result.
        """
        # Detect language
        lang_result = self.detect_language(text)
        
        # If language is not supported
        if lang_result.language not in self.supported_languages:
            return {
                'status': 'error',
                'message': 'Unsupported language'
            }
        
        # Extract command
        command_result = self.extract_command_multilingual(text)
        
        # If command extraction failed
        if command_result['status'] == 'error':
            return {
                'status': 'error',
                'message': command_result['message'],
                'language': lang_result.language
            }
        
        return {
            'status': 'success',
            'command': command_result['command'],
            'language': lang_result.language,
            'confidence': lang_result.confidence
        } 