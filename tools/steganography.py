import os
import struct
import hashlib

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


MAGIC = b"STEG"
FLAG_PLAIN = 0x00
FLAG_ENCRYPTED = 0x01

HEADER_SIZE = 10
NONCE_SIZE = 12
SALT_SIZE = 16
KEY_ITERATIONS = 200_000


BIT_MASKS = {
    1: (0xFE, 0x01),
    2: (0xFC, 0x03),
}
def is_available() -> bool:
    return PIL_AVAILABLE


def _crypto_available() -> bool:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa
        return True
    except ImportError:
        return False


def capacity_bytes(image_path: str, bits_per_channel: int = 1) -> int:
    if not PIL_AVAILABLE or bits_per_channel not in (1, 2):
        return 0
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            total_bits = w * h * 3 * bits_per_channel
            total_bytes = total_bits // 8
            overhead = HEADER_SIZE + SALT_SIZE + NONCE_SIZE + 16
            return max(0, total_bytes - overhead)
    except Exception:
        return 0


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt,
        KEY_ITERATIONS, dklen=32,
    )


def _encrypt(payload: bytes, password: str) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import secrets

    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    key = _derive_key(password, salt)
    ct = AESGCM(key).encrypt(nonce, payload, associated_data=None)
    return salt + nonce + ct


def _decrypt(blob: bytes, password: str) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if len(blob) < SALT_SIZE + NONCE_SIZE + 16:
        raise ValueError("Недостаточно данных для расшифровки")

    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ct = blob[SALT_SIZE + NONCE_SIZE:]
    key = _derive_key(password, salt)
    return AESGCM(key).decrypt(nonce, ct, associated_data=None)


def _build_payload(data: bytes, password: str | None,
                   bits_per_channel: int) -> bytes:
    if password:
        if not _crypto_available():
            raise RuntimeError("Библиотека cryptography не установлена")
        body = _encrypt(data, password)
        flags = FLAG_ENCRYPTED
    else:
        body = data
        flags = FLAG_PLAIN

    header = (
        MAGIC
        + struct.pack(">I", len(body))
        + bytes([flags])
        + bytes([bits_per_channel])
    )
    return header + body


def _parse_payload_header(raw: bytes) -> tuple[int, int, int]:
    if len(raw) < HEADER_SIZE:
        raise ValueError("Заголовок слишком короткий")
    if raw[:4] != MAGIC:
        raise ValueError("no_magic")
    length = struct.unpack(">I", raw[4:8])[0]
    flags = raw[8]
    bits = raw[9]
    if bits not in (1, 2):
        raise ValueError("Некорректное значение битов на канал")
    return length, flags, bits


def hide_in_image(
    src_image: str,
    dst_image: str,
    data: bytes,
    password: str | None = None,
    bits_per_channel: int = 1,
) -> dict:
    if not PIL_AVAILABLE:
        return {"ok": False, "error": "no_pillow", "embedded": 0}
    if bits_per_channel not in (1, 2):
        return {"ok": False, "error": "bad_bits", "embedded": 0}
    if not os.path.isfile(src_image):
        return {"ok": False, "error": "file_not_found", "embedded": 0}

    try:
        payload = _build_payload(data, password, bits_per_channel)
    except Exception as e:
        return {"ok": False, "error": str(e), "embedded": 0}

    try:
        with Image.open(src_image) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            if img.mode == "RGBA":
                pixels = list(img.getdata())
                channels = 4
                use_channels = 3
            else:
                img = img.convert("RGB")
                pixels = list(img.getdata())
                channels = 3
                use_channels = 3
            w, h = img.size

        total_bits = w * h * use_channels * bits_per_channel
        total_bytes = total_bits // 8

        if len(payload) > total_bytes:
            return {
                "ok": False,
                "error": f"capacity_exceeded: {len(payload)} > {total_bytes}",
                "embedded": 0,
            }

        bit_stream = []
        for byte in payload:
            for i in range(7, -1, -1):
                bit_stream.append((byte >> i) & 1)

        clear_mask, write_mask = BIT_MASKS[bits_per_channel]

        bit_index = 0
        new_pixels = []
        for pixel in pixels:
            new_px = list(pixel)
            for ch in range(use_channels):
                if bit_index + bits_per_channel <= len(bit_stream):
                    val = 0
                    for _ in range(bits_per_channel):
                        val = (val << 1) | bit_stream[bit_index]
                        bit_index += 1
                    new_px[ch] = (new_px[ch] & clear_mask) | val
            new_pixels.append(tuple(new_px))

        mode = "RGBA" if channels == 4 else "RGB"
        out_img = Image.new(mode, (w, h))
        out_img.putdata(new_pixels)
        out_img.save(dst_image, format="PNG", optimize=True)

        return {"ok": True, "error": None, "embedded": len(payload)}
    except Exception as e:
        return {"ok": False, "error": str(e), "embedded": 0}


def extract_from_image(
    src_image: str,
    password: str | None = None,
    max_payload: int = 100 * 1024 * 1024,
) -> dict:
    if not PIL_AVAILABLE:
        return {"ok": False, "error": "no_pillow", "data": b"", "flags": 0, "size": 0}
    if not os.path.isfile(src_image):
        return {"ok": False, "error": "file_not_found", "data": b"", "flags": 0, "size": 0}

    try:
        with Image.open(src_image) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            pixels = list(img.getdata())
            use_channels = 3

        lsb_bits = []
        for pixel in pixels:
            for ch in range(use_channels):
                lsb_bits.append(pixel[ch] & 1)

        def _read_bytes_1bit(start_bit: int, n: int) -> bytes:
            if start_bit + n * 8 > len(lsb_bits):
                raise ValueError("not_enough")
            out = bytearray()
            for i in range(n):
                b = 0
                for j in range(8):
                    b = (b << 1) | lsb_bits[start_bit + i * 8 + j]
                out.append(b)
            return bytes(out)

        header_1 = None
        try:
            header_1 = _read_bytes_1bit(0, HEADER_SIZE)
        except Exception:
            pass

        if header_1 is not None and header_1[:4] == MAGIC:
            try:
                length, flags, bits = _parse_payload_header(header_1)
            except ValueError as e:
                return {"ok": False, "error": str(e),
                        "data": b"", "flags": 0, "size": 0}

            if bits == 1:
                return _read_and_finalize(
                    lsb_bits, 1, length, flags, password, max_payload
                )
        return _extract_2bit(pixels, use_channels, password, max_payload)

    except Exception as e:
        return {"ok": False, "error": str(e), "data": b"", "flags": 0, "size": 0}


def _read_and_finalize(bits, bits_per_channel: int,
                       length: int, flags: int,
                       password, max_payload) -> dict:
    if length <= 0 or length > max_payload:
        return {"ok": False, "error": f"bad_length: {length}",
                "data": b"", "flags": flags, "size": 0}
    header_bits = HEADER_SIZE * 8
    total_needed = header_bits + length * 8
    if len(bits) < total_needed:
        return {"ok": False, "error": "truncated",
                "data": b"", "flags": flags, "size": 0}

    body = bytearray()
    for i in range(length):
        b = 0
        for j in range(8):
            idx = header_bits + i * 8 + j
            b = (b << 1) | bits[idx]
        body.append(b)
    body = bytes(body)

    if flags == FLAG_ENCRYPTED:
        if not password:
            return {"ok": False, "error": "password_required",
                    "data": b"", "flags": flags, "size": 0}
        try:
            data = _decrypt(body, password)
        except Exception:
            return {"ok": False, "error": "wrong_password",
                    "data": b"", "flags": flags, "size": 0}
        return {"ok": True, "error": None, "data": data,
                "flags": flags, "size": len(data)}

    return {"ok": True, "error": None, "data": body,
            "flags": flags, "size": len(body)}


def _extract_2bit(pixels, use_channels: int, password, max_payload) -> dict:
    values = []
    for pixel in pixels:
        for ch in range(use_channels):
            values.append(pixel[ch] & 0x03)

    def _read_bytes(start_val: int, n: int) -> bytes:
        needed_values = n * 4
        if start_val + needed_values > len(values):
            raise ValueError("not_enough")
        out = bytearray()
        v_idx = start_val
        for _ in range(n):
            byte = 0
            for _ in range(4):
                byte = (byte << 2) | values[v_idx]
                v_idx += 1
            out.append(byte)
        return bytes(out)

    try:
        header = _read_bytes(0, HEADER_SIZE)
    except ValueError:
        return {"ok": False, "error": "no_magic",
                "data": b"", "flags": 0, "size": 0}

    if header[:4] != MAGIC:
        return {"ok": False, "error": "no_magic",
                "data": b"", "flags": 0, "size": 0}

    try:
        length, flags, bits = _parse_payload_header(header)
    except ValueError as e:
        return {"ok": False, "error": str(e),
                "data": b"", "flags": 0, "size": 0}

    if bits != 2:
        return {"ok": False, "error": "no_magic",
                "data": b"", "flags": 0, "size": 0}

    if length <= 0 or length > max_payload:
        return {"ok": False, "error": f"bad_length: {length}",
                "data": b"", "flags": flags, "size": 0}

    try:
        body = _read_bytes(HEADER_SIZE * 4, length)
    except ValueError:
        return {"ok": False, "error": "truncated",
                "data": b"", "flags": flags, "size": 0}

    if flags == FLAG_ENCRYPTED:
        if not password:
            return {"ok": False, "error": "password_required",
                    "data": b"", "flags": flags, "size": 0}
        try:
            data = _decrypt(body, password)
        except Exception:
            return {"ok": False, "error": "wrong_password",
                    "data": b"", "flags": flags, "size": 0}
        return {"ok": True, "error": None, "data": data,
                "flags": flags, "size": len(data)}

    return {"ok": True, "error": None, "data": body,
            "flags": flags, "size": len(body)}