from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def marketing_filter(img: Image.Image) -> Image.Image:
    """
    Greita marketinginė korekcija:
    - truputį padidinam kontrastą
    - šiek tiek paryškinam spalvas
    - mažai padidinam ryškumą
    - auto-kontrastas
    - lengvas sharpen
    """
    img = img.copy()

    # Auto-kontrastas
    img = ImageOps.autocontrast(img, cutoff=2)

    # Spalvų sodrumas
    color_enh = ImageEnhance.Color(img)
    img = color_enh.enhance(1.2)  # 20% daugiau spalvų

    # Kontrastas
    contrast_enh = ImageEnhance.Contrast(img)
    img = contrast_enh.enhance(1.15)

    # Šviesumas
    bright_enh = ImageEnhance.Brightness(img)
    img = bright_enh.enhance(1.05)

    # Šiek tiek ryškumo
    sharp_enh = ImageEnhance.Sharpness(img)
    img = sharp_enh.enhance(1.1)

    # Lengvas Unsharp Mask
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

    return img
