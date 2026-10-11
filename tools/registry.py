MAIN_TOOLS = [
    {
        "id": "info",
        "icon": "ℹ",
        "name": "Информация о файле",
        "desc": "Размер, тип, даты, владелец и права доступа.",
        "color": "c_info",
        "group": "Анализ",
        "main": True,
        "impl": "info",
    },
    {
        "id": "hash",
        "icon": "#",
        "name": "Хеширование",
        "desc": "SHA-256, SHA-512, MD5, BLAKE3 — контрольные суммы.",
        "color": "c_hash",
        "group": "Анализ",
        "main": True,
        "impl": "hash",
    },
    {
        "id": "meta",
        "icon": "☷",
        "name": "Метаданные",
        "desc": "EXIF, ID3, свойства PDF и Office-документов.",
        "color": "c_meta",
        "group": "Анализ",
        "main": True,
        "impl": "meta",
    },
    {
        "id": "hex",
        "icon": "▦",
        "name": "Hex-просмотр",
        "desc": "Содержимое файла в шестнадцатеричном виде.",
        "color": "c_hex",
        "group": "Анализ",
        "main": True,
        "impl": "hex",
    },
    {
        "id": "convert",
        "icon": "⇋",
        "name": "Конвертация",
        "desc": "Кодировка, формат, пересчёт контрольных сумм.",
        "color": "c_convert",
        "group": "Утилиты",
        "main": True,
        "impl": "convert",
    },
]


EXTRA_TOOLS = [
    {
        "id": "encoding",
        "icon": "⌘",
        "name": "Определение кодировки",
        "desc": "Распознаёт UTF-8, UTF-16, Windows-1251 и другие.",
        "color": "c_info",
        "group": "Анализ",
        "main": False,
        "impl": "encoding",
    },
    {
        "id": "base64",
        "icon": "⬡",
        "name": "Base64",
        "desc": "Кодирование и декодирование текста и файлов.",
        "color": "c_convert",
        "group": "Утилиты",
        "main": False,
        "impl": "base64",
    },
    {
        "id": "permissions",
        "icon": "⚿",
        "name": "Права доступа",
        "desc": "Просмотр и изменение прав файла (Unix/Windows).",
        "color": "c_settings",
        "group": "Утилиты",
        "main": False,
        "impl": "permissions",
    },
    {
        "id": "regex",
        "icon": ".*",
        "name": "Regex-тестер",
        "desc": "Поиск и замена по регулярным выражениям.",
        "color": "c_hash",
        "group": "Разработка",
        "main": False,
        "impl": "regex",
    },
    {
        "id": "sqlite",
        "icon": "▤",
        "name": "SQLite Viewer",
        "desc": "Просмотр и редактирование SQLite баз данных.",
        "color": "c_search",
        "group": "Анализ",
        "main": False,
        "impl": "sqlite",
    },
    {
        "id": "password",
        "icon": "⚷",
        "name": "Генератор паролей",
        "desc": "Пароли, UUID, парольные фразы и hex-строки.",
        "color": "c_report",
        "group": "Утилиты",
        "main": False,
        "impl": "password",
    },
    {
        "id": "fonts",
        "icon": "ƒ",
        "name": "Просмотр шрифтов",
        "desc": "Разбор TTF, OTF, TTC, WOFF: имена, метрики, глифы.",
        "color": "c_report",
        "group": "Анализ",
        "main": False,
        "impl": "fonts",
    },
    {
        "id": "exif_clean",
        "icon": "⌦",
        "name": "Санитайзер EXIF",
        "desc": "Удаление GPS, дат, камеры и автора из фото.",
        "color": "c_meta",
        "group": "Анализ",
        "main": False,
        "impl": "exif_clean",
    },
    {
        "id": "qr",
        "icon": "▩",
        "name": "QR-коды",
        "desc": "Генерация и декодирование QR-кодов.",
        "color": "c_info",
        "group": "Утилиты",
        "main": False,
        "impl": "qr",
    },
    {
        "id": "stego",
        "icon": "◐",
        "name": "Стеганография",
        "desc": "Скрытие текста или файла в PNG (LSB).",
        "color": "c_convert",
        "group": "Безопасность",
        "main": False,
        "impl": "stego",
    },
]


ALL_TOOLS = MAIN_TOOLS + EXTRA_TOOLS


def get_tool(tool_id: str) -> dict | None:
    for t in ALL_TOOLS:
        if t["id"] == tool_id:
            return t
    return None


def search_tools(query: str, group: str | None = None) -> list[dict]:
    pool = ALL_TOOLS
    if group:
        pool = [t for t in pool if t.get("group") == group]
    if not query:
        return list(pool)
    q = query.lower().strip()
    result = []
    for t in pool:
        haystack = f"{t['name']} {t['desc']}".lower()
        if q in haystack:
            result.append(t)
    return result


def list_groups() -> list[str]:
    return sorted({t.get("group", "Другое") for t in ALL_TOOLS})