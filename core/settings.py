from PySide6.QtCore import QSettings, QObject, Signal


class AppSettings(QObject):

    changed = Signal(str, object)

    DEFAULTS = {
        "theme": "light",
        "remember_theme": True,

        "default_dir": "",
        "reports_dir": "",

        "language": "ru",
        "size_units": "binary",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qs = QSettings("SemeryFiles", "SemeryFiles")

    def get(self, key: str):
        if key not in self.DEFAULTS:
            raise KeyError(f"Unknown setting: {key}")
        default = self.DEFAULTS[key]
        value = self._qs.value(key, default)

        if isinstance(default, bool):
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
            return bool(value)

        return value

    def set(self, key: str, value):
        if key not in self.DEFAULTS:
            raise KeyError(f"Unknown setting: {key}")
        self._qs.setValue(key, value)
        self._qs.sync()
        self.changed.emit(key, value)

    def reset_all(self):
        for key in self.DEFAULTS:
            self.set(key, self.DEFAULTS[key])

    @property
    def theme(self) -> str:
        return self.get("theme")

    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)

    @property
    def remember_theme(self) -> bool:
        return self.get("remember_theme")

    @remember_theme.setter
    def remember_theme(self, value: bool):
        self.set("remember_theme", value)

    @property
    def default_dir(self) -> str:
        return self.get("default_dir")

    @default_dir.setter
    def default_dir(self, value: str):
        self.set("default_dir", value)

    @property
    def reports_dir(self) -> str:
        return self.get("reports_dir")

    @reports_dir.setter
    def reports_dir(self, value: str):
        self.set("reports_dir", value)

    @property
    def language(self) -> str:
        return self.get("language")

    @language.setter
    def language(self, value: str):
        self.set("language", value)

    @property
    def size_units(self) -> str:
        return self.get("size_units")

    @size_units.setter
    def size_units(self, value: str):
        self.set("size_units", value)