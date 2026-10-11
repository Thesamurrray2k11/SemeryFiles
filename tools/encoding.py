import os
import codecs


BOMS = [
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF8,     "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
]

CANDIDATES = [
    ("utf-8",       "UTF-8",        100),
    ("utf-16-le",   "UTF-16 LE",     85),
    ("utf-16-be",   "UTF-16 BE",     85),
    ("cp1251",      "Windows-1251",  70),
    ("cp866",       "DOS (CP866)",   60),
    ("koi8-r",      "KOI8-R",        55),
    ("iso-8859-5",  "ISO-8859-5",    45),
    ("mac-cyrillic","Mac Cyrillic",  40),
    ("cp1252",      "Windows-1252",  35),
    ("iso-8859-1",  "ISO-8859-1",    30),
]


RU_LETTERS = set("оеаинтсрвлкмдпуяызьгбчйхжшюцщэфъё")
RU_UPPER = set("ОЕАИНТСРВЛКМДПУЯЫЗЬГБЧЙХЖШЮЦЩЭФЪЁ")

EN_LETTERS = set("etaoinshrdlucmfwypvbgkjqxz")
EN_UPPER = set("ETAOINSHRDLUCMFWYPVBGKJQXZ")


def _read_head(path: str, n: int = 65536) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except OSError:
        return b""


def detect_bom(data: bytes) -> str | None:
    for bom, enc in BOMS:
        if data.startswith(bom):
            return enc
    return None


def _score_text(text: str) -> float:
    if not text:
        return 0.0

    total = len(text)
    letters = 0
    ru = 0
    en = 0
    control = 0
    replacement = 0

    for ch in text:
        if ch == "\ufffd":
            replacement += 1
        elif ch.isalpha():
            letters += 1
            if ch in RU_LETTERS or ch in RU_UPPER:
                ru += 1
            elif ch.lower() in EN_LETTERS:
                en += 1
        elif ch in "\n\r\t":
            pass
        elif ord(ch) < 32 and ch not in "\n\r\t":
            control += 1

    if replacement > 0:
        return -1.0

    letter_ratio = letters / total
    control_penalty = control / total
    cyr_or_lat = (ru + en) / max(1, letters)

    score = letter_ratio * 50 + cyr_or_lat * 30 - control_penalty * 200
    return score


def detect_encoding(path: str, sample_size: int = 65536) -> dict:
    if not path or not os.path.isfile(path):
        return {"ok": False, "error": "file_not_found", "candidates": []}

    try:
        data = _read_head(path, sample_size)
    except OSError as e:
        return {"ok": False, "error": str(e), "candidates": []}

    if not data:
        return {
            "ok": False, "error": "empty_file",
            "encoding": "utf-8", "display_name": "UTF-8",
            "confidence": 0, "has_bom": False,
            "candidates": [], "sample": "", "char_count": 0,
        }

    bom_enc = detect_bom(data)
    if bom_enc:
        display = next(
            (d for n, d, _ in CANDIDATES if n == bom_enc),
            bom_enc.upper()
        )
        try:
            text = data.decode(bom_enc, errors="replace")
        except Exception:
            text = ""
        return {
            "ok": True, "error": None,
            "encoding": bom_enc,
            "display_name": f"{display}  (BOM)",
            "confidence": 100,
            "has_bom": True,
            "candidates": [{"name": bom_enc, "display": display, "score": 100}],
            "sample": text[:2048],
            "char_count": len(text),
        }

    candidates = []
    for name, display, priority in CANDIDATES:
        try:
            text = data.decode(name, errors="strict")
        except UnicodeDecodeError:
            try:
                text = data.decode(name, errors="replace")
                if "\ufffd" in text:
                    continue
            except Exception:
                continue
        except Exception:
            continue

        score = _score_text(text) + priority * 0.1
        if score > 0:
            candidates.append({
                "name": name,
                "display": display,
                "score": round(score, 2),
                "text": text,
            })

    if not candidates:
        text = data.decode("utf-8", errors="replace")
        return {
            "ok": True, "error": None,
            "encoding": "utf-8",
            "display_name": "UTF-8  (с потерями)",
            "confidence": 0,
            "has_bom": False,
            "candidates": [],
            "sample": text[:2048],
            "char_count": len(text),
        }

    candidates.sort(key=lambda c: c["score"], reverse=True)
    best = candidates[0]

    if len(candidates) >= 2:
        first, second = candidates[0]["score"], candidates[1]["score"]
        if first <= 0:
            conf = 0
        else:
            gap = (first - second) / max(first, 1)
            conf = int(min(100, max(20, gap * 100 + 50)))
    else:
        conf = 95

    return {
        "ok": True,
        "error": None,
        "encoding": best["name"],
        "display_name": best["display"],
        "confidence": conf,
        "has_bom": False,
        "candidates": [
            {"name": c["name"], "display": c["display"], "score": c["score"]}
            for c in candidates[:6]
        ],
        "sample": best["text"][:2048],
        "char_count": len(best["text"]),
    }


def convert_file(src: str, dst: str, src_enc: str, dst_enc: str = "utf-8") -> None:
    decoder = codecs.getincrementaldecoder(src_enc)(errors="replace")
    chunk_size = 1 << 20

    with open(src, "rb") as f_in, open(dst, "wb") as f_out:
        while True:
            block = f_in.read(chunk_size)
            if not block:
                break
            text = decoder.decode(block)
            f_out.write(text.encode(dst_enc, errors="replace"))
        tail = decoder.decode(b"", final=True)
        if tail:
            f_out.write(tail.encode(dst_enc, errors="replace"))