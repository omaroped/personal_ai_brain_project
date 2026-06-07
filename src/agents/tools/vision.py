# MODULE: Screen Capture and Vision processing tool.
"""Tool for the agent to 'see' the user's screen using screenshot utilities and vision models."""

from __future__ import annotations

import base64
import logging
import os
import subprocess
import time
from pathlib import Path

from src.common.logging_utils import configure_logging
import config

LOGGER = configure_logging(__name__)

class VisionService:
    """Handles communicating with Vision-capable LLMs (Gemini/Ollama)."""
    
    @staticmethod
    def analyze_image(image_path: Path, prompt: str) -> str:
        """Send image to a vision model for analysis."""
        
        # Prefer Gemini if available as it is exceptionally fast and accurate for vision
        if config.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                from PIL import Image
                
                genai.configure(api_key=config.GEMINI_API_KEY)
                # gemini-1.5-flash supports multimodal inputs
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                img = Image.open(image_path)
                LOGGER.info("Sending screenshot to Gemini Vision...")
                response = model.generate_content([prompt, img])
                return response.text
            except Exception as e:
                LOGGER.error("Gemini Vision failed: %s", e)
                return f"Vision analysis failed: {e}"
        
        # Fallback to local Ollama vision model (e.g., llava or qwen-vl)
        # Note: User must have pulled a vision model first
        try:
            import httpx
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
                
            payload = {
                "model": "llava:latest", # Common local vision model
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [img_b64]
                    }
                ],
                "stream": False
            }
            
            LOGGER.info("Sending screenshot to local Ollama Vision...")
            resp = httpx.post(f"{config.OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "No description returned.")
            
        except Exception as e:
            LOGGER.error("Local Vision failed: %s", e)
            return "Vision analysis failed. Make sure a vision model (like llava) is installed locally, or provide a GEMINI_API_KEY."

def capture_screen(prompt: str = "Describe what is currently visible on my screen.") -> str:
    """Take a screenshot and analyze it.
    
    Parameters:
        prompt: The specific question to ask the vision model about the screen.
    """
    screenshot_dir = config.DATA_DIR / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"capture_{int(time.time())}.png"
    file_path = screenshot_dir / file_name
    
    try:
        # Determine display server and capture method
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            # gnome-screenshot or grim
            subprocess.run(["gnome-screenshot", "-f", str(file_path)], check=True)
        else:
            # X11 fallback
            subprocess.run(["scrot", str(file_path)], check=True)
            
        if not file_path.exists():
            return "Error: Screenshot command executed but no file was created."
            
        # Analyze
        result = VisionService.analyze_image(file_path, prompt)
        
        # Cleanup to save space
        try:
            file_path.unlink()
        except: pass
        
        return result
        
    except FileNotFoundError:
        return "Error: Screenshot utility (scrot or gnome-screenshot) not installed on host OS."
    except Exception as e:
        return f"Screenshot capture failed: {e}"

if __name__ == "__main__":
    print(capture_screen("What applications are open?"))
