from .locales import (
    LOCALES,
    available_languages,
    get_translations,
    has_language,
)


class I18N:
    FALLBACK_LANGUAGE = "ru"

    def __init__(self, language: str = "ru"):
        self._lang = language if has_language(language) else "ru"

    @property
    def language(self) -> str:
        return self._lang

    @property
    def available(self) -> list[dict]:
        return available_languages()

    def set_language(self, code: str):
        if has_language(code):
            self._lang = code

    def t(self, key: str, default: str = "") -> str:
        text = get_translations(self._lang).get(key)
        if text is not None:
            return text

        if self._lang != self.FALLBACK_LANGUAGE:
            text = get_translations(self.FALLBACK_LANGUAGE).get(key)
            if text is not None:
                return text

        return default or key

    def __call__(self, key: str, default: str = "") -> str:
        return self.t(key, default)


i18n = I18N()


__all__ = ["i18n", "I18N", "available_languages", "has_language"]