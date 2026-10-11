import os


DEFAULT_BLOCK = 16 * 1024
MAX_VIEW_BYTES = 16 * 1024 * 1024


def file_size(path: str) -> int:
    return os.path.getsize(path)


def read_block(path: str, offset: int, size: int = DEFAULT_BLOCK) -> bytes:
    with open(path, "rb") as f:
        f.seek(offset)
        return f.read(size)


def find_pattern(
    path: str,
    pattern: bytes,
    start: int = 0,
    max_hits: int = 1000,
    chunk: int = 1 << 20,
) -> list[int]:
    if not pattern:
        return []

    hits: list[int] = []
    tail_len = len(pattern) - 1
    tail = b""

    with open(path, "rb") as f:
        f.seek(start)
        pos = start
        while True:
            block = f.read(chunk)
            if not block:
                break
            buf = tail + block
            buf_start = pos - len(tail)

            idx = 0
            while True:
                i = buf.find(pattern, idx)
                if i == -1:
                    break
                hits.append(buf_start + i)
                if len(hits) >= max_hits:
                    return hits
                idx = i + 1

            tail = buf[-tail_len:] if tail_len > 0 else b""
            pos += len(block)

    return hits


def parse_hex_pattern(text: str) -> bytes | None:
    cleaned = (
        text.replace(" ", "")
            .replace("-", "")
            .replace(":", "")
            .replace("0x", "")
            .replace("0X", "")
    )
    if not cleaned:
        return None
    if len(cleaned) % 2 != 0:
        return None
    try:
        return bytes.fromhex(cleaned)
    except ValueError:
        return None


def parse_ascii_pattern(text: str) -> bytes:
    return text.encode("utf-8", errors="replace")