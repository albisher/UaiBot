import pytest
from app.core.command_processor.multilingual_support import MultilingualSupport

class TestMultilingualSupport:
    @pytest.fixture
    def multilingual(self):
        return MultilingualSupport()

    def test_detect_language_english(self, multilingual):
        """Test English language detection."""
        text = "Hello, how are you?"
        language = multilingual.detect_language(text)
        assert language == "en"

    def test_detect_language_arabic(self, multilingual):
        """Test Arabic language detection."""
        text = "مرحبا، كيف حالك؟"
        language = multilingual.detect_language(text)
        assert language == "ar"

    def test_translate_text(self, multilingual):
        """Test text translation."""
        text = "Hello, how are you?"
        translated = multilingual.translate_text(text, "ar")
        assert translated is not None
        assert len(translated) > 0

    def test_extract_command_multilingual(self, multilingual):
        """Test command extraction in multiple languages."""
        # English
        text_en = "Run this command: echo 'Hello'"
        command_en = multilingual.extract_command(text_en)
        assert command_en == "echo 'Hello'"

        # Arabic
        text_ar = "قم بتنفيذ هذا الأمر: echo 'Hello'"
        command_ar = multilingual.extract_command(text_ar)
        assert command_ar == "echo 'Hello'"

    def test_handle_multilingual_input(self, multilingual):
        """Test handling of multilingual input."""
        # English input
        input_en = "Create a file named test.txt"
        result_en = multilingual.handle_input(input_en)
        assert result_en["language"] == "en"
        assert "test.txt" in result_en["command"]

        # Arabic input
        input_ar = "إنشاء ملف باسم test.txt"
        result_ar = multilingual.handle_input(input_ar)
        assert result_ar["language"] == "ar"
        assert "test.txt" in result_ar["command"]

    def test_language_preference(self, multilingual):
        """Test language preference handling."""
        # Set language preference
        multilingual.set_language_preference("ar")
        assert multilingual.get_language_preference() == "ar"

        # Test with preference
        text = "Hello"
        result = multilingual.handle_input(text)
        assert result["language"] == "ar"

    def test_command_patterns(self, multilingual):
        """Test command pattern recognition in different languages."""
        patterns = {
            "en": [
                "Run this command: {command}",
                "Execute: {command}",
                "Please run: {command}"
            ],
            "ar": [
                "قم بتنفيذ هذا الأمر: {command}",
                "نفذ: {command}",
                "الرجاء تنفيذ: {command}"
            ]
        }

        for lang, pattern_list in patterns.items():
            for pattern in pattern_list:
                command = "echo 'test'"
                text = pattern.format(command=command)
                result = multilingual.extract_command(text)
                assert result == command

    def test_error_handling(self, multilingual):
        """Test error handling in multilingual support."""
        # Test with invalid language
        with pytest.raises(ValueError):
            multilingual.set_language_preference("invalid")

        # Test with empty text
        result = multilingual.handle_input("")
        assert result["error"] is not None

        # Test with unsupported language
        result = multilingual.handle_input("こんにちは")
        assert result["error"] is not None

    @pytest.mark.parametrize("text,expected_lang", [
        ("Hello world", "en"),
        ("مرحبا بالعالم", "ar"),
        ("", None),
        ("123", None),
    ])
    def test_language_detection_variations(self, multilingual, text, expected_lang):
        """Test language detection with various inputs."""
        language = multilingual.detect_language(text)
        assert language == expected_lang

    def test_translation_quality(self, multilingual):
        """Test translation quality and consistency."""
        # Test bidirectional translation
        original = "Hello, how are you?"
        translated = multilingual.translate_text(original, "ar")
        back_translated = multilingual.translate_text(translated, "en")
        
        # Check if back translation maintains meaning
        assert len(back_translated) > 0
        assert any(word in back_translated.lower() for word in ["hello", "how", "are", "you"])

    def test_command_extraction_edge_cases(self, multilingual):
        """Test command extraction with edge cases."""
        test_cases = [
            ("Run: echo 'test'", "echo 'test'"),
            ("Execute command: echo 'test'", "echo 'test'"),
            ("Please run this: echo 'test'", "echo 'test'"),
            ("Command: echo 'test'", "echo 'test'"),
            ("", None),
            ("No command here", None),
        ]

        for input_text, expected in test_cases:
            result = multilingual.extract_command(input_text)
            assert result == expected 