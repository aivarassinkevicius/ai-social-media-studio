import io
import requests
from PIL import Image

def upscale_image_with_replicate(img: Image.Image, api_key: str) -> Image.Image:
    """
    Pagerina nuotrauką naudojant Real-ESRGAN modelį per Replicate API.
    Tinka 10-20 MP nuotraukoms, nes neturi Clipdrop limitų.
    """

    if not api_key:
        raise ValueError("Reikia Replicate API rakto")

    # Konvertuojam į bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Upload nuotrauka į Replicate
    upload_resp = requests.post(
        "https://api.replicate.com/v1/uploads",
        headers={"Authorization": f"Token {api_key}"},
        json={"filename": "input.png", "content_type": "image/png"}
    ).json()

    upload_url = upload_resp["upload_url"]
    input_url = upload_resp["input"]["url"]

    # Įkeliame failą į upload URL
    requests.put(upload_url, data=buf, headers={"Content-Type": "image/png"})

    # Paleidžiam Real-ESRGAN inference
    run = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "version": "7de2ea26f905829919f6d13b7caa7f0a574919aa7a16e0d5d70573a4cb5f5f55",  # Real-ESRGAN
            "input": {"image": input_url}
        }
    ).json()

    prediction_id = run["id"]

    # Laukiam rezultatų
    while True:
        status = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers={"Authorization": f"Token {api_key}"}
        ).json()

        if status["status"] == "succeeded":
            img_url = status["output"][0]
            break
        elif status["status"] == "failed":
            raise RuntimeError("Replicate: prediction failed")

    # Atsisiunčiam rezultatą
    out = requests.get(img_url)
    result_img = Image.open(io.BytesIO(out.content)).convert("RGB")

    return result_img
