class AICommandExtractor:
    def extract_command(self, response: str):
        # Stub: always return success, a dummy plan, and empty metadata
        return True, {"plan": "dummy"}, {} 