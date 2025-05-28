"""
Internationalization support for platform core.

This module provides internationalization support for platform-specific messages
and system information labels, with special handling for RTL languages.
"""
import os
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Default language
DEFAULT_LANGUAGE = 'ar'  # Changed to Arabic as default

# RTL languages
RTL_LANGUAGES = {'ar', 'ar-SA', 'ar-KW', 'ar-MA', 'ar-EG', 'ar-AE', 'ar-QA', 'ar-BH', 'ar-OM', 'ar-YE', 'ar-SD', 'ar-LY', 'ar-DZ', 'ar-TN'}

# Arabic regional variants
ARABIC_VARIANTS = {
    'ar': 'Modern Standard Arabic',
    'ar-SA': 'Saudi Arabic',
    'ar-EG': 'Egyptian Arabic',
    'ar-MA': 'Moroccan Arabic',
    'ar-KW': 'Kuwaiti Arabic',
    'ar-AE': 'Emirati Arabic',
    'ar-QA': 'Qatari Arabic',
    'ar-BH': 'Bahraini Arabic',
    'ar-OM': 'Omani Arabic',
    'ar-YE': 'Yemeni Arabic',
    'ar-SD': 'Sudanese Arabic',
    'ar-LY': 'Libyan Arabic',
    'ar-DZ': 'Algerian Arabic',
    'ar-TN': 'Tunisian Arabic'
}

# Supported languages with regional variants
SUPPORTED_LANGUAGES = {
    # Primary Languages (Arabic and its variants)
    'ar': 'العربية',
    'ar-SA': 'العربية (السعودية)',
    'ar-EG': 'العربية (مصر)',
    'ar-MA': 'العربية (المغرب)',
    'ar-KW': 'العربية (الكويت)',
    'ar-AE': 'العربية (الإمارات)',
    'ar-QA': 'العربية (قطر)',
    'ar-BH': 'العربية (البحرين)',
    'ar-OM': 'العربية (عمان)',
    'ar-YE': 'العربية (اليمن)',
    'ar-SD': 'العربية (السودان)',
    'ar-LY': 'العربية (ليبيا)',
    'ar-DZ': 'العربية (الجزائر)',
    'ar-TN': 'العربية (تونس)',
    # Secondary Languages
    'en': 'English',
    'fr': 'Français',
    'es': 'Español'
}

# Translation cache
_translations: Dict[str, Dict[str, str]] = {}

# Current language settings
_current_language = DEFAULT_LANGUAGE
_is_rtl = False

def _normalize_language_code(language: str) -> Tuple[str, str]:
    """Normalize language code and get base language.
    
    Args:
        language: Language code (e.g., 'ar-SA', 'en-US')
        
    Returns:
        Tuple[str, str]: (normalized language code, base language code)
    """
    # Split into language and region
    parts = language.split('-')
    base_lang = parts[0].lower()
    
    # Handle Arabic variants
    if base_lang == 'ar' and len(parts) > 1:
        variant = f"{base_lang}-{parts[1].upper()}"
        if variant in ARABIC_VARIANTS:
            return variant, base_lang
    
    return base_lang, base_lang

def _load_translations(language: str) -> Dict[str, str]:
    """Load translations for a specific language.
    
    Args:
        language: Language code (e.g., 'en', 'ar-SA')
        
    Returns:
        Dict[str, str]: Dictionary of translations
    """
    normalized_lang, base_lang = _normalize_language_code(language)
    
    # Check if language is supported
    if normalized_lang not in SUPPORTED_LANGUAGES:
        normalized_lang = DEFAULT_LANGUAGE
        base_lang = DEFAULT_LANGUAGE
    
    # Check cache first
    if normalized_lang in _translations:
        return _translations[normalized_lang]
    
    # Try loading specific variant first
    translations_file = Path(__file__).parent / 'translations' / f'{normalized_lang}.json'
    
    if not translations_file.exists() and normalized_lang != base_lang:
        # Fallback to base language
        translations_file = Path(__file__).parent / 'translations' / f'{base_lang}.json'
    
    if not translations_file.exists():
        # Fallback to default language
        if normalized_lang != DEFAULT_LANGUAGE:
            return _load_translations(DEFAULT_LANGUAGE)
        return {}
    
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations[normalized_lang] = translations
            return translations
    except Exception:
        return {}

def setup_language(language: str) -> None:
    """Set up language settings for the application.
    
    Args:
        language: Language code (e.g., 'en', 'ar-SA')
    """
    global _current_language, _is_rtl
    
    normalized_lang, _ = _normalize_language_code(language)
    
    # Check if language is supported
    if normalized_lang not in SUPPORTED_LANGUAGES:
        normalized_lang = DEFAULT_LANGUAGE
    
    # Update current language and RTL status
    _current_language = normalized_lang
    _is_rtl = normalized_lang in RTL_LANGUAGES
    
    # Load translations
    _load_translations(normalized_lang)
    
    # Set environment variables
    os.environ['LANG'] = normalized_lang
    os.environ['LANGUAGE'] = normalized_lang

def is_rtl(language: Optional[str] = None) -> bool:
    """Check if a language is RTL.
    
    Args:
        language: Language code (e.g., 'en', 'ar-SA'). If None, uses current language.
        
    Returns:
        bool: True if the language is RTL, False otherwise
    """
    if language is None:
        return _is_rtl
    
    normalized_lang, _ = _normalize_language_code(language)
    return normalized_lang in RTL_LANGUAGES

def gettext(key: str, language: Optional[str] = None) -> str:
    """Get translated text for a key.
    
    Args:
        key: Translation key
        language: Language code (e.g., 'en', 'ar-SA'). If None, uses current language.
        
    Returns:
        str: Translated text or key if translation not found
    """
    if language is None:
        language = _current_language
    
    translations = _load_translations(language)
    return translations.get(key, key)

def get_supported_languages() -> Dict[str, str]:
    """Get dictionary of supported languages.
    
    Returns:
        Dict[str, str]: Dictionary mapping language codes to language names
    """
    return SUPPORTED_LANGUAGES.copy()

def get_current_language() -> str:
    """Get current language.
    
    Returns:
        str: Language code (e.g., 'en', 'ar-SA')
    """
    return _current_language

def get_arabic_variants() -> Dict[str, str]:
    """Get dictionary of Arabic language variants.
    
    Returns:
        Dict[str, str]: Dictionary mapping Arabic variant codes to their names
    """
    return ARABIC_VARIANTS.copy() 