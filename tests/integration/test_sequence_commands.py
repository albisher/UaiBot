import pytest
import os
import sys
from pathlib import Path
import logging
from typing import Generator

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from uaibot.main import UaiBot

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def uaibot() -> Generator[UaiBot, None, None]:
    """Fixture to create and yield a UaiBot instance."""
    bot = UaiBot()
    yield bot

def test_sequence_commands(uaibot: UaiBot):
    """Test sequence of commands as specified in sequence_test_explanation.txt."""
    
    # Step 1: Set up environment
    logger.info("Step 1: Setting up environment")
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Step 2: Search for Kuwait
    logger.info("Step 2: Searching for Kuwait")
    result = uaibot.process_command("where is Kuwait")
    assert result['status'] == 'success', f"Failed to search for Kuwait: {result.get('message')}"
    
    # Step 3: Click the middle link
    logger.info("Step 3: Clicking the middle link")
    result = uaibot.process_command("in that browser click the middle link")
    assert result['status'] == 'success', f"Failed to click the middle link: {result.get('message')}"
    
    # Step 4: Adjust browser focus
    logger.info("Step 4: Adjusting browser focus")
    result = uaibot.process_command("make that browser more focused on the text")
    assert result['status'] == 'success', f"Failed to adjust browser focus: {result.get('message')}"
    
    # Step 5: Adjust volume
    logger.info("Step 5: Adjusting volume")
    result = uaibot.process_command("increase volume to 80%")
    assert result['status'] == 'success', f"Failed to adjust volume: {result.get('message')}"
    
    # Step 6: Navigate to YouTube
    logger.info("Step 6: Navigating to YouTube")
    result = uaibot.process_command("now in safari go to youtube")
    assert result['status'] == 'success', f"Failed to navigate to YouTube: {result.get('message')}"
    
    # Step 7: Search for Quran
    logger.info("Step 7: Searching for Quran")
    result = uaibot.process_command("in there search for Quran by Al Husay")
    assert result['status'] == 'success', f"Failed to search for Quran: {result.get('message')}"
    
    # Step 8: Play and cast to TV
    logger.info("Step 8: Playing and casting to TV")
    result = uaibot.process_command("play that and cast it to my tv")
    assert result['status'] == 'success', f"Failed to play and cast to TV: {result.get('message')}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 