
from PIL import Image
from base64 import b64decode
import io
import requests
import os

from .image import ArticleImage

class ImageBackendStableDiffusionWebui:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:7860"
        self.TIMEOUT = 30 * 60
        # TODO auto-select checkpoint by calling api
        self.CHECKPOINT = "future-diffusion-v1.ckpt [a41d2d0b20]"

    def _payload(self, prompt: str) -> dict:
        return {
            "prompt": prompt,
            "sd_model_checkpoint": self.CHECKPOINT
        }

    def get_image(self, description: str, caption: str, id_: str, output_dir: str) -> Image:
        path = os.path.join(output_dir, "static", "images", id_+".png")
        try:
            resp = requests.post(url=f"{self.BASE_URL}/sdapi/v1/txt2img", json=self._payload(description), timeout=self.TIMEOUT)
        except Exception:
            print("failed to connect to stable diffusion api. Is it running (press enter to proceed)?")
            if input().strip() == "":
                try:
                    resp = requests.post(url=f"{self.BASE_URL}/sdapi/v1/txt2img", json=self._payload(description), timeout=self.TIMEOUT)
                except Exception:
                    print("failed to connect to stable diffusion api, skipping image generation")
                    return None
        if resp.status_code != 200:
            return None
        # TODO pass image data as byte array, let BlogGenerator write it to file
        Image.open(io.BytesIO(b64decode(resp.json()["images"][0].split(",", 1)[0]))).save(path)
        return ArticleImage(id_, caption, "Stable Diffusion Webui", description)

