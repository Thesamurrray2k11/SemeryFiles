import hashlib
import os
from typing import Callable


ALGO_LABELS = {
    "md5":       "MD5",
    "sha1":      "SHA-1",
    "sha224":    "SHA-224",
    "sha256":    "SHA-256",
    "sha384":    "SHA-384",
    "sha512":    "SHA-512",
    "sha3_256":  "SHA3-256",
    "sha3_512":  "SHA3-512",
    "blake2b":   "BLAKE2b",
    "blake2s":   "BLAKE2s",
}


DEFAULT_ORDER = [
    "md5", "sha1", "sha224", "sha256", "sha384",
    "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s",
]


def available_algorithms() -> list[str]:
    available = set(hashlib.algorithms_available)
    result = [a for a in DEFAULT_ORDER if a in available]
    return result


def label_for(algo: str) -> str:
    return ALGO_LABELS.get(algo, algo.upper())


def hash_file_multi(
    path: str,
    algorithms: list[str],
    chunk_size: int = 1 << 20,
    on_progress: Callable[[int, int], None] | None = None,
    cancel_flag: Callable[[], bool] | None = None,
) -> dict[str, str]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    total = os.path.getsize(path)

    hashers: dict[str, "hashlib._Hash"] = {}
    for algo in algorithms:
        hashers[algo] = hashlib.new(algo)

    processed = 0
    with open(path, "rb", buffering=0) as f:
        while True:
            if cancel_flag and cancel_flag():
                raise InterruptedError("Хеширование отменено")
            chunk = f.read(chunk_size)
            if not chunk:
                break
            for h in hashers.values():
                h.update(chunk)
            processed += len(chunk)
            if on_progress:
                on_progress(processed, total)

    return {algo: h.hexdigest() for algo, h in hashers.items()}