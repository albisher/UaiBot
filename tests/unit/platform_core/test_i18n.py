"""
Tests for internationalization support.
"""
import pytest
import os
import json
from pathlib import Path
from src.app.platform_core.i18n import (
    gettext,
    get_supported_languages,
    get_current_language,
    is_rtl,
    get_arabic_variants,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    RTL_LANGUAGES,
    ARABIC_VARIANTS
)

@pytest.fixture
def mock_translations(tmp_path):
    """Create mock translation files for testing."""
    translations_dir = tmp_path / "translations"
    translations_dir.mkdir()
    
    # Create English translations
    en_translations = {
        "test_key": "Test Value",
        "nested.key": "Nested Value",
        "platform_info": "Platform Information"
    }
    with open(translations_dir / "en.json", "w", encoding="utf-8") as f:
        json.dump(en_translations, f)
    
    # Create Arabic translations
    ar_translations = {
        "test_key": "قيمة الاختبار",
        "nested.key": "قيمة متداخلة",
        "platform_info": "معلومات النظام"
    }
    with open(translations_dir / "ar.json", "w", encoding="utf-8") as f:
        json.dump(ar_translations, f)
    
    # Create Saudi Arabic translations
    ar_sa_translations = {
        "test_key": "قيمة الاختبار",
        "nested.key": "قيمة متداخلة",
        "platform_info": "معلومات النظام"
    }
    with open(translations_dir / "ar-SA.json", "w", encoding="utf-8") as f:
        json.dump(ar_sa_translations, f)
    
    return translations_dir

def test_gettext_default_language():
    """Test gettext with default language."""
    # Test with existing key
    assert gettext("platform_info") == "Platform Information"
    
    # Test with non-existing key
    assert gettext("non_existing_key") == "non_existing_key"

def test_gettext_specific_language():
    """Test gettext with specific language."""
    # Test with Arabic
    assert gettext("platform_info", "ar") == "معلومات النظام"
    
    # Test with Saudi Arabic
    assert gettext("platform_info", "ar-SA") == "معلومات النظام"
    
    # Test with non-existing language (should fallback to English)
    assert gettext("platform_info", "fr") == "Platform Information"

def test_gettext_with_mock_translations(mock_translations, monkeypatch):
    """Test gettext with mock translation files."""
    # Mock the translations directory
    monkeypatch.setattr("src.app.platform_core.i18n.Path", lambda x: mock_translations / x)
    
    # Test English translations
    assert gettext("test_key", "en") == "Test Value"
    assert gettext("nested.key", "en") == "Nested Value"
    
    # Test Arabic translations
    assert gettext("test_key", "ar") == "قيمة الاختبار"
    assert gettext("nested.key", "ar") == "قيمة متداخلة"
    
    # Test Saudi Arabic translations
    assert gettext("test_key", "ar-SA") == "قيمة الاختبار"
    assert gettext("nested.key", "ar-SA") == "قيمة متداخلة"
    
    # Test fallback to base language for non-existing key
    assert gettext("non_existing_key", "ar-SA") == "non_existing_key"

def test_get_supported_languages():
    """Test getting supported languages."""
    languages = get_supported_languages()
    
    # Check that all expected languages are present
    assert "en" in languages
    assert "ar" in languages
    assert "ar-SA" in languages
    assert "ar-EG" in languages
    assert "ar-MA" in languages
    assert "ar-KW" in languages
    
    # Check language names
    assert languages["en"] == "English"
    assert languages["ar"] == "العربية"
    assert languages["ar-SA"] == "العربية (السعودية)"

def test_get_current_language():
    """Test getting current system language."""
    # Test with LANG environment variable
    os.environ["LANG"] = "ar_SA.UTF-8"
    assert get_current_language() == "ar-SA"
    
    # Test with unsupported language (should return default)
    os.environ["LANG"] = "xx_XX.UTF-8"
    assert get_current_language() == DEFAULT_LANGUAGE
    
    # Test with no LANG environment variable (should return default)
    del os.environ["LANG"]
    assert get_current_language() == DEFAULT_LANGUAGE

def test_is_rtl():
    """Test RTL language detection."""
    # Test RTL languages
    assert is_rtl("ar") == True
    assert is_rtl("ar-SA") == True
    assert is_rtl("he") == True
    assert is_rtl("fa") == True
    assert is_rtl("ur") == True
    
    # Test non-RTL languages
    assert is_rtl("en") == False
    assert is_rtl("es") == False
    assert is_rtl("fr") == False
    
    # Test with system language
    os.environ["LANG"] = "ar_SA.UTF-8"
    assert is_rtl() == True
    
    os.environ["LANG"] = "en_US.UTF-8"
    assert is_rtl() == False

def test_get_arabic_variants():
    """Test getting Arabic language variants."""
    variants = get_arabic_variants()
    
    # Check that all expected variants are present
    assert "ar" in variants
    assert "ar-SA" in variants
    assert "ar-EG" in variants
    assert "ar-MA" in variants
    assert "ar-KW" in variants
    
    # Check variant names
    assert variants["ar"] == "Modern Standard Arabic"
    assert variants["ar-SA"] == "Saudi Arabic"
    assert variants["ar-EG"] == "Egyptian Arabic"
    assert variants["ar-MA"] == "Moroccan Arabic"
    assert variants["ar-KW"] == "Kuwaiti Arabic" 