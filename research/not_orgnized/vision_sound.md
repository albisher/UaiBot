## Step-by-Step: 100% Local Use of SmolVLM-256M and Whisper Tiny with Python

---

### **SmolVLM-256M (Vision-Language Model)**

#### 1. **Install Python and Required Libraries**
- Make sure Python is installed (Python 3.8+ recommended).
- Install PyTorch and Hugging Face Transformers:
  ```bash
  pip install torch transformers pillow
  ```

#### 2. **Download or Prepare Your Image**
- Have a local image file (e.g., `my_image.jpg`) ready.

#### 3. **Python Script to Run SmolVLM-256M Locally**
```python
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq

# Load model and processor
processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
model = AutoModelForVision2Seq.from_pretrained(
    "HuggingFaceTB/SmolVLM-256M-Instruct",
    torch_dtype=torch.bfloat16
)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Load and process image
image = Image.open("my_image.jpg")
inputs = processor(
    text="Can you describe this image?",
    images=[image],
    return_tensors="pt"
).to(device)

# Run inference
generated_ids = model.generate(**inputs, max_new_tokens=500)
generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
print(generated_texts)
```
- Replace `"my_image.jpg"` with your image path.
- This script works 100% locally after the initial model download[2][3].

#### **Tips for Optimization**
- You can use quantization (e.g., 4/8-bit with bitsandbytes) for even lower memory usage.
- For CPU-only use, omit `.to(device)` or set device to `"cpu"`[2].

---

### **Whisper Tiny (Speech-to-Text Model)**

#### 1. **Install Python and Required Libraries**
- Install PyTorch, FFmpeg (for audio), and Whisper:
  ```bash
  pip install torch
  pip install git+https://github.com/openai/whisper.git
  ```
- Install FFmpeg:
  - **Linux:** `sudo apt install ffmpeg`
  - **macOS:** `brew install ffmpeg`
  - **Windows:** Use Chocolatey: `choco install ffmpeg`[8].

#### 2. **Download or Prepare Your Audio File**
- Have a local audio file ready (e.g., `audio.wav`).

#### 3. **Python Script to Run Whisper Tiny Locally**
```python
import whisper

# Load the tiny model
model = whisper.load_model("tiny")

# Transcribe your audio file
result = model.transcribe("audio.wav")
print(result["text"])
```
- Replace `"audio.wav"` with your audio file path.
- This runs fully offline after the first model download[8][9].

#### **Offline/Portable Use**
- For true offline use, download the model weights and required files once, then copy the `.cache/whisper` folder to your offline machine as needed[9].

---

## **Summary Table**

| Model           | Task                | Main Steps                                                                                  |
|-----------------|---------------------|--------------------------------------------------------------------------------------------|
| SmolVLM-256M    | Image → Text        | Install deps → Load model/processor → Prepare image → Run inference → Print output          |
| Whisper Tiny    | Audio → Text        | Install deps (incl. FFmpeg) → Load model → Transcribe audio → Print output                 |

---

**Both models are open source, run 100% locally after initial setup, and require no internet connection for inference.**

Citations:
[1] https://huggingface.co/blog/smolvlm2
[2] https://digialps.com/smolvlm-256m-the-worlds-smallest-ai-model-running-100-locally-in-browser-on-webgpu/
[3] https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct/blob/cee7dc33d83ff2ddec17238b7aba85145169e631/README.md
[4] https://www.youtube.com/watch?v=T_D_LFJFVvI
[5] https://www.reddit.com/r/LocalLLaMA/comments/1kmi6vl/i_updated_the_smolvlm_llamacpp_webcam_demo_to_run/
[6] https://blog.paperspace.com/whisper-openai-flask-application-deployment/
[7] https://www.reddit.com/r/LocalLLaMA/comments/1je4eka/smoldocling_256m_vlm_for_document_understanding/
[8] https://assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model
[9] https://github.com/openai/whisper/discussions/1463

---
Answer from Perplexity: pplx.ai/share