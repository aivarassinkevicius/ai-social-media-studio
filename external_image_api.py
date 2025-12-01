import io
from typing import Optional

import requests
from PIL import Image


CLIPDROP_ENDPOINT = "https://apis.clipdrop.co/super-resolution/v1"


def enhance_with_clipdrop(img: Image.Image, api_key: str, scale: int = 2) -> Optional[Image.Image]:
    """
    AI upscaling / pagerinimas per Clipdrop API.
    - api_key: tavo Clipdrop API raktas
    - scale: 2 arba 4 (realiai Clipdrop leidžia kelis režimus, čia paprastas variantas)
    """
    if not api_key:
        raise ValueError("Trūksta Clipdrop API rakto")

    # Konvertuojam į JPEG baitus
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    files = {
        "image_file": ("image.jpg", buf, "image/jpeg")
    }

    # Clipdrop pagal dokumentaciją naudoja API key per x-api-key headerį
    headers = {
        "x-api-key": api_key
    }

    # Paprastas requestas
    response = requests.post(CLIPDROP_ENDPOINT, headers=headers, files=files)

    if response.status_code != 200:
        # Gali pasitikrinti response.text debugui
        raise RuntimeError(f"Clipdrop klaida: {response.status_code} {response.text[:200]}")

    # Grąžinam kaip PIL vaizdą
    out_buf = io.BytesIO(response.content)
    out_img = Image.open(out_buf).convert("RGB")
    return out_img
