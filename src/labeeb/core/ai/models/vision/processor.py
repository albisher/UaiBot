import torch
from PIL import Image
from dataclasses import dataclass
from transformers import AutoProcessor, AutoModelForVision2Seq
from typing import Optional

@dataclass
class VisionResult:
    description: str
    confidence: float = 1.0
    raw: Optional[str] = None

class VisionProcessor:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
        self.model = AutoModelForVision2Seq.from_pretrained(
            "HuggingFaceTB/SmolVLM-256M-Instruct",
            torch_dtype=torch.bfloat16
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

    def process_image(self, image_path: str, prompt: str = "Can you describe this image?") -> VisionResult:
        image = Image.open(image_path)
        inputs = self.processor(
            text=prompt,
            images=[image],
            return_tensors="pt"
        ).to(self.device)
        generated_ids = self.model.generate(**inputs, max_new_tokens=500)
        description = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return VisionResult(description=description, confidence=1.0, raw=description)

    def process_screenshot(self, image_path: str) -> VisionResult:
        return self.process_image(image_path, prompt="What is on the screen?")

    def analyze_document(self, image_path: str) -> VisionResult:
        return self.process_image(image_path, prompt="Analyze this document.") 