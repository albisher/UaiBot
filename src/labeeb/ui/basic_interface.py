import gettext
import os
from pathlib import Path

# Initialize translations
LOCALE_DIR = Path(__file__).parent.parent.parent / 'locales'
gettext.bindtextdomain('labeeb', str(LOCALE_DIR))
gettext.textdomain('labeeb')
_ = gettext.gettext

class BasicInterface:
    """Basic interface class with i18n support."""
    
    def __init__(self):
        self.current_language = 'en'
        self._load_translations()
    
    def _load_translations(self):
        """Load translations for the current language."""
        try:
            lang = gettext.translation('labeeb', 
                                     localedir=str(LOCALE_DIR),
                                     languages=[self.current_language])
            lang.install()
            self._ = lang.gettext
        except FileNotFoundError:
            # Fallback to default language if translation not found
            self._ = gettext.gettext
    
    def set_language(self, language_code):
        """Set the interface language.
        
        Args:
            language_code (str): Language code (e.g., 'en', 'ar', 'fr')
        """
        self.current_language = language_code
        self._load_translations()
    
    def get_text(self, text_id):
        """Get translated text.
        
        Args:
            text_id (str): Text identifier to translate
            
        Returns:
            str: Translated text
        """
        return self._(text_id)
    
    def format_text(self, text_id, *args, **kwargs):
        """Get translated text with formatting.
        
        Args:
            text_id (str): Text identifier to translate
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting
            
        Returns:
            str: Formatted and translated text
        """
        return self._(text_id).format(*args, **kwargs)
