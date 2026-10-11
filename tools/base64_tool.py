import os
import base64
import binascii
import mimetypes

def encode_text(text: str, urlsafe: bool = False) -> str:
    raw = text.encode("utf-8")
    if urlsafe:
        return base64.urlsafe_b64encode(raw).decode("ascii")
    return base64.b64encode(raw).decode("ascii")


def decode_text(b64: str) -> tuple[bool, str]:
    try:
        clean = _clean_b64(b64)
        raw = _decode_bytes(clean)
        try:
            return True, raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return True, raw.decode("cp1251")
            except UnicodeDecodeError:
                return False, "decode_error: not_text"
    except Exception as e:
        return False, f"decode_error: {e}"


def _clean_b64(s: str) -> str:
    return "".join(
        c for c in s
        if c.isalnum() or c in "+/=_-"
    )


def _decode_bytes(clean: str) -> bytes:
    pad = len(clean) % 4
    if pad:
        clean += "=" * (4 - pad)

    try:
        return base64.b64decode(clean)
    except binascii.Error:
        pass

    try:
        return base64.urlsafe_b64decode(clean)
    except binascii.Error as e:
        raise ValueError(str(e))


def encode_file(path: str, line_width: int = 76,
                on_progress=None, cancel_flag=None) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    total = os.path.getsize(path)
    processed = 0
    parts = []
    chunk_size = 3 * 1024

    with open(path, "rb") as f:
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Кодирование отменено")
            block = f.read(chunk_size)
            if not block:
                break
            parts.append(base64.b64encode(block).decode("ascii"))
            processed += len(block)
            if on_progress:
                on_progress(processed, total)

    big = "".join(parts)

    if line_width and line_width > 0:
        lines = [big[i:i + line_width] for i in range(0, len(big), line_width)]
        return "\n".join(lines)
    return big


def decode_file_to_bytes(b64: str,
                         on_progress=None, cancel_flag=None) -> bytes:

    clean = _clean_b64(b64)
    pad = len(clean) % 4
    if pad:
        clean += "=" * (4 - pad)

    try:
        return base64.b64decode(clean)
    except binascii.Error:
        return base64.urlsafe_b64decode(clean)


def decode_file_to_file(b64_path: str, out_path: str,
                        on_progress=None, cancel_flag=None) -> int:
    total = os.path.getsize(b64_path)
    processed = 0
    written = 0
    buffer = b""

    with open(b64_path, "rb") as f_in, open(out_path, "wb") as f_out:
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Декодирование отменено")
            block = f_in.read(64 * 1024)
            if not block:
                break

            clean = bytes(
                c for c in buffer + block
                if c not in b" \t\r\n" and
                (48 <= c <= 57 or 65 <= c <= 90 or 97 <= c <= 122 or c in b"+/=_-")
            )
            usable = len(clean) - (len(clean) % 4)
            if usable:
                try:
                    out = base64.b64decode(clean[:usable])
                except binascii.Error:
                    out = base64.urlsafe_b64decode(clean[:usable])
                f_out.write(out)
                written += len(out)
            buffer = clean[usable:]

            processed += len(block)
            if on_progress:
                on_progress(processed, total)

    if buffer:
        try:
            out = base64.b64decode(buffer)
        except binascii.Error:
            out = base64.urlsafe_b64decode(buffer)
        f_out.write(out)
        written += len(out)

    return written


def detect_decoded_type(raw: bytes) -> str:
    if not raw:
        return "empty"
    try:
        text = raw.decode("utf-8")
        printable = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
        if printable / len(text) > 0.9:
            return "text"
    except UnicodeDecodeError:
        pass

    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:4] == b"GIF8":
        return "image/gif"
    if raw[:4] == b"%PDF":
        return "application/pdf"
    if raw[:4] == b"PK\x03\x04":
        return "application/zip"
    if raw[:2] == b"\x1f\x8b":
        return "application/gzip"
    if raw[:4] == b"7z\xbc\xaf":
        return "application/x-7z-compressed"
    if raw[:4] == b"Rar!":
        return "application/x-rar-compressed"
    if raw[:3] == b"ID3" or raw[:2] == b"\xff\xfb":
        return "audio/mpeg"
    if raw[:4] == b"OggS":
        return "audio/ogg"
    if raw[:4] == b"fLaC":
        return "audio/flac"
    if raw[:4] == b"RIFF":
        return "audio/wav"
    if raw[4:8] == b"ftyp":
        return "video/mp4"
    if raw[:4] == b"\x7fELF":
        return "application/x-elf"
    if raw[:2] == b"MZ":
        return "application/x-dosexec"
    if raw[:16].startswith(b"SQLite format 3"):
        return "application/x-sqlite3"

    return "application/octet-stream"


def format_size(n: int) -> str:
    f = float(n)
    for suf in ("Б", "KiB", "MiB", "GiB", "TiB"):
        if f < 1024:
            return f"{int(f)} {suf}" if suf == "Б" else f"{f:.2f} {suf}"
        f /= 1024
    return f"{f:.2f} PiB"