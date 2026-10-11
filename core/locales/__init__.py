import importlib

LOCALES: dict[str, dict] = {}

_KNOWN_LOCALES = [
    "ru",
]


def _discover():
    for module_name in _KNOWN_LOCALES:
        full_name = f"{__name__}.{module_name}"
        try:
            module = importlib.import_module(full_name)
        except Exception as e:
            print(f"[i18n] failed to load {module_name}: {e}")
            continue

        code = getattr(module, "LANGUAGE_CODE", None)
        translations = getattr(module, "TRANSLATIONS", None)

        if not code or not isinstance(translations, dict):
            continue

        LOCALES[code] = {
            "code": code,
            "name": getattr(module, "LANGUAGE_NAME", code),
            "name_en": getattr(module, "LANGUAGE_NAME_EN", code),
            "locale": getattr(module, "LOCALE", ""),
            "translations": translations,
        }


def available_languages() -> list[dict]:
    return sorted(
        [{"code": v["code"], "name": v["name"]} for v in LOCALES.values()],
        key=lambda x: x["name"],
    )


def get_translations(code: str) -> dict:
    entry = LOCALES.get(code)
    return entry["translations"] if entry else {}


def has_language(code: str) -> bool:
    return code in LOCALES


_discover()
