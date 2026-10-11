# -*- coding: utf-8 -*-
"""
tools/convert.py

Конвертация файлов: кодировка, Base64, изображения, окончания строк.

Не требует обязательных зависимостей.
Для изображений используется Pillow, если он установлен.
"""

import os
import base64
import codecs


# ------------------------------------------------------------------
#  Доступные кодировки (без экзотики)
# ------------------------------------------------------------------
TEXT_ENCODINGS = [
    "utf-8",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "utf-32",
    "cp1251",      # Windows-1251
    "cp866",       # DOS
    "koi8-r",
    "iso-8859-1",
    "iso-8859-5",
    "mac-cyrillic",
]


# ------------------------------------------------------------------
#  Действия
# ------------------------------------------------------------------
ACTIONS = [
    "encoding",        # смена кодировки
    "base64_encode",   # → Base64
    "base64_decode",   # ← Base64
    "line_endings",    # CRLF / LF
    "image",           # конвертация изображений (Pillow)
]


# ------------------------------------------------------------------
#  Кодировка
# ------------------------------------------------------------------
def convert_encoding(
    src: str, dst: str, src_enc: str, dst_enc: str,
    chunk: int = 1 << 20,
    on_progress=None,
    cancel_flag=None,
) -> None:
    """
    Перекодирует текстовый файл.
    Читает потоково, декодирует построчно с сохранением смешанных окончаний.
    """
    total = os.path.getsize(src)
    processed = 0

    # Используем инкрементальный декодер, чтобы корректно обрабатывать
    # многобайтовые последовательности на границе чанка
    decoder = codecs.getincrementaldecoder(src_enc)(errors="replace")

    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Конвертация отменена")
            chunk_bytes = f_in.read(chunk)
            if not chunk_bytes:
                break
            text = decoder.decode(chunk_bytes)
            f_out.write(text.encode(dst_enc, errors="replace"))
            processed += len(chunk_bytes)
            if on_progress:
                on_progress(processed, total)

        tail = decoder.decode(b"", final=True)
        if tail:
            f_out.write(tail.encode(dst_enc, errors="replace"))


# ------------------------------------------------------------------
#  Base64
# ------------------------------------------------------------------
def base64_encode(
    src: str, dst: str,
    chunk: int = 3 * 1024,
    on_progress=None,
    cancel_flag=None,
    line_width: int = 76,
) -> None:
    """Кодирует файл в Base64 с переносами строк."""
    total = os.path.getsize(src)
    processed = 0
    col = 0

    with open(src, "rb") as f_in, open(dst, "w", encoding="ascii") as f_out:
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Конвертация отменена")
            block = f_in.read(chunk)
            if not block:
                break
            encoded = base64.b64encode(block).decode("ascii")
            # Разбиваем на строки по line_width
            i = 0
            while i < len(encoded):
                take = line_width - col
                f_out.write(encoded[i:i + take])
                col += take
                i += take
                if col >= line_width:
                    f_out.write("\n")
                    col = 0
            processed += len(block)
            if on_progress:
                on_progress(processed, total)
        if col > 0:
            f_out.write("\n")


def base64_decode(
    src: str, dst: str,
    chunk: int = 64 * 1024,
    on_progress=None,
    cancel_flag=None,
) -> None:
    """Декодирует Base64-файл в бинарный."""
    total = os.path.getsize(src)
    processed = 0

    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        buffer = b""
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Конвертация отменена")
            block = f_in.read(chunk)
            if not block:
                break
            buffer += block
            # Убираем все пробельные символы
            clean = bytes(c for c in buffer if c not in b" \t\r\n")
            # Декодируем кратно 4
            usable = len(clean) - (len(clean) % 4)
            if usable:
                try:
                    f_out.write(base64.b64decode(clean[:usable]))
                except Exception as e:
                    raise ValueError(f"Некорректный Base64: {e}")
                buffer = clean[usable:]
            else:
                buffer = clean
            processed += len(block)
            if on_progress:
                on_progress(processed, total)

        if buffer:
            try:
                f_out.write(base64.b64decode(buffer))
            except Exception as e:
                raise ValueError(f"Некорректный Base64 в конце: {e}")


# ------------------------------------------------------------------
#  Окончания строк
# ------------------------------------------------------------------
def convert_line_endings(
    src: str, dst: str, target: str,
    chunk: int = 1 << 20,
    on_progress=None,
    cancel_flag=None,
) -> None:
    """
    target: "lf" | "crlf" | "cr"
    Работает как с бинарным содержимым — CR/LF не зависят от кодировки.
    """
    total = os.path.getsize(src)
    processed = 0

    newline_map = {"lf": b"\n", "crlf": b"\r\n", "cr": b"\r"}
    target_bytes = newline_map[target]

    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        prev_cr = False
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Конвертация отменена")
            block = f_in.read(chunk)
            if not block:
                break

            out = bytearray()
            i = 0
            while i < len(block):
                b = block[i]
                if b == 0x0D:  # \r
                    if i + 1 < len(block) and block[i + 1] == 0x0A:
                        # \r\n
                        out += target_bytes
                        i += 2
                    else:
                        out += target_bytes
                        i += 1
                elif b == 0x0A:  # \n
                    out += target_bytes
                    i += 1
                else:
                    out.append(b)
                    i += 1

            f_out.write(bytes(out))
            processed += len(block)
            if on_progress:
                on_progress(processed, total)


# ------------------------------------------------------------------
#  Изображения (Pillow)
# ------------------------------------------------------------------
IMAGE_FORMATS = ["PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"]


def has_pillow() -> bool:
    try:
        import PIL  # noqa
        return True
    except ImportError:
        return False


def convert_image(src: str, dst: str, target_format: str,
                  quality: int = 90) -> None:
    """Конвертирует изображение. Требует Pillow."""
    from PIL import Image  # type: ignore

    target_format = target_format.upper()
    with Image.open(src) as img:
        save_kwargs = {}
        if target_format == "JPEG":
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            save_kwargs["quality"] = quality
        elif target_format == "WEBP":
            save_kwargs["quality"] = quality
        img.save(dst, format=target_format, **save_kwargs)



EXT_TO_FORMAT = {
    ".png":  "PNG",
    ".jpg":  "JPEG",
    ".jpeg": "JPEG",
    ".webp": "WEBP",
    ".bmp":  "BMP",
    ".tif":  "TIFF",
    ".tiff": "TIFF",
    ".gif":  "GIF",
}


def image_targets(src: str) -> list[str]:
    src_ext = os.path.splitext(src)[1].lower()
    src_fmt = EXT_TO_FORMAT.get(src_ext)
    return [f for f in IMAGE_FORMATS if f != src_fmt]