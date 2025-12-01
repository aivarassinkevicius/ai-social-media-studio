import os
from typing import List

import streamlit as st
from PIL import Image

from image_utils import marketing_filter
from caption_utils import generate_captions

# Optional: jei nori naudoti Clipdrop AI upscaling
try:
    from external_image_api import enhance_with_clipdrop
    HAS_CLIPDROP = True
except ImportError:
    HAS_CLIPDROP = False


st.set_page_config(
    page_title="AI Social Media Studio",
    layout="wide"
)


def load_images(files) -> List[Image.Image]:
    images = []
    for uf in files:
        img = Image.open(uf).convert("RGB")
        images.append(img)
    return images


# ----------------------------------------
# Šoninė juosta – nustatymai
# ----------------------------------------
with st.sidebar:
    st.header("⚙️ Nustatymai")

    # API raktai
    openai_default = os.getenv("OPENAI_API_KEY", "")
    openai_key = st.text_input(
        "OpenAI API raktas",
        type="password",
        value=openai_default,
        help="Gausi iš platform.openai.com (API Keys skiltis)."
    )

    clipdrop_default = os.getenv("CLIPDROP_API_KEY", "")
    clipdrop_key = st.text_input(
        "Clipdrop API raktas (nebūtina)",
        type="password",
        value=clipdrop_default,
        help="Naudojamas AI upscalingui, jei suvesi."
    )

    st.markdown("---")

    season = st.selectbox(
        "Sezonas",
        ["Pavasaris", "Vasara", "Ruduo", "Žiema"],
        index=1
    )

    holiday = st.selectbox(
        "Šventė / proga",
        ["Be šventės", "Kalėdos", "Velykos", "Naujieji metai", "Joninės", "Gimtadienis"]
    )

    st.markdown("---")
    st.caption("💡 Patarimas: API raktus geriau saugoti `.env` arba OS aplinkoje.")


st.title("📸 AI Social Media Studio")
st.write("Įkelk 1–4 nuotraukas, mes jas patvarkysim ir sukursim tekstus Facebook / Instagram įrašams.")


# ----------------------------------------
# 1. Nuotraukų įkėlimas
# ----------------------------------------
uploaded_files = st.file_uploader(
    "Įkelkite nuo 1 iki 4 nuotraukų:",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 4:
        st.warning("Prašau įkelti ne daugiau kaip 4 nuotraukas – apdorosim pirmas 4.")
        uploaded_files = uploaded_files[:4]

    images = load_images(uploaded_files)

    st.subheader("📸 Originalios nuotraukos")
    col1, col2 = st.columns(2)
    for i, img in enumerate(images):
        col = col1 if i % 2 == 0 else col2
        col.image(img, caption=f"Originali #{i+1}", use_column_width=True)

    # ----------------------------------------
    # 2. Greita vietinė korekcija
    # ----------------------------------------
    st.subheader("✨ Greita marketinginė korekcija (lokali, greita)")

    enhanced_images = [marketing_filter(img) for img in images]

    col1, col2 = st.columns(2)
    for i, ei in enumerate(enhanced_images):
        col = col1 if i % 2 == 0 else col2
        col.image(ei, caption=f"Marketinginė #{i+1}", use_column_width=True)

    # ----------------------------------------
    # 3. Pasirenkamas AI kokybės pagerinimas per Clipdrop
    # ----------------------------------------
    ai_enhanced_images = enhanced_images  # default – jei nenaudojam AI, liks tokios pat

    if clipdrop_key and HAS_CLIPDROP:
        if st.button("⚡ AI kokybės pagerinimas per Clipdrop API"):
            st.info("Siunčiame nuotraukas į AI upscalingą...")
            tmp = []
            for i, img in enumerate(enhanced_images):
                try:
                    out = enhance_with_clipdrop(img, clipdrop_key)
                    tmp.append(out)
                except Exception as e:
                    st.error(f"Nuotrauka #{i+1}: nepavyko pagerinti per Clipdrop ({e})")
                    tmp.append(img)
            ai_enhanced_images = tmp

            st.subheader("🔍 AI pagerintos nuotraukos")
            col1, col2 = st.columns(2)
            for i, ei in enumerate(ai_enhanced_images):
                col = col1 if i % 2 == 0 else col2
                col.image(ei, caption=f"AI pagerinta #{i+1}", use_column_width=True)
    else:
        st.info("Jei nori pažangesnio AI pagerinimo (upscaling/denoise), įvesk Clipdrop API raktą šoninėje juostoje.")

    # ----------------------------------------
    # 4. Tekstų generavimas
    # ----------------------------------------
    captions = None
    if st.button("✏️ Generuoti 3 tekstus pagal nuotraukas ir kontekstą"):
        if not openai_key:
            st.error("Reikia OpenAI API rakto tekstų generavimui.")
        else:
            with st.spinner("Generuojame tekstus su OpenAI..."):
                try:
                    captions = generate_captions(
                        images=ai_enhanced_images,
                        season=season,
                        holiday=holiday,
                        openai_api_key=openai_key,
                        language="lt"
                    )
                except Exception as e:
                    st.error(f"Nepavyko sugeneruoti tekstų: {e}")
                    captions = None

    if captions:
        st.subheader("📝 Sugeneruoti tekstai")

        tab1, tab2, tab3 = st.tabs(["Marketinginis", "Draugiškas", "Juokingas"])

        with tab1:
            st.markdown(f"**Marketinginis:**\n\n{captions.get('marketing', '')}")

        with tab2:
            st.markdown(f"**Draugiškas:**\n\n{captions.get('friendly', '')}")

        with tab3:
            st.markdown(f"**Juokingas:**\n\n{captions.get('funny', '')}")

        # ----------------------------------------
        # 5. Socialinio posto "šablonas"
        # ----------------------------------------
        st.subheader("📱 Socialinio tinklo šablono peržiūra")

        # Imame pirmą pagerintą nuotrauką kaip pagrindinę
        main_img = ai_enhanced_images[0]

        left, right = st.columns([2, 1])

        with left:
            st.image(main_img, caption="Pagrindinė nuotrauka", use_column_width=True)

        with right:
            st.markdown("### Paruoštas įrašas")
            st.markdown(f"**Sezonas:** {season}")
            st.markdown(f"**Proga:** {holiday}")
            st.markdown("---")
            st.markdown("**Siūlomas tekstas:**")
            st.markdown(captions.get("marketing", ""))

            st.caption("💡 Gali čia pakeisti tekstą prieš kopijuodamas į Facebook / Instagram.")
else:
    st.info("Įkelk bent vieną nuotrauką, kad pradėtume darbą.")
