"""Tests for the vision processor module."""

import pytest
from pathlib import Path
from uaibot.core.vision import VisionProcessor, VisionResult

@pytest.fixture
def vision_processor():
    """Create a vision processor instance for testing."""
    return VisionProcessor()

@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image for testing."""
    image_path = tmp_path / "test_image.png"
    # Create a simple image using PIL
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_path)
    return image_path

def test_process_image(vision_processor, sample_image):
    """Test processing an image."""
    result = vision_processor.process_image(str(sample_image), "What is in this image?")
    assert isinstance(result, VisionResult)
    assert isinstance(result.description, str)
    assert isinstance(result.confidence, float)
    assert 0 <= result.confidence <= 1

def test_process_screenshot(vision_processor, sample_image):
    """Test processing a screenshot."""
    result = vision_processor.process_screenshot(str(sample_image))
    assert isinstance(result, VisionResult)
    assert isinstance(result.description, str)
    assert isinstance(result.confidence, float)
    assert 0 <= result.confidence <= 1

def test_analyze_document(vision_processor, sample_image):
    """Test analyzing a document."""
    result = vision_processor.analyze_document(str(sample_image))
    assert isinstance(result, VisionResult)
    assert isinstance(result.description, str)
    assert isinstance(result.confidence, float)
    assert 0 <= result.confidence <= 1

def test_invalid_image_path(vision_processor):
    """Test processing an invalid image path."""
    result = vision_processor.process_image("nonexistent.png", "What is in this image?")
    assert isinstance(result, VisionResult)
    assert "Error" in result.description
    assert result.confidence == 0.0 