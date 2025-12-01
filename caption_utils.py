import json
from typing import List, Dict
from PIL import Image
from openai import OpenAI


def generate_captions(
    images: List[Image.Image],
    season: str,
    holiday: str,
    openai_api_key: str,
    language: str = "lt"
) -> Dict[str, str]:
    """
    Sugeneruoja 3 socialinių tinklų tekstus:
    - marketing
    - friendly
    - funny
    """

    if not openai_api_key:
        raise ValueError("Reikia OpenAI API rakto")

    client = OpenAI(api_key=openai_api_key)

    img_count = len(images)
    base_desc = f"Tiek nuotraukų: {img_count}. Jose matomi žmonės, kasdienybė arba produktai."

    user_prompt = f"""
Tu esi lietuviškas socialinių tinklų marketingo specialistas.

Kontekstas:
- Sezonas: {season}
- Šventė: {holiday}
- Nuotraukų skaičius: {img_count}
- Bendra nuotraukų atmosfera: {base_desc}

Sugeneruok 3 trumpus socialinių tinklų įrašų tekstus:
1) "marketing"
2) "friendly"
3) "funny"

Reikalavimai:
- Kalba: lietuvių
- Kiekvienas variantas turi būti 2–3 sakinių
- Gali naudoti 2–4 emoji, bet ne per daug
- Atsakyk griežtai JSON formatu:

{{
  "marketing": "...",
  "friendly": "...",
  "funny": "..."
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # galima pakeisti į gpt-4o-mini
        messages=[
            {"role": "system", "content": "Tu kuri trumpus socialinių tinklų įrašus."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,
    )

    raw_text = response.choices[0].message.content

    try:
        return json.loads(raw_text)
    except:
        # jeigu JSON netinkamas, grąžinam tekstą į visas 3
        return {
            "marketing": raw_text,
            "friendly": raw_text,
            "funny": raw_text
        }
