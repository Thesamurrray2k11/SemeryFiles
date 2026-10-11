import os
import io
from typing import Optional

try:
    import qrcode
    from qrcode.constants import (
        ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
    )
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from pyzbar import pyzbar
    from PIL import Image
    PYZBAR_AVAILABLE = True
except (ImportError, OSError):
    PYZBAR_AVAILABLE = False


ERROR_LEVELS = {
    "L": ("Low (7%)", ERROR_CORRECT_L if QRCODE_AVAILABLE else 1),
    "M": ("Medium (15%)", ERROR_CORRECT_M if QRCODE_AVAILABLE else 0),
    "Q": ("Quartile (25%)", ERROR_CORRECT_Q if QRCODE_AVAILABLE else 3),
    "H": ("High (30%)", ERROR_CORRECT_H if QRCODE_AVAILABLE else 2),
}


def is_available() -> bool:
    return QRCODE_AVAILABLE


def is_decoder_available() -> bool:
    return PYZBAR_AVAILABLE


def generate_qr(
    data: str,
    size_px: int = 512,
    error_level: str = "M",
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    border: int = 4,
) -> Optional["PILImage"]:
    if not QRCODE_AVAILABLE:
        return None
    if not data:
        return None

    level = ERROR_LEVELS.get(error_level, ERROR_LEVELS["M"])[1]

    qr = qrcode.QRCode(
        version=None,
        error_correction=level,
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")

    img = img.resize((size_px, size_px), resample=0)
    return img


def save_qr(
    img,
    path: str,
    fmt: str = "PNG",
) -> tuple[bool, str | None]:
    try:
        if fmt.upper() == "SVG":
            return _save_as_svg(img, path)
        else:
            img.save(path, format=fmt.upper())
            return True, None
    except Exception as e:
        return False, str(e)


def _save_as_svg(img, path: str) -> tuple[bool, str | None]:
    try:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        import base64
        b64 = base64.b64encode(buf.read()).decode("ascii")
        w, h = img.size

        svg = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'  <image width="{w}" height="{h}" '
            f'xlink:href="data:image/png;base64,{b64}"/>\n'
            f'</svg>\n'
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        return True, None
    except Exception as e:
        return False, str(e)



def decode_qr(path: str) -> dict:

    if not PYZBAR_AVAILABLE:
        return {"ok": False, "error": "no_pyzbar", "results": []}

    if not path or not os.path.isfile(path):
        return {"ok": False, "error": "file_not_found", "results": []}

    try:
        img = Image.open(path)
        decoded = pyzbar.decode(img)
        results = []
        for d in decoded:
            results.append({
                "type": d.type,
                "data": d.data.decode("utf-8", errors="replace"),
                "rect": (d.rect.left, d.rect.top, d.rect.width, d.rect.height),
            })
        return {"ok": True, "error": None, "results": results}
    except Exception as e:
        return {"ok": False, "error": str(e), "results": []}