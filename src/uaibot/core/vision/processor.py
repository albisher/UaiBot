"""
Vision processor module for UaiBot.

This module provides vision processing capabilities using SmolVLM-256M.
"""
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ..logging_manager import get_logger

logger = get_logger(__name__)

@dataclass
class VisionResult:
    """Data class for vision processing results."""
    description: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class VisionProcessor:
    """Vision processing using SmolVLM-256M."""
    
    def __init__(self):
        """Initialize the vision processor."""
        try:
            self.processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
            self.model = AutoModelForVision2Seq.from_pretrained(
                "HuggingFaceTB/SmolVLM-256M-Instruct",
                torch_dtype=torch.bfloat16
            )
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            logger.info("Vision processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vision processor: {str(e)}")
            raise

    def process_image(self, image_path: str, prompt: str = "Can you describe this image?") -> VisionResult:
        """
        Process an image and return its description.
        
        Args:
            image_path: Path to the image file
            prompt: Prompt for the vision model
            
        Returns:
            VisionResult containing the description and confidence
        """
        try:
            image = Image.open(image_path)
            inputs = self.processor(
                text=prompt,
                images=[image],
                return_tensors="pt"
            ).to(self.device)
            
            generated_ids = self.model.generate(**inputs, max_new_tokens=500)
            description = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # For now, we'll use a default confidence since SmolVLM doesn't provide it
            return VisionResult(
                description=description,
                confidence=0.95,  # Placeholder confidence
                metadata={"model": "SmolVLM-256M"}
            )
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def process_screenshot(self, screenshot_path: str) -> VisionResult:
        """
        Process a screenshot and analyze its contents.
        
        Args:
            screenshot_path: Path to the screenshot file
            
        Returns:
            VisionResult containing the analysis
        """
        return self.process_image(
            screenshot_path,
            "What's on the screen? Please describe the content and any important elements."
        )

    def analyze_document(self, document_path: str) -> VisionResult:
        """
        Analyze a document image.
        
        Args:
            document_path: Path to the document image
            
        Returns:
            VisionResult containing the document analysis
        """
        return self.process_image(
            document_path,
            "Please analyze this document. What type of document is it? What's its content?"
        ) 