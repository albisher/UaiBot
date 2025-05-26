"""Internationalization (i18n) support for the Labeeb platform.

This module provides functionality for:
- Loading and managing translations
- String translation
- Language switching
- Plural forms handling
- Locale management
"""

import os
import gettext
from typing import Optional, Dict, Any
from pathlib import Path

class I18nManager:
    """Manages internationalization for the Labeeb platform.
    
    This class handles:
    - Translation loading and caching
    - Language switching
    - String translation
    - Plural forms
    """

    def __init__(self, domain: str = "labeeb", locale_dir: str = "locales"):
        """Initialize the i18n manager.
        
        Args:
            domain: The translation domain name
            locale_dir: Directory containing translation files
        """
        self.domain = domain
        self.locale_dir = Path(locale_dir)
        self.translations: Dict[str, gettext.GNUTranslations] = {}
        self.current_language = "en"
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all available translations."""
        if not self.locale_dir.exists():
            return

        for lang_dir in self.locale_dir.iterdir():
            if not lang_dir.is_dir():
                continue

            try:
                translation = gettext.translation(
                    self.domain,
                    localedir=str(self.locale_dir),
                    languages=[lang_dir.name]
                )
                self.translations[lang_dir.name] = translation
            except Exception as e:
                print(f"Failed to load translation for {lang_dir.name}: {e}")

    def set_language(self, language: str) -> bool:
        """Set the current language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            bool: True if language was set successfully
        """
        if language not in self.translations:
            return False
        
        self.current_language = language
        return True

    def get_language(self) -> str:
        """Get the current language.
        
        Returns:
            str: Current language code
        """
        return self.current_language

    def get_available_languages(self) -> list[str]:
        """Get list of available languages.
        
        Returns:
            list[str]: List of available language codes
        """
        return list(self.translations.keys())

    def translate(self, text: str, **kwargs: Any) -> str:
        """Translate a string.
        
        Args:
            text: Text to translate
            **kwargs: Format arguments for the translation
            
        Returns:
            str: Translated text
        """
        if self.current_language not in self.translations:
            return text

        translation = self.translations[self.current_language].gettext(text)
        return translation.format(**kwargs) if kwargs else translation

    def translate_plural(self, singular: str, plural: str, count: int, **kwargs: Any) -> str:
        """Translate a string with plural forms.
        
        Args:
            singular: Singular form of the text
            plural: Plural form of the text
            count: Number to determine plural form
            **kwargs: Format arguments for the translation
            
        Returns:
            str: Translated text in appropriate plural form
        """
        if self.current_language not in self.translations:
            return singular if count == 1 else plural

        translation = self.translations[self.current_language].ngettext(singular, plural, count)
        return translation.format(**kwargs) if kwargs else translation

# Create global instance
i18n = I18nManager()

def _(text: str, **kwargs: Any) -> str:
    """Shortcut function for translation.
    
    Args:
        text: Text to translate
        **kwargs: Format arguments for the translation
        
    Returns:
        str: Translated text
    """
    return i18n.translate(text, **kwargs)

def ngettext(singular: str, plural: str, count: int, **kwargs: Any) -> str:
    """Shortcut function for plural translation.
    
    Args:
        singular: Singular form of the text
        plural: Plural form of the text
        count: Number to determine plural form
        **kwargs: Format arguments for the translation
        
    Returns:
        str: Translated text in appropriate plural form
    """
    return i18n.translate_plural(singular, plural, count, **kwargs) 