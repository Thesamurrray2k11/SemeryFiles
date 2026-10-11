import secrets
import string
import uuid
import math


LOWERCASE = string.ascii_lowercase           # a-z
UPPERCASE = string.ascii_uppercase           # A-Z
DIGITS    = string.digits                    # 0-9
SYMBOLS   = "!@#$%^&*()-_=+[]{};:,.<>?/|~"   # спецсимволы
SIMILAR   = "il1Lo0O"                        # похожие символы
AMBIGUOUS = "{}[]()/\\'\"`~,;:.<>"           # неоднозначные в некоторых шрифтах


RU_WORDS = [
    "сокол", "ветер", "камень", "море", "звезда", "лес", "река", "гром",
    "север", "юг", "восток", "запад", "дракон", "феникс", "тигр", "волк",
    "медведь", "лиса", "сова", "кот", "собака", "птица", "гора", "долина",
    "облако", "дождь", "снег", "лёд", "огонь", "пепел", "сталь", "меч",
    "щит", "клинок", "лук", "стрела", "книга", "перо", "чернила", "свеча",
]


def generate_password(
    length: int = 16,
    use_lowercase: bool = True,
    use_uppercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_similar: bool = False,
    exclude_ambiguous: bool = False,
    require_each_type: bool = True,
) -> str:
    pools = []
    if use_lowercase:
        pools.append(LOWERCASE)
    if use_uppercase:
        pools.append(UPPERCASE)
    if use_digits:
        pools.append(DIGITS)
    if use_symbols:
        pools.append(SYMBOLS)

    if not pools:
        raise ValueError("Не выбран ни один набор символов")

    def filter_pool(pool: str) -> str:
        result = pool
        if exclude_similar:
            result = "".join(c for c in result if c not in SIMILAR)
        if exclude_ambiguous:
            result = "".join(c for c in result if c not in AMBIGUOUS)
        return result

    filtered = [filter_pool(p) for p in pools]
    filtered = [p for p in filtered if p]
    if not filtered:
        raise ValueError("После фильтрации не осталось символов")

    length = max(length, len(filtered) if require_each_type else 1)

    chars = []
    if require_each_type:
        for pool in filtered:
            chars.append(secrets.choice(pool))

    full_pool = "".join(filtered)
    remaining = length - len(chars)
    for _ in range(remaining):
        chars.append(secrets.choice(full_pool))

    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars)


def estimate_strength(password: str) -> dict:
    if not password:
        return {"entropy": 0, "score": 0, "label": "weak", "crack_time": "—"}

    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(not c.isalnum() for c in password): pool += len(SYMBOLS)
    if any(ord(c) > 127 for c in password): pool += 100

    if pool == 0:
        pool = 1

    entropy = len(password) * math.log2(pool)

    if entropy < 28:
        score, label = 0, "weak"
    elif entropy < 40:
        score, label = 1, "fair"
    elif entropy < 60:
        score, label = 2, "good"
    elif entropy < 90:
        score, label = 3, "strong"
    else:
        score, label = 4, "excellent"

    attempts = 2 ** entropy
    seconds = attempts / 1e11
    crack_time = _humanize_seconds(seconds)

    return {
        "entropy": round(entropy, 1),
        "score": score,
        "label": label,
        "crack_time": crack_time,
    }


def _humanize_seconds(s: float) -> str:
    if s < 1:
        return "мгновенно"
    if s < 60:
        return f"{int(s)} сек"
    if s < 3600:
        return f"{int(s / 60)} мин"
    if s < 86400:
        return f"{int(s / 3600)} ч"
    if s < 86400 * 365:
        return f"{int(s / 86400)} дн"
    if s < 86400 * 365 * 1000:
        return f"{int(s / (86400 * 365))} лет"
    if s < 86400 * 365 * 1e9:
        return f"{s / (86400 * 365):.0f} лет"
    return "миллиарды лет"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_uuid_list(count: int = 1) -> list[str]:
    return [str(uuid.uuid4()) for _ in range(count)]

def generate_passphrase(
    word_count: int = 4,
    separator: str = "-",
    add_digit: bool = True,
    capitalize: bool = True,
) -> str:
    words = []
    for _ in range(max(2, word_count)):
        w = secrets.choice(RU_WORDS)
        if capitalize:
            w = w.capitalize()
        words.append(w)

    result = separator.join(words)
    if add_digit:
        result += separator + str(secrets.randbelow(100))
    return result


def generate_hex(byte_count: int = 16) -> str:
    return secrets.token_hex(byte_count)


def generate_base64(byte_count: int = 16) -> str:
    import base64
    raw = secrets.token_bytes(byte_count)
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")