import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from typing import Optional
from labeeb.core.ai.tool_base import BaseTool
import logging
import pyautogui
import tempfile

logger = logging.getLogger(__name__)

class VisionTool(BaseTool):
    """
    VisionTool for Labeeb using SmolVLM-256M. All processing is 100% local.
    Do not send any data to the internet unless explicitly requested by the user.
    """
    def __init__(self):
        super().__init__(name="vision", description="Local vision-language tool using SmolVLM-256M.")
        self._init_model()

    def _init_model(self):
        try:
            self.processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
            self.model = AutoModelForVision2Seq.from_pretrained(
                "HuggingFaceTB/SmolVLM-256M-Instruct",
                torch_dtype=torch.bfloat16
            )
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            logger.info("SmolVLM-256M loaded locally on %s", self.device)
        except Exception as e:
            logger.error(f"Failed to load SmolVLM-256M: {e}")
            raise

    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> str:
        """
        Analyze an image and return a description. All processing is local.
        Args:
            image_path: Path to the image file
            prompt: Optional prompt/question for the model
        Returns:
            str: Model's description/caption
        """
        if prompt is None:
            prompt = "Can you describe this image?"
        # Ensure the prompt includes <image> for each image
        if '<image>' not in prompt:
            prompt = prompt.strip() + ' <image>'
        try:
            image = Image.open(image_path)
            inputs = self.processor(
                text=prompt,
                images=[image],
                return_tensors="pt"
            ).to(self.device)
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=500)
            return self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        except Exception as e:
            logger.error(f"VisionTool failed to analyze image: {e}")
            return f"[VisionTool error: {e}]"

    async def _execute_command(self, action: str, args: dict) -> dict:
        if action == "analyze_image":
            image_path = args.get("image_path")
            prompt = args.get("prompt")
            filename = args.get("filename")
            if not image_path:
                # Take screenshot using pyautogui
                if filename:
                    screenshot = pyautogui.screenshot()
                    screenshot.save(filename)
                    image_path = filename
                else:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        screenshot = pyautogui.screenshot()
                        screenshot.save(tmp.name)
                        image_path = tmp.name
            try:
                result = self.analyze_image(image_path, prompt)
                return {"result": result, "image_path": image_path}
            except Exception as e:
                return {"error": str(e), "image_path": image_path}
        else:
            return {"error": f"Unknown action: {action}"} 