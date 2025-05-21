import unittest
import langdetect

class TestMultilingual(unittest.TestCase):
    def setUp(self):
        self.supported_languages = ['en', 'ar']
        self.current_language = 'en'
        self.translations = {
            'en': {
                'Hello World': 'Hello World',
                'This is a test': 'This is a test',
                'Welcome': 'Welcome',
                'Goodbye': 'Goodbye'
            },
            'ar': {
                'Hello World': 'مرحبا بالعالم',
                'This is a test': 'هذا اختبار',
                'Welcome': 'مرحبا',
                'Goodbye': 'مع السلامة'
            }
        }
        
    def execute_command(self, command):
        """Execute a multilingual command"""
        command_lower = command.lower()
        words = command_lower.split()
        
        # Language settings command
        if any(word in ['set', 'change', 'switch'] for word in words) and 'language' in words and 'to' in words:
            # Find language after 'to'
            to_index = words.index('to')
            if to_index + 1 < len(words):
                lang = words[to_index + 1].lower()
                if lang in self.supported_languages:
                    self.current_language = lang
                    return {
                        "status": "success",
                        "language": lang,
                        "message": f"Language changed to {lang}"
                    }
            return {
                "status": "error",
                "message": "Invalid language specified"
            }
            
        # Language detection command
        elif any(word in ['detect', 'what', 'identify'] for word in words) and 'language' in words:
            # Find text between quotes
            quote_start = command.find('"')
            if quote_start == -1:
                quote_start = command.find("'")
            if quote_start != -1:
                quote_end = command.find('"', quote_start + 1)
                if quote_end == -1:
                    quote_end = command.find("'", quote_start + 1)
                if quote_end != -1:
                    text = command[quote_start + 1:quote_end]
                    try:
                        lang = langdetect.detect(text)
                        return {
                            "status": "success",
                            "text": text,
                            "detected_language": lang
                        }
                    except:
                        return {
                            "status": "error",
                            "message": "Could not detect language"
                        }
            return None
            
        # Translation command
        elif any(word in ['translate', 'convert', 'change'] for word in words) and 'to' in words:
            # Find text between quotes
            quote_start = command.find('"')
            if quote_start == -1:
                quote_start = command.find("'")
            if quote_start != -1:
                quote_end = command.find('"', quote_start + 1)
                if quote_end == -1:
                    quote_end = command.find("'", quote_start + 1)
                if quote_end != -1:
                    text = command[quote_start + 1:quote_end]
                    # Find target language after 'to'
                    to_index = words.index('to')
                    if to_index + 1 < len(words):
                        target_lang = words[to_index + 1].lower()
                        if target_lang in self.supported_languages:
                            # Use our translation dictionary for testing
                            if text in self.translations[target_lang]:
                                return {
                                    "status": "success",
                                    "original_text": text,
                                    "translated_text": self.translations[target_lang][text],
                                    "target_language": target_lang
                                }
            return {
                "status": "error",
                "message": "Invalid translation request"
            }
            
        # Language support command
        elif any(word in ['show', 'list', 'what'] for word in words) and 'languages' in words and 'supported' in words:
            return {
                "status": "success",
                "supported_languages": self.supported_languages,
                "current_language": self.current_language
            }
            
        # Language preferences command
        elif any(word in ['set', 'change'] for word in words) and 'default' in words and 'language' in words and 'to' in words:
            # Find language after 'to'
            to_index = words.index('to')
            if to_index + 1 < len(words):
                lang = words[to_index + 1].lower()
                if lang in self.supported_languages:
                    self.current_language = lang
                    return {
                        "status": "success",
                        "language": lang,
                        "message": f"Default language set to {lang}"
                    }
            return {
                "status": "error",
                "message": "Invalid language specified"
            }
            
        # Arabic commands
        elif 'تعيين' in command or 'تغيير' in command:
            # Find language after 'إلى'
            if 'إلى' in command:
                lang_index = command.find('إلى') + len('إلى')
                lang = command[lang_index:].strip().lower()
                if lang in self.supported_languages:
                    self.current_language = lang
                    return {
                        "status": "success",
                        "language": lang,
                        "message": f"تم تغيير اللغة إلى {lang}"
                    }
            return {
                "status": "error",
                "message": "لغة غير صالحة"
            }
            
        return None

    def test_language_settings(self):
        """Test language settings commands"""
        commands = [
            "set language to english",
            "change language to arabic",
            "switch language to en"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("language", result)
                self.assertIn("message", result)
                self.assertEqual(result["status"], "success")

    def test_language_detection(self):
        """Test language detection commands"""
        commands = [
            "detect language of 'Hello World'",
            "what language is 'مرحبا بالعالم'",
            "identify language of 'This is a test'"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("text", result)
                self.assertIn("detected_language", result)
                self.assertEqual(result["status"], "success")

    def test_translation(self):
        """Test translation commands"""
        commands = [
            "translate 'Hello World' to arabic",
            "convert to 'This is a test' to ar",
            "change to 'Welcome' to english"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("original_text", result)
                self.assertIn("translated_text", result)
                self.assertIn("target_language", result)
                self.assertEqual(result["status"], "success")

    def test_language_support(self):
        """Test language support commands"""
        commands = [
            "show supported languages",
            "list languages",
            "what languages are supported"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("supported_languages", result)
                self.assertIn("current_language", result)
                self.assertEqual(result["status"], "success")
                self.assertEqual(len(result["supported_languages"]), 2)

    def test_language_preferences(self):
        """Test language preferences commands"""
        commands = [
            "set default language to english",
            "change default language to arabic"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("language", result)
                self.assertIn("message", result)
                self.assertEqual(result["status"], "success")

    def test_arabic_commands(self):
        """Test Arabic commands"""
        commands = [
            "تعيين اللغة إلى العربية",
            "تغيير اللغة إلى الانجليزية"
        ]
        
        for cmd in commands:
            with self.subTest(cmd=cmd):
                result = self.execute_command(cmd)
                self.assertIsNotNone(result)
                self.assertIn("status", result)
                self.assertIn("language", result)
                self.assertIn("message", result)
                self.assertEqual(result["status"], "success")

if __name__ == '__main__':
    unittest.main() 