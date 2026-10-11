import os
import stat
import mimetypes
import hashlib
from datetime import datetime


def _fmt_size(size: int, units: str = "binary") -> str:
    if units == "decimal":
        base = 1000
        suffixes = ["Б", "KB", "MB", "GB", "TB", "PB"]
    else:
        base = 1024
        suffixes = ["Б", "KiB", "MiB", "GiB", "TiB", "PiB"]

    f = float(size)
    for suf in suffixes:
        if f < base:
            if suf == "Б":
                return f"{int(f)} {suf}"
            return f"{f:.2f} {suf}"
        f /= base
    return f"{f:.2f} {suffixes[-1]}"


def _fmt_date(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M:%S")
    except (OSError, OverflowError, ValueError):
        return "—"


def _detect_kind(path: str) -> str:
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return "unknown"

    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG image"
    if head.startswith(b"\xff\xd8\xff"):
        return "JPEG image"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "GIF image"
    if head.startswith(b"BM"):
        return "BMP image"
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return "WebP image"
    if head.startswith(b"%PDF"):
        return "PDF document"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP / Office / JAR archive"
    if head.startswith(b"\x1f\x8b"):
        return "GZIP archive"
    if head.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7-Zip archive"
    if head.startswith(b"Rar!\x1a\x07"):
        return "RAR archive"
    if head.startswith(b"ID3") or head[0:2] == b"\xff\xfb":
        return "MP3 audio"
    if head.startswith(b"OggS"):
        return "OGG media"
    if head.startswith(b"fLaC"):
        return "FLAC audio"
    if head[4:8] == b"ftyp":
        return "MP4 / MOV video"
    if head.startswith(b"\x7fELF"):
        return "ELF executable"
    if head.startswith(b"MZ"):
        return "Windows executable (PE)"
    if head.startswith(b"SQLite format 3\x00"):
        return "SQLite database"
    return "unknown"


def _hash_file(path: str, algo: str = "sha256", chunk: int = 1 << 20) -> str:
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            while True:
                block = f.read(chunk)
                if not block:
                    break
                h.update(block)
    except OSError:
        return "—"
    return h.hexdigest()


def collect_info(path: str, units: str = "binary",
                 hash_algo: str = "sha256") -> dict:
    if not path or not os.path.exists(path):
        return {"ok": False, "error": "file_not_found", "groups": []}

    try:
        st = os.stat(path)
    except OSError as e:
        return {"ok": False, "error": str(e), "groups": []}

    name = os.path.basename(path)
    full = os.path.abspath(path)
    ext = os.path.splitext(name)[1].lstrip(".").upper() or "—"

    mime, _ = mimetypes.guess_type(path)
    mime = mime or "—"

    kind = _detect_kind(path)
    mode = st.st_mode
    perms = stat.filemode(mode)

    groups = []
    general = [
        ("info.field.name", name),
        ("info.field.path", full),
        ("info.field.size", _fmt_size(st.st_size, units)),
        ("info.field.size_bytes", f"{st.st_size:,} Б".replace(",", " ")),
        ("info.field.type_mime", mime),
        ("info.field.type_ext", ext),
        ("info.field.type_magic", kind),
    ]
    groups.append({"title_key": "info.group.general", "rows": general})

    dates = [
        ("info.field.created", _fmt_date(st.st_ctime)),
        ("info.field.modified", _fmt_date(st.st_mtime)),
        ("info.field.accessed", _fmt_date(st.st_atime)),
    ]
    groups.append({"title_key": "info.group.dates", "rows": dates})
    rights = [
        ("info.field.permissions", perms),
        ("info.field.mode_octal", oct(mode & 0o777)),
        ("info.field.readonly", "Да" if not (mode & stat.S_IWUSR) else "Нет"),
    ]
    groups.append({"title_key": "info.group.permissions", "rows": rights})

    hashes = [
        ("SHA-256", _hash_file(path, "sha256")),
        ("SHA-1",   _hash_file(path, "sha1")),
        ("MD5",     _hash_file(path, "md5")),
    ]
    groups.append({"title_key": "info.group.hashes", "rows": hashes})

    return {"ok": True, "error": None, "groups": groups}